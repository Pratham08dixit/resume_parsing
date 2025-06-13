import os
import fitz  # PyMuPDF
from docx import Document
import streamlit as st
import json
from dotenv import load_dotenv
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import time


load_dotenv()

# Get API key from environment 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("⚠ Missing GEMINI_API_KEY.")

# Configuring API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Resume Extraction Functions
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

def extract_text_from_docx(docx_file):
    document = Document(docx_file)
    return "\n".join(p.text for p in document.paragraphs)

def extract_text_from_txt(txt_file):
    return txt_file.read().decode('utf-8')

# AI Analysis Functions
def analyze_resume(resume_text):
    """Analyze resume and return structured feedback"""
    prompt = f"""
    Analyze this resume and return ONLY a valid JSON object with exactly these fields:
    - sections_detected: array of strings (sections found in the resume)
    - missing_sections: array of strings (important sections that are missing)
    - well_written_sections: array of strings (sections that are well-written)
    - resume_quality_score: number between 0-100 (overall resume quality)
    - skills_sentiment_summary: string (sentiment analysis of skills section)
    - improvement_suggestions: array of strings (specific improvement suggestions)

    Resume:
    {resume_text}

    Return ONLY the JSON object, no other text or explanation.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f'{{"error": "Failed to analyze resume: {str(e)}"}}'

def parse_structured_resume(resume_text):
    """Parse resume into standardized JSON format"""
    prompt = f"""
    Parse this resume into a standardized, code-readable JSON format with these exact fields:
    {{
        "personal_info": {{
            "name": "string",
            "email": "string",
            "phone": "string",
            "location": "string",
            "linkedin": "string"
        }},
        "summary": "string",
        "experience": [
            {{
                "title": "string",
                "company": "string",
                "duration": "string",
                "details": ["array of strings"]
            }}
        ],
        "education": [
            {{
                "degree": "string",
                "institution": "string",
                "year": "string",
                "details": "string"
            }}
        ],
        "skills": ["array of strings"],
        "certifications": ["array of strings"],
        "projects": [
            {{
                "name": "string",
                "description": "string",
                "technologies": ["array of strings"]
            }}
        ]
    }}

    Resume:
    {resume_text}

    Return ONLY the JSON object. If a section is not found, use empty string or empty array.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f'{{"error": "Failed to parse resume: {str(e)}"}}'

