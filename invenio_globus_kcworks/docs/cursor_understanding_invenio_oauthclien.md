# Understanding invenio_oauthclient module functionality
_Exported on 6/24/2025 at 16:03:47 EDT from Cursor (1.0.0)_

---

**User**

Explain to me how the invenio_oauthclient module works to manage an OAuth authorization connection with an external provider

---

**Cursor**

I'll explain how the `invenio_oauthclient` module works to manage OAuth authorization connections with external providers, using the Globus OAuth implementation as an example.


Based on my analysis of the `invenio_oauthclient` module and the Globus OAuth implementation, I can explain how the module works to manage OAuth authorization connections with external providers.

## How `invenio_oauthclient` Works

The `invenio_oauthclient` module provides a comprehensive framework for managing OAuth 2.0 authorization flows with external providers. Here's how it works:

### 1. **Configuration and Setup**

The module uses a configuration-based approach where OAuth providers are defined in the application configuration:

```python
# In invenio.cfg
OAUTHCLIENT_REMOTE_APPS = {
    'globus': globus.REMOTE_APP,
}

GLOBUS_APP_CREDENTIALS = {
    'consumer_key': 'your-client-id',
    'consumer_secret': 'your-client-secret',
}
```

### 2. **Provider-Specific Implementation**

Each OAuth provider (like Globus) has its own implementation that extends the base `OAuthSettingsHelper` class:

```python
class GlobusOAuthSettingsHelper(OAuthSettingsHelper):
    def __init__(self, title=None, description=None, base_url=None, app_key=None):
        super().__init__(
            title or "Globus",
            description or "Research data management simplified.",
            base_url or "https://auth.globus.org/v2/",
            app_key or "GLOBUS_APP_CREDENTIALS",
            request_token_params={"scope": "openid email profile"},
        )
```

### 3. **OAuth Flow Handlers**

The module defines several key handlers that manage different parts of the OAuth flow:

#### **Authorization Handler**
```python
authorized_handler="invenio_oauthclient.handlers:authorized_signup_handler"
```
This handles the callback from the OAuth provider after the user authorizes the application.

#### **Account Information Handler**
```python
info="invenio_oauthclient.contrib.globus:account_info"
```
This retrieves user information from the OAuth provider's API.

#### **Account Setup Handler**
```python
setup="invenio_oauthclient.contrib.globus:account_setup"
```
This sets up the local user account and links it to the external OAuth account.

### 4. **OAuth Flow Process**

The complete OAuth flow works as follows:

#### **Step 1: User Initiates Login**
- User clicks "Login with Globus" 
- Application redirects to Globus authorization URL with required scopes
- URL includes `client_id`, `redirect_uri`, `scope`, and `state` parameters

#### **Step 2: User Authorization**
- User authenticates with Globus and grants permissions
- Globus redirects back to the application with an authorization code

#### **Step 3: Token Exchange**
```python
def get_user_info(remote):
    """Get user information from Globus."""
    response = remote.get(_globus_app.user_info_url)
    user_info = get_dict_from_response(response)
    return user_info
```

#### **Step 4: Account Creation/Linking**
```python
def account_setup(remote, token, resp):
    """Perform additional setup after user has been logged in."""
    info = get_user_info(remote)
    user_id = get_user_id(remote, info["preferred_username"])
    
    with db.session.begin_nested():
        token.remote_account.extra_data = {
            "login": info["username"], 
            "id": user_id
        }
        
        # Create user <-> external id link
        oauth_link_external_id(
            token.remote_account.user,
            dict(id=user_id, method=remote.name),
        )
```

### 5. **Data Models**

The module uses several key models to track OAuth connections:

- **`RemoteAccount`**: Stores OAuth tokens and account information
- **`UserIdentity`**: Links local users to external OAuth identities
- **`RemoteToken`**: Manages access tokens and refresh tokens

### 6. **Security Features**

The module includes several security features:

- **State parameter validation** to prevent CSRF attacks
- **Token storage** in encrypted database fields
- **External ID linking** to prevent account duplication
- **Disconnect handlers** for unlinking accounts

### 7. **REST API Support**

The module also provides REST API handlers for programmatic OAuth flows:

