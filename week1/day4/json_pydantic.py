import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")
client = Groq(api_key=my_api_key)
model = "openai/gpt-oss-20b"
role = "user"

from pydantic import BaseModel
class Ticket(BaseModel):
    name:str
    email:str
    issue:str

schema=Ticket.model_json_schema()

response_format = {
    "type":"json_object"
}

system_prompt = f"""
Extract personal information strictly based on this schema: {schema} and give me a JSON output.
"""

message_system = {
    "role":"system",
    "content": system_prompt
}
text = "Hello My name is Swarnendu, I have bought an iphone which is not working. My Address is Delhi and email abc@gmail.com. my mobile noumber is 99999. I ate biriyani today"
prompt = f"""
Extract personal information fields from the customer ticket.
Ticket:{text}
"""
message = {
    "role": role,
    "content": prompt
}
messages = [message_system, message]

response = client.chat.completions.create(model = model, messages = messages, response_format=response_format)

answer = response.choices[0].message.content
print(answer)


# isko padte kaise hai?
import json
raw_json = answer
data_file = json.loads(raw_json)
ticket = Ticket(**data_file)
print(ticket)