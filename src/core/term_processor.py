# src/core/term_processor.py
from typing import Dict, List, Any, Set
import re
import logging
from datetime import datetime
import openai

class TermExplanationError(Exception):
    """Raised when term explanation generation fails."""
    pass

class TechnicalTermProcessor:
    """Handles technical term identification and explanation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.term_cache = {}  # Cache for term definitions
        self.logger = logging.getLogger(__name__)
        
    async def process_terms(self, text: str) -> Dict[str, Any]:
        """Process technical terms in text."""
        try:
            # Identify technical terms
            terms = self.identify_terms(text)
            
            # Get explanations for new terms
            term_explanations = await self.get_term_explanations(terms)
            
            return {
                'terms': term_explanations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Term processing error: {str(e)}")
            raise
    async def get_term_explanations(
        self,
        terms: Set[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Get explanations for technical terms."""
        explanations = {}
        
        for term in terms:
            # Check cache first
            if term in self.term_cache:
                explanations[term] = self.term_cache[term]
                continue
                
            # Generate new explanation
            try:
                explanation = await self.generate_term_explanation(term)
                self.term_cache[term] = explanation
                explanations[term] = explanation
                
            except Exception as e:
                self.logger.error(f"Error explaining term '{term}': {str(e)}")
                continue
                
        return explanations
    
    async def generate_term_explanation(
        self,
        term: str
    ) -> Dict[str, Any]:
        """Generate explanation for a technical term."""
        prompt = f"""
        Provide a clear, concise explanation of the technical term "{term}".
        Focus on its meaning and significance in technical or business contexts.
        Keep the explanation brief (2-3 sentences) but informative.
        """        

        try:
            response = await openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a technical expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            return {
                'term': term,
                'explanation': response.choices[0].message.content.strip(),
                'created_at': datetime.now().isoformat(),
                'source': 'gpt-4'
            }
            
        except Exception as e:
            raise TermExplanationError(f"Failed to explain term: {str(e)}")
        
class TermIntegrator:
    """Integrates term explanations into summaries."""
    
    def __init__(self):
        self.explained_terms = set()  # Track already explained terms
        
    def integrate_terms(
        self,
        summary: str,
        term_explanations: Dict[str, Dict[str, Any]]
    ) -> str:
        """Integrate term explanations into summary."""
        modified_summary = summary

        for term, explanation in term_explanations.items():
            if term not in self.explained_terms:
                # Add explanation on first occurrence
                pattern = re.compile(f"\\b{re.escape(term)}\\b", re.IGNORECASE)
                replacement = f"{term} ({explanation['explanation']})"
                
                # Replace only first occurrence
                modified_summary = pattern.sub(replacement, modified_summary, count=1)
                self.explained_terms.add(term)
                
        return modified_summary

class TermCache:
    """Manages technical term caching."""
    
    def __init__(self, max_cache_size: int = 1000):
        self.cache = {}
        self.max_size = max_cache_size
        
    def add_term(
        self,
        term: str,
        explanation: Dict[str, Any]
    ):
        """Add term to cache with management."""
        if len(self.cache) >= self.max_size:
            # Remove oldest terms if cache is full
            oldest_terms = sorted(
                self.cache.items(),
                key=lambda x: x[1]['created_at']
            )[:100]  # Remove oldest 100 terms
            
            for old_term, _ in oldest_terms:
                del self.cache[old_term]
                
        self.cache[term] = explanation
        
    def get_term(self, term: str) -> Optional[Dict[str, Any]]:
        """Get term explanation from cache."""
        return self.cache.get(term)    