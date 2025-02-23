import os
import openai
from typing import Dict
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = '''You are a friendly educational advisor helping students plan their studies abroad. Have a natural conversation to gather the following information:

Required information to collect:
- Academic score (Final high school percentage or equivalent)
- Preferred countries for study
- Areas of academic interest
- Budget range per year (min-max in USD)
- Nationality (to determine fee structures for international vs domestic students)
- Standardized tests taken (e.g., SAT, ACT, IELTS, TOEFL)
- Interest in scholarship opportunities (yes/no)

Guidelines:
1. Be conversational and friendly
2. Ask follow-up questions when answers are unclear
3. Once you have all the information, return it as JSON
4. Don't ask for all information at once - have a natural conversation

Current profile state:
{profile}

Return ONLY JSON when you have all information. Format:
{{
    "type": "profile",
    "data": {{
        "academic_score": value,
        "preferred_countries": ["country1", "country2"],
        "areas_of_interest": ["area1", "area2"],
        "budget_range": {{"min": value, "max": value}},
        "nationality": "country_name",
        "tests_taken": ["SAT", "ACT", "IELTS", "TOEFL"],
        "scholarship_interest": true/false
    }}
}}

Otherwise, return:
{{
    "type": "message",
    "data": "Your next message to the user"
}}'''

class ProfileBuilder:
    def __init__(self):
        self.profile = {
            "academic_score": None,
            "preferred_countries": None,
            "areas_of_interest": None,
            "budget_range": None,
            "nationality": None,
            "tests_taken": None,
            "scholarship_interest": None
        }
                
    def process_conversation(self, conversation: list[str]) -> Dict:
        formatted_prompt = SYSTEM_PROMPT.format(profile=self.profile)
        
        messages = [
            {"role": "system", "content": formatted_prompt}
        ]
        
        # Add conversation history
        for i, message in enumerate(conversation):
            role = "assistant" if i % 2 == 0 else "user"
            messages.append({"role": role, "content": message})
            
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=messages
        )
        
        try:
            result = response.choices[0].message.content
            response_data = eval(result)  # Safe since we specified json_object format
            
            if response_data["type"] == "profile":
                self.profile = response_data["data"]
                return {"profile": self.profile}
            else:
                return {"question": response_data["data"]}
        except Exception as e:
            return {"question": "I'm sorry, I had trouble processing that. Could you please repeat your last response?"}

# Global dictionary to store profile builders for each session
profile_builders = {}

def generate_next_step(conversation: list[str], session_id: str) -> Dict:
    # Get or create profile builder for this session
    if session_id not in profile_builders:
        profile_builders[session_id] = ProfileBuilder()
    
    builder = profile_builders[session_id]
    return builder.process_conversation(conversation)