```python
self._rest_handlers = dict(
    authorized_handler="invenio_oauthclient.handlers.rest:authorized_signup_handler",
    disconnect_handler="invenio_oauthclient.contrib.globus:disconnect_rest_handler",
    # ... other handlers
)
```

### 8. **Error Handling**

The module includes comprehensive error handling:

```python
def get_dict_from_response(response):
    """Check for errors in the response and return the resulting JSON."""
    if getattr(response, "_resp") and response._resp.code > 400:
        raise OAuthResponseError(
            "Application mis-configuration in Globus", None, response
        )
    return response.data
```

### 9. **Integration with InvenioRDM**

The OAuth client integrates seamlessly with InvenioRDM's authentication system:

- Users can link multiple OAuth accounts to a single local account
- OAuth accounts can be used for both login and API access
- The system supports both web-based and API-based OAuth flows
- Integration with Invenio's permission system

This architecture provides a flexible, secure, and extensible way to integrate OAuth providers into InvenioRDM applications while maintaining consistency with the broader Invenio ecosystem.

```python
# In invenio.cfg
OAUTHCLIENT_REMOTE_APPS = {
    'globus': globus.REMOTE_APP,
}

GLOBUS_APP_CREDENTIALS = {
    'consumer_key': 'your-client-id',
    'consumer_secret': 'your-client-secret',
}
```

```python
class GlobusOAuthSettingsHelper(OAuthSettingsHelper):
    def __init__(self, title=None, description=None, base_url=None, app_key=None):
        super().__init__(
            title or "Globus",
            description or "Research data management simplified.",
            base_url or "https://auth.globus.org/v2/",
            app_key or "GLOBUS_APP_CREDENTIALS",
            request_token_params={"scope": "openid email profile"},
        )
```

```python
authorized_handler="invenio_oauthclient.handlers:authorized_signup_handler"
```

```python
info="invenio_oauthclient.contrib.globus:account_info"
```

```python
setup="invenio_oauthclient.contrib.globus:account_setup"
```

```python
def get_user_info(remote):
    """Get user information from Globus."""
    response = remote.get(_globus_app.user_info_url)
    user_info = get_dict_from_response(response)
    return user_info
```

```python
def account_setup(remote, token, resp):
    """Perform additional setup after user has been logged in."""
    info = get_user_info(remote)
    user_id = get_user_id(remote, info["preferred_username"])
    
    with db.session.begin_nested():
        token.remote_account.extra_data = {
            "login": info["username"], 
            "id": user_id
        }
        
        # Create user <-> external id link
        oauth_link_external_id(
            token.remote_account.user,
            dict(id=user_id, method=remote.name),
        )
```

```python
self._rest_handlers = dict(
    authorized_handler="invenio_oauthclient.handlers.rest:authorized_signup_handler",
    disconnect_handler="invenio_oauthclient.contrib.globus:disconnect_rest_handler",
    # ... other handlers
)
```

```python
def get_dict_from_response(response):
    """Check for errors in the response and return the resulting JSON."""
    if getattr(response, "_resp") and response._resp.code > 400:
        raise OAuthResponseError(
            "Application mis-configuration in Globus", None, response
        )
    return response.data
```

---

**User**

How would I use the package to handle OAuth connections, not for login in Invenio, but for authorizing API calls to an external service made by Invenio on behalf of a user

---

**Cursor**

Great question! The `invenio_oauthclient` package can indeed be used for authorizing API calls to external services on behalf of users, not just for login. Let me explain how to set this up and use it.


Perfect! Now I have a comprehensive understanding of how to use `invenio_oauthclient` for authorizing API calls to external services. Let me explain how to set this up and use it.

## Using `invenio_oauthclient` for External API Authorization

The `invenio_oauthclient` package can indeed be used for authorizing API calls to external services on behalf of users, not just for login. Here's how to set it up and use it:

### 1. **Configuration Setup**

First, configure the OAuth provider for API access:

```python
# In invenio.cfg
from invenio_oauthclient.contrib import globus

OAUTHCLIENT_REMOTE_APPS = {
    'globus_api': globus.REMOTE_APP,
}

GLOBUS_API_CREDENTIALS = {
    'consumer_key': 'your-client-id',
    'consumer_secret': 'your-client-secret',
}
```

