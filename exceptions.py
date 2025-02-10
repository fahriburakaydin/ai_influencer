class AppError(Exception):
    """Base exception class for the application"""
    def __init__(self, message="Application error occurred", original=None):
        super().__init__(message)
        self.original = original

class APIError(AppError):
    """Exception for API-related errors"""

class DatabaseError(AppError):
    """Exception for database-related errors"""

class ValidationError(AppError):
    """Exception for input validation errors"""