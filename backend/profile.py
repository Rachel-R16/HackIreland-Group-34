import os
import json
from openai import OpenAI
from typing import Dict

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

PROFILE_PROMPT = '''You are a friendly university advisor chatbot. Your task is to collect information about a student's profile through conversation. You need to gather:

1. Academic score (GPA/test scores)
2. Preferred countries for study
3. Academic interests/subjects
4. Budget range (min/max per year)

Guidelines:
- Ask ONE question at a time
- Be conversational and friendly
- Acknowledge information when provided
- Move to next missing field once current is answered
- When all info is collected, return complete profile

Return JSON in exactly ONE of these formats:
1. When information is missing:
{{
    "question": "your friendly question here"
}}

2. When all information is collected:
{{
    "profile": {{
        "academic_score": "value",
        "preferred_countries": ["country1", "country2"],
        "areas_of_interest": ["subject1", "subject2"],
        "budget_range": {{"min": number, "max": number}}
    }}
}}

Current conversation:
{conversation}'''

def generate_next_step(conversation: list[str]) -> Dict:
    formatted_prompt = PROFILE_PROMPT.format(
        conversation="\n".join(conversation) if conversation else "No messages yet."
    )
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": "Let's start building my profile"}
        ]
    )
    
    try:
        result = json.loads(response.choices[0].message.content)
        if not ('question' in result or 'profile' in result):
            return {"question": "I apologize, but I need to gather some information about you. What's your academic performance like (GPA or test scores)?"}
        return result
    except Exception as e:
        return {"question": "I apologize for the error. Could you tell me about your academic performance?"}