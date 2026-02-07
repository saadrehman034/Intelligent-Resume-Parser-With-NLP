def generate_explanation(candidate_name, matched_skills, missing_skills, 
                         cand_exp, req_exp):
    
    text = f"Candidate analysis for {candidate_name or 'the applicant'}:\n"
    
    # Skills
    if len(matched_skills) > 0:
        top_matches = ", ".join(matched_skills[:5])
        text += f"✅ Strong match on key skills: {top_matches}. "
    
    if len(missing_skills) > 0:
        top_missing = ", ".join(missing_skills[:3])
        text += f"⚠️ Missing or unmatched skills: {top_missing}. "
        
    # Experience
    if cand_exp >= req_exp:
        text += f"✅ Experience requirement met ({cand_exp} years vs {req_exp} required)."
    else:
        text += f"❌ Experience gap detected ({cand_exp} years found, {req_exp} required)."
        
    return text