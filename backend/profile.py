import os
import openai
from typing import Dict, Optional
from dotenv import load_dotenv
import json

load_dotenv()
OPENAI_API_KEY = os.getenv("API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

PROFILE_TEMPLATES = {
    "general": {
        "academic_score": None,
        "preferred_countries": [],
        "areas_of_interest": [],
        "budget_range_for_yearly_fees": {"min": None, "max": None},
        "nationality": None,
        "tests_taken": {},
        "scholarship_interest": None,
        "budget_range_for_weekly_accommodation":{"min": None, "max": None}
    },
    "university_profile": {
        "course_considered": None,
        "academic_score": None,
        "preferred_countries": [],
        "nationality": None,
        "tests_taken": {},
        "scholarship_interest": None,
        "budget_range_for_yearly_fees": {"min": None, "max": None},
    },
    "course_profile": {
        "university_considered": None,
        "budget_range_for_yearly_fees": {"min": None, "max": None},
        "areas_of_interest": [],
        "academic_score": None,
        "nationality": None,
        "tests_taken": {},
        "scholarship_interest": True
    },
    "accommodation_profile": {
        "budget_range_for_accommodation": {"min": None, "max": None},
        "university_considered": None
    }
}


class ProfileBuilder:
    def __init__(self, profile_type="general"):
        if profile_type not in PROFILE_TEMPLATES:
            raise ValueError(f"Invalid profile type: {profile_type}")

        self.profile_type = profile_type
        self.profile = PROFILE_TEMPLATES[profile_type]

        
    def process_conversation(self, conversation: list[str]) -> Dict:
        system_prompt = f'''You are a friendly educational advisor helping students plan their studies abroad. Have a natural conversation to gather the following information based on profile type: {self.profile_type}.

        Required information to collect: {json.dumps(self.profile, indent=4)}

        Guidelines:
        1. Be conversational and friendly.
        2. Ask follow-up questions when answers are unclear.
        3. Once you have all the information, return it as JSON.
        4. Don't ask for all information at once - have a natural conversation.
        5. Test scores refers to ACT, SAT, IELTS and TOEFL while academic score refers to a percentage or GPA value from high school

        Current profile state:
        {json.dumps(self.profile, indent=4)}

        Return ONLY JSON when you have all information. Format:
        {{
            "type": "profile",
            "data": {json.dumps(self.profile, indent=4)}
        }}

        Otherwise, return:
        {{
            "type": "message",
            "data": "Your next message to the user"
        }}'''

        messages = [{"role": "system", "content": system_prompt}]

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
            response_data = json.loads(result)
            if response_data["type"] == "profile":
                self.profile = response_data["data"]
                return {"profile": self.profile}
            else:
                return {"question": response_data["data"]}
        except Exception as e:
            return {"question": "I'm sorry, I had trouble processing that. Could you please repeat your last response?"}


# Global dictionary to store profile builders for each session
profile_builders = {}

def generate_next_step(conversation: list[str], session_id: str, profile_type="general") -> Dict:
    """Manages the conversation and determines the next step based on profile type."""
    if session_id not in profile_builders:
        profile_builders[session_id] = ProfileBuilder(profile_type)

    builder = profile_builders[session_id]
    return builder.process_conversation(conversation)