### 2. **Custom OAuth Provider for API Access**

Create a custom OAuth provider specifically for API access:

```python
# myapp/oauth_providers.py
from invenio_oauthclient.contrib.settings import OAuthSettingsHelper

class GlobusAPIOAuthSettingsHelper(OAuthSettingsHelper):
    """OAuth configuration for Globus API access."""
    
    def __init__(self):
        super().__init__(
            title="Globus API",
            description="Access Globus API on your behalf",
            base_url="https://auth.globus.org/v2/",
            app_key="GLOBUS_API_CREDENTIALS",
            request_token_params={
                "scope": "urn:globus:auth:scope:transfer.api.globus.org:all"
            },
        )
        
        # Configure handlers for API access (not login)
        self._handlers = dict(
            authorized_handler="myapp.handlers:api_authorized_handler",
            disconnect_handler="myapp.handlers:api_disconnect_handler",
            signup_handler=dict(
                info="myapp.handlers:api_account_info",
                setup="myapp.handlers:api_account_setup",
                view="invenio_oauthclient.handlers:signup_handler",
            ),
        )

GLOBUS_API_REMOTE_APP = GlobusAPIOAuthSettingsHelper().remote_app
```

### 3. **Custom Handlers for API Access**

Create handlers that focus on API authorization rather than login:

```python
# myapp/handlers.py
from flask import current_app, redirect, url_for
from invenio_db import db
from invenio_oauthclient import current_oauthclient
from invenio_oauthclient.models import RemoteAccount, RemoteToken
from invenio_oauthclient.oauth import oauth_link_external_id

def api_account_info(remote, resp):
    """Extract account information for API access."""
    user_info = get_user_info(remote)
    user_id = get_user_id(remote, user_info["preferred_username"])
    
    return {
        'user': {
            'email': user_info["email"],
            'profile': {
                'username': user_info["username"],
                'full_name': user_info["name"],
            },
        },
        'external_id': user_id,
        'external_method': remote.name,
    }

def api_account_setup(remote, token, resp):
    """Setup account for API access."""
    info = get_user_info(remote)
    user_id = get_user_id(remote, info["preferred_username"])
    
    with db.session.begin_nested():
        # Store API-specific data
        token.remote_account.extra_data = {
            "api_access": True,
            "globus_id": user_id,
            "username": info["username"],
        }
        
        # Link external ID
        oauth_link_external_id(
            token.remote_account.user,
            dict(id=user_id, method=remote.name),
        )

def api_authorized_handler(remote, resp):
    """Handle OAuth callback for API access."""
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    
    # Process the authorization
    handlers = current_oauthclient.signup_handlers[remote.name]
    account_info = handlers["info"](remote, resp)
    
    # Setup the account
    handlers["setup"](remote, token, resp)
    
    db.session.commit()
    
    return redirect(url_for('api_dashboard'))
```

### 4. **Token Management for API Calls**

Create utilities to retrieve and use stored tokens:

```python
# myapp/api_utils.py
from invenio_oauthclient.models import RemoteToken, RemoteAccount
from flask import current_app
import requests

def get_user_api_token(user_id, provider_name):
    """Get stored API token for a user."""
    remote_token = RemoteToken.get(
        user_id=user_id,
        client_id=provider_name,
        token_type=""
    )
    
    if remote_token:
        return remote_token.access_token
    return None

def make_authenticated_api_call(user_id, provider_name, endpoint, method='GET', data=None):
    """Make an authenticated API call using stored OAuth token."""
    access_token = get_user_api_token(user_id, provider_name)
    
    if not access_token:
        raise ValueError(f"No API token found for user {user_id} and provider {provider_name}")
    
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
    
    return response

def refresh_api_token(user_id, provider_name):
    """Refresh an expired API token."""
    remote_token = RemoteToken.get(
        user_id=user_id,
        client_id=provider_name
    )
    
    if not remote_token:
        return None
    
    # Get the OAuth remote app
    remote_app = current_oauthclient.remote_apps[provider_name]
    
    # Refresh the token
    new_token = remote_app.refresh_token(remote_token.access_token)
    
    if new_token:
        remote_token.update_token(new_token['access_token'], new_token.get('refresh_token', ''))
        db.session.commit()
        return new_token['access_token']
    
    return None
```

