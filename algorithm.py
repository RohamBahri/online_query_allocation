from abc import ABC, abstractmethod

class Algorithm(ABC):
    """
    Abstract base class for query allocation algorithms.
    """

    @abstractmethod
    def allocate_query(self, query):
        """
        Allocate a single query to an advertiser.
        
        Args:
            query (str): The query keyword to allocate.

        Returns:
            str or None: The advertiser assigned to the query, or None if no allocation is possible.
        """
        pass
