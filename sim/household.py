from sim.energy_bank import EnergyBank


class Household:
    def __init__(self, daily_energy_usage: float, energy_bank_capacity: float, energy_bank_charge_per_hour: float,
                 energy_bank_discharge_per_hour: float, energy_bank_initial_energy: float = 0):
        """
        Init the household with a given daily energy usage and an energy bank
        :param daily_energy_usage: the daily energy usage of the household in kWh
        :param energy_bank_capacity: the capacity of the energy bank in kWh
        :param energy_bank_charge_per_hour: the rate at which the energy bank can be charged in kWh
        :param energy_bank_discharge_per_hour: the rate at which the energy bank can be discharged in kWh
        :param energy_bank_initial_energy: the initial energy level of the energy bank in kWh
        """
        self.daily_energy_usage = daily_energy_usage
        self.energy_bank = EnergyBank(
            energy_bank_capacity,
            energy_bank_charge_per_hour,
            energy_bank_discharge_per_hour,
            energy_bank_initial_energy
        )
        self.cash_balance = 0


    def energy_bank_charge(self):
        return self.energy_bank.charge()


    def energy_bank_charge_amount(self, amount: float):
        return self.energy_bank.charge_amount(amount)


    def energy_bank_discharge(self):
        return self.energy_bank.discharge()


    def energy_bank_discharge_amount(self, amount: float):
        return self.energy_bank.discharge_amount(amount)

    def get_energy_bank_energy_percentage(self):
        return self.energy_bank.get_energy_percentage()


    def get_daily_energy_usage(self):
        return self.daily_energy_usage


    def get_cash_balance(self):
        return self.cash_balance


    def update_cash_balance(self, amount: float):
        self.cash_balance += amount