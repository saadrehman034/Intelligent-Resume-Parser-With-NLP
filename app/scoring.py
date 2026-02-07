import re
def extract_years_of_experience(text: str) -> float:
    # Regex for patterns like "5+ years", "3 years of experience"
    pattern = r"(\d+)\+?\s*(?:years|yrs)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    if matches:
        # Take the maximum number found (often indicative of total exp)
        return float(max(map(int, matches)))
    return 0.0

def calculate_scores(skill_match_rate, candidate_exp, required_exp=2.0):
    # 1. Skill Score (40%)
    skill_score = skill_match_rate * 100
    
    # 2. Experience Score (30%)
    # Cap at 100% if they meet requirements
    if required_exp > 0:
        exp_ratio = min(candidate_exp / required_exp, 1.5) # Allow bonus for extra exp
        exp_score = min(exp_ratio * 100, 100)
    else:
        exp_score = 100
        
    # 3. Overall Weighted Score
    # Weights: Skill 0.6, Exp 0.4 (Simplification for demo)
    overall_score = (skill_score * 0.6) + (exp_score * 0.4)
    
    return {
        "skill_score": round(skill_score, 2),
        "experience_score": round(exp_score, 2),
        "overall_score": round(overall_score, 2)
    }