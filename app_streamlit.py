import streamlit as st
import tempfile
import os
import shutil
from app.resume_parser import extract_text_from_pdf
from app.ner_model import extract_entities
from app.skill_matcher import semantic_match
from app.scoring import extract_years_of_experience, calculate_scores
from app.explainer import generate_explanation

# Page configuration
st.set_page_config(
    page_title="Intelligent Resume Matcher",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-card {
        background-color: #F8F9FA;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .skill-match {
        padding: 0.5rem;
        margin: 0.2rem;
        border-radius: 5px;
        display: inline-block;
    }
    .matched-skill {
        background-color: #D1FAE5;
        color: #065F46;
        border: 1px solid #10B981;
    }
    .missing-skill {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #EF4444;
    }
</style>
""", unsafe_allow_html=True)

# Title and header
st.markdown('<h1 class="main-header">📄 Intelligent Resume Matcher</h1>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    Upload a resume and job description to analyze compatibility and get match scores
</div>
""", unsafe_allow_html=True)

# Sidebar for inputs
with st.sidebar:
    st.header("⚙️ Input Parameters")
    
    # File upload section
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload the candidate's resume in PDF format"
    )
    
    if uploaded_file:
        st.success(f"✓ {uploaded_file.name} uploaded")
        st.caption(f"Size: {uploaded_file.size / 1024:.1f} KB")
    
    st.divider()
    
    # Job description section
    st.subheader("2. Job Description")
    jd_text = st.text_area(
        "Paste the job description:",
        height=250,
        placeholder="""Example: Looking for Administrative Assistant with:
• 5+ years experience
• Microsoft Excel proficiency
• Strong organizational skills
• Problem-solving abilities
• Time management skills""",
        help="Enter the complete job description for matching"
    )
    
    st.divider()
    
    # Experience requirement
    st.subheader("3. Requirements")
    required_exp = st.slider(
        "Required Experience (years)",
        min_value=0,
        max_value=20,
        value=5,
        help="Minimum years of experience required for the position"
    )
    
    # Match threshold
    match_threshold = st.slider(
        "Skill Match Threshold",
        min_value=0.1,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Similarity threshold for skill matching"
    )
    
    st.divider()
    
    # Analyze button
    analyze_btn = st.button(
        "🚀 Analyze Resume Match",
        type="primary",
        use_container_width=True,
        disabled=(not uploaded_file or not jd_text)
    )

