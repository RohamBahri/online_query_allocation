import numpy as np
from scipy.optimize import linprog
from algorithm import Algorithm
from advertiser import Advertiser


class OfflineMaximizationProblem:
    """
    Implements the offline optimistic algorithm using a linear programming (LP) approach.
    """

    def __init__(self, n_keywords, bids, advertisers, predicted_queries, solver_method="highs"):
        self.n_keywords = n_keywords
        self.bids = bids
        self.advertisers = advertisers
        self.predicted_queries = predicted_queries
        self.solver_method = solver_method
        self.solution = None  # Stores the LP decision variables
        self.allocations = None  # Stores the final integer allocations

    def solve_allocation(self):
        """
        Solve the offline LP for optimal allocation and store the decision variables.
        """
        n_advertisers = len(self.advertisers)
        n_keywords = self.n_keywords
        keywords = [f"k{i+1}" for i in range(self.n_keywords)]

        # Flatten bids for LP
        c = []
        for keyword in keywords:
            c.extend([-self.bids.get(advertiser.name, {}).get(keyword, 0) for advertiser in self.advertisers])
        
        # Constraints for budgets and queries
        A_ub = []
        b_ub = []

        # Budget constraints
        for i, advertiser in enumerate(self.advertisers):
            row = [0] * (n_advertisers * n_keywords)
            for j, keyword in enumerate(keywords):
                row[i + j * n_advertisers] = self.bids.get(advertiser.name, {}).get(keyword, 0)
            A_ub.append(row)
            b_ub.append(advertiser.initial_budget)

        # Query volume constraints
        for j, keyword in enumerate(keywords):
            row = [0] * (n_advertisers * n_keywords)
            for i, advertiser in enumerate(self.advertisers):
                row[i + j * n_advertisers] = 1
            A_ub.append(row)
            b_ub.append(self.predicted_queries[keyword])

        bounds = [(0, None) for _ in range(n_advertisers * n_keywords)]

        # Solve LP
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method=self.solver_method)

        if result.success:
            # Store fractional decision variables
            self.solution = result.x

            # Convert to integer allocations while respecting constraints
            self.round_solution_to_integers(n_advertisers, keywords)
        else:
            print("LP solver error details:")
            print("Message:", result.message)
            print("Status:", result.status)
            raise ValueError("LP solver failed to find an optimal solution.")

    def round_solution_to_integers(self, n_advertisers, keywords):
        """
        Round fractional solutions to integers without violating constraints and store in a 2D matrix.
        """
        allocations = np.zeros((n_advertisers, len(keywords)), dtype=int)
        advertisers = self.advertisers.copy()
        remaining_queries = {keyword: self.predicted_queries[keyword] for keyword in keywords}

        # Prioritize higher fractional values
        fractional_indices = sorted(
            range(len(self.solution)), key=lambda i: -self.solution[i]
        )

        for idx in fractional_indices:
            if self.solution[idx] == 0:
                continue

            advertiser_idx = idx % n_advertisers
            keyword_idx = idx // n_advertisers
            advertiser = advertisers[advertiser_idx]
            keyword = keywords[keyword_idx]

            # Allocate as much as possible while respecting constraints
            max_allocation = min(
                int(self.solution[idx]),  # Fractional allocation rounded down
                remaining_queries[keyword],
                (advertiser.initial_budget - advertiser.spent_budget) // self.bids[advertiser.name].get(keyword, 1),
            )
            allocations[advertiser_idx, keyword_idx] = max_allocation
            advertiser.deduct_budget(max_allocation * self.bids[advertiser.name].get(keyword, 1))
            remaining_queries[keyword] -= max_allocation

        # Store the allocations in the 2D matrix
        self.allocations = allocations


class OptimisticAlgorithm(Algorithm):
    def __init__(self, n_keywords, bids, predicted_queries, running_in_balanced):
        """
        Initialize the online allocator, solving the offline allocation problem internally.

        Args:
            n_keywords (int): Number of keywords.
            bids (dict): Advertisers' bids for queries.
            advertisers (list[Advertisers]): Advertisers.
            predicted_queries (dict): Predicted query frequencies (e.g., {'k1': 3, 'k2': 2, ...}).
        """
        # Create and solve the OfflineMaximizationProblem internally
        oracle = OfflineMaximizationProblem(n_keywords, bids, Advertiser.get_advertiser_list_copy(), predicted_queries)
        oracle.solve_allocation()

        # Use the oracle's solution for online allocation
        self.remaining_queries = predicted_queries.copy()
        self.offline_allocations = oracle.allocations  # 2D matrix of allocations
        self.advertisers = Advertiser.get_advertiser_list_copy() if running_in_balanced else Advertiser.get_advertisers()
        self.bids = bids
        self.keywords = list(predicted_queries.keys())

    def allocate_query(self, query):
        """
        Allocate a single query as it arrives, updating internal states incrementally.

        Args:
            query (str): The query keyword to allocate.

        Returns:
            Advertiser or None: The advertiser assigned to the query, or None if no allocation is possible, bid 
        """
        # If the query exceeds its predicted frequency, dismiss it
        if self.remaining_queries.get(query, 0) <= 0:
            return None, 0

        # Get the index of the query in the keywords list
        if query not in self.keywords:
            return None, 0
        keyword_idx = self.keywords.index(query)

        # Find the list of advertisers assigned to this query in the offline allocations
        assigned_advertisers = []
        for advertiser_idx, advertiser in enumerate(self.advertisers):
            if self.offline_allocations[advertiser_idx][keyword_idx] > 0:
                assigned_advertisers.append(advertiser)

        if not assigned_advertisers:
            # If no offline assignment exists, dismiss the query
            return None, 0

        # Find the highest bid among the assigned advertisers
        assigned_advertiser = None
        highest_bid = -1
        for advertiser in assigned_advertisers:
            bid = self.bids[advertiser.name].get(query, 0)
            if (advertiser.remaining_budget()) >= bid and bid > highest_bid:
                assigned_advertiser = advertiser
                highest_bid = bid

        # Allocate the query if a suitable advertiser is found
        if assigned_advertiser:
            advertiser_idx = self.advertisers.index(assigned_advertiser)
            self.offline_allocations[advertiser_idx][keyword_idx] -= 1
            assigned_advertiser.deduct_budget(highest_bid)
            self.remaining_queries[query] -= 1
            return assigned_advertiser, highest_bid

        # Otherwise, no allocation is possible
        return None, 0


# Example usage
if __name__ == "__main__":
    advertisers = [Advertiser("A1", 1000), Advertiser("A2", 1000)]    
    bids = {
        advertisers[0].name: {"k1": 10, "k2": 1},
        advertisers[1].name: {"k1": 1, "k2": 10, 'k3': 1},
    }
    
    n_keywords = 3
    predicted_query_sequence = ['k2', 'k2', 'k1', 'k1', 'k2', 'k3']
    predicted_queries = {f"k{i+1}": predicted_query_sequence.count(f"k{i+1}") for i in range(n_keywords)}

    # Initialize the optimistic allocator
    allocator = OptimisticAlgorithm(n_keywords, bids, predicted_queries, False)

    online_query_sequence = ['k2', 'k2', 'k1', 'k1', 'k2', 'k3']

    for query in online_query_sequence:
        allocation, bid = allocator.allocate_query(query)
        print(f"Query '{query}' allocated to: {allocation, allocation.spent_budget} with bid {bid}")

    print([(advertiser.name, advertiser.spent_budget) for advertiser in Advertiser.get_advertisers()])
    print([(advertiser.name, advertiser.spent_budget) for advertiser in Advertiser.get_advertiser_list_copy()])