import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# AI configuration from environment variables
AI_API_KEY = os.getenv("AI_API_KEY")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
AI_MODEL = os.getenv("AI_MODEL", "gpt-3.5-turbo")

if not AI_API_KEY:
    print("Warning: AI_API_KEY not found in environment variables.")

client = OpenAI(
    api_key=AI_API_KEY,
    base_url=AI_BASE_URL
)

MODEL = AI_MODEL

def analyze_job_fit(resume_text: str, job_description: str, job_title: str = "", company_name: str = ""):
    # Groq Free Tier TPM limit is 6000 tokens. 
    resume_text = resume_text[:2500]
    job_description = job_description[:2500]

    prompt = f"""
You are a senior technical recruiter. Your task is to analyze a candidate's fit for a job and write a professional application email.

CRITICAL INSTRUCTIONS:
1. IDENTIFY THE NAME: The candidate's name is usually the VERY FIRST LINE/HEADING in the resume. For example, if you see "DHRUBA DATTA" at the top, that is the name.
2. AVOID ADDRESSES: Do NOT use street names or addresses as the person's name. (e.g., "Mohini Mohan Das Lane" contains an address, the name is NOT Mohan Das).
3. NO HALLUCINATIONS: Do NOT invent names. If the name is "Dhruba Datta" in the resume, use "Dhruba Datta". 
4. BE ACCURATE: Only match skills that are explicitly stated in the resume.

INPUT DATA:
- JOB TITLE: {job_title}
- COMPANY: {company_name}
- RESUME: 
{resume_text}
- JOB DESCRIPTION: 
{job_description}

OUTPUT REQUIREMENTS:
Return ONLY valid JSON. Ensure all strings (especially the email) are correctly escaped.
Structure:
{{
  "match_score": number, // MUST be an integer between 0 and 100
  "fit_summary": "2-3 sentences",
  "strengths": ["list of matched skills"],
  "missing_skills": ["missing requirements"],
  "recommendations": ["how to improve fit"],
  "application_email": "A professional email body."
}}

EMAIL RULES:
- IMPORTANT: Return ONLY the email body.
- Do NOT include "From:", "To:", "Subject:", or any headers.
- Start directly with the salutation (e.g., "Dear Hiring Manager,").
- Use double newlines (\\n\\n) for paragraphs.
- Tone: Professional and confident.
- Signature: MUST use the candidate's name found at the top of the resume. NEVER use a name from the address line.
"""
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        print("--- AI analysis complete! ---")
        import json
        analysis_result = json.loads(response.choices[0].message.content)
        
        try:
            raw_score = analysis_result.get("match_score", 0)
            score = int(float(raw_score))
            # If the score is between 0 and 1 (like 0.6), scale it to 0-100
            if 0 < float(raw_score) <= 1:
                score = int(float(raw_score) * 100)
        except:
            score = 0
            
        return {
            **analysis_result,
            "match_score": min(100, max(0, score))
        }
    except Exception as e:
        print(f"--- AI analysis FAILED: {str(e)} ---")
        raise e
