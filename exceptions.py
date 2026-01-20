class ATMError(Exception):
    pass

class InsufficientFundsError(ATMError):
    pass

class InvalidAmountError(ATMError):
    pass
