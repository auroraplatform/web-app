import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import pickle
import os

class EmbeddingManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.embeddings_cache = {}
        self.text_to_embedding = {}
        self.cache_file = "embeddings_cache.pkl"
        self._load_cache()
    
    def _load_cache(self):
        """Load embeddings cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.embeddings_cache = cache_data.get('embeddings', {})
                    self.text_to_embedding = cache_data.get('text_mapping', {})
            except Exception as e:
                print(f"Error loading cache: {e}")
    
    def _save_cache(self):
        """Save embeddings cache to file"""
        try:
            cache_data = {
                'embeddings': self.embeddings_cache,
                'text_mapping': self.text_to_embedding
            }
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if text in self.text_to_embedding:
            return self.embeddings_cache[self.text_to_embedding[text]]
        
        embedding = self.model.encode(text)
        
        # Store in cache
        embedding_id = f"emb_{len(self.embeddings_cache)}"
        self.embeddings_cache[embedding_id] = embedding
        self.text_to_embedding[text] = embedding_id
        
        return embedding
    
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts"""
        new_texts = [t for t in texts if t not in self.text_to_embedding]
        
        if new_texts:
            new_embeddings = self.model.encode(new_texts)
            
            for text, embedding in zip(new_texts, new_embeddings):
                embedding_id = f"emb_{len(self.embeddings_cache)}"
                self.embeddings_cache[embedding_id] = embedding
                self.text_to_embedding[text] = embedding_id
        
        return [self.embeddings_cache[self.text_to_embedding[text]] for text in texts]
    
    def find_similar(self, query_text: str, candidate_texts: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """Find most similar texts to query"""
        query_embedding = self.embed_text(query_text)
        candidate_embeddings = self.embed_batch(candidate_texts)
        
        similarities = []
        for text, embedding in zip(candidate_texts, candidate_embeddings):
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            similarities.append((text, float(similarity)))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

embedding_manager = EmbeddingManager()
