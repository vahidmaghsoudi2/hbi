class HBIException(Exception):
    pass

class NotFoundError(HBIException):
    pass

class ConflictError(HBIException):
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details
        super().__init__(message)

class ConsentError(HBIException):
    pass

class ValidationError(HBIException):
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details
        super().__init__(message)
