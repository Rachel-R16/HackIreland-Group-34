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
            "  \"course at university\": {\"tuition_fee\": 20000, \"academic_requirement\": 85, \"SAT score\": 85, \"IELTS score\": 8.5, \"ACT score\": 37, \"TOEFL score\": 30, \"Scholarship availability\": \"Yes\"}\n"
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
            print("OpenAI Raw Response:", raw_response)  # Debugging line

            # Extract JSON portion using regex to find the first `{` and the last `}`
            match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if match:
                json_text = match.group(0)  # Extract matched JSON portion
                batch_results = json.loads(json_text)  # Convert to dictionary
                results.update(batch_results)
            else:
                print("Error: No valid JSON found in response.")

        except json.JSONDecodeError:
            print("Error: OpenAI response is not valid JSON.")
        except Exception as e:
            print(f"Error: {e}")

    return results

def filter_courses(course_estimates, academic_score, relevant_courses, budget_range_for_yearly_fees, tests_taken, scholarship_interest):
    recommendations = []
    
    # Handle None values in budget range
    min_budget = budget_range_for_yearly_fees.get("min", 0)
    max_budget = budget_range_for_yearly_fees.get("max", float('inf'))
    
    # Convert None values to appropriate defaults
    min_budget = 0 if min_budget is None else min_budget
    max_budget = float('inf') if max_budget is None else max_budget
    
    for university, course in relevant_courses:
        key = f"{course} at {university}"
        course_data = course_estimates.get(key, {})

        tuition_fee = course_data.get("tuition_fee", float('inf'))
        required_score = course_data.get("academic_requirement", 0)
        scholarship_availability = course_data.get("Scholarship availability", "No").lower()

        # Ensure academic score is integer or set to 0 if None
        academic_score = 0 if academic_score is None else int(str(academic_score).replace("%", ""))

        # Budget & academic score filtering
        if not (min_budget <= tuition_fee <= max_budget and academic_score >= required_score):
            continue

        # Test score filtering
        test_passed = False
        for test, score in tests_taken.items():
            required_test_score = course_data.get(f"{test} score", 0)
            if required_test_score and score >= required_test_score:
                test_passed = True
                break

        if tests_taken and not test_passed:
            continue

        # Scholarship filtering
        if scholarship_interest and scholarship_availability != "yes":
            continue

        recommendations.append({
            "university": university,
            "course": course,
            "estimated_tuition_fee": tuition_fee,
            "required_academic_score": required_score,
            "scholarship_availability": scholarship_availability,
            "SAT_score": course_data.get("SAT score", 0),
            "IELTS_score": course_data.get("IELTS score", 0),
            "ACT_score": course_data.get("ACT score", 0),
            "TOEFL_score": course_data.get("TOEFL score", 0)
        })

    return recommendations

def recommend(profile, country_university_data, university_course_data, university_accommodation_data):
    profile_type = profile["profile_type"]
    profile_data = profile["data"]["profile"] if "profile" in profile["data"] else profile["data"]
    recommendations = []

    def get_university_recommendations(data):
        uni_recommendations = []
        course_considered = data.get("course_considered", "")
        academic_score = data.get("academic_score", "0")
        preferred_countries = data.get("preferred_countries", [])
        nationality = data.get("nationality", "")
        tests_taken = data.get("tests_taken", {})
        scholarship_interest = data.get("scholarship_interest", False)
        budget_range_for_yearly_fees = data.get("budget_range_for_yearly_fees", {"min": 0, "max": float('inf')})

        # Convert academic score to int if it's not None
        if academic_score is not None:
            academic_score = int(str(academic_score).replace("%", ""))
        else:
            academic_score = 0

        relevant_universities = set()

        for entry in country_university_data:
            for country, universities in entry.items():
                if not preferred_countries or country in preferred_countries:
                    for uni in universities:
                        for items in university_course_data:
                            for course in items.get(uni, []):
                                if not course_considered or course_considered.lower() in course.lower():
                                    relevant_universities.add(uni)
                                    break

        relevant_courses = []

        for university in relevant_universities:
            for vals in university_course_data:
                courses = vals.get(university, [])
                for course in courses:
                    if not course_considered or course_considered.lower() in course.lower():
                        relevant_courses.append((university, course))

        if not relevant_courses:
            print("No relevant courses found based on input preferences.")
            return []

        course_estimates = get_llm_estimates(relevant_courses, nationality or "International")

        if not course_estimates:
            print("No course estimates received from LLM.")
            return []

        uni_recommendations.extend(filter_courses(course_estimates, academic_score, relevant_courses, budget_range_for_yearly_fees, tests_taken, scholarship_interest))
        return uni_recommendations

    def get_course_recommendations(data):
        course_recommendations = []
        university = data.get("university_considered", "")
        budget_range = data.get("budget_range_for_yearly_fees", {"min": 0, "max": float('inf')})
        areas_of_interest = data.get("areas_of_interest", [])
        academic_score = data.get("academic_score", "0")
        nationality = data.get("nationality", "")
        tests_taken = data.get("tests_taken", {})
        scholarship_interest = data.get("scholarship_interest", False)

        # Convert academic score to int if it's not None
        if academic_score is not None:
            academic_score = int(str(academic_score).replace("%", ""))
        else:
            academic_score = 0

        relevant_courses = []
        
        for vals in university_course_data:
            if not university or university in vals:
                courses = vals.get(university, []) if university else [course for uni in vals.values() for course in uni]
                for course in courses:
                    if not areas_of_interest or any(area.lower() in course.lower() for area in areas_of_interest):
                        relevant_courses.append((university if university else next(iter(vals.keys())), course))

        if not relevant_courses:
            print("No relevant courses found based on input preferences.")
            return []

        course_estimates = get_llm_estimates(relevant_courses, nationality or "International")

        if not course_estimates:
            print("No course estimates received from LLM.")
            return []

        course_recommendations.extend(filter_courses(course_estimates, academic_score, relevant_courses, budget_range, tests_taken, scholarship_interest))
        return course_recommendations

    def get_accommodation_recommendations(data):
        accommodation_recommendations = []
        accommodation_budget = data.get("budget_range_for_accommodation", {"min": 0, "max": float('inf')})
        if accommodation_budget.get("min") is None:
            accommodation_budget["min"] = 0
        if accommodation_budget.get("max") is None:
            accommodation_budget["max"] = float('inf')
            
        university_considered = data.get("university_considered", "")

        for entry in university_accommodation_data:
            if not university_considered or university_considered in entry:
                accommodations = entry[next(iter(entry.keys()))]
                for accommodation in accommodations:
                    for name, data in accommodation.items():
                        if accommodation_budget["min"] <= data["rent"] <= accommodation_budget["max"]:
                            accommodation_recommendations.append({
                                "accommodation_name": name,
                                "accommodation_cost": data["rent"],
                                "accommodation_link": data["link"]
                            })

        return accommodation_recommendations

    # Handle each profile type
    if profile_type == "general":
        # For general profile, get recommendations from all three types
        recommendations.extend(get_university_recommendations(profile_data))
        recommendations.extend(get_course_recommendations(profile_data))
        recommendations.extend(get_accommodation_recommendations(profile_data))
    elif profile_type == "university_profile":
        recommendations.extend(get_university_recommendations(profile_data))
    elif profile_type == "course_profile":
        recommendations.extend(get_course_recommendations(profile_data))
    elif profile_type == "accommodation_profile":
        recommendations.extend(get_accommodation_recommendations(profile_data))

    return recommendations
