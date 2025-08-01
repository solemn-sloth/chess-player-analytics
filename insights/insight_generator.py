from abc import ABC, abstractmethod

class InsightGenerator(ABC):
    """Abstract base class for generating insights from metrics"""
    
    @abstractmethod
    def generate_priorities(self, metrics):
        """Generate top 3 priorities for improvement
        
        Returns:
            list: List of priority dicts with 'title', 'stat', 'action' keys
        """
        pass
    
    @abstractmethod
    def generate_strengths(self, metrics):
        """Identify player strengths
        
        Returns:
            list: List of strength descriptions
        """
        pass
    
    @abstractmethod
    def generate_recommendations(self, metrics):
        """Generate personalized recommendations
        
        Returns:
            list: List of recommendation strings
        """
        pass
    
    @abstractmethod
    def generate_patterns(self, metrics):
        """Identify patterns in play
        
        Returns:
            dict: Various pattern analyses
        """
        pass
    
    @abstractmethod
    def generate_projections(self, metrics):
        """Project future performance
        
        Returns:
            dict: Projected outcomes and improvements
        """
        pass