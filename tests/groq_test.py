from dotenv import load_dotenv
load_dotenv(dotenv_path="D:/AI intern task/rag-multimodal/.env")
import os
print("DEBUG: GROQ_API_KEY=", os.getenv("GROQ_API_KEY"))

from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
response = client.chat.completions.create(
    model='llama-3.3-70b-versatile',
    messages=[{"role": "user", "content": "Say hello in JSON."}]
)
print(response.choices[0].message.content)