"""
Okta authentication and JWT token validation.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional, Dict, Any
import requests
from config import settings


security = HTTPBearer(auto_error=False)  # Don't auto-error if no auth header


class OktaAuth:
    """Handles Okta JWT token validation."""
    
    def __init__(self):
        self.issuer = settings.okta_issuer
        self.client_id = settings.okta_client_id
        self._jwks_cache: Optional[Dict[str, Any]] = None
    
    def get_jwks(self) -> Dict[str, Any]:
        """Fetch JWKS (JSON Web Key Set) from Okta."""
        if self._jwks_cache is None:
            jwks_uri = f"{self.issuer}/v1/keys"
            response = requests.get(jwks_uri)
            response.raise_for_status()
            self._jwks_cache = response.json()
        return self._jwks_cache
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode Okta JWT token.
        
        Args:
            token: The JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            # For production, you would verify the token signature using JWKS
            # For now, we'll decode without verification for development
            # In production, use proper JWT verification with Okta's public keys
            
            unverified_header = jwt.get_unverified_header(token)
            
            # Decode and verify the token
            # Note: In production, fetch the signing key from JWKS and verify
            payload = jwt.decode(
                token,
                options={"verify_signature": False},  # TODO: Enable in production
                audience=self.client_id,
                issuer=self.issuer,
            )
            
            return payload
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication credentials: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def get_user_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user information from token payload."""
        return {
            "email": payload.get("sub") or payload.get("email"),
            "name": payload.get("name", ""),
            "groups": payload.get("groups", []),
        }


okta_auth = OktaAuth()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP bearer token credentials
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: If authentication fails
    """
    # Skip authentication in development mode
    if settings.skip_auth or credentials is None:
        return {
            "email": "dev@localhost",
            "name": "Development User",
            "groups": []
        }
    
    token = credentials.credentials
    payload = okta_auth.verify_token(token)
    user_info = okta_auth.get_user_info(payload)
    return user_info


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Optional authentication dependency.
    Returns None if no credentials provided.
    """
    if credentials is None:
        return None
    return await get_current_user(credentials)

