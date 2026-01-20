import sys
from atm_core import ATM
from error_handling import error_manager

def display_status(atm):
    report = atm.get_status_report()
    print("\n--- ATM Status ---")
    for denom, data in report["breakdown"].items():
        print(f"₹{denom:<4}: {data['count']} notes = ₹{data['value']}")
    print(f"Total Cash: ₹{report['total']}")
    print("------------------")

def main():
    atm = ATM()
    
    while True:
        print("\n=== ATM SYSTEM ===")
        print("1. Withdraw Cash")
        print("2. Admin: Add Cash")
        print("3. Admin: View Status")
        print("4. Exit")
        
        try:
            choice = input("Select Option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break
        
        if choice == "1":
            try:
                raw_amt = input("Enter withdrawal amount: ")
                if not raw_amt.isdigit():
                    raise ValueError("Amount must be numeric")
                    
                amount = int(raw_amt)
                breakdown = atm.withdraw(amount)
                
                print("\nTransaction Successful!")
                print("Dispensing:")
                for denom, count in breakdown.items():
                    print(f"  ₹{denom} x {count}")
                    
            except Exception as e:
                msg = error_manager.handle_user_error(e)
                print(msg)

        elif choice == "2":
            try:
                denom_input = input("Enter denomination (100, 200, 500): ")
                if not denom_input.isdigit():
                    raise ValueError("Denomination must be numeric")
                denom = int(denom_input)
                
                if denom not in [100, 200, 500]:
                     raise ValueError("Invalid denomination")

                count_input = input("Enter quantity to add: ")
                if not count_input.isdigit():
                    raise ValueError("Quantity must be numeric")
                count = int(count_input)
                
                msg = atm.add_cash(denom, count)
                print(f"{msg}")
            except Exception as e:
                msg = error_manager.handle_user_error(e)
                print(msg)

        elif choice == "3":
            display_status(atm)

        elif choice == "4":
            print("Thank you for banking with us.")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
