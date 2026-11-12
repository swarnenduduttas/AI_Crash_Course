import os
from pathlib import Path
from time import time
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from time import sleep

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")
client = Groq(api_key=my_api_key)
model = "openai/gpt-oss-120b"

job_description = """
Description
Do you want to shape how AWS understands and improves the experience of millions of customers? The AWS Experience Analytics team is building a unified analytics, experimentation, and user-insights platform that spans every channel customers use — web, mobile, CLI, SDK, docs, and conversational interfaces. We just shipped our first wave of capabilities and are now designing the next, much larger version: large-scale data pipelines, real-time streaming, applied ML and generative AI, and an intelligence layer that lets teams query insights in natural language. This is an early, formative stage where the architecture and engineering norms are being set, so you won't inherit a finished system — you'll help define it.

As a Software Development Engineer on this team, you will own features end to end — from shaping requirements with product and science partners to shipping production services that AWS service teams rely on to find and fix customer friction. If you're excited about combining open-source technologies, AWS services like Redshift and Kinesis, and big-data and ML techniques to drive the future of the AWS customer experience, we'd love to hear from you.

Key job responsibilities
- Design, build, test, and operate scalable services and data pipelines that power the analytics platform, ensuring reliability and fresh data for downstream consumers.
- Own a meaningful component or feature area end to end — from system design through production deployment and ongoing operations — bringing clarity to problems and identifying simple, maintainable solutions.
- Collaborate with product managers, applied scientists, and partner engineering teams to translate requirements into working software that improves customer-journey and experience-health metrics.
- Contribute to code reviews and mentor teammates, raising the bar on code quality, documentation, and engineering standards across the team.
- Evaluate and integrate generative AI tools and techniques where they can accelerate development or improve the platform's insights capabilities.

About the team
AWS Experience Analytics is a newly formed organization with a rapidly expanding charter. We own the services and data warehouses AWS uses to gather quantitative insights (analytics, experimentation) and qualitative insights (user feedback, ratings) and turn them into actions that improve the AWS customer experience. Our customers are the service teams across AWS who need reliable metrics and tooling to understand how people use their products.

Over the coming months and years, we are investing in a unified data-collection-to-insights platform, richer customer-journey metrics across every AWS channel, behavioral segmentation powered by ML, and an agentic insights layer driven by generative AI. It's a collaborative, builder-friendly environment where engineers take on increasing scope as the platform grows.

Basic Qualifications
- 3+ years of non-internship professional software development experience
- 2+ years of non-internship design or architecture (design patterns, reliability and scaling) of new and existing systems experience
- 1+ years of software development engineer or related occupational experience
- 1+ years of designing and developing large-scale, multi-tiered, multi-threaded, embedded or distributed software applications, tools, systems, and services using: C#, C++, Java, or Perl experience
- 1+ years of Object Oriented Design experience
- Bachelor's degree or foreign equivalent in Computer Science, Engineering, Mathematics, or a related field
- Experience programming with at least one software programming language

Preferred Qualifications
- 3+ years of full software development life cycle, including coding standards, code reviews, source control management, build processes, testing, and operations experience
- Bachelor's degree in computer science or equivalent

Amazon is an equal opportunity employer and does not discriminate on the basis of protected veteran status, disability, or other legally protected status.

Our inclusive culture empowers Amazonians to deliver the best results for our customers. If you have a disability and need a workplace accommodation or adjustment during the application and hiring process, including support for the interview or onboarding process, please visit https://amazon.jobs/content/en/how-we-hire/accommodations for more information. If the country/region you’re applying in isn’t listed, please contact your Recruiting Partner.


The base salary range for this position is listed below. Your Amazon package will include sign-on payments and restricted stock units (RSUs). Final compensation will be determined based on factors including experience, qualifications, and location. Amazon also offers comprehensive benefits including health insurance (medical, dental, vision, prescription, Basic Life & AD&D insurance and option for Supplemental life plans, EAP, Mental Health Support, Medical Advice Line, Flexible Spending Accounts, Adoption and Surrogacy Reimbursement coverage), 401(k) matching, paid time off, and parental leave. Learn more about our benefits at https://amazon.jobs/en/benefits.
"""
class JobD(BaseModel):
    role: str
    required_skills: list[str]
    preferred_skills: list[str]
    educational_requiremets: list[str]
    minimum_experience: float|None
    responsibilities: list[str]

job_schema = JobD.model_json_schema()

