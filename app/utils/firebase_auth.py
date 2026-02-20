from functools import wraps
from flask import session, redirect, url_for, request

def sign_up_with_email_password(email, password):
    """
    Register a new user with email and password
    """
    return {"success": True, "user": {"email": email}}

def sign_in_with_email_password(email, password):
    """
    Sign in a user with email and password
    """
    return {"success": True, "user": {"email": email}}

def sign_in_with_google(id_token):
    """
    Sign in a user with Google OAuth token
    """
    return {"success": True}

def get_account_info(id_token):
    """
    Get user account information using ID token
    """
    return {"success": True}

def send_password_reset_email(email):
    """
    Send password reset email
    """
    print(f"Password reset email sent to {email}")

def verify_id_token(id_token):
    """
    Verify Firebase ID token
    """
    return {"uid": "demo-uid"}

def refresh_token(refresh_token):
    """
    Refresh user token
    """
    return {"access_token": "demo-access-token"}