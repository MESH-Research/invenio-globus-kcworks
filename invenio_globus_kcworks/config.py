# -*- coding: utf-8 -*-
#
# This file is part of Invenio Globus KCWorks.
# Copyright (C) 2024-2025 MESH Research.
#
# Invenio Globus KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Configuration for Invenio Globus KCWorks."""

import os

OAUTHCLIENT_REMOTE_APPS = {
    "globus_transfer": REMOTE_APP,
}  # configure external login providers

# Globus Transfer OAuth credentials
# You need to register your application at https://developers.globus.org/
# and get your client ID and secret
GLOBUS_TRANSFER_APP_CREDENTIALS = dict(
    consumer_key=os.getenv("GLOBUS_CLIENT_ID", "changeme"),
    consumer_secret=os.getenv("GLOBUS_CLIENT_SECRET", "changeme"),
)

# Auto-redirect to external login if enabled
OAUTHCLIENT_AUTO_REDIRECT_TO_EXTERNAL_LOGIN = False