system_prompt = f"""
You are an expert HR assistant.
Your job is to analyze the job description and extract structured information from it.
Return only valid JSON matching this schema : {job_schema}.

IMPORTANT:
Donot return the schema itself.
Do not return fields like "properties", "title" or "type".
Fill the schema with actual information from the job description.

If minimum experience is not mentioned in the job description, return null for that field.
If any of the required fields are not mentioned in the job description, return an empty list for that field.
Donot invent information that is not present in the job description.
"""
message_system = {
    "role": "system",
    "content": system_prompt
}

user_prompt = f"""
Analyze the following job description {job_description}.
"""
message = {
    "role": "user",
    "content": user_prompt
}
messages = [message_system, message]

response_format = {
    "type": "json_object"
}

response = client.chat.completions.create(model = model, messages = messages, response_format = response_format)

answer = response.choices[0].message.content
# print(answer)

import json
raw_json = answer
job_data = json.loads(raw_json)
job = JobD(**job_data)

#print(job)

class Experience(BaseModel):
    company:str|None=None
    role:str|None=None
    duration:str|None=None
    description:str|None=None
    skills_used:list[str] = []

class Resume(BaseModel):
    name:str|None=None
    email:str|None=None
    phone:str|None=None
    total_experience : float|None=None
    skills : list[str]|None=None
    experiences : list[Experience] = []
    educational_qualifications : list[str] = []
    projects : list[str] = []
    certifications : list[str]|None=None

class MatchResult(BaseModel):
    score : float
    details: dict

resume_schema = Resume.model_json_schema()
match_schema = MatchResult.model_json_schema()

from pypdf import PdfReader
def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text +"\n"
    return text

from docx import Document
def read_docx(file_path):
    document = Document(file_path)
    text=""
    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                text += cell.text + "\n"    

    return text

def read_resume(file_path):
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return read_pdf(file_path)
    elif ext == ".docx":
        return read_docx(file_path)
    else:
        return None


def parse_resume(resume_text):
   system_prompt = f"""
You are an expert resume parser. 
Extract information fomr the resume based on its meaning not only based on exact section heading.
Different resumes may have different formats and section headings for e.g
- Experience
- Work History
- Employment
- Internships
These heading may contain details about the candidate's work experience.

Skills may appear in the skills section or may be mentioned in the experience section, so you need to understand the content and context to extract the relevant information accurately.   

Return ONLY valid JSON matching this schema : {resume_schema}.

IMPORTANT:
- Donot invent information.
- If any of the required fields are not mentioned in the resume, return null for that field.
- Include interships in the experiences list.
- Extract skills mentioned in across the resume, including those mentioned in the experience section.
""" 
   user_prompt = f""" 
Parse the follwing resume : {resume_text}
"""

   message_system = {
       "role":"system",
       "content":system_prompt
   }

   message_user = {
       "role":"user",
       "content" : user_prompt
   }
   response_format = {
       "type":"json_object"
   }
   messages = [message_system, message_user]
   response = client.chat.completions.create(model = model, messages = messages, response_format = response_format)
   raw_output = response.choices[0].message.content
   data = json.loads(raw_output)
   resume = Resume(**data)
   return resume

def final_score(job, resume):
    match_score = MatchResult.model_json_schema()

    prompt = f"""
    You are an HR recruiter.
    Compare the job requirements with the candidate's resume and calculate a matching score.

    JOB_DESCRIPTION:
    {job.model_dump_json(indent=2)}
    CANDIDATE_RESUME:
    {resume.model_dump_json(indent=2)}

    Return JSON matching this schema : {match_schema}
    Give the following details:
    1. Candidate's name
    2. Matching skills
    3. Missing important skills
    4. Whether the candidate meets the minimum experience requirement
    5. Overall match percentage score (0-100)
    6. Short final verdict

    Keep the response concise and to the point. Do not include any additional explanations or information.
    """
    message = {
        "role":"user",
        "content": prompt
    }

    messages = [message]
    response_format = {
        "type": "json_object"
    }
    response = client.chat.completions.create(model = model, messages = messages, response_format = response_format)
    data = json.loads(response.choices[0].message.content)
    match_result = MatchResult(**data)
    return match_result

resume_folder = Path("resumes")
all_results = []
for file_path in resume_folder.iterdir():
    if file_path.suffix.lower() not in [".pdf", ".docx"]:
        continue
    #print(f"Processing resume: {file_path.name}")
    resume_text = read_resume(file_path)
    parsed_resume = parse_resume(resume_text)

    print(file_path.name, "->", repr(parsed_resume.name))
    print(resume_text[:500])

    sleep(2)  #To avoid hitting rate limits
    result = final_score(job, parsed_resume)
    sleep(5)  #To avoid hitting rate limits

    all_results.append({
        "name" : parsed_resume.name,
        "score" : result.score,
        "details" : result.details
    })

    print(all_results)





