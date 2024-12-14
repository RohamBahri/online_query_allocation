import math
import random


def phi_alpha(f, alpha):
    """
    Args:
        f (float): Fraction of budget spent.
        alpha (float): Parameter controlling the shape of Φα.

    Returns:
        float: Value of Φα(f).
    """
    return 1 - math.exp(alpha * (f - 1))


def generate_predicted_query_sequence(actual_query_sequence, n_keywords, prediction_error_level):
        """
        Generate a predicted query sequence with a specified level of change.

        Args:
            actual_query_sequence (list): The actual sequence of queries (list of keywords).
            prediction_error_level (float): Level of change between 0 and 1. 0 means no change, 1 means full transformation.

        Returns:
            list: A modified query sequence.
        """

        # If change level is 0, return the original sequence
        if prediction_error_level == 0:
            return {f"k{i+1}": actual_query_sequence.count(f"k{i+1}") for i in range(n_keywords)}

        # Count the occurrences of each keyword
        keyword_counts = {keyword: actual_query_sequence.count(keyword) for keyword in set(actual_query_sequence)}

        # Determine the number of changes based on prediction_error_level
        num_changes = int(prediction_error_level * len(actual_query_sequence))

        # Make changes to the sequence
        for _ in range(num_changes):
            # Randomly select two distinct keywords
            if len(keyword_counts) < 2:
                break  # Not enough keywords to swap

            keyword1, keyword2 = random.sample(list(keyword_counts.keys()), 2)

            # Calculate the transfer amount (at least 1 query, if possible)
            transfer_amount = min(1, keyword_counts[keyword1])

            if transfer_amount > 0:
                # Reduce from keyword1 and add to keyword2
                keyword_counts[keyword1] -= transfer_amount
                keyword_counts[keyword2] += transfer_amount

                # Remove keyword1 if count drops to 0
                if keyword_counts[keyword1] == 0:
                    del keyword_counts[keyword1]

        # Reconstruct the predicted sequence based on modified counts
        predicted_sequence = []
        for keyword, count in keyword_counts.items():
            predicted_sequence.extend([keyword] * count)

        predicted_queries = {f"k{i+1}": predicted_sequence.count(f"k{i+1}") for i in range(n_keywords)}

        return predicted_queries