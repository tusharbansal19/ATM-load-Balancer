class ATMError(Exception):
    """Base class for ATM exceptions."""
    pass

class InsufficientFundsError(ATMError):
    """Raised when ATM does not have enough cash."""
    pass

class InvalidAmountError(ATMError):
    """Raised when amount is invalid (negative, not multiple of 100)."""
    pass
