# -*- coding: utf-8 -*-
#
# This file is part of Invenio Globus KCWorks.
# Copyright (C) 2024-2025 MESH Research.
#
# Invenio Globus KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for OAuth functionality."""

import pytest
from invenio_globus_kcworks.oauth import (
    get_globus_access_token,
    list_user_collections,
    make_globus_api_request,
)


def test_get_globus_access_token_no_user(app):
    """Test getting access token with no authenticated user."""
    with app.test_request_context():
        token = get_globus_access_token(None)
        assert token is None


def test_list_user_collections_no_user(app):
    """Test listing collections with no authenticated user."""
    with app.test_request_context():
        collections = list_user_collections(None)
        assert collections == []


def test_make_globus_api_request_no_user(app):
    """Test making API request with no authenticated user."""
    with app.test_request_context():
        with pytest.raises(Exception):
            make_globus_api_request(None, "https://api.example.com")
