import json
import os
from openai import OpenAI
import requests

# Load API Key
OPENAI_API_KEY = os.getenv("API_KEY")

def batch_list(data, batch_size):
    """Splits a list into smaller batches of given size."""
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

def get_llm_estimates(courses, batch_size=20):
    """Fetch tuition fees and academic requirements in smaller batches to avoid token limits."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    results = {}

    for batch in batch_list(courses, batch_size):
        prompt = (
            "Estimate the annual tuition fee (in USD) and the general academic score requirement "
            "for each of the following courses at their respective universities. The data does not have to be accurate, estimations are alright. Return the response in JSON format.\n\n"
            "{\n"
            "  \"course at university\": {\"tuition_fee\": 20000, \"academic_requirement\": 85},\n"
            "  \"another course at another university\": {\"tuition_fee\": 25000, \"academic_requirement\": 90}\n"
            "}\n\n"
            "Courses:\n" + "\n".join([f"{course} at {university}" for university, course in batch])
        )

        print("Sending Prompt to OpenAI:", prompt)  # Debugging line
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are an education advisor."},
                          {"role": "user", "content": prompt}],
            )

            raw_response = response.choices[0].message.content
            print("OpenAI Raw Response:", raw_response)  # Debugging line

            batch_results = json.loads(raw_response)  # Ensure valid JSON
            results.update(batch_results)
        
        except json.JSONDecodeError:
            print("Error: OpenAI response is not valid JSON:", raw_response)  # Debugging line
            continue
        except Exception as e:
            print(f"Error: {e}")
            continue

    return results

def recommend_courses(profile, country_university_data, university_course_data):
    client = OpenAI(api_key=OPENAI_API_KEY)

    preferred_countries = profile["data"]["preferred_countries"]
    areas_of_interest = profile["data"]["areas_of_interest"]
    academic_score = profile["data"]["academic_score"]
    budget_range = profile["data"]["budget_range"]
    print("before 1")
    
    # Step 1: Extract universities from preferred countries
    potential_universities = []
    for entry in country_university_data:
        for country, universities in entry.items():
            if country in preferred_countries:
                potential_universities.extend(universities)
    print("after 1")
    
    # Step 2: Gather all courses from those universities
    potential_courses = []
    for entry in university_course_data:
        for university, courses in entry.items():
            if university in potential_universities:
                for course in courses:
                    potential_courses.append((university, course))
    print("After 2")
    
    # Step 3: Filter courses based on keyword matching
    keywords = {word.lower() for word in areas_of_interest}  # Convert to lowercase set for fast lookup
    relevant_courses = []
    
    for university, course in potential_courses:
        course_lower = course.lower()
        if any(keyword in course_lower for keyword in keywords):
            relevant_courses.append((university, course))
    print("after 3")
    
    # Step 4: Estimate tuition fees and academic requirements in batches
    course_estimates = get_llm_estimates(relevant_courses, batch_size=20)
    print("after 4")
    
    # Step 5: Filter based on budget and academic score
    final_recommendations = []
    for university, course in relevant_courses:
        key = f"{course} at {university}"
        if key in course_estimates:
            tuition_fee = course_estimates[key].get("tuition_fee", 0)
            academic_requirement = course_estimates[key].get("academic_requirement", 0)
        else:
            print(f"Missing estimate for: {key}")  # Debugging line
            tuition_fee = 0
            academic_requirement = 0
        
        print(tuition_fee)
        print(academic_requirement)
        
        if budget_range["min"] <= tuition_fee <= budget_range["max"] and academic_score >= academic_requirement:
            final_recommendations.append({
                "university": university,
                "course": course,
                "estimated_tuition_fee": tuition_fee,
                "required_academic_score": academic_requirement
            })
    print("after 5")
    return final_recommendations
