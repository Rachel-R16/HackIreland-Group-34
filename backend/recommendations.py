import json
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

    for batch in batch_list(courses, batch_size):
        prompt = (
            "Estimate the annual tuition fee (in USD) based on nationality (higher for international students and lower for national students) "
            "and the general requirements for each of the following courses at their respective universities. The data does not have to be accurate; estimations are acceptable. "
            "Return the response in JSON format.\n\n"
            "{\n"
            "  \"course at university\": {\"tuition_fee\": 20000, \"academic_requirement\": 85, \"SAT score\": 85, \"IELTS score\": 8.5, \"ACT score\": 37, \"TOEFL score\": 30, \"Scholarship availability\": \"Yes\"},\n"
            "}\n\n"
            "Courses:\n" + "\n".join([f"{course} at {university}" for university, course in batch]) +
            f"\n\n Student is from {nationality}. Base student fees on nationality."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are an education advisor."},
                          {"role": "user", "content": prompt}],
            )

            raw_response = response.choices[0].message.content
            batch_results = json.loads(raw_response)  # Ensure valid JSON
            results.update(batch_results)

        except json.JSONDecodeError:
            print("Error: OpenAI response is not valid JSON.")
            continue
        except Exception as e:
            print(f"Error: {e}")
            continue

    return results

def filter_courses(course_estimates, academic_score, relevant_courses, budget_range_for_yearly_fees, tests_taken, scholarship_interest):
    recommendations=[]
    for university, course in relevant_courses:
        key = f"{course} at {university}"
        course_data = course_estimates.get(key, {})
        tuition_fee = course_data.get("tuition_fee", 0)
        required_score = course_data.get("academic_requirement", 0)
        sat_score = course_data.get("SAT score", 0)
        ielts_score = course_data.get("IELTS score", 0)
        act_score = course_data.get("ACT score", 0)
        toefl_score = course_data.get("TOEFL score", 0)
        scholarship_availability = course_data.get("Scholarship availability", "No")

        if not (budget_range_for_yearly_fees["min"] <= tuition_fee <= budget_range_for_yearly_fees["max"] and academic_score >= required_score):
            continue

        if tests_taken:
            if not (
                ("SAT" in tests_taken and tests_taken["SAT"] >= sat_score) or
                ("IELTS" in tests_taken and tests_taken["IELTS"] >= ielts_score) or
                ("ACT" in tests_taken and tests_taken["ACT"] >= act_score) or
                ("TOEFL" in tests_taken and tests_taken["TOEFL"] >= toefl_score)
            ):
                continue

        if scholarship_interest and scholarship_availability.lower() != "yes":
            continue

        recommendations.append({
            "university": university,
            "course": course,
            "estimated_tuition_fee": tuition_fee,
            "required_academic_score": required_score,
            "scholarship_availability": scholarship_availability,
            "sat_score": sat_score,
            "act_score": act_score,
            "toefl_score": toefl_score,
            "ielts_score": ielts_score
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

        course_estimates = get_llm_estimates(relevant_courses, nationality)
        recommendations.extend(filter_courses(course_estimates, academic_score, relevant_courses, budget_range_for_yearly_fees, tests_taken, scholarship_interest))

        for recommendation in recommendations:
            for entry in university_accommodation_data:
                if recommendation["university"] in entry:
                    accommodations = entry[recommendation["university"]]
                    matching_accommodations = [
                        (name, data) for accommodation in accommodations for name, data in accommodation.items() if accommodation_budget["min"] <= data["rent"] <= accommodation_budget["max"]
                    ]
                    if matching_accommodations:
                        best_accommodation = min(matching_accommodations, key=lambda x: x[1]["rent"])
                        recommendation["accommodation_name"] = best_accommodation[0]
                        recommendation["accommodation_cost"] = best_accommodation[1]["rent"]
                        recommendation["accommodation_link"] = best_accommodation[1]["link"]
    
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

        course_estimates = get_llm_estimates(relevant_courses, nationality)
        recommendations.extend(filter_courses(course_estimates, academic_score, relevant_courses, budget_range_for_yearly_fees, tests_taken, scholarship_interest))


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

        course_estimates = get_llm_estimates(relevant_courses, nationality)
        recommendations.extend(filter_courses(course_estimates, academic_score, relevant_courses, budget_range_for_yearly_fees, tests_taken, scholarship_interest))



    elif profile_type == "accommodation_profile":
        accommodation_budget = profile_data.get("budget_range_for_accommodation", {"min": 0, "max": float('inf')})
        university_considered = profile_data.get("university_considered", "")

        relevant_accommodations = []
        for entry in university_accommodation_data:
            if university_considered in entry:
                accommodations = entry[university_considered]
                for accommodation in accommodations:
                    for name, data in accommodation.items():
                        if accommodation_budget["min"] <= data["rent"] <= accommodation_budget["max"]:
                            relevant_accommodations.append({
                                "accommodation_name": name,
                                "accommodation_cost": data["rent"],
                                "accommodation_link": data["link"]
                            })

        recommendations.extend(relevant_accommodations)
    

        

    return recommendations
