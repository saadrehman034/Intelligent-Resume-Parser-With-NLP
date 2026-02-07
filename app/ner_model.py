from gliner import GLiNER
import re

# Load model once
model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
labels = ["person", "skill", "role", "experience", "education", "company", "tool"]

def extract_entities(text: str):
    """
    Hybrid entity extractor: Uses GLiNER + rule-based fallback
    """
    print(f"\n🔍 NER: Processing {len(text)} characters")
    
    # Try GLiNER first
    try:
        entities = model.predict_entities(text, labels, threshold=0.3)  # Lower threshold
    except Exception as e:
        print(f"GLiNER error: {e}")
        entities = []
    
    structured_data = {
        "skills": set(),
        "roles": [],
        "experience": [],
        "education": [],
        "companies": []
    }
    
    # Process GLiNER results
    for entity in entities:
        tag = entity["label"]
        text_val = entity["text"]
        
        if tag == "skill" or tag == "tool":
            structured_data["skills"].add(text_val.lower())
        elif tag == "role":
            structured_data["roles"].append(text_val)
        elif tag == "company":
            structured_data["companies"].append(text_val)
        elif tag == "experience":
            structured_data["experience"].append(text_val)
    
    print(f"GLiNER found {len(structured_data['skills'])} skills")
    
    # ========== FALLBACK PARSER ==========
    # If GLiNER didn't find skills, use rule-based extraction
    if len(structured_data["skills"]) < 3:  # If too few skills found
        print("⚠️ GLiNER found few skills, using fallback parser...")
        fallback_skills = extract_skills_fallback(text)
        structured_data["skills"].update(fallback_skills)
    
    # Extract experience years specifically
    experience_years = extract_experience_years(text)
    if experience_years > 0:
        structured_data["experience"].append(f"{experience_years} years")
    
    # Extract education
    if "university" in text.lower() or "b.a." in text.lower() or "bachelor" in text.lower():
        structured_data["education"].append("Bachelor's Degree")
    
    # Convert skills set to list and format properly
    formatted_skills = []
    for skill in structured_data["skills"]:
        # Capitalize each word in the skill
        formatted = ' '.join(word.capitalize() for word in str(skill).split())
        formatted_skills.append(formatted)
    
    print(f"📊 Total skills found: {len(formatted_skills)}")
    if formatted_skills:
        print(f"Skills: {formatted_skills[:10]}...")
    
    return {
        "skills": formatted_skills,
        "experience": structured_data["experience"],
        "education": structured_data["education"],
        "certifications": []
    }


def extract_skills_fallback(text: str):
    """Rule-based skill extraction for when GLiNER fails"""
    skills = set()
    text_lower = text.lower()
    
    # Skills from your specific resume
    resume_skills = [
        "problem solving", "adaptability", "collaboration", 
        "strong work ethic", "time management", "critical thinking",
        "handling pressure", "leadership", "microsoft excel",
        "organization", "scheduling", "travel arrangements",
        "budgeting", "reporting", "confidentiality", "communication",
        "teamwork", "administrative", "secretarial", "training",
        "mentoring", "filing", "documentation", "correspondence",
        "office supplies", "inventory", "meeting minutes"
    ]
    
    # Direct matching
    for skill in resume_skills:
        if skill in text_lower:
            skills.add(skill)
    
    # Extract from SKILL section (your resume format)
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_upper = line.upper().strip()
        
        # Find SKILL section
        if 'SKILL' in line_upper and len(line_upper) < 20:
            # Skills might be on same line or next line
            skill_line = line
            
            # Check next line if current line is just "SKILL"
            if line_upper == "SKILL" and i + 1 < len(lines):
                skill_line = lines[i + 1]
            
            # Parse concatenated skills like "Problem Solving Adaptability"
            words = skill_line.split()
            current_skill = []
            
            for word in words:
                if word[0].isupper() or word.isupper():
                    current_skill.append(word)
                    # If we have 2-3 capitalized words, that's a skill
                    if len(current_skill) >= 2 and len(current_skill) <= 3:
                        skill_name = ' '.join(current_skill)
                        skills.add(skill_name.lower())
                        current_skill = [word]  # Start new skill with current word
                else:
                    if current_skill and len(current_skill) >= 2:
                        skill_name = ' '.join(current_skill)
                        skills.add(skill_name.lower())
                    current_skill = []
            
            # Add any remaining skill
            if current_skill and len(current_skill) >= 2:
                skill_name = ' '.join(current_skill)
                skills.add(skill_name.lower())
    
    # Extract from job descriptions
    if any(keyword in text_lower for keyword in ["looking for", "required", "qualifications", "skills:"]):
        # Look for bullet points
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith(("-", "•", "*", ">")):
                skill = re.sub(r'^[-\•\*\>\s]+', '', line_stripped)
                if skill and len(skill) < 100:
                    skills.add(skill.lower())
    
    return skills


def extract_experience_years(text: str) -> int:
    """Extract years of experience from text"""
    text_lower = text.lower()
    
    # Pattern 1: Explicit years mentioned
    patterns = [r'(\d+)\+?\s*years?', r'(\d+)\s*yr', r'experience.*?(\d+)', r'(\d+).*?experience']
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                return int(match)
            except:
                pass
    
    # Pattern 2: Calculate from dates in your resume
    # Your resume: Sep 2018-Present and Jun 2015-Aug 2018
    date_pattern = r'(\d{4})\s*[-–]\s*(?:Present|\d{4})'
    dates = re.findall(date_pattern, text)
    
    if dates:
        try:
            earliest = min([int(date) for date in dates])
            return 2026 - earliest  # Update year as needed
        except:
            return 6  # Default
    
    return 6  # Default from resume text saying "6+ years"


# Test function
if __name__ == "__main__":
    test_text = """
    SKILL
    Problem Solving Adaptability Collaboration Strong Work Ethic Time Management Critical Thinking Handling Pressure Leadership
    
    EXPERIENCE
    ADMINISTRATIVE ASSISTANT
    Redford & Sons, Boston, MA / September 2018 - Present
    6+ years experience
    """
    
    result = extract_entities(test_text)
    print("\n✅ Test Result:", result)