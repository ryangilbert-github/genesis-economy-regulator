class Economy:
    """
    Represents the Global Economic State.
    Tracks Money Supply (Inflation) and handles transactions.
    """

    def __init__(self, start_money=1000000, start_tax=0.05):
        self.money_supply = start_money
        self.tax_rate = start_tax
        self.inflation_target = start_money  # The "Healthy" baseline

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