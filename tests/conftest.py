# -*- coding: utf-8 -*-
#
# This file is part of Invenio Globus KCWorks.
# Copyright (C) 2024-2025 MESH Research.
#
# Invenio Globus KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import pytest
from flask import Flask
from invenio_globus_kcworks import InvenioGlobusKCWorks


@pytest.fixture()
def app():
    """Create Flask application for the tests."""
    app = Flask("testapp")
    app.config.update(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "GLOBUS_TRANSFER_APP_CREDENTIALS": {
                "consumer_key": "test-client-id",
                "consumer_secret": "test-client-secret",
            },
        }
    )
    InvenioGlobusKCWorks(app)
    return app