### 5. **Service Layer Integration**

Create a service that uses the OAuth tokens for API calls:

```python
# myapp/services/globus_service.py
from invenio_rdm_records.services import RecordService
from myapp.api_utils import make_authenticated_api_call, refresh_api_token

class GlobusAPIService:
    """Service for making Globus API calls on behalf of users."""
    
    def __init__(self):
        self.base_url = "https://transfer.api.globus.org/v0.10"
    
    def list_user_endpoints(self, user_id):
        """List user's Globus endpoints."""
        try:
            response = make_authenticated_api_call(
                user_id=user_id,
                provider_name='globus_api',
                endpoint=f"{self.base_url}/endpoint_search",
                method='GET',
                data={'filter_scope': 'my-endpoints'}
            )
            
            if response.status_code == 401:
                # Token expired, try to refresh
                new_token = refresh_api_token(user_id, 'globus_api')
                if new_token:
                    response = make_authenticated_api_call(
                        user_id=user_id,
                        provider_name='globus_api',
                        endpoint=f"{self.base_url}/endpoint_search",
                        method='GET',
                        data={'filter_scope': 'my-endpoints'}
                    )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            current_app.logger.error(f"Error calling Globus API: {e}")
            raise
    
    def transfer_files(self, user_id, source_endpoint, dest_endpoint, files):
        """Initiate a file transfer."""
        transfer_data = {
            'source_endpoint': source_endpoint,
            'destination_endpoint': dest_endpoint,
            'DATA': files
        }
        
        response = make_authenticated_api_call(
            user_id=user_id,
            provider_name='globus_api',
            endpoint=f"{self.base_url}/transfer",
            method='POST',
            data=transfer_data
        )
        
        response.raise_for_status()
        return response.json()
```

### 6. **API Views**

Create views that use the service:

```python
# myapp/views.py
from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user
from myapp.services.globus_service import GlobusAPIService

api_bp = Blueprint('globus_api', __name__)
globus_service = GlobusAPIService()

@api_bp.route('/globus/endpoints')
@login_required
def list_endpoints():
    """List user's Globus endpoints."""
    try:
        endpoints = globus_service.list_user_endpoints(current_user.id)
        return jsonify(endpoints)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/globus/transfer', methods=['POST'])
@login_required
def transfer_files():
    """Initiate a file transfer."""
    data = request.get_json()
    
    try:
        result = globus_service.transfer_files(
            user_id=current_user.id,
            source_endpoint=data['source'],
            dest_endpoint=data['destination'],
            files=data['files']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 7. **User Interface for Authorization**

Create a UI for users to authorize API access:

```python
# myapp/views.py
@api_bp.route('/globus/authorize')
@login_required
def authorize_globus_api():
    """Redirect user to authorize Globus API access."""
    return current_oauthclient.authorize('globus_api')

@api_bp.route('/globus/status')
@login_required
def globus_api_status():
    """Check if user has authorized Globus API access."""
    from invenio_oauthclient.models import RemoteAccount
    
    account = RemoteAccount.get(current_user.id, 'globus_api')
    if account:
        return jsonify({
            'authorized': True,
            'username': account.extra_data.get('username')
        })
    else:
        return jsonify({'authorized': False})
```

### 8. **Token Expiration Handling**

Implement automatic token refresh:

```python
# myapp/api_utils.py
def get_valid_api_token(user_id, provider_name):
    """Get a valid API token, refreshing if necessary."""
    access_token = get_user_api_token(user_id, provider_name)
    
    if not access_token:
        return None
    
    # Test if token is still valid
    try:
        test_response = make_authenticated_api_call(
            user_id=user_id,
            provider_name=provider_name,
            endpoint="https://auth.globus.org/v2/oauth2/userinfo"
        )
        
        if test_response.status_code == 200:
            return access_token
        elif test_response.status_code == 401:
            # Token expired, refresh it
            return refresh_api_token(user_id, provider_name)
            
    except Exception:
        # Try to refresh token
        return refresh_api_token(user_id, provider_name)
    
    return access_token
