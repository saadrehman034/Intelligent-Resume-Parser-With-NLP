# app/scoring.py
import re

def extract_years_of_experience(text: str) -> float:
    # Use the same logic as NER model
    text_lower = text.lower()
    
    patterns = [
        r'(\d+)\+?\s*years?',
        r'(\d+)\s*yr', 
        r'experience.*?(\d+)',
        r'(\d+).*?experience',
        r'(\d+)\+'
    ]
    
    max_years = 0
    for pattern in patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            try:
                years = int(match)
                if years > max_years:
                    max_years = years
            except:
                pass
    
    # If no explicit years, calculate from dates
    if max_years == 0:
        date_pattern = r'(\d{4})\s*[-–]\s*(?:Present|\d{4})'
        dates = re.findall(date_pattern, text)
        if dates:
            try:
                earliest = min([int(date) for date in dates])
                max_years = 2026 - earliest
            except:
                max_years = 0
    
    return float(max_years) if max_years > 0 else 0.0

def calculate_scores(skill_match_rate, candidate_exp, required_exp=2.0):
    # Skill Score (0-100)
    skill_score = skill_match_rate * 100
    
    # Experience Score (0-100)
    if required_exp > 0:
        if candidate_exp >= required_exp:
            exp_score = 100
        else:
            exp_score = (candidate_exp / required_exp) * 100
    else:
        exp_score = 100
    
    # Overall Score (weighted)
    overall_score = (skill_score * 0.6) + (exp_score * 0.4)
    
    return {
        "skill_score": round(skill_score, 1),
        "experience_score": round(exp_score, 1),
        "overall_score": round(overall_score, 1)
    }