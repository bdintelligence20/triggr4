import logging
from typing import Dict, Any, List, Optional
from langchain.evaluation import load_evaluator
from langchain_rag import LangChainRAG

logger = logging.getLogger(__name__)

class RAGEvaluator:
    """Evaluator for RAG system performance."""
    
    def __init__(
        self, 
        openai_api_key: str, 
        anthropic_api_key: str, 
        pinecone_api_key: str, 
        index_name: str,
        organization_id: Optional[str] = None
    ):
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key
        self.pinecone_api_key = pinecone_api_key
        self.index_name = index_name
        self.organization_id = organization_id
        
        # Initialize RAG system
        self.rag_system = LangChainRAG(
            openai_api_key=self.openai_api_key,
            anthropic_api_key=self.anthropic_api_key,
            pinecone_api_key=self.pinecone_api_key,
            index_name=self.index_name,
            organization_id=self.organization_id
        )
        
        # Initialize evaluator
        self.evaluator = load_evaluator("qa")
        
        logger.info(f"Initialized RAGEvaluator for organization: {organization_id or 'global'}")
    
    def evaluate_query(self, query: str, expected_answer: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Evaluate a query against an expected answer."""
        try:
            # Query the RAG system
            result = self.rag_system.query(
                query_text=query,
                category=category
            )
            
            # Get the generated answer
            generated_answer = result["answer"]
            
            # Evaluate the answer
            eval_result = self.evaluator.evaluate_strings(
                prediction=generated_answer,
                reference=expected_answer,
                input=query
            )
            
            # Format the result
            evaluation = {
                "query": query,
                "generated_answer": generated_answer,
                "expected_answer": expected_answer,
                "evaluation": eval_result,
                "sources": result["sources"]
            }
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error in evaluate_query: {str(e)}")
            return {
                "query": query,
                "error": str(e),
                "status": "error"
            }
    
    def evaluate_batch(self, test_cases: List[Dict[str, str]]) -> Dict[str, Any]:
        """Evaluate a batch of test cases."""
        results = []
        success_count = 0
        total_count = len(test_cases)
        
        for test_case in test_cases:
            query = test_case.get("query")
            expected_answer = test_case.get("expected_answer")
            category = test_case.get("category")
            
            if not query or not expected_answer:
                continue
                
            result = self.evaluate_query(query, expected_answer, category)
            results.append(result)
            
            # Check if evaluation was successful
            if "error" not in result:
                success_count += 1
        
        # Calculate success rate
        success_rate = success_count / total_count if total_count > 0 else 0
        
        return {
            "results": results,
            "success_count": success_count,
            "total_count": total_count,
            "success_rate": success_rate
        }
