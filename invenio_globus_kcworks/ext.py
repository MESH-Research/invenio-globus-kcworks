# -*- coding: utf-8 -*-
#
# This file is part of Invenio Globus KCWorks.
# Copyright (C) 2024-2025 MESH Research.
#
# Invenio Globus KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Globus KCWorks extension."""

from flask import Flask
from invenio_globus_kcworks import __version__


class InvenioGlobusKCWorks:
    """Invenio Globus KCWorks extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["invenio-globus-kcworks"] = self

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault("INVENIO_GLOBUS_KCWORKS_VERSION", __version__)

        # Load configuration from this package
        from invenio_globus_kcworks.config import (
            OAUTHCLIENT_REMOTE_APPS,
            GLOBUS_TRANSFER_APP_CREDENTIALS,
            OAUTHCLIENT_AUTO_REDIRECT_TO_EXTERNAL_LOGIN,
        )

        # Set configuration values if not already set
        app.config.setdefault("OAUTHCLIENT_REMOTE_APPS", {}).update(
            OAUTHCLIENT_REMOTE_APPS
        )
        app.config.setdefault(
            "GLOBUS_TRANSFER_APP_CREDENTIALS", GLOBUS_TRANSFER_APP_CREDENTIALS
        )
        app.config.setdefault(
            "OAUTHCLIENT_AUTO_REDIRECT_TO_EXTERNAL_LOGIN",
            OAUTHCLIENT_AUTO_REDIRECT_TO_EXTERNAL_LOGIN,
        )
