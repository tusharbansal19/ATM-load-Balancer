import json
import os
import logging
from exceptions import ATMError, InsufficientFundsError, InvalidAmountError

class ATM:
    def __init__(self, state_file="cash_state.json"):
        self.state_file = state_file
        self.cash = {500: 20, 200: 20, 100: 20}
        self.load_state()

    def load_state(self):
        if not os.path.exists(self.state_file):
            self.save_state()
            return

        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
                self.cash = {int(k): v for k, v in data.items()}
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Failed to load state: {e}")
            print("Error loading system state. Resetting to default.")
            self.save_state()
        except IOError as e:
            logging.error(f"IO Error during load: {e}")
            print(f"System Error: {e}")

    def save_state(self):
        try:
            temp_file = self.state_file + ".tmp"
            with open(temp_file, "w") as f:
                json.dump(self.cash, f, indent=4)
            
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
            os.rename(temp_file, self.state_file)
        except IOError as e:
            logging.error(f"Failed to save state: {e}")
            print("Critical Error: Could not save transaction state.")

    def add_cash(self, denomination, count):
        if denomination not in self.cash:
            print("Invalid denomination.")
            return
        self.cash[denomination] += count
        self.save_state()
        logging.info(f"Admin added {count} notes of ₹{denomination}")
        print(f"Added {count} notes of ₹{denomination}.")

    def get_breakdown(self, amount):
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
        try:
            if amount <= 0:
                raise InvalidAmountError("Amount must be positive.")
            if amount % 100 != 0:
                raise InvalidAmountError("Amount must be a multiple of 100.")

            total_balance = sum(k * v for k, v in self.cash.items())
            if amount > total_balance:
                raise InsufficientFundsError("ATM Insufficient funds.")

            plan = self.get_breakdown(amount)
            if not plan:
                raise InsufficientFundsError("Cannot dispense this amount with available denominations.")

            for denom, count in plan.items():
                self.cash[denom] -= count
            
            self.save_state()
            logging.info(f"Withdrawal: ₹{amount} | Breakdown: {plan}")
            return plan

        except ATMError as e:
            logging.warning(f"Transaction failed: {e}")
            raise e

    def get_status_report(self):
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
