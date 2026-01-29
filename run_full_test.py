from src.analyzer import ResumeAnalyzer
from pypdf import PdfReader
import os

# 1. Extract real text from your PDF
reader = PdfReader("data/resumes/test_resume.pdf") # Change this to your actual file path
full_text = ""
for page in reader.pages:
    full_text += page.extract_text()

# 2. Run the analyzer on the FULL text
analyzer = ResumeAnalyzer()
result = analyzer.analyze(full_text)

print(result)
