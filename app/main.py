from fastapi import FastAPI, UploadFile, File, Form
from app.resume_parser import extract_text_from_pdf
from app.ner_model import extract_entities
from app.skill_matcher import semantic_match
from app.scoring import extract_years_of_experience, calculate_scores
from app.explainer import generate_explanation
import shutil
import os

app = FastAPI(title="Intelligent Resume Matcher")

@app.post("/match")
async def match_resume(
    file: UploadFile = File(...),
    jd_text: str = Form(...),
    required_exp: int = Form(2)
):
    # 1. Save and Parse Resume
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb+") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    resume_text = extract_text_from_pdf(file_location)
    os.remove(file_location) # Cleanup
    
    # 2. Extract Entities (Resume)
    resume_data = extract_entities(resume_text)
    candidate_exp = extract_years_of_experience(resume_text)
    
    # 3. Extract Entities (JD) - Reusing NER for JD parsing
    jd_data = extract_entities(jd_text)
    jd_skills = list(jd_data["skills"])
    
    # 4. Semantic Matching
    match_rate, matched, missing = semantic_match(resume_data["skills"], jd_skills)
    
    # 5. Scoring
    scores = calculate_scores(match_rate, candidate_exp, required_exp)
    
    # 6. Explainability
    explanation = generate_explanation(
        "Candidate", matched, missing, candidate_exp, required_exp
    )
    
    return {
        "candidate_profile": {
            "extracted_skills": list(resume_data["skills"]),
            "extracted_experience": candidate_exp
        },
        "scores": scores,
        "match_details": {
            "matched_skills": matched,
            "missing_skills": missing
        },
        "explanation": explanation
    }