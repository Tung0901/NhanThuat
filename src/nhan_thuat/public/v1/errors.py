"""
Public errors for NhanThuat Contract V1.
"""


class PublicError(Exception):
    """Base class for all NhanThuat public errors."""
    def __init__(self, message: str, error_code: str):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class InsufficientVerifiedKnowledgeError(PublicError):
    """
    Raised when the KnowledgeEngine cannot safely answer a query
    due to a lack of verified knowledge.
    """
    def __init__(self, message: str = "Insufficient verified knowledge to answer query."):
        super().__init__(message, "INSUFFICIENT_VERIFIED_KNOWLEDGE")
