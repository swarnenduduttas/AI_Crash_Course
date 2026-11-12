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

def llm_ans(prompt):
    message = {
        "role": "user",
        "content": prompt
    }
    messages = [message]
    response = client.chat.completions.create(model=model, messages= messages)
    ans = response.choices[0].message.content
    return ans

bad_prompt= """
#ROLE:
You are a support staff in a mobile/laptop company.

#TASK:
You have to classify the user complaint in a category.

#CONSTRAINS:
You have to classify the complaint in one of the following categories namely billing, technical, return.

#OUTPUTFORMAT:
your answer should be in one word and should be one of the category given in constraints.
#Example
For instance if the user complaint says he wants refund then the category is return.

#FALLBACK:
If the issue is not related to any of the categories then you have to say "not related".

This is a user complaint. 
My girlfriend left me. I want a return.
Classify this
"""

print(llm_ans(bad_prompt))