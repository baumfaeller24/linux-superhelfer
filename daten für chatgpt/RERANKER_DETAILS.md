# Reranker Details

## Status: NICHT IMPLEMENTIERT

Das System hat aktuell **keinen Reranker** implementiert.

### Aktuelle Ranking-Methode
- **Methode**: Einfache Cosine Similarity
- **Score-Berechnung**: `np.dot(candidate_norms, query_norm)`
- **Sortierung**: Absteigende Reihenfolge nach Similarity Score
- **Cutoff**: Threshold-basiert (default 0.6)

### Pseudo-Reranking in `search_with_context()`
```python
# Re-score results based on original query
for result in results:
    content_embedding = await self.embedding_manager.generate_embedding(result["content"])
    similarity_results = await self.embedding_manager.similarity_search_embedding(
        query_embedding, [content_embedding], threshold=0.0
    )
    if similarity_results:
        result["score"] = similarity_results[0]["score"]
```

### Fehlende Reranker-Features
- ❌ Cross-encoder Modell
- ❌ BERT-basiertes Reranking  
- ❌ Learning-to-Rank
- ❌ Query-Document Interaction Scoring
- ❌ Multi-stage Ranking Pipeline

### Empfohlene Reranker-Integration
```python
# Beispiel für zukünftige Implementation
class Reranker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = SentenceTransformer(model_name)
        self.score_cutoff = 0.3
    
    def rerank(self, query: str, candidates: List[str]) -> List[Dict]:
        scores = self.model.predict([(query, candidate) for candidate in candidates])
        return [{"text": cand, "score": score} 
                for cand, score in zip(candidates, scores) 
                if score >= self.score_cutoff]
```

## Aktueller Workaround
Das System nutzt **doppelte Embedding-Berechnung** in `search_with_context()` als primitiven Reranker-Ersatz.