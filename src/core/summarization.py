# src/core/summarization.py
from typing import List, Dict, Any, Optional
import openai
import logging
from datetime import datetime

class SummarizationPipeline:
    """Handles the summarization process."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.prompt_template = self.load_prompt_template()
        self.logger = logging.getLogger(__name__)
        
    async def summarize_chunk(
        self,
        chunk: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Summarize a single chunk with context awareness."""
        try:
            # Create prompt
            prompt = self.create_prompt(chunk, context)
            
            # Generate summary
            summary = await self.generate_summary(prompt)
            
            return {
                'summary': summary,
                'chunk_id': id(chunk),
                'timestamp': datetime.now().isoformat(),
                'context_used': bool(context)
            }
            
        except Exception as e:
            self.logger.error(f"Summarization error: {str(e)}")
            raise

    def create_prompt(
        self,
        chunk: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Create summarization prompt."""
        base_prompt = """
        Summarize the following text in a concise, structured way, keeping the tone 
        conversational yet analytical, as if summarizing key insights from a podcast. 
        Focus on preserving the speaker's perspective, key arguments, and specific 
        examples, while avoiding unnecessary details. Use paragraph breaks to group 
        ideas logically and emphasize the progression of thought.
        """
    async def generate_summary(self, prompt: str) -> str:
            """Generate summary using GPT-4."""
            try:
                response = await openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.config['system_prompt']},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Lower temperature for consistency
                    max_tokens=1000
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                self.logger.error(f"Summary generation error: {str(e)}")
                raise

def load_prompt_template(self) -> str:
        """Load the prompt template from config."""
        return self.config.get('prompt_template', """
            Summarize the following text, keeping the following in mind:
            - Maintain a conversational yet analytical tone
            - Preserve speaker perspectives and key arguments
            - Include specific examples when relevant
            - Group ideas logically with paragraph breaks
            
            If technical terms are present, provide brief explanations 
            on first mention.
        """)

class SummaryAggregator:
    """Aggregates individual summaries into a coherent whole."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def aggregate_summaries(
        self,
        summaries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Combine individual summaries into final output."""
        # Sort summaries by chunk_id to maintain order
        sorted_summaries = sorted(summaries, key=lambda x: x['chunk_id'])
        
        # Combine summaries with proper formatting
        combined_text = []
        for summary in sorted_summaries:
            combined_text.append(summary['summary'])
            
        return {
            'full_summary': '\n\n'.join(combined_text),
            'chunk_count': len(summaries),
            'timestamp': datetime.now().isoformat()
        }