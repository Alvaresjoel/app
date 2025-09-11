"""
Tool Router - Pre-routing mechanism to help with tool selection
"""
import re
from typing import Dict, List, Tuple
from enum import Enum

class QueryType(Enum):
    SEMANTIC = "semantic"
    METADATA = "metadata"
    AMBIGUOUS = "ambiguous"

class ToolRouter:
    """
    Pre-routing mechanism to determine the most appropriate tool for a query
    """
    
    def __init__(self):
        # Keywords that indicate semantic search is needed
        self.semantic_keywords = [
            r'\bproject\s+\w+',  # "project X"
            r'\btask\s+\w+',     # "task Y"
            r'\bfind\s+tasks?\s+related\s+to',
            r'\bget\s+details?\s+about',
            r'\bwhat\s+comments?\s+did\s+i\s+add',
            r'\bshow\s+me\s+all\s+tasks?\s+for\s+\w+',  # "show me all tasks for Project A"
            r'\btasks?\s+associated\s+with',
            r'\btasks?\s+for\s+\w+',  # "tasks for Project B"
            r'\bshow\s+me\s+all\s+tasks?\s+for\s+project\s+\w+',  # "show me all tasks for Project A"
        ]
        
        # Keywords that indicate metadata query is needed
        self.metadata_keywords = [
            r'\b(august|september|october|november|december|january|february|march|april|may|june|july)\b',
            r'\b(last\s+week|last\s+month|last\s+year|last\s+\d+\s+months?|last\s+\d+\s+days?|last\s+\d+\s+weeks?)',
            r'\b(completed|in\s+progress|pending|done|finished)',
            r'\b(total\s+time|time\s+spent|duration|how\s+much\s+time)',
            r'\b(longest|shortest|most\s+time|least\s+time)',
            r'\bfrom\s+\d{4}-\d{2}-\d{2}\s+to\s+\d{4}-\d{2}-\d{2}',
            r'\b(give\s+me\s+tasks?|show\s+me\s+tasks?|list\s+tasks?)\s+(in|from|during)',
            r'\bsummarize\s+(my\s+)?(completed\s+)?tasks?',
            r'\btasks?\s+(completed|done|finished)\s+(in|during|from)',
        ]
        
        # Compile regex patterns for better performance
        self.semantic_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.semantic_keywords]
        self.metadata_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.metadata_keywords]
    
    def analyze_query(self, query: str) -> Tuple[QueryType, float, str]:
        """
        Analyze a query and determine the most appropriate tool
        
        Returns:
            Tuple of (query_type, confidence, reasoning)
        """
        query_lower = query.lower()
        
        # Check for semantic search indicators
        semantic_matches = 0
        for pattern in self.semantic_patterns:
            if pattern.search(query_lower):
                semantic_matches += 1
        
        # Check for metadata query indicators
        metadata_matches = 0
        for pattern in self.metadata_patterns:
            if pattern.search(query_lower):
                metadata_matches += 1
        
        # Determine query type based on matches
        if semantic_matches > 0 and metadata_matches == 0:
            confidence = min(0.9, 0.5 + (semantic_matches * 0.2))
            return QueryType.SEMANTIC, confidence, f"Found {semantic_matches} semantic indicators"
        
        elif metadata_matches > 0:
            confidence = min(0.9, 0.5 + (metadata_matches * 0.2))
            return QueryType.METADATA, confidence, f"Found {metadata_matches} metadata indicators"
        
        elif semantic_matches > 0 and metadata_matches > 0:
            # Ambiguous case - prioritize semantic if specific project/task mentioned
            # Check for specific project/task patterns first
            project_task_patterns = [
                r'\bproject\s+\w+',
                r'\btask\s+\w+',
                r'\bshow\s+me\s+all\s+tasks?\s+for\s+\w+',
                r'\btasks?\s+for\s+\w+'
            ]
            
            if any(re.search(pattern, query_lower) for pattern in project_task_patterns):
                return QueryType.SEMANTIC, 0.7, "Ambiguous but specific project/task mentioned"
            elif any(pattern.search(query_lower) for pattern in self.metadata_patterns[:3]):  # Date patterns
                return QueryType.METADATA, 0.6, "Ambiguous but date indicators present"
            else:
                return QueryType.AMBIGUOUS, 0.4, "Both semantic and metadata indicators found"
        
        else:
            # No clear indicators - default to metadata for general queries
            return QueryType.METADATA, 0.3, "No clear indicators, defaulting to metadata"
    
    def get_tool_recommendation(self, query: str) -> Dict:
        """
        Get a tool recommendation with reasoning
        """
        query_type, confidence, reasoning = self.analyze_query(query)
        
        if query_type == QueryType.SEMANTIC:
            recommended_tool = "SemanticRetriever"
        elif query_type == QueryType.METADATA:
            recommended_tool = "MetadataQuery"
        else:
            recommended_tool = "MetadataQuery"  # Default fallback
        
        return {
            "recommended_tool": recommended_tool,
            "confidence": confidence,
            "reasoning": reasoning,
            "query_type": query_type.value
        }

# Example usage and testing
if __name__ == "__main__":
    router = ToolRouter()
    
    test_queries = [
        "Give me tasks in August and September",
        "Find tasks related to Project X",
        "Show completed tasks last week",
        "What is the total time spent on tasks in September?",
        "Get details about Task Y",
        "What is the longest task I worked on in the past year?",
        "Show me all tasks for Project A last week",
        "Summarize my completed tasks for the past week"
    ]
    
    print("Tool Router Test Results:")
    print("=" * 50)
    
    for query in test_queries:
        result = router.get_tool_recommendation(query)
        print(f"Query: {query}")
        print(f"Recommended: {result['recommended_tool']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Reasoning: {result['reasoning']}")
        print("-" * 30)
