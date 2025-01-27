class EnergyBank:
    def __init__(self, capacity: float, charge_per_hour: float, discharge_per_hour: float, initial_energy: float=0):
        """
        Init the energy bank with a given capacity
        :param capacity: the capacity of the energy bank in kWh
        :param charge_per_hour: the rate at which the energy bank can be charged in kWh
        :param discharge_per_hour: the rate at which the energy bank can be discharged in kWh
        :param initial_energy: the initial energy level of the energy bank in kWh
        """
        self.capacity = capacity
        self.charge_per_hour = charge_per_hour
        self.discharge_per_hour = discharge_per_hour
        self.energy = initial_energy
        # TODO: Add the energy bank efficiency

    def charge(self):
        """
        Charge the energy bank by the charge_per_hour rate
        :return: the amount of energy charged
        """
        charged = min(self.capacity - self.energy, self.charge_per_hour) # TODO: Multiply it by the efficiency factor
        self.energy += charged
        return charged


    def charge_amount(self, amount):
        """
        Charge the energy bank by the given amount
        :param amount: the amount of energy to charge
        :return: the amount of energy charged
        """
        charged = min(self.capacity - self.energy, amount)  # TODO: Multiply it by the efficiency factor
        self.energy += charged
        return charged

    def discharge(self):
        """
        Discharge the energy bank by the given amount
        :return: the amount of energy discharged
        """
        discharged = min(self.energy, self.discharge_per_hour) # TODO: Multiply it by the efficiency factor
        self.energy -= discharged
        return discharged


    def discharge_amount(self, amount):
        """
        Discharge the energy bank by the given amount
        :param amount: the amount of energy to discharge
        :return: the amount of energy discharged
        """
        discharged = min(self.energy, amount) # TODO: Multiply it by the efficiency factor
        self.energy -= discharged
        return discharged

    def get_energy_percentage(self):
        """
        Get the percentage of energy stored in the energy bank
        :return: the percentage of energy stored
        """
        return self.energy / self.capacity