import json
import re
import os
from openai import OpenAI

# Load API Key
OPENAI_API_KEY = os.getenv("API_KEY")

def batch_list(data, batch_size):
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

def get_llm_estimates(courses, nationality, batch_size=20):
    client = OpenAI(api_key=OPENAI_API_KEY)
    results = {}

    if not courses:
        print("Error: No courses available for estimation.")
        return {}

    for batch in batch_list(courses, batch_size):
        prompt = (
            "Estimate the annual tuition fee (in USD) based on nationality (higher for international students and lower for national students) "
            "and the general requirements for each of the following courses at their respective universities. The data does not have to be accurate; estimations are acceptable. "
            "Return the response in JSON format.\n\n"
            "{\n"
            "  \"course at university\": {\"tuition_fee\": 20000, \"academic_requirement\": 85, \"SAT_score\": 85, \"IELTS_score\": 8.5, \"ACT_score\": 37, \"TOEFL_score\": 30, \"Scholarship_availability\": \"Yes\"}\n"
            "}\n\n"
            "Courses:\n" + "\n".join([f"{course} at {university}" for university, course in batch]) +
            f"\n\n Student is from {nationality}. Base student fees on nationality."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are an education advisor."},
                          {"role": "user", "content": prompt}],
            )

            raw_response = response.choices[0].message.content

            match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if match:
                json_text = match.group(0)
                batch_results = json.loads(json_text)
                results.update(batch_results)
            else:
                print("Error: No valid JSON found in response.")
        except json.JSONDecodeError:
            print("Error: OpenAI response is not valid JSON.")
        except Exception as e:
            print(f"Error: {e}")

    return results

def filter_courses(course_estimates, relevant_courses):
    recommendations = []

    for university, course in relevant_courses:
        key = f"{course} at {university}"
        course_data = course_estimates.get(key, {})

        recommendations.append({
            "university": university,
            "course": course,
            "estimated_tuition_fee": course_data.get("tuition_fee", "N/A"),
            "required_academic_score": course_data.get("academic_requirement", "N/A"),
            "scholarship_availability": course_data.get("Scholarship availability", "Unknown"),
            "SAT_score": course_data.get("SAT score", "N/A"),
            "IELTS_score": course_data.get("IELTS score", "N/A"),
            "ACT_score": course_data.get("ACT score", "N/A"),
            "TOEFL_score": course_data.get("TOEFL score", "N/A")
        })

    return recommendations

def recommend(profile, country_university_data, university_course_data, university_accommodation_data):
    profile_type = profile["profile_type"]
    profile_data = profile["data"]
    recommendations = []

    if profile_type == "general":
        academic_score = profile_data.get("academic_score", 0)
        preferred_countries = profile_data.get("preferred_countries", [])
        areas_of_interest = profile_data.get("areas_of_interest", [])
        budget_range_for_yearly_fees = profile_data.get("budget_range_for_yearly_fees", profile_data.get("budget_range_for_yearly_fees", {"min": 0, "max": float('inf')}))
        nationality = profile_data.get("nationality", "")
        tests_taken = profile_data.get("tests_taken", {})
        scholarship_interest = profile_data.get("scholarship_interest", False)        
        accommodation_budget = profile_data.get("budget_range_for_accommodation", {"min": 0, "max": float('inf')})

        relevant_universities = [
            uni for entry in country_university_data for country, universities in entry.items() if country in preferred_countries for uni in universities
        ]
        
        relevant_courses = [
            (university, course) for entry in university_course_data for university, courses in entry.items() if university in relevant_universities for course in courses if any(area.lower() in course.lower() for area in areas_of_interest)
        ]

        recommendations.extend(relevant_courses[0:6])


    elif profile_type == "university_profile":
        course_considered = profile_data.get("course_considered", "")
        academic_score = profile_data.get("academic_score", 0)
        preferred_countries = profile_data.get("preferred_countries", [])
        nationality = profile_data.get("nationality", "")
        tests_taken = profile_data.get("tests_taken", {})
        scholarship_interest = profile_data.get("scholarship_interest", False)        
        budget_range_for_yearly_fees = profile_data.get("budget_range_for_yearly_fees", profile_data.get("budget_range_for_yearly_fees", {"min": 0, "max": float('inf')}))

        relevant_universities = [
            uni for entry in country_university_data for country, universities in entry.items() if country in preferred_countries for uni in universities if any(course_considered.lower() in course.lower() for course in university_course_data.get(uni, []))
        ]
        
        relevant_courses = [
            (university, course) for university in relevant_universities for course in university_course_data.get(university, []) if course_considered.lower() in course.lower()
        ]
        recommendations.extend(relevant_courses[0:6])

    elif profile_type == "course_profile":
        university_considered = profile_data.get("university_considered", "")
        budget_range_for_yearly_fees = profile_data.get("budget_range_for_yearly_fees", profile_data.get("budget_range_for_yearly_fees", {"min": 0, "max": float('inf')}))
        areas_of_interest = profile_data.get("areas_of_interest", [])
        academic_score = profile_data.get("academic_score", 0)
        nationality = profile_data.get("nationality", "")
        tests_taken = profile_data.get("tests_taken", {})
        scholarship_interest = profile_data.get("scholarship_interest", False)        

        relevant_courses = [
            (university_considered, course) for course in university_course_data.get(university_considered, []) if any(area.lower() in course.lower() for area in areas_of_interest)
        ]

    recommendations.extend(relevant_courses[0:6])
    return recommendations