```

### Key Benefits of This Approach:

1. **Secure Token Storage**: Tokens are encrypted and stored in the database
2. **Automatic Refresh**: Handles token expiration automatically
3. **User-Specific**: Each user has their own OAuth tokens
4. **Separation of Concerns**: API authorization is separate from login
5. **Reusable**: The same pattern can be used for multiple external APIs
6. **Audit Trail**: All API calls are made on behalf of specific users

This approach allows Invenio to make authenticated API calls to external services (like Globus) on behalf of users while maintaining security and providing a good user experience.

```python
# In invenio.cfg
from invenio_oauthclient.contrib import globus

OAUTHCLIENT_REMOTE_APPS = {
    'globus_api': globus.REMOTE_APP,
}

GLOBUS_API_CREDENTIALS = {
    'consumer_key': 'your-client-id',
    'consumer_secret': 'your-client-secret',
}
```

```python
# myapp/oauth_providers.py
from invenio_oauthclient.contrib.settings import OAuthSettingsHelper

class GlobusAPIOAuthSettingsHelper(OAuthSettingsHelper):
    """OAuth configuration for Globus API access."""
    
    def __init__(self):
        super().__init__(
            title="Globus API",
            description="Access Globus API on your behalf",
            base_url="https://auth.globus.org/v2/",
            app_key="GLOBUS_API_CREDENTIALS",
            request_token_params={
                "scope": "urn:globus:auth:scope:transfer.api.globus.org:all"
            },
        )
        
        # Configure handlers for API access (not login)
        self._handlers = dict(
            authorized_handler="myapp.handlers:api_authorized_handler",
            disconnect_handler="myapp.handlers:api_disconnect_handler",
            signup_handler=dict(
                info="myapp.handlers:api_account_info",
                setup="myapp.handlers:api_account_setup",
                view="invenio_oauthclient.handlers:signup_handler",
            ),
        )

GLOBUS_API_REMOTE_APP = GlobusAPIOAuthSettingsHelper().remote_app
```

```python
# myapp/handlers.py
from flask import current_app, redirect, url_for
from invenio_db import db
from invenio_oauthclient import current_oauthclient
from invenio_oauthclient.models import RemoteAccount, RemoteToken
from invenio_oauthclient.oauth import oauth_link_external_id

def api_account_info(remote, resp):
    """Extract account information for API access."""
    user_info = get_user_info(remote)
    user_id = get_user_id(remote, user_info["preferred_username"])
    
    return {
        'user': {
            'email': user_info["email"],
            'profile': {
                'username': user_info["username"],
                'full_name': user_info["name"],
            },
        },
        'external_id': user_id,
        'external_method': remote.name,
    }

def api_account_setup(remote, token, resp):
    """Setup account for API access."""
    info = get_user_info(remote)
    user_id = get_user_id(remote, info["preferred_username"])
    
    with db.session.begin_nested():
        # Store API-specific data
        token.remote_account.extra_data = {
            "api_access": True,
            "globus_id": user_id,
            "username": info["username"],
        }
        
        # Link external ID
        oauth_link_external_id(
            token.remote_account.user,
            dict(id=user_id, method=remote.name),
        )

def api_authorized_handler(remote, resp):
    """Handle OAuth callback for API access."""
    if not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    
    # Process the authorization
    handlers = current_oauthclient.signup_handlers[remote.name]
    account_info = handlers["info"](remote, resp)
    
    # Setup the account
    handlers["setup"](remote, token, resp)
    
    db.session.commit()
    
    return redirect(url_for('api_dashboard'))
```

```python
# myapp/api_utils.py
from invenio_oauthclient.models import RemoteToken, RemoteAccount
from flask import current_app
import requests

def get_user_api_token(user_id, provider_name):
    """Get stored API token for a user."""
    remote_token = RemoteToken.get(
        user_id=user_id,
        client_id=provider_name,
        token_type=""
    )
    
    if remote_token:
        return remote_token.access_token
    return None

def make_authenticated_api_call(user_id, provider_name, endpoint, method='GET', data=None):
    """Make an authenticated API call using stored OAuth token."""
    access_token = get_user_api_token(user_id, provider_name)
    
    if not access_token:
        raise ValueError(f"No API token found for user {user_id} and provider {provider_name}")
    
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
    
    return response

