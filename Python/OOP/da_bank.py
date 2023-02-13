class BankAccount:
    def __init__(self, holder_name: str, initial_balance: float = 0) -> None:
        self.holder_name = holder_name
        self.balance = initial_balance

    def deposit(self, amount: float) -> float:
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        self.balance -= amount
        return self.balance

mybankaccount = BankAccount("Nathan Reynolds", 5)

mybankaccount.deposit(100)  # Moneyyy!
mybankaccount.withdraw(15)  # For a nice meal.

print(mybankaccount.balance)