# -*- coding: utf-8 -*-
#
# This file is part of Invenio Globus KCWorks.
# Copyright (C) 2024-2025 MESH Research.
#
# Invenio Globus KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Custom Globus OAuth handler for guest collection access."""

from datetime import UTC, datetime
from flask import current_app, redirect, url_for
from flask_login import current_user
from invenio_db import db
from invenio_oauthclient import current_oauthclient
from invenio_oauthclient.contrib.globus import (
    GlobusOAuthSettingsHelper,
    get_user_info,
    get_user_id,
)
from invenio_oauthclient.errors import OAuthResponseError
from invenio_oauthclient.handlers.rest import response_handler
from invenio_oauthclient.handlers.utils import require_more_than_one_external_account
from invenio_oauthclient.models import RemoteAccount
from invenio_oauthclient.oauth import oauth_link_external_id, oauth_unlink_external_id


class GlobusTransferOAuthSettingsHelper(GlobusOAuthSettingsHelper):
    """Extended Globus OAuth configuration for Transfer API access."""

    def __init__(
        self,
        title=None,
        description=None,
        base_url=None,
        app_key=None,
        precedence_mask=None,
        signup_options=None,
    ):
        """Constructor with extended scopes for Transfer API."""
        super().__init__(
            title or "Globus Transfer",
            description or "Access Globus guest collections and transfer data.",
            base_url or "https://auth.globus.org/v2/",
            app_key or "GLOBUS_TRANSFER_APP_CREDENTIALS",
            request_token_params={
                "scope": (
                    "openid email profile "
                    "urn:globus:auth:scope:transfer.api.globus.org:all"
                )
            },
            precedence_mask=precedence_mask,
            signup_options=signup_options,
        )

        self._handlers = dict(
            authorized_handler=(
                "invenio_oauthclient.handlers:authorized_signup_handler"
            ),
            disconnect_handler=("invenio_globus_kcworks.oauth:disconnect_handler"),
            signup_handler=dict(
                info="invenio_globus_kcworks.oauth:account_info",
                info_serializer=(
                    "invenio_globus_kcworks.oauth:account_info_serializer"
                ),
                setup="invenio_globus_kcworks.oauth:account_setup",
                view="invenio_oauthclient.handlers:signup_handler",
            ),
        )

        self._rest_handlers = dict(
            authorized_handler=(
                "invenio_oauthclient.handlers.rest:authorized_signup_handler"
            ),
            disconnect_handler=("invenio_globus_kcworks.oauth:disconnect_rest_handler"),
            signup_handler=dict(
                info="invenio_globus_kcworks.oauth:account_info",
                info_serializer=(
                    "invenio_globus_kcworks.oauth:account_info_serializer"
                ),
                setup="invenio_globus_kcworks.oauth:account_setup",
                view="invenio_oauthclient.handlers.rest:signup_handler",
            ),
            response_handler=(
                "invenio_oauthclient.handlers.rest:default_remote_response_handler"
            ),
            authorized_redirect_url="/",
            disconnect_redirect_url="/",
            signup_redirect_url="/",
            error_redirect_url="/",
        )


_globus_transfer_app = GlobusTransferOAuthSettingsHelper()

REMOTE_APP = _globus_transfer_app.remote_app
"""Globus Transfer remote application configuration."""
REMOTE_REST_APP = _globus_transfer_app.remote_rest_app
"""Globus Transfer remote rest application configuration."""


def account_info_serializer(remote, resp, user_info, user_id, **kwargs):
    """Serialize the account info response object.

    :param remote: The remote application.
    :param resp: The response of the `authorized` endpoint.
    :param user_info: The response of the `user info` endpoint.
    :param user_id: The user id.
    :returns: A dictionary with serialized user information.
    """
    return {
        "user": {
            "email": user_info["email"],
            "profile": {
                "username": user_info["username"],
                "full_name": user_info["name"],
            },
        },
        "external_id": user_id,
        "external_method": remote.name,
    }


def account_info(remote, resp):
    """Retrieve remote account information used to find local user.

    It returns a dictionary with the following structure:

    .. code-block:: python

        {
            'user': {
                'email': '...',
                'profile': {
                    'username': '...',
                    'full_name': '...',
                }
            },
            'external_id': 'globus-unique-identifier',
            'external_method': 'globus_transfer',
        }

    :param remote: The remote application.
    :param resp: The response of the `authorized` endpoint.
    :returns: A dictionary with the user information.
    """
    user_info = get_user_info(remote)
    user_id = get_user_id(remote, user_info["preferred_username"])

    handlers = current_oauthclient.signup_handlers[remote.name]
    # `remote` param automatically injected via `make_handler` helper
    return handlers["info_serializer"](resp, user_info, user_id=user_id)


