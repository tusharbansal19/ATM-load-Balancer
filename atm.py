import json
import os
import logging
from datetime import datetime

logging.basicConfig(
    filename='atm_transactions.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ATMError(Exception):
    pass

class InsufficientFundsError(ATMError):
    pass

class InvalidAmountError(ATMError):
    pass

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

    def display_status(self):
        print("\n--- ATM Status ---")
        total = 0
        for denom in sorted(self.cash.keys(), reverse=True):
            count = self.cash[denom]
            val = denom * count
            total += val
            print(f"₹{denom:<4}: {count} notes = ₹{val}")
        print(f"Total Cash: ₹{total}")
        print("------------------")

def main():
    atm = ATM()
    
    while True:
        print("\n=== ATM SYSTEM ===")
        print("1. Withdraw Cash")
        print("2. Admin: Add Cash")
        print("3. Admin: View Status")
        print("4. Exit")
        
        choice = input("Select Option: ").strip()
        
        if choice == "1":
            try:
                raw_amt = input("Enter withdrawal amount: ")
                if not raw_amt.isdigit():
                    print("Error: Please enter a valid numeric amount.")
                    continue
                    
                amount = int(raw_amt)
                breakdown = atm.withdraw(amount)
                
                print("\nTransaction Successful!")
                print("Dispensing:")
                for denom, count in breakdown.items():
                    print(f"  ₹{denom} x {count}")
                    
            except ATMError as e:
                print(f"\nError: {e}")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                print("\nAn unexpected error occurred. Please try again.")

        elif choice == "2":
            try:
                denom = int(input("Enter denomination (100, 200, 500): "))
                if denom not in [100, 200, 500]:
                    print("Invalid denomination.")
                    continue
                count = int(input("Enter quantity to add: "))
                if count < 0:
                    print("Quantity cannot be negative.")
                    continue
                atm.add_cash(denom, count)
            except ValueError:
                print("Invalid input.")

        elif choice == "3":
            atm.display_status()

        elif choice == "4":
            print("Thank you for banking with us.")
            break
        else:
            print("Invalid option. Please try again.")
            

if __name__ == "__main__":
    main()
