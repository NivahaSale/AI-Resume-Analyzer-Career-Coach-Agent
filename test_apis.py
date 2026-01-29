import os
import time
from groq import Groq
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

def test_pdf_extraction(file_path):
    print("--- Testing PDF Extraction ---")
    try:
        reader = PdfReader(file_path)
        text = reader.pages[0].extract_text()
        if text.strip():
            print(f" Success! Extracted {len(text)} characters from page 1.")
            return True
        return False
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return False

def test_groq_api():
    print("\n--- Testing Groq API ---")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print(" Error: No GROQ_API_KEY found in your .env file.")
        return False

    client = Groq(api_key=api_key)

    try:
        # Using Llama 3.3 70B - a powerful, fast free-tier model
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'Groq is ready!'"}]
        )
        print(f" Success! Groq says: {completion.choices[0].message.content}")
        return True
    except Exception as e:
        print(f" Groq API Error: {e}")
        return False

if __name__ == "__main__":
    sample_pdf = os.path.join("data", "resumes", "test_resume.pdf")
    if os.path.exists(sample_pdf):
        test_pdf_extraction(sample_pdf)
    
    test_groq_api()