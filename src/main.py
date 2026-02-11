import time
from economy import Economy  # <--- FIXED IMPORT
from quest_generator import QuestGenerator


def run_simulation_cycle():
    """
    The Master Loop:
    1. Steps the Economy forward.
    2. Checks for crisis.
    3. If crisis -> Generates AI Quest to fix it.
    4. Saves everything to the Database.
    """
    print("\n" + "=" * 50)
    print("🚀 STARTING GENESIS ECONOMY SIMULATION")
    print("=" * 50)

    # 1. Initialize the Sub-Systems
    # We use your Economy class now!
    economy = Economy(start_money=150_000_000)  # Start high to force inflation
    quest_bot = QuestGenerator()

    # 2. Run the Economy (Simulate 1 Month of trading)
    print("\n📊 STEP 1: Simulating Economy...")
    stats = economy.update_economy()

    print(f"   - Money Supply: {stats['money_supply']:,} Gold")
    print(f"   - Inflation Rate: {stats['inflation_rate']:.2f}%")
    print(f"   - Tax Rate: {stats['tax_rate'] * 100:.1f}%")

    # 3. Analyze the Condition
    if stats['inflation_rate'] > 5.0:
        condition = "Hyper-Inflation"
        severity = 8
        sentiment = "Panic"
    elif stats['inflation_rate'] < -2.0:
        condition = "Deflationary Spiral"
        severity = 7
        sentiment = "Depression"
    else:
        condition = "Stable"
        severity = 0
        sentiment = "Happy"

    print(f"\n🔍 STEP 2: Diagnosing State -> {condition.upper()}")

    # 4. Trigger AI if needed
    if condition != "Stable":
        print(f"   ⚠️ CRISIS DETECTED! Awakening the Grand Archivist...")

        # Prepare the data packet for the AI
        economy_state = {
            "condition": condition,
            "severity": severity,
            "inflation": stats['inflation_rate'],
            "sentiment": sentiment
        }

        # Generate and Save
        quest = quest_bot.generate_quest(economy_state)

        if "error" not in quest:
            # We call save_quest (which saves to Cloud AND Disk)
            quest_bot.save_quest(quest)
            print(f"\n✅ ACTION TAKEN: Generated Quest '{quest['title']}'")
        else:
            print(f"\n❌ ERROR: {quest['error']}")

    else:
        print("\n✅ ECONOMY STABLE: No AI intervention needed.")

    print("\n" + "=" * 50)
    print("🏁 CYCLE COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    run_simulation_cycle()