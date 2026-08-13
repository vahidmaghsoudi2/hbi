class InterfaceError(Exception):
    """Base exception for Interface Layer"""
    pass

class NotFoundError(InterfaceError):
    """Resource not found"""
    pass

class ValidationError(InterfaceError):
    """Input validation failed"""
    pass

class BusinessRuleError(InterfaceError):
    """Business rule violation raised from Service Layer"""
    pass
