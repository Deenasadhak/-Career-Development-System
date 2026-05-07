import google.generativeai as genai
from django.conf import settings
import json
import os

def generate_career_roadmap(career_name, course_name):
    """
    Generates a professional roadmap using Google Gemini.
    If API fails or is not configured, returns a smart fallback.
    """
    # Try to get from settings or directly from environment
    api_key = getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY', ''))
    
    if api_key and len(api_key) > 10:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            prompt = f"""
            You are an expert career counselor for students in Kerala, India.
            Provide a detailed professional roadmap for a student pursuing a career in '{career_name}' after completing '{course_name}'.
            
            Structure the response in a clear, step-by-step format:
            1. Foundation Phase (Year 1-2): Key skills and tools to learn.
            2. Specialization Phase (Year 3-4): Certifications and projects.
            3. Early Career Phase (First 2 years of work): Top companies to target and entry-level roles.
            4. Pro Tips: Specific advice for students in Kerala (e.g., relevant PSC exams, local networking).

            Keep the response concise and use Markdown bullet points.
            Return ONLY the roadmap content without any introductory or concluding conversational text.
            """
            response = model.generate_content(prompt)
            if response.text:
                return {"content": response.text}
        except Exception as e:
            # Log the error or print it for debugging if needed
            print(f"AI Generation Error: {e}")

    # Dynamic Fallback based on career type
    is_medical = any(word in career_name.lower() for word in ['medicine', 'medical', 'mbbs', 'doctor', 'nursing', 'health', 'clinic'])
    
    if is_medical:
        content = f"""
### 🩺 Professional Roadmap: {career_name}
*(Note: Real-time AI generation requires a valid Gemini API Key)*

#### 1. Foundation Phase (Year 1-2)
*   **Anatomy & Physiology:** Build a rock-solid understanding of the human body.
*   **Clinical Skills:** Learn patient interaction and basic diagnostics.
*   **Volunteer Work:** Gain experience in local clinics or community health centers.

#### 2. Specialization Phase (Year 3-4)
*   **Clinical Rotations:** Focus on core departments like Surgery, Pediatrics, and Internal Medicine.
*   **Exam Prep:** Start intensive preparation for licensing exams (NEXT/NEET PG).
*   **Research:** Contribute to medical journals or participate in hospital research projects.

#### 3. Early Career Phase
*   **House Surgeoncy:** Complete your mandatory internship with excellence.
*   **Specialization:** Pursue MD/MS or DNB in your chosen field.
*   **Top Institutions:** Target major networks like Amrita, Aster Medcity, or GMCs.

#### 4. Pro Tips for Kerala Students
*   **GMC Prestige:** Government Medical Colleges offer the best clinical exposure in Kerala.
*   **Language:** Ensure fluency in Malayalam to communicate effectively with local patients.
*   **Government Schemes:** Stay updated on health initiatives like Karunya and Aardhram.
"""
    else:
        content = f"""
### 🚀 Professional Roadmap: {career_name}
*(Note: Real-time AI generation requires a valid Gemini API Key)*

#### 1. Foundation Phase (Year 1-2)
*   **Master the Core:** Focus on fundamental principles of {career_name} and {course_name}.
*   **Skill Up:** Learn relevant tools and technologies (e.g., specialized software or programming).
*   **Academic Base:** Build a strong foundation in theory while exploring practical applications.

#### 2. Specialization Phase (Year 3-4)
*   **Certifications:** Aim for globally recognized professional certs.
*   **Internships:** Gain real-world experience during your breaks.
*   **Digital Presence:** Build a strong professional profile on LinkedIn and GitHub (if technical).

#### 3. Early Career Phase
*   **Portfolio Building:** Create a portfolio showcasing your best academic and independent projects.
*   **Placement Focus:** Target leading companies in Kerala (Infopark/Technopark) and beyond.
*   **Soft Skills:** Focus on communication, leadership, and professional ethics.

#### 4. Pro Tips for Kerala Students
*   **K-DISC & ASAP:** Utilize Kerala government programs like ASAP for niche skill training.
*   **Startup Mission:** If you have an entrepreneurial idea, reach out to KSUM.
*   **PSC Guidance:** Monitor Kerala PSC for technical and administrative roles in your field.
"""

    return {"content": content}

import time
from google.api_core import exceptions

def generate_aptitude_feedback(student_name, score, categories_summary):
    """
    Generates AI evaluation of aptitude results focusing on Skill & Growth Architecture.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        api_key = os.getenv('GEMINI_API_KEY', '')

    if api_key and len(api_key.strip()) > 10:
        available_models = ['gemini-1.5-flash', 'gemini-pro', 'gemini-2.0-flash']
        
        for model_name in available_models:
            for attempt in range(2):
                try:
                    genai.configure(api_key=api_key.strip())
                    model = genai.GenerativeModel(model_name)
                    
                    prompt = f"""
                    Role: Psychological Skill & Growth Architect.
                    Student: {student_name}
                    Aptitude Score: {score}/100
                    Dimension Scores: {categories_summary}
                    
                    Task: Provide a "Psychological Professional Audit" in Markdown format.
                    Constraints:
                    1. DO NOT predict specific courses or colleges.
                    2. Identify the 'Power Trait' (highest score) and explain how to leverage it professionally.
                    3. Identify the 'Growth Gap' (lowest score) and suggest one actionable habit to improve it.
                    4. 'Kerala Advantage': Recommend EXACTLY ONE Kerala-specific initiative (ASAP Kerala, K-DISC, or KSUM) that fits their profile.
                    
                    Tone: Insightful, executive, and encouraging. 150 words max.
                    """
                    
                    response = model.generate_content(prompt)
                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                        
                except Exception as e:
                    print(f"AI Model {model_name} failed: {e}")
                    break 

    # Robust Local Fallback (Skill Architect Style)
    traits_list = categories_summary.split(', ')
    # Parse scores to find high/low
    parsed_traits = {}
    for t in traits_list:
        try:
            name, val = t.split(': ')
            parsed_traits[name] = int(val.replace('%', ''))
        except: continue
    
    if not parsed_traits:
        parsed_traits = {"Analytical & Technical": 50, "Social & Empathetic": 50}

    high_trait = max(parsed_traits, key=parsed_traits.get)
    low_trait = min(parsed_traits, key=parsed_traits.get)
    
    kerala_init = "ASAP Kerala"
    if "Creative" in high_trait or "Leadership" in high_trait:
        kerala_init = "KSUM (Kerala Startup Mission)"
    elif "Analytical" in high_trait:
        kerala_init = "K-DISC (Kerala Development and Innovation Strategic Council)"

    return f"""
### 🧠 Psychological Professional Audit for {student_name}

**⚡ The Power Trait: {high_trait}**
Your profile shines in {high_trait}. In a professional setting, you should lead initiatives that require these strengths, as they will be your primary driver for rapid career advancement.

**🌱 The Growth Gap: {low_trait}**
While you are strong elsewhere, {low_trait} is an area for development. **Actionable Habit:** Dedicate 15 minutes daily to a task that pushes you out of this comfort zone to build well-rounded professional resilience.

**🌴 The Kerala Advantage: {kerala_init}**
To accelerate your growth, we recommend enrolling in **{kerala_init}**. This initiative provides the specific infrastructure and networking needed to translate your personality profile into a high-impact career in Kerala.
"""
