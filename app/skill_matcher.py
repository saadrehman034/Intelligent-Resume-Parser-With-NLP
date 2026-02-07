from sentence_transformers import SentenceTransformer, util
import torch

# Load lightweight embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_match(resume_skills: list, jd_skills: list, threshold=0.5):
    if not resume_skills or not jd_skills:
        return 0.0, [], list(jd_skills)

    # Encode
    resume_embeddings = embedder.encode(list(resume_skills), convert_to_tensor=True)
    jd_embeddings = embedder.encode(jd_skills, convert_to_tensor=True)

    # Compute Cosine Similarity Matrix
    cosine_scores = util.cos_sim(resume_embeddings, jd_embeddings)
    
    matched_skills = set()
    missing_skills = set(jd_skills)
    
    # Analyze matches
    # Rows = Resume Skills, Cols = JD Skills
    for i, jd_skill in enumerate(jd_skills):
        # Find best match in resume for this JD skill
        best_score = torch.max(cosine_scores[:, i]).item()
        
        if best_score >= threshold:
            matched_skills.add(jd_skill)
            if jd_skill in missing_skills:
                missing_skills.remove(jd_skill)
                
    match_percentage = len(matched_skills) / len(jd_skills)
    
    return match_percentage, list(matched_skills), list(missing_skills)