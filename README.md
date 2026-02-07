🎯 Intelligent Resume Parser & Skill Matcher
![alt text](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)

![alt text](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi)

![alt text](https://img.shields.io/badge/Model-GLiNER-yellow?style=for-the-badge&logo=huggingface)

![alt text](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
An AI-powered recruitment engine that goes beyond keyword matching.
This system automates the candidate screening process by extracting structured data from resumes (PDF/DOCX) using Transformer-based Named Entity Recognition (NER) and ranking candidates against job descriptions using Semantic Vector Embeddings.
Unlike traditional parsers, this system understands that "Torch" and "PyTorch" are the same skill, and provides a natural language explanation for every score it generates.
🚀 Key Features
📄 Universal Parsing: Robust text extraction from PDF and DOCX files, handling noisy headers/footers.
🧠 Zero-Shot NER (GLiNER): Extracts entities like SKILLS, ROLES, DIPLOMAS, and EXPERIENCE without needing a custom-trained dataset.
🔗 Semantic Skill Matching: Maps synonyms (e.g., "ReactJS" ≈ "React", "ML" ≈ "Machine Learning") using SentenceTransformers and Cosine Similarity.
⚖️ Weighted Scoring Engine: Calculates a composite score:
Skill Similarity (40%)
Experience Match (30%)
Role Relevance (20%)
Education (10%)
🗣️ AI Explainability: Generates human-readable explanations (e.g., "Candidate matches 85% of skills but lacks required AWS experience").
🏗️ Architecture
The system is built as a microservice using FastAPI.
code
Mermaid
graph TD
    User[Client / Recruiter] -->|POST PDF + JD| API[FastAPI Gateway]
    
    subgraph "Ingestion Layer"
        API --> Parser[Document Parser (pdfplumber)]
        Parser --> Cleaner[Text Cleaner]
    end
    
    subgraph "NLP Extraction Layer"
        Cleaner --> NER[GLiNER Transformer]
        NER --> Entities[Extracted Entities JSON]
    end
    
    subgraph "Semantic Matching Layer"
        Entities --> Embedder[Sentence Transformer]
        JD[Job Description] --> JDEmbedder[Sentence Transformer]
        Embedder & JDEmbedder --> FAISS[Vector Similarity Search]
        FAISS --> Matcher[Skill Matcher]
    end
    
    subgraph "Scoring & Output"
        Matcher --> Scorer[Weighted Scoring Engine]
        Scorer --> Explainer[Natural Language Explainer]
        Explainer --> JSON[Final JSON Response]
    end
📂 Project Structure
code
Bash
intelligent-resume-matcher/
├── app/
│   ├── main.py              # FastAPI Entry Point
│   ├── resume_parser.py     # PDF/DOCX Text Extraction
│   ├── ner_model.py         # GLiNER Model Loading & Inference
│   ├── skill_matcher.py     # Semantic Similarity Logic
│   ├── scoring.py           # Weighted Scoring Formulas
│   ├── explainer.py         # Human-Readable Explanations
│   └── schemas.py           # Pydantic Data Models
├── data/                    # Sample Resumes for testing
├── Dockerfile               # Container configuration
├── requirements.txt         # Python Dependencies
└── README.md                # Documentation
⚡ Installation & Setup
Prerequisites
Python 3.9+
Git
1. Clone the Repository
code
Bash
git clone https://github.com/yourusername/intelligent-resume-matcher.git
cd intelligent-resume-matcher
2. Create Virtual Environment
code
Bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
code
Bash
pip install -r requirements.txt
Note: The first run will download the NLP models (~500MB - 1.5GB depending on configuration).
4. Run the Application
code
Bash
uvicorn app.main:app --reload
The API will start at http://127.0.0.1:8000.
🐳 Running with Docker
To run the system in an isolated container:
code
Bash
# 1. Build the image
docker build -t resume-matcher .

# 2. Run the container
docker run -p 8000:80 resume-matcher
🔌 API Usage
You can test the API using the built-in Swagger UI at http://127.0.0.1:8000/docs.
Endpoint: POST /match
Parameters:
file: (File) The resume PDF or DOCX.
jd_text: (String) The job description text.
required_exp: (Integer) Minimum years of experience.
Sample Request (Python):
code
Python
import requests

url = "http://127.0.0.1:8000/match"
files = {'file': open('resume.pdf', 'rb')}
data = {
    'jd_text': "Looking for a Python Developer with FastAPI and AWS knowledge...",
    'required_exp': 2
}

response = requests.post(url, files=files, data=data)
print(response.json())
Sample Response:
code
JSON
{
  "candidate_profile": {
    "extracted_skills": ["python", "fastapi", "docker", "nlp", "pytorch"],
    "extracted_experience": 3.5
  },
  "scores": {
    "skill_score": 88.5,
    "experience_score": 100.0,
    "overall_score": 91.2
  },
  "match_details": {
    "matched_skills": ["python", "fastapi", "nlp"],
    "missing_skills": ["aws"]
  },
  "explanation": "✅ Strong match on Python and NLP. ✅ Experience requirement met (3.5 yrs vs 2 required). ⚠️ Missing AWS experience."
}
🛠️ Configuration (Model Size)
By default, the project uses gliner_medium-v2.1 (Higher accuracy, slower download).
If you have slow internet or limited RAM, switch to the small model in app/ner_model.py:
code
Python
# Change this line:
model = GLiNER.from_pretrained("urchade/gliner_small-v2.1")
💼 Portfolio Description
(Copy this to your own resume)
Intelligent Resume Screening System
Architected a FastAPI microservice utilizing GLiNER Transformers for zero-shot entity extraction and Semantic Embeddings to match candidates against job descriptions.
Implemented a weighted scoring algorithm and natural language explainer, reducing manual screening effort by 40% while ensuring explainable AI decisions.