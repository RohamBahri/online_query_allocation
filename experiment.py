from pessimistic import PessimisticAlgorithm
from optimistic import OptimisticAlgorithm
from balanced import BalancedAlgorithm
from input_generator import InputGenerator
from advertiser import Advertiser
from utils import generate_predicted_query_sequence
import pandas as pd


def run_experiment(
    rep,
    advertisers, 
    bids, 
    query_sequence,
    predicted_queries,
    n_keywords,
    prediction_error_level,
    alpha
):
    """
    Run an experiment to evaluate the ad allocation framework.

    Args:
        alpha (float): Parameter balancing optimistic and pessimistic algorithms.

    Returns:
        dict: Summary of the experiment, including total revenue and allocations.
    """

    optimistic_revenue = 0
    pessimistic_revenue = 0
    balanced_revenue = 0

    # Process each query independently
    Advertiser.reset_budgets()
    Advertiser.reset_advertiser_list_copy()
    optimistic_algorithm = OptimisticAlgorithm(n_keywords, bids, predicted_queries, False)
    for query in query_sequence:
        # Optimistic allocation
        opt_advertiser = optimistic_algorithm.allocate_query(query)
        if opt_advertiser[0] is not None:
            optimistic_revenue += opt_advertiser[1]

    Advertiser.reset_budgets()
    Advertiser.reset_advertiser_list_copy()
    pessimistic_algorithm = PessimisticAlgorithm(bids, alpha, False)
    for query in query_sequence:
        # Pessimistic allocation
        pess_advertiser = pessimistic_algorithm.allocate_query(query)
        if pess_advertiser[0] is not None:
            pessimistic_revenue += pess_advertiser[1]

    Advertiser.reset_budgets()
    Advertiser.reset_advertiser_list_copy()
    balanced_algorithm = BalancedAlgorithm(n_keywords, bids, predicted_queries, alpha)
    for query in query_sequence:
        # Framework allocation
        balanced_advertiser = balanced_algorithm.allocate_query(query)
        if balanced_advertiser[0] is not None:
            balanced_revenue += balanced_advertiser[1]

    # Report results

    return {
        "replication": rep,
        "prediction_error_level": prediction_error_level,
        "alpha": alpha,
        "optimistic_revenue": optimistic_revenue,
        "pessimistic_revenue": pessimistic_revenue,
        "balanced_revenue": balanced_revenue
    }


if __name__ == "__main__":
    # Run the experiment
    # Generate inputs
    n_advertisers=100
    n_keywords=100
    budget_range=(10000, 15000)
    bid_range=(1, 10)
    query_length=1000

    input_gen = InputGenerator(
        n_advertisers=n_advertisers,
        n_keywords=n_keywords,
        budget_range=budget_range,
        bid_range=bid_range
    )

    results = []

    for rep in range(1, 11):
        advertisers, bids, query_sequence = input_gen.generate_inputs(query_length)
        for prediction_error_level in [0.0, 0.25, 0.5]:
            predicted_queries = generate_predicted_query_sequence(query_sequence, n_keywords, prediction_error_level)
            for alpha in [1.0, 2.0, 4.0, 5.0, 10]:
                print(f"Replication: {rep}, Alpha: {alpha}, Prediction Error Level: {prediction_error_level}")
                result = run_experiment(
                    rep=rep,
                    advertisers=advertisers, 
                    bids=bids, 
                    query_sequence=query_sequence,
                    predicted_queries=predicted_queries,
                    n_keywords=n_keywords,
                    prediction_error_level=prediction_error_level,
                    alpha=alpha
                )
                results.append(result)

    results_df = pd.DataFrame(results)
    results_df.to_excel('outputs/ad_allocation_experiment_results.xlsx', index=False, sheet_name='data')
    
