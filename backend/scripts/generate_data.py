import openai
import json
import os, sys
import pandas as pd
import re
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("API_KEY")

def query_llm(prompt):
    """Query OpenAI's GPT model and return the response."""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)  # New API usage

    response = client.chat.completions.create(
        model="gpt-4o",  # Change to "gpt-4-turbo" for lower cost
        messages=[{"role": "system", "content": "You are a data extraction assistant."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content  # Updated response handling

def extract_vals(valid_key, text):
    lines = text.split("\n")
    result = []
    for line in lines:
        if line.lstrip().startswith(tuple(f"{i}. " for i in range(1, 21))):  # Check for "1. ", "2. ", ..., "50. "
            result.append(line.strip()[3:].lstrip(" ").strip("*"))
    print(result)
    return {valid_key: result}


def generate_data(prompts):
    dataset = []

    for prompt in prompts:
        response = query_llm(prompt)
        start = prompt.find("'") + 1
        end = prompt.rfind("'")
        valid_key = prompt[start:end]
        info_dict = extract_vals(valid_key, response)
        dataset.append(info_dict)

    return dataset


def save_to_json(dataset, path):
    """Save dataset to JSON, handling empty or corrupted files."""
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []  # Reset if corrupted
        except (json.JSONDecodeError, ValueError):  # Handle empty/corrupt file
            existing_data = []
    else:
        existing_data = []

    # Merge new data
    dataset = existing_data + dataset

    with open(path, "w") as f:
        json.dump(dataset, f, indent=4)

    print(f"Data successfully saved to {path}")



if __name__ == "__main__":

    find_university_prompts = []
    countries = ["Australia", "USA", "Canada", "Ireland", "UK"]

    for country in countries:
        find_university_prompts.append(f"List top 20 universities in '{country}'")

    dataset = generate_data(find_university_prompts)
    save_to_json(dataset, "data/country-university-dataset.json")

    find_course_prompts = []
    with open("data/country-university-dataset.json", "r", encoding="utf-8") as file:
        country_university_data = json.load(file)
    
    for country_entry in country_university_data:
        for country, universities in country_entry.items():
            for university in universities:
                find_course_prompts.append(f"List all undergraduate courses probably offered at '{university}' in a numbered format. Only provide the list, without any extra text or explanation.")

    dataset = generate_data(find_course_prompts)
    save_to_json(dataset, "data/university-course-dataset.json")

    print("Dataset saved successfully!")
