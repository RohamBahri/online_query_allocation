import copy

class Advertiser:
    advertisers = []  # Class variable to keep track of all advertisers
    _advertiser_list_copy = None  # Cached copy of the advertiser list

    def __init__(self, name, initial_budget):
        """
        Initialize an advertiser with a given budget.
        
        Args:
            name (str): Name of the advertiser.
            initial_budget (float): Initial budget of the advertiser.
        """
        self.name = name
        self.initial_budget = initial_budget
        self.spent_budget = 0.0
        Advertiser.advertisers.append(self)

    def remaining_budget(self):
        """Calculate the remaining budget."""
        return self.initial_budget - self.spent_budget

    def budget_fraction(self):
        """Calculate the fraction of the budget spent."""
        if self.initial_budget == 0:
            return 1.0  # Fully spent if the budget was zero
        return self.spent_budget / self.initial_budget

    def deduct_budget(self, amount):
        """
        Deduct a specific amount from the advertiser's budget.
        
        Args:
            amount (float): The amount to deduct.
            
        Raises:
            ValueError: If the amount exceeds the remaining budget.
        """
        if amount > self.remaining_budget():
            raise ValueError(f"Cannot deduct {amount}: Insufficient budget for advertiser {self.name}.")
        self.spent_budget += amount

    @classmethod
    def get_advertisers(cls):
        """Return the list of all advertisers."""
        return cls.advertisers

    @classmethod
    def get_advertiser_list_copy(cls):
        """Return a cached deep copy of the advertiser list."""
        if cls._advertiser_list_copy is None:
            cls._advertiser_list_copy = copy.deepcopy(cls.advertisers)
        return cls._advertiser_list_copy

    @classmethod
    def reset_advertiser_list_copy(cls):
        """Reset the cached copy and create a new one."""
        cls._advertiser_list_copy = copy.deepcopy(cls.advertisers)

    @classmethod
    def reset_budgets(cls):
        for a in cls.advertisers:
            a.spent_budget = 0.0

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

# Example usage:
if __name__ == '__main__':
    # Create advertisers
    advertiser1 = Advertiser("Advertiser 1", 1000.0)
    advertiser2 = Advertiser("Advertiser 2", 500.0)

    # Retrieve the original list
    original_list = Advertiser.get_advertisers()

    # Modify a copy of the list (this keeps the original intact)
    copy_list = Advertiser.get_advertiser_list_copy()
    copy_list[0].deduct_budget(200)  # Modifies the copy but not the original

    # Verify the original remains intact
    print([adv.remaining_budget() for adv in original_list])  # Outputs: [1000.0, 500.0]

    # Reset and get a new copy
    Advertiser.reset_advertiser_list_copy()
    new_copy_list = Advertiser.get_advertiser_list_copy()
    print([adv.remaining_budget() for adv in new_copy_list])  # Outputs the new state after reset
