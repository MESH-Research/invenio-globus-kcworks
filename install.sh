#!/bin/bash

# Installation script for invenio-globus-kcworks

set -e

echo "Installing invenio-globus-kcworks..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found. Please run this script from the package root directory."
    exit 1
fi

# Install the package in development mode
pip install -e .

echo "Package installed successfully!"
echo ""
echo "Next steps:"
echo "1. Set your Globus OAuth credentials as environment variables:"
echo "   export GLOBUS_CLIENT_ID='your-client-id'"
echo "   export GLOBUS_CLIENT_SECRET='your-client-secret'"
echo ""
echo "2. Update your InvenioRDM configuration to include:"
echo "   from invenio_globus_kcworks.oauth import REMOTE_APP"
echo "   OAUTHCLIENT_REMOTE_APPS = {'globus_transfer': REMOTE_APP}"
echo ""
echo "3. Restart your InvenioRDM application"
echo ""
echo "4. Access the dashboard at: /globus/dashboard"