def account_setup(remote, token, resp):
    """Perform additional setup after user has been logged in.

    This function stores the access token and user information for later use
    when making API calls to Globus Transfer.

    :param remote: The remote application.
    :param token: The token value.
    :param resp: The response.
    """
    info = get_user_info(remote)
    user_id = get_user_id(remote, info["preferred_username"])

    with db.session.begin_nested():
        # Store additional data including the access token for API calls
        token.remote_account.extra_data = {
            "login": info["username"],
            "id": user_id,
            "access_token": token.access_token,
            "token_expires_at": (
                token.expires_at.isoformat() if token.expires_at else None
            ),
            "refresh_token": token.refresh_token,
            "token_type": token.token_type,
        }

        # Create user <-> external id link.
        oauth_link_external_id(
            token.remote_account.user,
            dict(id=user_id, method=remote.name),
        )


def get_globus_access_token(user):
    """Get the current user's Globus access token.

    :param user: The current authenticated user.
    :returns: The access token if available and valid, None otherwise.
    """
    if not user.is_authenticated:
        return None

    remote_account = RemoteAccount.get(
        user_id=user.get_id(),
        client_id=current_app.config["GLOBUS_TRANSFER_APP_CREDENTIALS"]["consumer_key"],
    )

    if not remote_account or not remote_account.extra_data:
        return None

    extra_data = remote_account.extra_data
    access_token = extra_data.get("access_token")

    if not access_token:
        return None

    # Check if token is expired
    expires_at = extra_data.get("token_expires_at")
    if expires_at:
        try:
            expires_datetime = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if expires_datetime < datetime.now(UTC):
                # Token is expired, could implement refresh logic here
                current_app.logger.warning("Globus access token is expired")
                return None
        except (ValueError, TypeError):
            current_app.logger.warning("Could not parse token expiration date")

    return access_token


def make_globus_api_request(user, endpoint, method="GET", data=None, headers=None):
    """Make an authenticated request to the Globus API.

    :param user: The current authenticated user.
    :param endpoint: The API endpoint to call.
    :param method: HTTP method (GET, POST, etc.).
    :param data: Data to send with the request.
    :param headers: Additional headers to include.
    :returns: The API response.
    """
    import requests

    access_token = get_globus_access_token(user)
    if not access_token:
        raise OAuthResponseError("No valid Globus access token available", None, None)

    api_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    if headers:
        api_headers.update(headers)

    response = requests.request(
        method=method, url=endpoint, headers=api_headers, json=data
    )

    if response.status_code >= 400:
        raise OAuthResponseError(
            f"Globus API request failed: {response.status_code}", None, response
        )

    return response.json()


def list_user_collections(user):
    """List the user's accessible Globus collections.

    :param user: The current authenticated user.
    :returns: List of collections the user can access.
    """
    try:
        # Get user's endpoints (collections)
        response = make_globus_api_request(
            user,
            "https://transfer.api.globus.org/v0.10/endpoint_search",
            data={"filter_scope": "my-endpoints"},
        )
        return response.get("DATA", [])
    except OAuthResponseError as e:
        current_app.logger.error(f"Failed to list user collections: {e}")
        return []


def get_collection_info(user, collection_id):
    """Get information about a specific collection.

    :param user: The current authenticated user.
    :param collection_id: The Globus collection ID.
    :returns: Collection information.
    """
    try:
        response = make_globus_api_request(
            user, f"https://transfer.api.globus.org/v0.10/endpoint/{collection_id}"
        )
        return response
    except OAuthResponseError as e:
        current_app.logger.error(f"Failed to get collection info: {e}")
        return None


@require_more_than_one_external_account
def _disconnect(remote, *args, **kwargs):
    """Handle unlinking of remote account.

    :param remote: The remote application.
    :returns: The HTML response.
    """
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()

    remote_account = RemoteAccount.get(
        user_id=current_user.get_id(), client_id=remote.consumer_key
    )
    external_ids = [
        i.id for i in current_user.external_identifiers if i.method == remote.name
    ]

    if external_ids:
        oauth_unlink_external_id(dict(id=external_ids[0], method=remote.name))

    if remote_account:
        with db.session.begin_nested():
            remote_account.delete()


def disconnect_handler(remote, *args, **kwargs):
    """Handle unlinking of remote account.

    :param remote: The remote application.
    :returns: The HTML response.
    """
    _disconnect(remote, *args, **kwargs)
    return redirect(url_for("invenio_oauthclient_settings.index"))


def disconnect_rest_handler(remote, *args, **kwargs):
    """Handle unlinking of remote account.

    :param remote: The remote application.
    :returns: The HTML response.
    """
    _disconnect(remote, *args, **kwargs)
    redirect_url = current_app.config["OAUTHCLIENT_REST_REMOTE_APPS"][remote.name][
        "disconnect_redirect_url"
    ]
    return response_handler(remote, redirect_url)
