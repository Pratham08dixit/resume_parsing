# 🤖 AI-Powered Resume Analyzer

A comprehensive resume analysis tool built with **Streamlit** and **Google Gemini AI**. This application provides detailed resume feedback, structured data parsing, ATS optimization, and professional PDF reports.

## ✨ Features

### 📊 **Core Resume Analysis**
- **Comprehensive Feedback**: Detailed analysis with quality scoring (0-100)
- **Section Detection**: Identifies present and missing resume sections
- **Skills Sentiment Analysis**: Evaluates confidence and specificity of skills
- **Quality Assessment**: Evaluates well-written sections and areas for improvement
- **Actionable Suggestions**: Specific recommendations for enhancement

### 🏧 **Structured Resume Parsing**
- **Standardized JSON Format**: Converts resume to code-readable structure
- **Personal Information Extraction**: Name, email, phone, location, LinkedIn
- **Experience Parsing**: Job titles, companies, durations, and details
- **Education & Skills**: Structured extraction of qualifications
- **Projects & Certifications**: Organized project and certification data

### 🎯 **ATS Optimization & Jargon Detection**
- **ATS-Friendly Recommendations**: Keyword and formatting suggestions
- **Jargon Detection**: Identifies excessive jargon and filler phrases
- **Keyword Suggestions**: Industry-specific keywords to improve visibility
- **Formatting Analysis**: ATS-compatible structure recommendations

### 📄 **Professional PDF Reports**
- **Comprehensive Reports**: All analysis results in professional PDF format
- **Easy Sharing**: Download and share analysis with others
- **Structured Layout**: Well-organized report with clear sections
- **Export Options**: JSON data export for structured information

### 🔧 **Technical Features**
- **Multi-format Support**: Upload PDF, DOCX, or TXT resumes
- **Real-time Processing**: Instant AI analysis and feedback
- **User-friendly Interface**: Clean, intuitive Streamlit UI with tabs
- **Error Handling**: Robust error management with helpful messages

## 📋 Requirements

- `requirements.txt`:
```txt
streamlit
python-docx
pymupdf
python-dotenv
google-generativeai
reportlab
```


## 🚀 Usage

### 1. **Upload Your Resume**
- Click "Upload Resume (PDF, DOCX, or TXT)"
- Select your resume file
- Supported formats: PDF, DOCX, TXT

### 2. **Analyze Resume**
- Click "🔍 Analyze Resume"
- Wait for AI processing (usually 30-60 seconds)

### 3. **Review Results in Tabs**
- **Analysis**: Core feedback with quality scoring and suggestions
- **Structured Data**: Parsed resume in standardized JSON format
- **ATS & Jargon**: ATS recommendations and jargon detection
- **PDF Report**: Professional downloadable analysis report

### 4. **Download Reports**
- **JSON Data**: Download structured resume data
- **PDF Report**: Download comprehensive analysis report


### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/resume-analyzer.git
cd resume-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your API keys to .env

# Run the application
streamlit run main.py
```


---


*Transform your resume with AI-powered insights and land your dream job!*
