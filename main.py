import streamlit as st                              # For Web Interface (Front-End)
from streamlit_lottie import st_lottie
import requests                        
from pdfminer.high_level import extract_text      # To Extract Text from Resume PDF
from sentence_transformers import SentenceTransformer      # To generate Embeddings of text
from sklearn.metrics.pairwise import cosine_similarity     # To get Similarity Score of Resume and Job Description
from groq import Groq                             # API to use LLM's
import re                                         # To perform Regular Expression Functions
from dotenv import load_dotenv                    # Loading API Key from .env file
import os

# Initialize theme in session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True  # Default to dark mode

def apply_theme():
    """Apply dark or light theme based on session state"""
    
    if st.session_state.dark_mode:
        # Dark theme CSS
        theme_css = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
            
            .stApp {
                background: linear-gradient(135deg, #0E1117 0%, #1a1c29 100%);
                color: #FAFAFA;
                font-family: 'Poppins', sans-serif;
            }
            
            /* Animated title styling */
            .animated-title {
                font-family: 'Poppins', sans-serif;
                font-size: 3rem;
                font-weight: 700;
                color: white;
                animation: bounce 2s ease-in-out infinite;
                margin-bottom: 0;
                text-shadow: 0 4px 8px rgba(0,0,0,0.5);
            }
            
            /* Theme toggle button */
            .theme-toggle {
                position: fixed;
                top: 70px;
                right: 20px;
                z-index: 999;
                background: linear-gradient(45deg, #FF6B6B, #FF8E53);
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                font-size: 20px;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
            }
            
            .theme-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(255, 107, 107, 0.5);
            }
            
            /* Gradient animation */
            @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            /* Bounce animation */
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-10px); }
                60% { transform: translateY(-5px); }
            }
            
            /* Typewriter effect for subtitle */
            .typewriter {
                font-family: 'Poppins', sans-serif;
                font-size: 1.2rem;
                font-weight: 400;
                color: #B0BEC5;
                margin-top: 0;
                overflow: hidden;
                border-right: 2px solid #1E88E5;
                white-space: nowrap;
                animation: typing 3s steps(40, end), blink-caret 0.75s step-end infinite;
            }
            
            @keyframes typing {
                from { width: 0; }
                to { width: 100%; }
            }
            
            @keyframes blink-caret {
                from, to { border-color: transparent; }
                50% { border-color: #1E88E5; }
            }
            
            /* Form labels */
            .stTextArea label, .stFileUploader label {
                font-family: 'Poppins', sans-serif;
                font-weight: 600;
                color: #FAFAFA !important;
            }
            
            /* Button styling */
            .stButton > button {
                font-family: 'Poppins', sans-serif;
                font-weight: 600;
                background: linear-gradient(45deg, #1E88E5, #42A5F5);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0.5rem 2rem;
                font-size: 1.1rem;
                transition: all 0.3s ease;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(30, 136, 229, 0.4);
            }
            
            /* Metric styling */
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 15px;
                color: white;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-5px);
            }
            
            /* Report styling */
            .report-container {
                background: linear-gradient(135deg, #2C3E50 0%, #34495E 100%);
                padding: 2rem;
                border-radius: 15px;
                color: white;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                margin: 1rem 0;
            }
            
            /* Section headers */
            .section-header {
                font-family: 'Poppins', sans-serif;
                font-size: 1.8rem;
                font-weight: 600;
                color: #64B5F6;
                margin: 2rem 0 1rem 0;
                border-bottom: 3px solid #64B5F6;
                padding-bottom: 0.5rem;
                animation: slideIn 1s ease-out;
            }
            
            @keyframes slideIn {
                from { opacity: 0; transform: translateX(-50px); }
                to { opacity: 1; transform: translateX(0); }
            }
        </style>
        """
    else:
        # Light theme CSS
        theme_css = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
            
            .stApp {
                background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
                color: #2C3E50;
                font-family: 'Poppins', sans-serif;
            }
            
            /* Animated title styling */
            .animated-title {
                font-family: 'Poppins', sans-serif;
                font-size: 3rem;
                font-weight: 700;
                color: #2C3E50;
                animation: bounce 2s ease-in-out infinite;
                margin-bottom: 0;
                text-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            
            /* Theme toggle button */
            .theme-toggle {
                position: fixed;
                top: 70px;
                right: 20px;
                z-index: 999;
                background: linear-gradient(45deg, #007BFF, #0056B3);
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                font-size: 20px;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
            }
            
            .theme-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(0, 123, 255, 0.5);
            }
            
            /* Bounce animation */
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-10px); }
                60% { transform: translateY(-5px); }
            }
            
            /* Typewriter effect for subtitle */
            .typewriter {
                font-family: 'Poppins', sans-serif;
                font-size: 1.2rem;
                font-weight: 400;
                color: #6C757D;
                margin-top: 0;
                overflow: hidden;
                border-right: 2px solid #007BFF;
                white-space: nowrap;
                animation: typing 3s steps(40, end), blink-caret 0.75s step-end infinite;
            }
            
            @keyframes typing {
                from { width: 0; }
                to { width: 100%; }
            }
            
            @keyframes blink-caret {
                from, to { border-color: transparent; }
                50% { border-color: #007BFF; }
            }
            
            /* Form labels */
            .stTextArea label, .stFileUploader label {
                font-family: 'Poppins', sans-serif;
                font-weight: 600;
                color: #2C3E50 !important;
            }
            
            /* Button styling */
            .stButton > button {
                font-family: 'Poppins', sans-serif;
                font-weight: 600;
                background: linear-gradient(45deg, #007BFF, #0056B3);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0.5rem 2rem;
                font-size: 1.1rem;
                transition: all 0.3s ease;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 123, 255, 0.4);
            }
            
            /* Metric styling */
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 15px;
                color: white;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-5px);
            }
            
            /* Report styling */
            .report-container {
                background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%);
                padding: 2rem;
                border-radius: 15px;
                color: #2C3E50;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                margin: 1rem 0;
                border: 1px solid #DEE2E6;
            }
            
            /* Section headers */
            .section-header {
                font-family: 'Poppins', sans-serif;
                font-size: 1.8rem;
                font-weight: 600;
                color: #007BFF;
                margin: 2rem 0 1rem 0;
                border-bottom: 3px solid #007BFF;
                padding-bottom: 0.5rem;
                animation: slideIn 1s ease-out;
            }
            
            @keyframes slideIn {
                from { opacity: 0; transform: translateX(-50px); }
                to { opacity: 1; transform: translateX(0); }
            }
        </style>
        """
    
    st.markdown(theme_css, unsafe_allow_html=True)

def theme_toggle():
    """Create theme toggle button"""
    # Create columns to position the toggle button
    col1, col2, col3 = st.columns([7, 1, 1])
    
    with col3:
        if st.session_state.dark_mode:
            if st.button("🌙", help="Switch to light mode", key="theme_toggle"):
                st.session_state.dark_mode = False
                st.rerun()
        else:
            if st.button("☀️", help="Switch to dark mode", key="theme_toggle"):
                st.session_state.dark_mode = True
                st.rerun()

# Apply theme first
apply_theme()

# Add theme toggle
theme_toggle()

# Load environment variables from .env
load_dotenv()

# Fetch the key from the environment
api_key = os.getenv("GROQ_API_KEY")

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Data analysis animation charts
lottie_coding = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_qp1q7mct.json") 

# Create columns for title and animation layout
title_col1, title_col2 = st.columns([3, 1])

with title_col1:
    # Animated title
    st.markdown('<h1 class="animated-title">AI Resume Analyzer 📝</h1>', unsafe_allow_html=True)
    st.markdown('<p class="typewriter">Analyze your resume with AI-powered insights</p>', unsafe_allow_html=True)

with title_col2:
    # Display Lottie animation if loaded successfully
    if lottie_coding:
        st_lottie(lottie_coding, height=150, key="coding")

# Session States to store values 
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

if "resume" not in st.session_state:
    st.session_state.resume = ""

if "job_desc" not in st.session_state:
    st.session_state.job_desc = ""

# <------- Defining Functions ------->

# Function to extract text from PDF
def extract_pdf_text(uploaded_file):
    try:
        extracted_text = extract_text(uploaded_file)
        return extracted_text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return "Could not extract text from the PDF file."

# Function to calculate similarity 
def calculate_similarity_bert(text1, text2):
    ats_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    embeddings1 = ats_model.encode([text1])
    embeddings2 = ats_model.encode([text2])
    similarity = cosine_similarity(embeddings1, embeddings2)[0][0]
    return similarity

def get_report(resume, job_desc):
    client = Groq(api_key=api_key)
    prompt = f"""
    # Context:
    - You are an AI Resume Analyzer, you will be given Candidate's resume and Job Description of the role he is applying for.

    # Instruction:
    - Analyze candidate's resume based on the possible points that can be extracted from job description,and give your evaluation on each point with the criteria below:  
    - Consider all points like required skills, experience,etc that are needed for the job role.
    - Calculate the score to be given (out of 5) for every point based on evaluation at the beginning of each point with a detailed explanation.  
    - If the resume aligns with the job description point, mark it with ✅ and provide a detailed explanation.  
    - If the resume doesn't align with the job description point, mark it with ❌ and provide a reason for it.  
    - If a clear conclusion cannot be made, use a ⚠️ sign with a reason.  
    - The Final Heading should be "Suggestions to improve your resume:" and give where and what the candidate can improve to be selected for that job role.

    # Inputs:
    Candidate Resume: {resume}
    ---
    Job Description: {job_desc}

    # Output:
    - Each any every point should be given a score (example: 3/5 ). 
    - Mention the scores and  relevant emoji at the beginning of each point and then explain the reason.
    """

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def extract_scores(text):
    pattern = r'(\d+(?:\.\d+)?)/5'
    matches = re.findall(pattern, text)
    scores = [float(match) for match in matches]
    return scores

# <--------- Starting the Work Flow ---------> 

if not st.session_state.form_submitted:
    with st.form("my_form"):
        resume_file = st.file_uploader(label="📄 Upload your Resume/CV in PDF format", type="pdf")
        st.session_state.job_desc = st.text_area("📋 Enter the Job Description of the role you are applying for:", placeholder="Job Description...")
        submitted = st.form_submit_button("🚀 Analyze Resume")
        if submitted:
            if st.session_state.job_desc and resume_file:
                st.info("🔍 Extracting Information...")
                st.session_state.resume = extract_pdf_text(resume_file)
                st.session_state.form_submitted = True
                st.rerun()
            else:
                st.warning("⚠️ Please Upload both Resume and Job Description to analyze")

if st.session_state.form_submitted:
    score_place = st.info("⚡ Generating Scores...")
    ats_score = calculate_similarity_bert(st.session_state.resume, st.session_state.job_desc)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎯 ATS Similarity Score</h3>
            <h2>{ats_score:.3f}</h2>
            <p>Score used by ATS systems</p>
        </div>
        """, unsafe_allow_html=True)

    report = get_report(st.session_state.resume, st.session_state.job_desc)
    report_scores = extract_scores(report)
    if report_scores:
        avg_score = sum(report_scores) / (5 * len(report_scores))
    else:
        avg_score = 0

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🤖 AI Analysis Score</h3>
            <h2>{avg_score:.3f}</h2>
            <p>AI-powered evaluation score</p>
        </div>
        """, unsafe_allow_html=True)
    
    score_place.success("✅ Scores generated successfully!")
    st.markdown('<h2 class="section-header">📊 AI Generated Analysis Report</h2>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="report-container">
        {report.replace('\n', '<br>')}
    </div>
    """, unsafe_allow_html=True)
    
    st.download_button(
        label="📥 Download Report",
        data=report,
        file_name="ai_resume_analysis_report.txt",
        icon=":material/download:",
        )
