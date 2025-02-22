import os
import json
from openai import OpenAI
from typing import Dict, Optional
from enum import Enum, auto

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class ProfileMetric(Enum):
    ACADEMIC_SCORE = auto()
    COUNTRIES = auto()
    INTERESTS = auto()
    BUDGET = auto()

METRIC_PROMPTS = {
    ProfileMetric.ACADEMIC_SCORE: "What is your GPA or academic test scores?",
    ProfileMetric.COUNTRIES: "Which countries are you interested in studying in?",
    ProfileMetric.INTERESTS: "What academic subjects or areas interest you most?",
    ProfileMetric.BUDGET: "What is your budget range per year for studying (minimum and maximum)?"
}

EXTRACTION_PROMPT = '''Extract the requested information from the conversation. If the information is not present or unclear, return null.
Current metric: {metric}

Guidelines for extraction:
- Academic Score: Return GPA (0-4.0 scale) or standardized test scores
- Countries: Return list of countries
- Interests: Return list of academic subjects/areas
- Budget: Return object with min and max values in USD

Return JSON in this format:
{{
    "value": extracted_value_or_null
}}

Conversation:
{conversation}
'''

class ProfileBuilder:
    def __init__(self):
        self.profile = {
            "academic_score": None,
            "preferred_countries": None,
            "areas_of_interest": None,
            "budget_range": None
        }
        self.current_metric = ProfileMetric.ACADEMIC_SCORE
        self.metrics_order = list(ProfileMetric)
        self.metric_index = 0

    def get_next_question(self) -> str:
        return METRIC_PROMPTS[self.current_metric]

    def extract_metric_value(self, conversation: list[str]) -> Optional[any]:
        formatted_prompt = EXTRACTION_PROMPT.format(
            metric=self.current_metric.name,
            conversation="\n".join(conversation)
        )
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": formatted_prompt}
            ]
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            return result.get('value')
        except Exception:
            return None

    def process_conversation(self, conversation: list[str]) -> Dict:
        # Try to extract value for current metric
        value = self.extract_metric_value(conversation)
        
        if value is not None:
            # Store the value and move to next metric
            if self.current_metric == ProfileMetric.ACADEMIC_SCORE:
                self.profile["academic_score"] = value
            elif self.current_metric == ProfileMetric.COUNTRIES:
                self.profile["preferred_countries"] = value
            elif self.current_metric == ProfileMetric.INTERESTS:
                self.profile["areas_of_interest"] = value
            elif self.current_metric == ProfileMetric.BUDGET:
                self.profile["budget_range"] = value
            
            # Move to next metric if available
            self.metric_index += 1
            if self.metric_index < len(self.metrics_order):
                self.current_metric = self.metrics_order[self.metric_index]
                return {"question": self.get_next_question()}
            else:
                return {"profile": self.profile}
        
        # If value wasn't extracted, ask a follow-up question
        return {"question": f"I still need to know {self.get_next_question()}"}

# Global dictionary to store profile builders for each session
profile_builders = {}

def generate_next_step(conversation: list[str], session_id: str) -> Dict:
    # Get or create profile builder for this session
    if session_id not in profile_builders:
        profile_builders[session_id] = ProfileBuilder()
    
    builder = profile_builders[session_id]
    return builder.process_conversation(conversation)