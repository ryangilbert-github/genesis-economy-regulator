import random

class Economy:
    """
    Represents the Global Economic State.
    Tracks Money Supply (Inflation) and handles transactions.
    """

    def __init__(self, start_money=100_000_000, start_tax=0.05):
        self.money_supply = start_money
        self.tax_rate = start_tax
        self.inflation_target = 100_000_000  # The "Healthy" baseline
        self.inflation_rate = 0.0

    def transaction(self, volume):
        """
        Simulates player trade volume.
        The Tax Rate determines how much money is BURNED (removed from game).
        """
        burn_amount = volume * self.tax_rate
        self.money_supply -= burn_amount
        return burn_amount

    def inject_money(self, amount):
        """ Simulates monster kills (Faucets) or Admin events. """
        self.money_supply += amount

    def update_economy(self):
        """
        Moves the economy forward by one 'month'.
        Simulates random market fluctuations and calculates inflation.
        """
        # 1. Simulate random market activity (Farming vs Taxes)
        # Growth factor between 0.98 (Recession) and 1.15 (Boom)
        growth_factor = random.uniform(0.98, 1.15)
        self.money_supply = int(self.money_supply * growth_factor)

        # 2. Calculate Inflation
        # Logic: (Current Money / Target Money) - 1
        # Example: 150M / 100M = 1.5 -> 50% Inflation
        raw_inflation = (self.money_supply / self.inflation_target) - 1.0
        self.inflation_rate = round(raw_inflation * 100, 2)

        # 3. Return stats for the AI
        return {
            "money_supply": self.money_supply,
            "inflation_rate": self.inflation_rate,
            "tax_rate": self.tax_rate
        }