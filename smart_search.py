from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def find_best_answer_ai(query, text_corpus):
    """Sử dụng toán học vector để tìm đoạn văn bản có ý nghĩa khớp nhất với câu hỏi"""
    if not text_corpus.strip():
        return None
    
    # Chia văn bản thành các câu nhỏ (loại bỏ câu quá ngắn)
    sentences = [s.strip() for s in re.split(r'[.!?\n]+', text_corpus) if len(s.strip()) > 15]
    if not sentences:
        return None
        
    try:
        # Chuyển đổi câu hỏi và tập văn bản thành ma trận toán học
        documents = sentences + [query]
        vectorizer = TfidfVectorizer().fit_transform(documents)
        vectors = vectorizer.toarray()
        
        # Tính độ tương đồng giữa câu hỏi (vector cuối) và các câu trong web
        query_vector = vectors[-1]
        doc_vectors = vectors[:-1]
        
        similarities = cosine_similarity([query_vector], doc_vectors)[0]
        
        # Lấy top 3 câu có độ tương đồng cao nhất
        best_indices = similarities.argsort()[::-1][:3]
        
        results = []
        for idx in best_indices:
            if similarities[idx] > 0.08: # Ngưỡng lọc độ chính xác
                results.append(sentences[idx])
                
        if results:
            return ". ".join(results) + "."
    except Exception:
        pass
        
    return None
                               
