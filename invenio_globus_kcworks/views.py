# -*- coding: utf-8 -*-
#
# This file is part of Invenio Globus KCWorks.
# Copyright (C) 2024-2025 MESH Research.
#
# Invenio Globus KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Views for demonstrating Globus OAuth integration."""

from flask import Blueprint, current_app, jsonify, render_template, request
from flask_login import current_user, login_required
from invenio_oauthclient.models import RemoteAccount
from invenio_globus_kcworks.oauth import (
    get_collection_info,
    get_globus_access_token,
    list_user_collections,
    make_globus_api_request,
)


def create_blueprint(app):
    """Create the Invenio Globus KCWorks blueprint."""
    blueprint = Blueprint(
        "invenio_globus_kcworks",
        __name__,
        url_prefix="/globus",
        template_folder="templates",
    )

    @blueprint.route("/dashboard")
    @login_required
    def dashboard():
        """Show the Globus dashboard with user's collections."""
        # Check if user has connected their Globus account
        has_globus_account = False
        collections = []

        try:
            remote_account = RemoteAccount.get(
                user_id=current_user.get_id(),
                client_id=current_app.config["GLOBUS_TRANSFER_APP_CREDENTIALS"][
                    "consumer_key"
                ],
            )
            has_globus_account = remote_account is not None

            if has_globus_account:
                collections = list_user_collections(current_user)
        except Exception as e:
            current_app.logger.error(f"Error checking Globus account: {e}")

        return render_template(
            "invenio_globus_kcworks/dashboard.html",
            has_globus_account=has_globus_account,
            collections=collections,
            user=current_user,
        )

    @blueprint.route("/collections")
    @login_required
    def collections():
        """API endpoint to get user's collections."""
        try:
            collections = list_user_collections(current_user)
            return jsonify({"success": True, "collections": collections})
        except Exception as e:
            current_app.logger.error(f"Error fetching collections: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @blueprint.route("/collections/<collection_id>")
    @login_required
    def collection_detail(collection_id):
        """Get detailed information about a specific collection."""
        try:
            collection_info = get_collection_info(current_user, collection_id)
            if collection_info:
                return jsonify({"success": True, "collection": collection_info})
            else:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Collection not found or access denied",
                        }
                    ),
                    404,
                )
        except Exception as e:
            current_app.logger.error(f"Error fetching collection info: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @blueprint.route("/transfer", methods=["POST"])
    @login_required
    def initiate_transfer():
        """Initiate a file transfer between collections."""
        try:
            data = request.get_json()
            source_endpoint = data.get("source_endpoint")
            dest_endpoint = data.get("dest_endpoint")
            source_path = data.get("source_path")
            dest_path = data.get("dest_path")

            if not all([source_endpoint, dest_endpoint, source_path, dest_path]):
                return (
                    jsonify({"success": False, "error": "Missing required parameters"}),
                    400,
                )

            # Create transfer request
            transfer_data = {
                "DATA_TYPE": "transfer",
                "submission_id": None,  # Will be set by Globus
                "source_endpoint": source_endpoint,
                "destination_endpoint": dest_endpoint,
                "DATA": [
                    {
                        "DATA_TYPE": "transfer_item",
                        "source_path": source_path,
                        "destination_path": dest_path,
                    }
                ],
            }

            response = make_globus_api_request(
                current_user,
                "https://transfer.api.globus.org/v0.10/transfer",
                method="POST",
                data=transfer_data,
            )

            return jsonify(
                {
                    "success": True,
                    "transfer_id": response.get("task_id"),
                    "message": "Transfer initiated successfully",
                }
            )

        except Exception as e:
            current_app.logger.error(f"Error initiating transfer: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    @blueprint.route("/status")
    @login_required
    def status():
        """Check the status of the user's Globus connection."""
        try:
            access_token = get_globus_access_token(current_user)
            has_token = access_token is not None

            remote_account = RemoteAccount.get(
                user_id=current_user.get_id(),
                client_id=current_app.config["GLOBUS_TRANSFER_APP_CREDENTIALS"][
                    "consumer_key"
                ],
            )

            account_info = None
            if remote_account and remote_account.extra_data:
                account_info = {
                    "username": remote_account.extra_data.get("login"),
                    "globus_id": remote_account.extra_data.get("id"),
                    "has_valid_token": has_token,
                }

            return jsonify(
                {
                    "success": True,
                    "connected": remote_account is not None,
                    "has_valid_token": has_token,
                    "account_info": account_info,
                }
            )

        except Exception as e:
            current_app.logger.error(f"Error checking status: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    return blueprint
