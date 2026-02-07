from gliner import GLiNER

# Load model once (Global variable or dependency injection)
# "urchade/gliner_medium-v2.1" is a great balance of speed/performance
model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")

labels = ["person", "skill", "role", "experience", "education", "company", "tool"]

def extract_entities(text: str):
    entities = model.predict_entities(text, labels, threshold=0.4)
    
    structured_data = {
        "skills": set(),
        "roles": [],
        "experience": [],
        "education": [],
        "companies": []
    }
    
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
             # Note: GLiNER might catch "3 years" or date ranges here
            structured_data["experience"].append(text_val)
            
    return structured_data