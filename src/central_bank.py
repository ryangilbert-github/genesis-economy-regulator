class CentralBankAI:
    """
    The Automated Regulator.
    Monitors the Economy and adjusts Tax Rates using Control Theory (PID-like logic).
    """

    def __init__(self, strategy="Balanced"):
        self.strategy = strategy

    def decide_policy(self, economy):
        """
        Analyzes the Money Supply and returns the new Tax Rate.
        """
        current = economy.money_supply
        target = economy.inflation_target

        # --- STRATEGY 1: LAISSEZ-FAIRE (Control Group) ---
        if "Laissez" in self.strategy:
            return 0.05  # Fixed 5% tax forever.

        # --- STRATEGY 2: THE HAWK (Aggressive) ---
        if "Hawk" in self.strategy:
            # Reacts early (5% inflation) and hits hard
            if current > target * 1.05:
                # Panic Mode: Raises tax drastically!
                step = 0.05 if current > target * 1.20 else 0.02
                economy.tax_rate = min(0.99, economy.tax_rate + step)
            elif current < target * 0.95:
                economy.tax_rate = max(0.01, economy.tax_rate - 0.02)

        # --- STRATEGY 3: THE DOVE (Conservative) ---
        elif "Dove" in self.strategy:
            # Waits for 20% inflation before moving
            if current > target * 1.20:
                # Gentle touches only
                step = 0.02 if current > target * 1.50 else 0.005
                economy.tax_rate = min(0.30, economy.tax_rate + step)  # Cap at 30% tax
            elif current < target * 0.80:
                economy.tax_rate = max(0.01, economy.tax_rate - 0.005)

        # --- STRATEGY 4: BALANCED (Standard) ---
        else:
            if current > target * 1.10:
                step = 0.05 if current > target * 1.50 else 0.01
                economy.tax_rate = min(0.50, economy.tax_rate + step)
            elif current < target * 0.90:
                economy.tax_rate = max(0.01, economy.tax_rate - 0.01)

        return economy.tax_rate