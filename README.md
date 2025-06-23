# Invenio Globus KCWorks

Globus OAuth integration for InvenioRDM instances, providing seamless access to Globus collections and file transfer capabilities.

## Features

- **OAuth 2.0 Authentication**: Secure authentication with Globus Auth
- **Transfer API Access**: Full access to Globus Transfer API with proper scopes
- **Token Management**: Automatic token storage and validation
- **User Interface**: Dashboard for managing collections and transfers
- **API Endpoints**: RESTful API for programmatic access
- **InvenioRDM Integration**: Seamless integration with InvenioRDM architecture

## Installation

### From PyPI

```bash
pip install invenio-globus-kcworks
```

### From Source

```bash
git clone https://github.com/MESH-Research/invenio-globus-kcworks.git
cd invenio-globus-kcworks
pip install -e .
```

## Setup

### 1. Register Your Application with Globus

1. Visit the [Globus Developer Console](https://developers.globus.org/)
2. Create a new application
3. Configure the following settings:
   - **App Name**: Your application name (e.g., "KCWorks Globus Integration")
   - **Redirect URLs**:
     - `http://localhost:5000/oauth/authorized/globus_transfer/` (for development)
     - `https://yourdomain.com/oauth/authorized/globus_transfer/` (for production)
   - **Scopes**:
     - `openid`
     - `email`
     - `profile`
     - `urn:globus:auth:scope:transfer.api.globus.org:all`

4. Note your **Client ID** and **Client Secret**

### 2. Configure Environment Variables

Set the following environment variables:

```bash
export GLOBUS_CLIENT_ID="your-client-id-here"
export GLOBUS_CLIENT_SECRET="your-client-secret-here"
```

### 3. Update InvenioRDM Configuration

Add the following to your `invenio.cfg`:

```python
# Import the custom Globus OAuth handler
from invenio_globus_kcworks.oauth import REMOTE_APP

OAUTHCLIENT_REMOTE_APPS = {
    'globus_transfer': REMOTE_APP,
}

# Globus Transfer OAuth credentials
GLOBUS_TRANSFER_APP_CREDENTIALS = dict(
    consumer_key=os.getenv('GLOBUS_CLIENT_ID', 'changeme'),
    consumer_secret=os.getenv('GLOBUS_CLIENT_SECRET', 'changeme'),
)
```

### 4. Restart the Application

After setting up the environment variables, restart your InvenioRDM application:

```bash
invenio run
```

## Usage

### For Users

1. **Connect Globus Account**:
   - Navigate to `/globus/dashboard`
   - Click "Connect Globus Account"
   - Complete the OAuth flow on Globus

2. **View Collections**:
   - After connecting, view your accessible collections
   - Use the dashboard to manage transfers

3. **Perform Transfers**:
   - Use the API endpoints to initiate transfers
   - Monitor transfer status

### For Developers

#### API Endpoints

- `GET /globus/dashboard` - User dashboard
- `GET /globus/collections` - List user's collections
- `GET /globus/collections/<collection_id>` - Get collection details
- `POST /globus/transfer` - Initiate a transfer
- `GET /globus/status` - Check connection status

#### Programmatic Usage

```python
from invenio_globus_kcworks.oauth import (
    get_globus_access_token,
    list_user_collections,
    make_globus_api_request
)

# Get user's collections
collections = list_user_collections(current_user)

# Make custom API calls
response = make_globus_api_request(
    current_user,
    'https://transfer.api.globus.org/v0.10/endpoint_search',
    data={'filter_scope': 'my-endpoints'}
)
```

#### Initiating a Transfer

```python
transfer_data = {
    'source_endpoint': 'source-collection-id',
    'dest_endpoint': 'destination-collection-id',
    'source_path': '/path/to/source/file',
    'dest_path': '/path/to/destination/file'
}

response = requests.post('/globus/transfer', json=transfer_data)
```

## Development

### Running Tests

```bash
pytest
```

### Building Documentation

```bash
cd docs
make html
```

### Code Style

This project uses:
- [Ruff](https://github.com/astral-sh/ruff) for linting
- [MyPy](https://mypy-lang.org/) for type checking
- [Black](https://black.readthedocs.io/) for code formatting

## Security Considerations

1. **Token Storage**: Access tokens are stored securely in the database
2. **Token Expiration**: Tokens are validated for expiration
3. **Scope Limitation**: Only necessary scopes are requested
4. **User Isolation**: Users can only access their own collections

## Troubleshooting

### Common Issues

1. **"No valid Globus access token available"**
   - User needs to reconnect their Globus account
   - Token may have expired

2. **"Application mis-configuration in Globus"**
   - Check your Client ID and Secret
   - Verify redirect URLs match exactly

3. **"Collection not found or access denied"**
   - User may not have access to the requested collection
   - Collection may be private or require additional permissions

### Debug Mode

Enable debug logging in your `invenio.cfg`:

```python
LOGGING_LEVEL = "DEBUG"
```

## API Reference

### Functions

#### `get_globus_access_token(user)`
Get the current user's valid Globus access token.

**Parameters:**
- `user`: The current authenticated user

**Returns:**
- Access token string if valid, None otherwise

#### `make_globus_api_request(user, endpoint, method='GET', data=None, headers=None)`
Make an authenticated request to the Globus API.

**Parameters:**
- `user`: The current authenticated user
- `endpoint`: The API endpoint URL
- `method`: HTTP method (default: 'GET')
- `data`: Request data (default: None)
- `headers`: Additional headers (default: None)

**Returns:**
- API response as JSON

#### `list_user_collections(user)`
List all collections accessible to the user.

**Parameters:**
- `user`: The current authenticated user

**Returns:**
- List of collection objects

#### `get_collection_info(user, collection_id)`
Get detailed information about a specific collection.

**Parameters:**
- `user`: The current authenticated user
- `collection_id`: The Globus collection ID

**Returns:**
- Collection information object

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [https://invenio-globus-kcworks.readthedocs.io/](https://invenio-globus-kcworks.readthedocs.io/)
- **Issues**: [https://github.com/MESH-Research/invenio-globus-kcworks/issues](https://github.com/MESH-Research/invenio-globus-kcworks/issues)
- **Email**: scottia4@msu.edu