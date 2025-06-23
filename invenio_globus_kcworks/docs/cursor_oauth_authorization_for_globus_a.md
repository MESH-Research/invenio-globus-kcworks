# OAuth authorization for Globus API access
_Exported on 6/23/2025 at 15:22:40 EDT from Cursor (1.0.0)_

---

**User**

How could I have a user get OAuth authorization for their account on a Globus server and then use that authorization (and their account) to authorize API requests to perform operations on a Globus guest collection.

---

**Cursor**

Based on the Globus Auth API documentation you've referenced, here's how you can implement OAuth authorization for a user to access a Globus guest collection:

## Overview

The process involves implementing the OAuth 2.0 Authorization Code Grant flow, which is the preferred method for web applications. Here's the step-by-step approach:

## 1. Register Your Application

First, you need to register your application with Globus Auth to get OAuth 2.0 credentials:

1. Visit the [Globus Client Registration Page](https://developers.globus.org/)
2. Create a new client application
3. You'll receive a `client_id` and `client_secret`
4. Configure your redirect URI (where users will be sent after authorization)

## 2. Implement the OAuth Flow

### Step 1: Redirect User to Globus Auth

```python
import urllib.parse

def get_authorization_url(client_id, redirect_uri, scope):
    """
    Generate the authorization URL for the user to visit.
    
    Args:
        client_id: Your registered client ID
        redirect_uri: Where to redirect after authorization
        scope: The scopes you need (e.g., 'urn:globus:auth:scope:transfer.api.globus.org:all')
    """
    base_url = "https://auth.globus.org/v2/oauth2/authorize"
    
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'response_type': 'code',
        'state': 'your-random-state-value'  # For security
    }
    
    return f"{base_url}?{urllib.parse.urlencode(params)}"
```

### Step 2: Exchange Authorization Code for Access Token

```python
import requests

def exchange_code_for_token(client_id, client_secret, authorization_code, redirect_uri):
    """
    Exchange the authorization code for an access token.
    """
    token_url = "https://auth.globus.org/v2/oauth2/token"
    
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    
    return response.json()
```

### Step 3: Use the Access Token for API Requests

```python
def make_globus_api_request(access_token, endpoint, method='GET', data=None):
    """
    Make an authenticated request to the Globus API.
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.request(
        method=method,
        url=endpoint,
        headers=headers,
        json=data
    )
    response.raise_for_status()
    
    return response.json()
```

## 3. Complete Implementation Example

Here's a more complete example using Flask:

```python
from flask import Flask, request, redirect, session, url_for
import requests
import secrets

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Your Globus application credentials
CLIENT_ID = 'your-client-id'
CLIENT_SECRET = 'your-client-secret'
REDIRECT_URI = 'http://localhost:5000/callback'

# Scopes you need for guest collection access
SCOPES = [
    'urn:globus:auth:scope:transfer.api.globus.org:all',
    'urn:globus:auth:scope:auth.globus.org:view_identities'
]

@app.route('/login')
def login():
    """Start the OAuth flow."""
    # Generate a random state for security
    session['state'] = secrets.token_urlsafe(32)
    
    # Build authorization URL
    auth_url = "https://auth.globus.org/v2/oauth2/authorize"
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPES),
        'response_type': 'code',
        'state': session['state']
    }
    
    auth_url_with_params = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url_with_params)

@app.route('/callback')
def callback():
    """Handle the OAuth callback."""
    # Verify state parameter
    if request.args.get('state') != session.get('state'):
        return 'State verification failed', 400
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        return 'No authorization code received', 400
    
    # Exchange code for tokens
    token_data = exchange_code_for_token(CLIENT_ID, CLIENT_SECRET, code, REDIRECT_URI)
    
    # Store tokens securely (in production, use a proper session store)
    session['access_token'] = token_data['access_token']
    session['refresh_token'] = token_data.get('refresh_token')
    session['token_expires_at'] = time.time() + token_data['expires_in']
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """User dashboard where they can perform operations."""
    if 'access_token' not in session:
        return redirect(url_for('login'))
    
    # Check if token is expired and refresh if needed
    if time.time() > session.get('token_expires_at', 0):
        refresh_access_token()
    
    return '''
    <h1>Globus Dashboard</h1>
    <p>You are authorized to access Globus guest collections!</p>
    <a href="/list-collections">List Collections</a>
    <a href="/transfer-files">Transfer Files</a>
    '''

@app.route('/list-collections')
def list_collections():
    """List available collections for the user."""
    access_token = session.get('access_token')
    
    # Get user's identity
    identity_response = make_globus_api_request(
        access_token,
        'https://auth.globus.org/v2/oauth2/userinfo'
    )
    
    # Get user's collections (this would use the Transfer API)
    collections_response = make_globus_api_request(
        access_token,
        'https://transfer.api.globus.org/v0.10/endpoint_search',
        data={'filter_scope': 'my-endpoints'}
    )
    
    return f'''
    <h2>Your Collections</h2>
    <p>User: {identity_response.get('preferred_username')}</p>
    <pre>{json.dumps(collections_response, indent=2)}</pre>
    '''

def refresh_access_token():
    """Refresh the access token using the refresh token."""
    refresh_token = session.get('refresh_token')
    if not refresh_token:
        return redirect(url_for('login'))
    
    token_url = "https://auth.globus.org/v2/oauth2/token"
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    
    token_data = response.json()
    session['access_token'] = token_data['access_token']
    session['token_expires_at'] = time.time() + token_data['expires_in']

if __name__ == '__main__':
    app.run(debug=True)
```

## 4. Key Points for Guest Collection Access

1. **Scopes**: You'll need the Transfer API scope (`urn:globus:auth:scope:transfer.api.globus.org:all`) to access collections.

2. **Guest Collections**: For guest collections, the user needs to have been granted access by the collection owner. The OAuth flow will only work if the user has permission to access the collection.

3. **Token Management**: Always handle token expiration and refresh tokens properly.

4. **Security**: Use HTTPS in production, validate the state parameter, and store tokens securely.

5. **Error Handling**: Implement proper error handling for cases where the user doesn't have access to the requested collection.

This implementation follows the [Globus Auth API documentation](https://docs.globus.org/api/auth/reference/) and uses the Authorization Code Grant flow, which is the recommended approach for web applications that can securely store a client secret.

```python
import urllib.parse

def get_authorization_url(client_id, redirect_uri, scope):
    """
    Generate the authorization URL for the user to visit.
    
    Args:
        client_id: Your registered client ID
        redirect_uri: Where to redirect after authorization
        scope: The scopes you need (e.g., 'urn:globus:auth:scope:transfer.api.globus.org:all')
    """
    base_url = "https://auth.globus.org/v2/oauth2/authorize"
    
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'response_type': 'code',
        'state': 'your-random-state-value'  # For security
    }
    
    return f"{base_url}?{urllib.parse.urlencode(params)}"
```

```python
import requests

def exchange_code_for_token(client_id, client_secret, authorization_code, redirect_uri):
    """
    Exchange the authorization code for an access token.
    """
    token_url = "https://auth.globus.org/v2/oauth2/token"
    
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    
    return response.json()
```

```python
def make_globus_api_request(access_token, endpoint, method='GET', data=None):
    """
    Make an authenticated request to the Globus API.
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.request(
        method=method,
        url=endpoint,
        headers=headers,
        json=data
    )
    response.raise_for_status()
    
    return response.json()
```

```python
from flask import Flask, request, redirect, session, url_for
import requests
import secrets

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Your Globus application credentials
CLIENT_ID = 'your-client-id'
CLIENT_SECRET = 'your-client-secret'
REDIRECT_URI = 'http://localhost:5000/callback'

# Scopes you need for guest collection access
SCOPES = [
    'urn:globus:auth:scope:transfer.api.globus.org:all',
    'urn:globus:auth:scope:auth.globus.org:view_identities'
]

@app.route('/login')
def login():
    """Start the OAuth flow."""
    # Generate a random state for security
    session['state'] = secrets.token_urlsafe(32)
    
    # Build authorization URL
    auth_url = "https://auth.globus.org/v2/oauth2/authorize"
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPES),
        'response_type': 'code',
        'state': session['state']
    }
    
    auth_url_with_params = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url_with_params)

@app.route('/callback')
def callback():
    """Handle the OAuth callback."""
    # Verify state parameter
    if request.args.get('state') != session.get('state'):
        return 'State verification failed', 400
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        return 'No authorization code received', 400
    
    # Exchange code for tokens
    token_data = exchange_code_for_token(CLIENT_ID, CLIENT_SECRET, code, REDIRECT_URI)
    
    # Store tokens securely (in production, use a proper session store)
    session['access_token'] = token_data['access_token']
    session['refresh_token'] = token_data.get('refresh_token')
    session['token_expires_at'] = time.time() + token_data['expires_in']
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """User dashboard where they can perform operations."""
    if 'access_token' not in session:
        return redirect(url_for('login'))
    
    # Check if token is expired and refresh if needed
    if time.time() > session.get('token_expires_at', 0):
        refresh_access_token()
    
    return '''
    <h1>Globus Dashboard</h1>
    <p>You are authorized to access Globus guest collections!</p>
    <a href="/list-collections">List Collections</a>
    <a href="/transfer-files">Transfer Files</a>
    '''

@app.route('/list-collections')
def list_collections():
    """List available collections for the user."""
    access_token = session.get('access_token')
    
    # Get user's identity
    identity_response = make_globus_api_request(
        access_token,
        'https://auth.globus.org/v2/oauth2/userinfo'
    )
    
    # Get user's collections (this would use the Transfer API)
    collections_response = make_globus_api_request(
        access_token,
        'https://transfer.api.globus.org/v0.10/endpoint_search',
        data={'filter_scope': 'my-endpoints'}
    )
    
    return f'''
    <h2>Your Collections</h2>
    <p>User: {identity_response.get('preferred_username')}</p>
    <pre>{json.dumps(collections_response, indent=2)}</pre>
    '''

def refresh_access_token():
    """Refresh the access token using the refresh token."""
    refresh_token = session.get('refresh_token')
    if not refresh_token:
        return redirect(url_for('login'))
    
    token_url = "https://auth.globus.org/v2/oauth2/token"
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    
    token_data = response.json()
    session['access_token'] = token_data['access_token']
    session['token_expires_at'] = time.time() + token_data['expires_in']

if __name__ == '__main__':
    app.run(debug=True)
```

