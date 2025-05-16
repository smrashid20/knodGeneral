from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from rouge_score import rouge_scorer

def cosine_similarity_between_texts(text1: str, text2: str, model_name: str = "all-MiniLM-L6-v2") -> float:
    model = SentenceTransformer(model_name)

    embedding1 = model.encode(
        text1, convert_to_numpy=True, clean_up_tokenization_spaces=True
    )
    embedding2 = model.encode(
        text2, convert_to_numpy=True, clean_up_tokenization_spaces=True
    )

    similarity = cosine_similarity(embedding1.reshape(1, -1), embedding2.reshape(1, -1))[0][0]
    return similarity


def rouge_l_score_between_texts(text1: str, text2: str) -> float:
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer.score(text1, text2)
    rouge_l_f1 = scores['rougeL'].fmeasure
    return rouge_l_f1




