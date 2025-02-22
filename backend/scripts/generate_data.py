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

def extract_universities(country, text):
    lines = text.split("\n")
    result = []
    for line in lines:
        if line.lstrip().startswith(tuple(f"{i}. " for i in range(1, 51))):  # Check for "1. ", "2. ", ..., "50. "
            result.append(line.strip()[3:].lstrip(" ").strip("*"))
    print(result)
    return {country: result}

def generate_data(prompts):
    dataset = []

    for prompt in prompts:
        response = query_llm(prompt)
        start = prompt.find("'") + 1
        end = prompt.rfind("'")
        country = prompt[start:end]
        country_university_dict = extract_universities(country, response)
        dataset.append(country_university_dict)

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

    prompts = []
    countries = [ "Australia", "USA", "Canada", "Ireland", "UK"]

    for i in countries:
        prompts.append(f"List top 50 universities in '{i}'. Use only the English translation of the university names.")

    dataset = generate_data(prompts)
    os.makedirs("data", exist_ok=True)  # Ensure 'data/' folder exists

    # Save dataset in JSON & CSV format
    save_to_json(dataset, "data/dataset.json")

    print("Dataset saved successfully!")
