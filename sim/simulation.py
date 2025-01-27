import pandas as pd
from household import Household
import data.data_scrapper as data
import time

# Percentage of the daily energy usage that the household will use per hour
energy_per_hour = {
    0: 0.015,
    1: 0.015,
    2: 0.015,
    3: 0.015,
    4: 0.015,
    5: 0.015,
    6: 0.04,
    7: 0.06,
    8: 0.06,
    9: 0.03,
    10: 0.03,
    11: 0.03,
    12: 0.03,
    13: 0.03,
    14: 0.03,
    15: 0.03,
    16: 0.075,
    17: 0.1,
    18: 0.1,
    19: 0.1,
    20: 0.125,
    21: 0.05,
    22: 0.04,
    23: 0.04
}


def run_sim():
    """

    :return:
    """
    # Create households
    household1 = Household(20, 50, 10, 10, 25)
    household2 = Household(20, 100, 10, 10, 50)
    householdTrading1 = Household(20, 50, 10, 10, 25)
    householdTrading2 = Household(20, 100, 10, 10, 50)

    # Load TGE data
    df = data.load_data_from_csv('../data/tge_data_2024_12_01__31_days_perdiod.csv')
    # Change the 'Kurs' from PLN/MWh to PLN/kWh and 'Wolumen' from MWh to kWh
    df.columns = ['Czas', 'Kurs', 'Wolumen']
    df['Kurs'] = df['Kurs'] / 1000
    df['Wolumen'] = df['Wolumen'] * 1000

    # Iterate through the data day by day (every 24 rows of df) starting from the second row
    for i in range(24, len(df), 24):
        print("Calculating for day: ", df['Czas'][i])
        # Get the data for the next day
        df_day = df[i:i+24]
        print(df_day)


        compared_data = data.compare_prices_to_statistics(
            df_day,
            data.average_price(df_day, 'Kurs'),
            data.std_dev_price(df_day, 'Kurs'),
            1.5,
            'Kurs'
        )
        # Get the cheapest and the most expensive hours of the day
        cheapest_hours = data.quantile_cheapest_hours(df_day, 0.25, 'Kurs')
        # Get the most expensive hours of the day
        expensive_hours = data.quantile_cheapest_hours(df_day, 0.75, 'Kurs')
        # Set the dictionary with the energy usage for the next day
        energy_usage = {}

        if len(compared_data['cheapest_hours']) > 6:
            for j in range(24):
                if j in compared_data['cheapest_hours']:
                    energy_usage[j] = "buy"
                elif j in expensive_hours:
                    energy_usage[j] = "sell"
                else:
                    energy_usage[j] = "depends"
        else:
            for j in range(24):
                if j in cheapest_hours:
                    energy_usage[j] = "buy"
                elif j in expensive_hours:
                    energy_usage[j] = "sell"
                else:
                    energy_usage[j] = "depends"

        print("strategy for the day: ", energy_usage)

        # Track the costs and/or incomes hour by hour
        for j in range(24):
            price_h = df_day['Kurs'].iloc[j]
            energy_usage_h = energy_per_hour[j]
            if energy_usage[j] == "buy":
                for household in [household1, household2, householdTrading1, householdTrading2]:
                    charged = household.energy_bank.charge()
                    household.update_cash_balance(-price_h * energy_usage_h * household.daily_energy_usage)
                    household.update_cash_balance(-price_h * charged)

            elif energy_usage[j] == "sell":
                for household in [household1, household2, householdTrading1, householdTrading2]:
                    energy_for_household = household.daily_energy_usage * energy_usage_h
                    discharged = household.energy_bank.discharge_amount(energy_for_household)
                    energy_for_household -= discharged
                    if energy_for_household > 0:
                        household.update_cash_balance(-price_h * energy_for_household)
                    if household in [householdTrading1, householdTrading2]:
                        discharged = household.energy_bank.discharge()
                        household.update_cash_balance(price_h * discharged)

            else:
                for household in [household1, household2, householdTrading1, householdTrading2]:
                    if household.energy_bank.get_energy_percentage() < 0.05:
                        charged = household.energy_bank.charge()
                        household.update_cash_balance(-price_h * charged)
                    elif household.energy_bank.get_energy_percentage() > 0.95 and household in [householdTrading1, householdTrading2]:
                        discharged = household.energy_bank.discharge()
                        household.update_cash_balance(price_h * discharged)
                    energy_for_household = household.daily_energy_usage * energy_usage_h
                    discharged = household.energy_bank.discharge_amount(energy_for_household)
                    energy_for_household -= discharged
                    if energy_for_household > 0:
                        household.update_cash_balance(-price_h * energy_for_household)

    print("Household 1 cash balance: ", household1.get_cash_balance())
    print("Household 2 cash balance: ", household2.get_cash_balance())
    print("Household Trading 1 cash balance: ", householdTrading1.get_cash_balance())
    print("Household Trading 2 cash balance: ", householdTrading2.get_cash_balance())


if __name__ == '__main__':
    run_sim()