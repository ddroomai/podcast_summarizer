# src/core/semantic.py
from typing import List, Dict, Any
import numpy as np
import openai
from collections import defaultdict
import logging

class SemanticProcessor:
    """Handles semantic processing and embeddings."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.embedding_cache = {}
        self.similarity_threshold = config.get('similarity_threshold', 0.85)
        
    async def enhance_chunks(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enhance chunks with semantic information."""
        try:
            # Generate embeddings for all chunks
            for chunk in chunks:
                chunk['embedding'] = await self.get_embedding(chunk['text'])
            
            # Analyze chunk relationships
            enhanced_chunks = self.analyze_relationships(chunks)
            
            return enhanced_chunks
            
        except Exception as e:
            logging.error(f"Error in semantic processing: {str(e)}")
            raise

    async def get_embedding(self, text: str) -> List[float]:
        """Get or compute embedding for text."""
        # Check cache first
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        try:
            response = await openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            
            embedding = response['data'][0]['embedding']
            self.embedding_cache[text] = embedding
            return embedding
            
        except Exception as e:
            logging.error(f"Error generating embedding: {str(e)}")
            raise

class ContextManager:
    """Manages context between chunks."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.context_window = []
        self.max_context_chunks = config.get('context_window_size', 3)
        
    def update_context(
        self,
        chunk: Dict[str, Any],
        summary: str
    ):
        """Update context with new chunk and its summary."""
        context_entry = {
            'chunk_text': chunk['text'],
            'summary': summary,
            'embedding': chunk['embedding'],
            'speakers': chunk['speakers']
        }
        
        self.context_window.append(context_entry)
        
        # Maintain window size
        if len(self.context_window) > self.max_context_chunks:
            self.context_window.pop(0)
    
    def get_relevant_context(
        self,
        current_chunk: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get relevant context for current chunk."""
        if not self.context_window:
            return None
        
        # Calculate similarities with context window
        similarities = []
        for entry in self.context_window:
            similarity = self.calculate_similarity(
                current_chunk['embedding'],
                entry['embedding']
            )
            similarities.append((similarity, entry))
        
        # Sort by similarity
        similarities.sort(reverse=True, key=lambda x: x[0])
        
        # Return most relevant context
        relevant_entries = [
            entry for sim, entry in similarities
            if sim > self.config.get('similarity_threshold', 0.85)
        ]
        
        if not relevant_entries:
            return None
            
        return {
            'summaries': [entry['summary'] for entry in relevant_entries],
            'speakers': list(set(
                speaker
                for entry in relevant_entries
                for speaker in entry['speakers']
            ))
        }
    
    @staticmethod
    def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings."""
        return np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )

class ChunkOptimizer:
    """Optimizes chunk boundaries based on semantic similarity."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def optimize_chunks(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Optimize chunk boundaries based on semantic similarity."""
        optimized_chunks = []
        current_chunk = chunks[0]
        
        for next_chunk in chunks[1:]:
            # Calculate similarity
            similarity = ContextManager.calculate_similarity(
                current_chunk['embedding'],
                next_chunk['embedding']
            )
            
            # If highly similar and combined size is acceptable,
            # merge chunks
            combined_size = current_chunk['size'] + next_chunk['size']
            if (similarity > self.config['similarity_threshold'] and
                combined_size <= self.config['max_chunk_size']):
                current_chunk = self.merge_chunks(
                    current_chunk,
                    next_chunk
                )
            else:
                optimized_chunks.append(current_chunk)
                current_chunk = next_chunk
        
        # Add final chunk
        optimized_chunks.append(current_chunk)
        
        return optimized_chunks
    
    def merge_chunks(
        self,
        chunk1: Dict[str, Any],
        chunk2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two chunks."""
        return {
            'text': f"{chunk1['text']}\n\n{chunk2['text']}",
            'size': chunk1['size'] + chunk2['size'],
            'speakers': list(set(chunk1['speakers'] + chunk2['speakers'])),
            'embedding': np.mean(
                [chunk1['embedding'], chunk2['embedding']],
                axis=0
            ).tolist()
        }