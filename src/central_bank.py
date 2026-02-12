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

        # --- STRATEGY 1: THE HAWK (Aggressive) ---
        if "Hawk" in self.strategy:
            # Panic Early: If inflation > 1%, slam the brakes
            if current > target * 1.01:
                # VIOLENT BRAKING: +15% Tax instantly
                economy.tax_rate = min(0.90, economy.tax_rate + 0.15)
            elif current < target * 0.99:
                economy.tax_rate = 0.01

        # --- STRATEGY 2: THE DOVE (Passive) ---
        elif "Dove" in self.strategy:
            # Wait until inflation is HUGE (>50%) before doing anything
            if current > target * 1.50:
                # TINY STEPS: +0.1% Tax only
                economy.tax_rate = min(0.20, economy.tax_rate + 0.001)
            elif current < target * 0.90:
                economy.tax_rate = max(0.01, economy.tax_rate - 0.01)

        # --- STRATEGY 3: BALANCED (Standard) ---
        else:
            # The Goldilocks Zone
            if current > target * 1.10:
                # Moderate Ramp: +2% Tax
                economy.tax_rate = min(0.50, economy.tax_rate + 0.02)
            elif current < target * 0.90:
                economy.tax_rate = max(0.01, economy.tax_rate - 0.01)

        return economy.tax_rate