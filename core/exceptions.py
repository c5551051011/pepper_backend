# app/core/exceptions.py
class StoreCrediteError(Exception):
    """Base exception for StoreCredit app"""
    pass

class WalletNotFoundError(StoreCrediteError):
    """Wallet not found or inactive"""
    pass

class InsufficientFundsError(StoreCrediteError):
    """Insufficient wallet balance"""
    pass

class UserNotVerifiedError(StoreCrediteError):
    """User phone not verified"""
    pass

class InvalidVerificationCodeError(StoreCrediteError):
    """Invalid or expired verification code"""
    pass