from algorithm import Algorithm
from utils import phi_alpha
from advertiser import Advertiser

class PessimisticAlgorithm(Algorithm):
    """
    Implements the pessimistic allocation algorithm.
    """

    def __init__(self, bids, alpha, running_in_balanced):
        """
        Initialize the pessimistic algorithm.

        Args:
            bids (dict): Advertisers' bids for queries.
            advertisers (list[Advertiser]): Advertisers with their respective budgets.
            alpha (float): Parameter controlling the scoring function.
        """
        self.bids = bids
        self.advertisers = Advertiser.get_advertiser_list_copy() if running_in_balanced else Advertiser.get_advertisers()  
        self.alpha = alpha if running_in_balanced else 1.0

    def allocate_query(self, query):
        """
        Recommend an advertiser for the given query based on the pessimistic strategy.

        Args:
            query (str): The query keyword to allocate.

        Returns:
            Advertiser or None: The recommended advertiser object, or None if no allocation is possible.
        """
        # Evaluate all advertisers for their scores
        best_advertiser = None
        highest_score = float('-inf')
        best_bid = 0

        for advertiser in self.advertisers:
            bid = self.bids.get(advertiser.name, {}).get(query, 0)
            
            if bid > 0 and advertiser.remaining_budget() >= bid:
                score = phi_alpha(advertiser.budget_fraction(), self.alpha) * bid
                if score > highest_score:
                    highest_score = score
                    best_advertiser = advertiser
                    best_bid = bid

        # Return the advertiser with the highest score
        if best_advertiser: 
            best_advertiser.deduct_budget(best_bid)
            return best_advertiser, best_bid

        return None, 0


# Example usage
if __name__ == "__main__":
    # Sample input
    advertisers = [Advertiser("A1", 1000), Advertiser("A2", 1000)]    
    alpha = 1.5
    bids = {
        advertisers[0].name: {'k1': 11, 'k2': 1}, 
        advertisers[1].name: {'k1': 1, 'k2': 10, 'k3': 1}
    }
    # Initialize the PessimisticAllocation instance
    allocator = PessimisticAlgorithm(bids, alpha, False)

    # Online query sequence
    online_query_sequence = ['k2', 'k1', 'k1', 'k1', 'k2', 'k3']

    # Process the query sequence
    for query in online_query_sequence:
        allocation, bid = allocator.allocate_query(query)
        print(f"Query '{query}' allocated to: {allocation, allocation.spent_budget} with bid {bid}")

    print([(advertiser.name, advertiser.spent_budget) for advertiser in Advertiser.get_advertisers()])
    print([(advertiser.name, advertiser.spent_budget) for advertiser in Advertiser.get_advertiser_list_copy()])
    
