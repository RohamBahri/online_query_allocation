import numpy as np
import random
from advertiser import Advertiser


class InputGenerator:
    """
    Generates input sequences (bids, budgets, and queries) for the optimistic and pessimistic algorithms.
    Allows adding patterns and noise to simulate realistic scenarios.
    """

    def __init__(self, n_advertisers, n_keywords, budget_range, bid_range, noise_level=0.2):
        """
        Initialize the input generator.

        Args:
            n_advertisers (int): Number of advertisers.
            n_keywords (int): Number of keywords.
            budget_range (tuple): Range of budgets (min, max).
            bid_range (tuple): Range of bids (min, max).
            noise_level (float): Level of randomness/noise to add to bids and budgets (0 to 1).
        """
        self.n_advertisers = n_advertisers
        self.n_keywords = n_keywords
        self.budget_range = budget_range
        self.bid_range = bid_range
        self.noise_level = noise_level

    def generate_advertisers(self):
        """
        Generate advertisers with random budgets with optional noise.

        Returns:
            list: [Advertiser].
        """
        budgets = np.random.uniform(
            self.budget_range[0], self.budget_range[1], self.n_advertisers
        )
        noise = np.random.normal(0, self.noise_level * np.mean(budgets), len(budgets))
        budgets = np.maximum(budgets + noise, 1)  # Ensure budgets are positive

        return [Advertiser(f"A{i+1}", budgets[i]) for i in range(self.n_advertisers)]

    def generate_bids(self, advertisers):
        """
        Generate random bids for each advertiser and keyword with optional noise.

        Returns:
            dict: Bids for each advertiser and keyword {advertiser: {keyword: bid}}.
        """
        bids = {}
        for advertiser in advertisers:
            bids[advertiser.name] = {
                f"k{j+1}": max(
                    round(np.random.uniform(self.bid_range[0], self.bid_range[1]) + np.random.normal(0, self.noise_level * self.bid_range[1]), 2),
                    0,
                )
                for j in range(self.n_keywords)
            }
        return bids

    def generate_query_sequence(self, length):
        """
        Generate a sequence of queries based on a specified pattern.

        Args:
            length (int): Length of the query sequence.
            pattern (str): Distribution pattern for queries ("uniform", "skewed").

        Returns:
            list: Sequence of keywords.
        """
        keywords = [f"k{i+1}" for i in range(self.n_keywords)]

        # Uniformly distributed queries
        return np.random.choice(keywords, size=length).tolist()


    def generate_inputs(self, query_length):
        """
        Generate full inputs for the algorithms: budgets, bids, and query sequence.

        Args:
            query_length (int): Length of the query sequence.
            query_pattern (str): Pattern of the query sequence ("uniform" or "skewed").

        Returns:
            tuple: (budgets, bids, query_sequence)
                - budgets: {advertiser: budget}.
                - bids: {advertiser: {keyword: bid}}.
                - query_sequence: List of keywords.
        """
        advertisers = self.generate_advertisers()
        bids = self.generate_bids(advertisers)
        query_sequence = self.generate_query_sequence(query_length)
        
        return advertisers, bids, query_sequence


# Example Usage
if __name__ == "__main__":
    # Parameters
    n_advertisers = 5
    n_keywords = 5
    budget_range = (500, 1000)
    bid_range = (1, 10)
    prediction_error_level = 0.5
    noise_level = 0.2
    query_length = 20

    # Instantiate the input generator
    generator = InputGenerator(n_advertisers, n_keywords, budget_range, bid_range, noise_level)

    # Generate inputs
    advertisers, bids, query_sequence = generator.generate_inputs(query_length)
    
    from utils import generate_predicted_query_sequence
    predicted_queries = generate_predicted_query_sequence(query_sequence, n_keywords, prediction_error_level)

    # Print generated inputs
    print("Advertisers:")
    print([advertiser.name for advertiser in advertisers])
    print("Bids:", bids)
    print("Query Sequence:", query_sequence)
    print("Predicted Sequence:", predicted_queries)
