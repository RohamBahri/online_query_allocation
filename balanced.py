from algorithm import Algorithm
from utils import phi_alpha
from pessimistic import PessimisticAlgorithm
from optimistic import OptimisticAlgorithm
from advertiser import Advertiser

class BalancedAlgorithm(Algorithm):
    """
    Implements the allocation framework combining optimistic (O) and pessimistic (P) algorithms.
    """

    def __init__(self, n_keywords, bids, predicted_queries, alpha):
        """
        Initialize the framework.

        Args:
            n_keywords (int): Number of keywords.
            bids (dict): Advertisers' bids for queries.
            predicted_queries (dict): Predicted query frequencies.
            alpha (float): Parameter controlling the balance between optimistic and pessimistic strategies.
        """
        self.bids = bids
        self.optimistic_algorithm = OptimisticAlgorithm(n_keywords, bids, predicted_queries, True)
        self.pessimistic_algorithm = PessimisticAlgorithm(bids, alpha, True)
        self.alpha = alpha

        self.allocations=[0,0] # o, p

    def allocate_query(self, query):
        """
        Allocate a query based on the balanced strategy.

        Args:
            query (str): The query to allocate.

        Returns:
            str or None: The name of the advertiser allocated to the query, or None if no allocation is possible.
        """
        Advertiser.reset_advertiser_list_copy()
        o_copy = self.optimistic_algorithm.allocate_query(query)
        p_copy = self.pessimistic_algorithm.allocate_query(query)

        if o_copy[0]:
            o = [adv for adv in Advertiser.get_advertisers() if adv.name == o_copy[0].name][0], o_copy[1]
        else:
            o = None, 0

        if p_copy[0]:
            p = [adv for adv in Advertiser.get_advertisers() if adv.name == p_copy[0].name][0], p_copy[1]
        else:
            p = None, 0

        if not o[0] and not p[0]:
            return None, 0

        # Calculate scores for both optimistic and pessimistic recommendations
        o_score = (
            phi_alpha(o[0].budget_fraction(), self.alpha)
            * o[1]
            if o[0] else float('-inf')
        )
        p_score = (
            phi_alpha(p[0].budget_fraction(), self.alpha)
            * p[1]
            if p[0] else float('-inf')
        )

        # Select advertiser based on scores   

        if (self.alpha * o_score) >= p_score:
            chosen_advertiser = o[0]
            bid_amount = o[1]
            self.allocations[0] += 1
        else:
            chosen_advertiser = p[0]
            bid_amount = p[1]
            self.allocations[1] += 1
            if (self.alpha > 1 and o[0]): print("alpha, o_score and p_score:", self.alpha, o_score, p_score)

        chosen_advertiser.deduct_budget(bid_amount)
        
        return chosen_advertiser, bid_amount


# Example usage
if __name__ == "__main__":
    # Sample input
    n_keywords = 3
    advertisers = [Advertiser("A1", 1000), Advertiser("A2", 500)]    
    alpha = 10
    bids = {
        advertisers[0].name: {'k1': 11, 'k2': 1}, 
        advertisers[1].name: {'k1': 1, 'k2': 10, 'k3': 1}
    }
    
    # Online query sequence
    predicted_query_sequence = ['k2', 'k1', 'k1', 'k1', 'k2', 'k3']
    predicted_queries = {f"k{i+1}": predicted_query_sequence.count(f"k{i+1}") for i in range(n_keywords)}

    allocator = BalancedAlgorithm(n_keywords, bids, predicted_queries, alpha)

    online_query_sequence = ['k2', 'k1', 'k1', 'k1', 'k2', 'k2']

    # Process the query sequence
    for query in online_query_sequence:
        allocation, bid = allocator.allocate_query(query)
        print(f"Query '{query}' allocated to: {allocation, allocation.spent_budget} with bid {bid}")
    print(allocator.allocations)

    print([(advertiser.name, advertiser.spent_budget) for advertiser in Advertiser.get_advertisers()])
