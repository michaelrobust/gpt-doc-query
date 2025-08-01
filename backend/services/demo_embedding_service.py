import numpy as np
from typing import List
import hashlib
import time

class DemoEmbeddingService:
    """
    Demo Embedding Service - No real API key needed
    Uses deterministic fake vectors to simulate real semantic search
    """
    
    def __init__(self):
        self.embedding_dim = 384  # Standard dimension
        print("🎭 Demo Embedding Service initialized - perfect for GitHub showcase!")
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate deterministic fake embeddings
        Similar texts will produce similar vectors
        """
        print(f"🔄 Generating demo embeddings for {len(texts)} texts...")
        
        embeddings = []
        for text in texts:
            # Use text content to generate deterministic vector
            embedding = self._text_to_vector(text)
            embeddings.append(embedding)
        
        # Simulate API delay
        time.sleep(0.1)
        
        embeddings_array = np.array(embeddings, dtype=np.float32)
        print(f"✅ Generated demo embeddings shape: {embeddings_array.shape}")
        return embeddings_array
    
    def _text_to_vector(self, text: str) -> np.ndarray:
        """
        Convert text to deterministic vector
        Similar semantic texts will produce similar vectors
        """
        # Basic text features
        text_lower = text.lower()
        text_hash = hashlib.md5(text_lower.encode()).hexdigest()
        
        # Generate base vector
        np.random.seed(int(text_hash[:8], 16) % (2**31))
        base_vector = np.random.normal(0, 1, self.embedding_dim)
        
        # Adjust vector based on text features
        # Similar words will have similar adjustments
        semantic_features = self._extract_semantic_features(text_lower)
        
        for feature, weight in semantic_features.items():
            feature_hash = hashlib.md5(feature.encode()).hexdigest()
            np.random.seed(int(feature_hash[:8], 16) % (2**31))
            feature_vector = np.random.normal(0, 1, self.embedding_dim)
            base_vector += feature_vector * weight * 0.1
        
        # Normalize vector
        base_vector = base_vector / np.linalg.norm(base_vector)
        
        return base_vector
    
    def _extract_semantic_features(self, text: str) -> dict:
        """Extract semantic features to make similar texts have similar vectors"""
        features = {}
        
        # Topic keywords
        topics = {
            'technology': ['tech', 'computer', 'software', 'ai', 'data', 'algorithm'],
            'business': ['company', 'market', 'profit', 'sales', 'customer'],
            'science': ['research', 'study', 'analysis', 'experiment', 'theory'],
            'education': ['learn', 'student', 'teach', 'knowledge', 'course']
        }
        
        for topic, keywords in topics.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                features[f'topic_{topic}'] = score
        
        # Text length features
        features['length_short'] = 1 if len(text) < 50 else 0
        features['length_medium'] = 1 if 50 <= len(text) < 200 else 0
        features['length_long'] = 1 if len(text) >= 200 else 0
        
        # Question features
        features['is_question'] = 1 if '?' in text else 0
        
        return features
