#!/usr/bin/env python3
"""
Generate a valid JWT token for testing the DAG system
"""

from jose import jwt
from datetime import datetime, timedelta

# JWT configuration from our app
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"

def create_test_token():
    """Create a test JWT token"""
    
    # Token payload
    payload = {
        "sub": "admin_123",  # User ID from our hardcoded user
        "email": "admin@notebook.ai",
        "role": "admin",
        "exp": datetime.utcnow() + timedelta(hours=24)  # Valid for 24 hours
    }
    
    # Create token
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return token

if __name__ == "__main__":
    token = create_test_token()
    print("Generated JWT Token:")
    print(f"Bearer {token}")
    print("\nUse this token in Authorization header:")
    print(f"Authorization: Bearer {token}")