def detect_jargon_and_ats_issues(resume_text):
    """Detect jargon and provide ATS recommendations"""
    prompt = f"""
    Analyze this resume for jargon and ATS-friendliness. Return ONLY a valid JSON object:
    {{
        "jargon_detected": ["array of jargon phrases found"],
        "filler_phrases": ["array of filler phrases found"],
        "ats_recommendations": ["array of ATS-friendly suggestions"],
        "keyword_suggestions": ["array of industry keywords to add"],
        "formatting_issues": ["array of formatting problems"]
    }}

    Resume:
    {resume_text}

    Return ONLY the JSON object.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f'{{"error": "Failed to analyze jargon/ATS: {str(e)}"}}'

def generate_pdf_report(analysis_data, structured_data, ats_data):
    """Generate PDF report of the analysis"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Centre focused 
    )
    story.append(Paragraph("Resume Analysis Report", title_style))
    story.append(Spacer(1, 20))

    # Quality Score
    score = analysis_data.get('resume_quality_score', 'N/A')
    story.append(Paragraph(f"<b>Resume Quality Score: {score}/100</b>", styles['Heading2']))
    story.append(Spacer(1, 12))

    # Sections Detected
    sections = analysis_data.get('sections_detected', [])
    story.append(Paragraph("<b>Sections Detected:</b>", styles['Heading3']))
    for section in sections:
        story.append(Paragraph(f"• {section}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Missing Sections
    missing = analysis_data.get('missing_sections', [])
    if missing:
        story.append(Paragraph("<b>Missing Sections:</b>", styles['Heading3']))
        for section in missing:
            story.append(Paragraph(f"• {section}", styles['Normal']))
        story.append(Spacer(1, 12))

    # Skills Sentiment
    sentiment = analysis_data.get('skills_sentiment_summary', '')
    if sentiment:
        story.append(Paragraph("<b>Skills Sentiment Analysis:</b>", styles['Heading3']))
        story.append(Paragraph(sentiment, styles['Normal']))
        story.append(Spacer(1, 12))

    # Improvement Suggestions
    suggestions = analysis_data.get('improvement_suggestions', [])
    if suggestions:
        story.append(Paragraph("<b>Improvement Suggestions:</b>", styles['Heading3']))
        for suggestion in suggestions:
            story.append(Paragraph(f"• {suggestion}", styles['Normal']))
        story.append(Spacer(1, 12))

    # ATS Recommendations
    ats_recs = ats_data.get('ats_recommendations', [])
    if ats_recs:
        story.append(Paragraph("<b>ATS-Friendly Recommendations:</b>", styles['Heading3']))
        for rec in ats_recs:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
        story.append(Spacer(1, 12))

    # Jargon Detection
    jargon = ats_data.get('jargon_detected', [])
    if jargon:
        story.append(Paragraph("<b>Jargon/Filler Phrases Detected:</b>", styles['Heading3']))
        for phrase in jargon:
            story.append(Paragraph(f"• {phrase}", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title(" AI-Powered Resume Analyzer")
st.caption("Comprehensive resume analysis with structured parsing and ATS recommendations")

uploaded_file = st.file_uploader("Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
analyze_button = st.button("🔍 Analyze Resume")

if analyze_button and uploaded_file:
    st.info("⏳ Processing your resume...")

    # Progress bar 
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()

    # Step 1: Extract resume text
    status_text.text(" Extracting text from resume...")
    progress_bar.progress(10)

    if uploaded_file.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        resume_text = extract_text_from_docx(uploaded_file)
    else:  # .txt file
        resume_text = extract_text_from_txt(uploaded_file)

    if not resume_text.strip():
        st.error("Could not extract text from resume.")
        st.stop()

    progress_bar.progress(20)
    status_text.text(" Text extraction completed")
    time.sleep(0.5)

    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["Analysis", "Structured Data", "ATS & Jargon", "PDF Report"])

    with tab1:
        st.subheader("Resume Analysis")

        # Step 2: Main Analysis
        status_text.text("🔍 Analyzing resume content...")
        progress_bar.progress(40)

        feedback_raw = analyze_resume(resume_text)

        progress_bar.progress(50)
        status_text.text("Resume analysis complete!")
        time.sleep(0.5)

        try:
            # Parse JSON
            raw_output = feedback_raw.strip()
            if raw_output.startswith('```json'):
                raw_output = raw_output.replace('```json', '').replace('```', '').strip()
            elif raw_output.startswith('```'):
                raw_output = raw_output.replace('```', '').strip()

            analysis_data = json.loads(raw_output)

            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Quality Score", f"{analysis_data.get('resume_quality_score', 'N/A')}/100")
            with col2:
                st.metric("Sections Detected", len(analysis_data.get('sections_detected', [])))
            with col3:
                st.metric("Missing Sections", len(analysis_data.get('missing_sections', [])))

            # Detailed Analysis
            with st.expander("📋 Detailed Analysis", expanded=True):
                st.json(analysis_data)

        except Exception as e:
            st.warning("Could not parse JSON feedback.")
            st.text_area("Raw Feedback", feedback_raw, height=200)
            st.error(f"Error details: {str(e)}")
            analysis_data = {}

    with tab2:
        st.subheader("Structured Resume Data")

        # Step 3: Structured Parsing
        status_text.text("Parsing structured data...")
        progress_bar.progress(65)

        structured_raw = parse_structured_resume(resume_text)

        progress_bar.progress(75)
        status_text.text("Structured parsing complete!")
        time.sleep(0.5)

        try:
            raw_output = structured_raw.strip()
            if raw_output.startswith('```json'):
                raw_output = raw_output.replace('```json', '').replace('```', '').strip()
            elif raw_output.startswith('```'):
                raw_output = raw_output.replace('```', '').strip()

            structured_data = json.loads(raw_output)

            # Display structured data
            st.json(structured_data)

            # Download structured data
            st.download_button(
                "Download Structured Data (JSON)",
                json.dumps(structured_data, indent=2),
                file_name="structured_resume.json",
                mime="application/json"
            )

        except Exception as e:
            st.warning("Could not parse structured data.")
            st.text_area("Raw Structured Data", structured_raw, height=200)
            st.error(f"Error details: {str(e)}")
            structured_data = {}

    with tab3:
        st.subheader("ATS & Jargon Analysis")

        # Step 4: ATS and Jargon Analysis
        status_text.text("Analyzing ATS compatibility and jargon...")
        progress_bar.progress(85)

        ats_raw = detect_jargon_and_ats_issues(resume_text)

        progress_bar.progress(95)
        status_text.text("ATS analysis complete!")
        time.sleep(0.5)

        try:
            raw_output = ats_raw.strip()
            if raw_output.startswith('```json'):
                raw_output = raw_output.replace('```json', '').replace('```', '').strip()
            elif raw_output.startswith('```'):
                raw_output = raw_output.replace('```', '').strip()

            ats_data = json.loads(raw_output)

            # Display ATS recommendations
            if ats_data.get('ats_recommendations'):
                st.subheader("ATS-Friendly Recommendations")
                for rec in ats_data['ats_recommendations']:
                    st.write(f"• {rec}")

            # Display jargon detection
            if ats_data.get('jargon_detected') or ats_data.get('filler_phrases'):
                st.subheader("Jargon & Filler Phrases Detected")
                jargon_list = ats_data.get('jargon_detected', []) + ats_data.get('filler_phrases', [])
                for phrase in jargon_list:
                    st.write(f"• {phrase}")

            # Display keyword suggestions
            if ats_data.get('keyword_suggestions'):
                st.subheader("Keyword Suggestions")
                for keyword in ats_data['keyword_suggestions']:
                    st.write(f"• {keyword}")

            # Full ATS data
            with st.expander("Complete ATS Analysis", expanded=False):
                st.json(ats_data)

        except Exception as e:
            st.warning("Could not parse ATS data. Showing raw output:")
            st.text_area("Raw ATS Data", ats_raw, height=200)
            st.error(f"Error details: {str(e)}")
            ats_data = {}

    with tab4:
        st.subheader("PDF Report Generation")

        if 'analysis_data' in locals() and 'structured_data' in locals() and 'ats_data' in locals():
            try:
                # Step 5: Generate PDF report
                status_text.text("Generating PDF report....")
                progress_bar.progress(98)

                pdf_buffer = generate_pdf_report(analysis_data, structured_data, ats_data)

                # Complete!
                progress_bar.progress(100)
                status_text.text("All analysis completed")

                # Clean up progress indicators 
                time.sleep(1.5)
                progress_bar.empty()
                status_text.empty()

                st.success("PDF report generated successfully")

                # Download button for PDF
                st.download_button(
                    "⬇️ Download PDF Report",
                    pdf_buffer.getvalue(),
                    file_name="resume_analysis_report.pdf",
                    mime="application/pdf"
                )

                st.info("The PDF report includes:")
                st.write("• Resume quality score and analysis")
                st.write("• Sections detected and missing")
                st.write("• Skills sentiment summary")
                st.write("• Improvement suggestions")
                st.write("• ATS-friendly recommendations")
                st.write("• Jargon and filler phrase detection")

            except Exception as e:
                st.error(f"Error while generating PDF report: {str(e)}")
        else:
            st.warning("lease complete the analysis first to generate the PDF report.")

# Sidebar with instructions for someone who doesn't know working 
with st.sidebar:
    st.header("Instructions")
    st.write("""
    1. Upload your resume (PDF, DOCX, or TXT)
    2. Click "Analyze Resume"
    3. Review analysis in different tabs:
       - **Analysis**: Core feedback & scoring
       - **Structured Data**: Parsed resume data
       - **ATS & Jargon**: ATS recommendations
       - **PDF Report**: Downloadable report
    """)