def refresh_api_token(user_id, provider_name):
    """Refresh an expired API token."""
    remote_token = RemoteToken.get(
        user_id=user_id,
        client_id=provider_name
    )
    
    if not remote_token:
        return None
    
    # Get the OAuth remote app
    remote_app = current_oauthclient.remote_apps[provider_name]
    
    # Refresh the token
    new_token = remote_app.refresh_token(remote_token.access_token)
    
    if new_token:
        remote_token.update_token(new_token['access_token'], new_token.get('refresh_token', ''))
        db.session.commit()
        return new_token['access_token']
    
    return None
```

```python
# myapp/services/globus_service.py
from invenio_rdm_records.services import RecordService
from myapp.api_utils import make_authenticated_api_call, refresh_api_token

class GlobusAPIService:
    """Service for making Globus API calls on behalf of users."""
    
    def __init__(self):
        self.base_url = "https://transfer.api.globus.org/v0.10"
    
    def list_user_endpoints(self, user_id):
        """List user's Globus endpoints."""
        try:
            response = make_authenticated_api_call(
                user_id=user_id,
                provider_name='globus_api',
                endpoint=f"{self.base_url}/endpoint_search",
                method='GET',
                data={'filter_scope': 'my-endpoints'}
            )
            
            if response.status_code == 401:
                # Token expired, try to refresh
                new_token = refresh_api_token(user_id, 'globus_api')
                if new_token:
                    response = make_authenticated_api_call(
                        user_id=user_id,
                        provider_name='globus_api',
                        endpoint=f"{self.base_url}/endpoint_search",
                        method='GET',
                        data={'filter_scope': 'my-endpoints'}
                    )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            current_app.logger.error(f"Error calling Globus API: {e}")
            raise
    
    def transfer_files(self, user_id, source_endpoint, dest_endpoint, files):
        """Initiate a file transfer."""
        transfer_data = {
            'source_endpoint': source_endpoint,
            'destination_endpoint': dest_endpoint,
            'DATA': files
        }
        
        response = make_authenticated_api_call(
            user_id=user_id,
            provider_name='globus_api',
            endpoint=f"{self.base_url}/transfer",
            method='POST',
            data=transfer_data
        )
        
        response.raise_for_status()
        return response.json()
```

```python
# myapp/views.py
from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user
from myapp.services.globus_service import GlobusAPIService

api_bp = Blueprint('globus_api', __name__)
globus_service = GlobusAPIService()

@api_bp.route('/globus/endpoints')
@login_required
def list_endpoints():
    """List user's Globus endpoints."""
    try:
        endpoints = globus_service.list_user_endpoints(current_user.id)
        return jsonify(endpoints)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/globus/transfer', methods=['POST'])
@login_required
def transfer_files():
    """Initiate a file transfer."""
    data = request.get_json()
    
    try:
        result = globus_service.transfer_files(
            user_id=current_user.id,
            source_endpoint=data['source'],
            dest_endpoint=data['destination'],
            files=data['files']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

```python
# myapp/views.py
@api_bp.route('/globus/authorize')
@login_required
def authorize_globus_api():
    """Redirect user to authorize Globus API access."""
    return current_oauthclient.authorize('globus_api')

@api_bp.route('/globus/status')
@login_required
def globus_api_status():
    """Check if user has authorized Globus API access."""
    from invenio_oauthclient.models import RemoteAccount
    
    account = RemoteAccount.get(current_user.id, 'globus_api')
    if account:
        return jsonify({
            'authorized': True,
            'username': account.extra_data.get('username')
        })
    else:
        return jsonify({'authorized': False})
```

```python
# myapp/api_utils.py
def get_valid_api_token(user_id, provider_name):
    """Get a valid API token, refreshing if necessary."""
    access_token = get_user_api_token(user_id, provider_name)
    
    if not access_token:
        return None
    
    # Test if token is still valid
    try:
        test_response = make_authenticated_api_call(
            user_id=user_id,
            provider_name=provider_name,
            endpoint="https://auth.globus.org/v2/oauth2/userinfo"
        )
        
        if test_response.status_code == 200:
            return access_token
        elif test_response.status_code == 401:
            # Token expired, refresh it
            return refresh_api_token(user_id, provider_name)
            
    except Exception:
        # Try to refresh token
        return refresh_api_token(user_id, provider_name)
    
    return access_token
```

