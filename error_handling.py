import logging
import traceback
from exceptions import ATMError, InsufficientFundsError, InvalidAmountError

class ErrorHandler:
    """Centralized error handling and logging module."""
    
    def __init__(self, log_file='atm_transactions.log'):
        self.setup_logging(log_file)
    
    def setup_logging(self, log_file):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def log_transaction(self, message):
        """Log a successful transaction or event."""
        logging.info(message)

    def log_system_error(self, message, error=None):
        """Log a system-level error (IO, unexpected crashes)."""
        error_msg = f"{message}: {str(error)}" if error else message
        logging.error(error_msg)
        if error:
            logging.debug(traceback.format_exc())

    def handle_user_error(self, error):
        """
        Process errors that occur during user interaction.
        Returns a friendly message to display to the user.
        """
        # Log the raw error internally
        logging.warning(f"User Action Failed: {str(error)}")

        # Return user-friendly messages based on exception type
        if isinstance(error, InsufficientFundsError):
            return "❌ Transaction Declined: Insufficient funds in ATM."
        elif isinstance(error, InvalidAmountError):
            return f"❌ Input Error: {str(error)}"
        elif isinstance(error, ATMError):
            return f"❌ ATM Error: {str(error)}"
        elif isinstance(error, ValueError):
            return "❌ Input Error: Please enter a valid number."
        else:
            # For unexpected errors, log full traceback and give generic message
            self.log_system_error("Unexpected UI Error", error)
            return "❌ An unexpected system error occurred. Please contact support."

# Global instance for easy import
error_manager = ErrorHandler()
