import json
import os
from exceptions import ATMError, InsufficientFundsError, InvalidAmountError
from error_handling import error_manager

class ATM:
    def __init__(self, state_file="cash_state.json"):
        self.state_file = state_file
        # Default state
        self.cash = {500: 20, 200: 20, 100: 20}
        self.load_state()

    def load_state(self):
        """Loads cash state from file with error handling."""
        if not os.path.exists(self.state_file):
            self.save_state()
            return

        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
                self.cash = {int(k): v for k, v in data.items()}
        except (json.JSONDecodeError, ValueError) as e:
            error_manager.log_system_error("Corrupt state file found. Resetting.", e)
            print("Notice: System state reset due to file corruption.")
            self.save_state()
        except IOError as e:
            error_manager.log_system_error("IO Error loading state", e)

    def save_state(self):
        """Saves cash state to file securely."""
        try:
            temp_file = self.state_file + ".tmp"
            with open(temp_file, "w") as f:
                json.dump(self.cash, f, indent=4)
            
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
            os.rename(temp_file, self.state_file)
        except IOError as e:
            error_manager.log_system_error("Critical: Failed to save state", e)
            print("Critical Error: Could not save transaction.")

    def add_cash(self, denomination, count):
        """Admin function to add cash."""
        if denomination not in self.cash:
            raise InvalidAmountError(f"Invalid denomination {denomination}")
        
        self.cash[denomination] += count
        self.save_state()
        
        msg = f"Admin added {count} notes of ₹{denomination}"
        error_manager.log_transaction(msg)
        return msg

    def get_breakdown(self, amount):
        """Calculates the best mix of notes using backtracking."""
        denominations = sorted(self.cash.keys(), reverse=True)
        
        def solve(target, idx):
            if target == 0:
                return {}
            if idx >= len(denominations):
                return None
            
            denom = denominations[idx]
            max_use = min(self.cash[denom], target // denom)
            
            for count in range(max_use, -1, -1):
                remainder = target - (count * denom)
                result = solve(remainder, idx + 1)
                
                if result is not None:
                    if count > 0:
                        result[denom] = count
                    return result
            return None

        return solve(amount, 0)

    def withdraw(self, amount):
        """Core withdrawal logic."""
        if amount <= 0:
            raise InvalidAmountError("Amount must be positive.")
        if amount % 100 != 0:
            raise InvalidAmountError("Amount must be a multiple of 100.")

        total_balance = sum(k * v for k, v in self.cash.items())
        if amount > total_balance:
            raise InsufficientFundsError("ATM Insufficient funds.")

        plan = self.get_breakdown(amount)
        if not plan:
            raise InsufficientFundsError("Cannot dispense this amount with available notes.")

        # Execute transaction
        for denom, count in plan.items():
            self.cash[denom] -= count
        
        self.save_state()
        error_manager.log_transaction(f"Withdrawal: ₹{amount} | Breakdown: {plan}")
        return plan

    def get_status_report(self):
        """Returns a formatted status report dictionary."""
        report = {
            "breakdown": {},
            "total": 0
        }
        for denom in sorted(self.cash.keys(), reverse=True):
            count = self.cash[denom]
            val = denom * count
            report["breakdown"][denom] = {"count": count, "value": val}
            report["total"] += val
        return report