# Main content area
if analyze_btn and uploaded_file and jd_text:
    with st.spinner("🔍 Analyzing resume and job description..."):
        # Save uploaded file temporarily (same as FastAPI)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # 1. Save and Parse Resume (same as FastAPI)
            resume_text = extract_text_from_pdf(tmp_path)
            
            # 2. Extract Entities (Resume) - same as FastAPI
            resume_data = extract_entities(resume_text)
            candidate_exp = extract_years_of_experience(resume_text)
            
            # 3. Extract Entities (JD) - same as FastAPI
            jd_data = extract_entities(jd_text)
            jd_skills = list(jd_data["skills"])
            
            # 4. Semantic Matching - same as FastAPI
            match_rate, matched, missing = semantic_match(resume_data["skills"], jd_skills, threshold=match_threshold)
            
            # 5. Scoring - same as FastAPI
            scores = calculate_scores(match_rate, candidate_exp, required_exp)
            
            # 6. Explainability - same as FastAPI
            explanation = generate_explanation(
                "Candidate", matched, missing, candidate_exp, required_exp
            )
            
            # ========== STREAMLIT UI DISPLAY ==========
            
            # Header with overall score
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                score_color = "green" if scores["overall_score"] >= 70 else "orange" if scores["overall_score"] >= 50 else "red"
                st.markdown(f"""
                <div style='text-align: center;'>
                    <h2 style='color: {score_color}; font-size: 3rem;'>{scores['overall_score']:.1f}/100</h2>
                    <h3>Overall Match Score</h3>
                </div>
                """, unsafe_allow_html=True)
            
            # Score cards in columns
            st.subheader("📊 Detailed Scores")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                with st.container():
                    st.markdown('<div class="score-card">', unsafe_allow_html=True)
                    st.metric("Experience Score", f"{scores['experience_score']:.1f}/100")
                    st.progress(scores['experience_score'] / 100)
                    exp_status = "✅ Exceeds" if candidate_exp >= required_exp else "⚠️ Below" if candidate_exp > 0 else "❌ None"
                    st.caption(f"{exp_status} requirement ({candidate_exp} vs {required_exp} years)")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                with st.container():
                    st.markdown('<div class="score-card">', unsafe_allow_html=True)
                    st.metric("Skill Match Score", f"{scores['skill_score']:.1f}/100")
                    st.progress(scores['skill_score'] / 100)
                    st.caption(f"Matched {len(matched)} of {len(jd_skills)} required skills")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                with st.container():
                    st.markdown('<div class="score-card">', unsafe_allow_html=True)
                    st.metric("Match Rate", f"{match_rate*100:.1f}%")
                    st.progress(match_rate)
                    match_status = "Strong" if match_rate >= 0.7 else "Moderate" if match_rate >= 0.4 else "Weak"
                    st.caption(f"{match_status} skill alignment")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Skills Analysis Section
            st.subheader("🔧 Skills Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if resume_data["skills"]:
                    st.markdown(f"**📋 Extracted from Resume ({len(resume_data['skills'])} skills)**")
                    skills_text = ", ".join(resume_data["skills"][:15])
                    if len(resume_data["skills"]) > 15:
                        skills_text += f"... (+{len(resume_data['skills']) - 15} more)"
                    st.info(skills_text)
                else:
                    st.warning("No skills extracted from resume")
                
                # Experience details
                st.markdown(f"**🎯 Experience: {candidate_exp} years**")
            
            with col2:
                if jd_skills:
                    st.markdown(f"**🎯 Required in Job ({len(jd_skills)} skills)**")
                    jd_skills_text = ", ".join(jd_skills[:15])
                    if len(jd_skills) > 15:
                        jd_skills_text += f"... (+{len(jd_skills) - 15} more)"
                    st.info(jd_skills_text)
                else:
                    st.warning("No skills extracted from job description")
            
            # Matched vs Missing Skills
            st.subheader("🎯 Skill Match Details")
            
            tab1, tab2 = st.tabs([f"✅ Matched Skills ({len(matched)})", f"⚠️ Missing Skills ({len(missing)})"])
            
            with tab1:
                if matched:
                    st.success(f"Candidate has {len(matched)} required skills:")
                    cols = st.columns(3)
                    for i, skill in enumerate(matched):
                        with cols[i % 3]:
                            st.markdown(f'<div class="skill-match matched-skill">✓ {skill}</div>', unsafe_allow_html=True)
                else:
                    st.info("No skills matched above the threshold")
            
            with tab2:
                if missing:
                    st.warning(f"Candidate is missing {len(missing)} required skills:")
                    cols = st.columns(3)
                    for i, skill in enumerate(missing):
                        with cols[i % 3]:
                            st.markdown(f'<div class="skill-match missing-skill">✗ {skill}</div>', unsafe_allow_html=True)
                else:
                    st.success("All required skills are matched!")
            
            # Explanation Section
            st.subheader("📝 Detailed Analysis")
            st.write(explanation)
            
            # Raw Data (expandable)
            with st.expander("📁 View Raw Data"):
                raw_data = {
                    "candidate_profile": {
                        "extracted_skills": list(resume_data["skills"]),
                        "extracted_experience": candidate_exp
                    },
                    "scores": scores,
                    "match_details": {
                        "matched_skills": matched,
                        "missing_skills": missing,
                        "match_rate": match_rate
                    },
                    "job_description_skills": jd_skills
                }
                st.json(raw_data)
                
                # Download button
                import json
                json_str = json.dumps(raw_data, indent=2)
                st.download_button(
                    label="📥 Download Results as JSON",
                    data=json_str,
                    file_name="resume_match_results.json",
                    mime="application/json"
                )
            
            # Cleanup
            st.caption(f"*Analysis completed for: {uploaded_file.name}*")
                
        except Exception as e:
            st.error(f"❌ Error processing resume: {str(e)}")
            st.exception(e)
        finally:
            # Cleanup temp file (same as FastAPI)
            try:
                os.unlink(tmp_path)
            except:
                pass

elif not uploaded_file or not jd_text:
    # Show empty state with instructions
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("👈 **Get Started**")
        st.markdown("""
        1. **Upload a resume** (PDF format) in the sidebar
        2. **Paste the job description** you want to match against
        3. **Set experience requirements** using the slider
        4. Click **'Analyze Resume Match'** to see results
        
        The system will:
        - Extract skills and experience from the resume
        - Identify required skills from the job description
        - Calculate match scores using semantic similarity
        - Provide detailed analysis and recommendations
        """)
    
    with col2:
        st.markdown("**📊 What's Analyzed?**")
        st.markdown("""
        - **Skills Match**: Semantic similarity between resume and JD skills
        - **Experience**: Years of experience vs requirement
        - **Overall Score**: Weighted combination of all factors
        - **Missing Skills**: Gaps that need addressing
        """)
    
    # Example section
    with st.expander("📚 See Example Job Description"):
        st.markdown("""
        **Administrative Assistant Job Description:**
        
        **Requirements:**
        - 5+ years administrative experience
        - Proficiency in Microsoft Office Suite (Excel, Word, PowerPoint)
        - Strong organizational and time management skills
        - Excellent communication and problem-solving abilities
        - Ability to handle confidential information
        - Experience with scheduling and calendar management
        
        **Responsibilities:**
        - Coordinate meetings and appointments
        - Prepare reports and presentations
        - Manage office supplies and budgets
        - Handle correspondence and documentation
        """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        Intelligent Resume Matcher v1.0 | Built with Streamlit & FastAPI backend
    </div>
    """,
    unsafe_allow_html=True
)