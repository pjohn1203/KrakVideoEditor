import os
import requests
import subprocess
import json
import time
import base64
import re
import datetime
from prompts import get_prompt
from dotenv import load_dotenv



load_dotenv()
# Configuration for the Gemini API
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?'
API_KEY = os.getenv('GEMINI_API_KEY')
 
# Configuration for ChatGPT
CHATGPT_API_KEY = os.getenv('CHATGPT_API_KEY')


# Function to send the podcast audio file to ChatGPT API for analysis
def analyze_podcast_chatgpt(audio_file_path):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHATGPT_API_KEY}'  # Use ChatGPT API key
    }
    
    with open(audio_file_path, 'rb') as audio_file:
        audio_content = audio_file.read()

    prompt = get_prompt()
    audio_content_b64 = base64.b64encode(audio_content).decode('utf-8')
    
    data = {
        "model": "gpt-4o-mini",  # Specify the model to use
        "prompt": f"{prompt}\n{audio_content_b64}",  # Combine prompt and audio content
        "temperature": 0.7,  # Example temperature value
        "max_tokens": 150,  # Example max tokens value
        "top_p": 1.0,  # Example top_p value
        "frequency_penalty": 0.0,  # Example frequency_penalty value
        "presence_penalty": 0.0  # Example presence_penalty value
    }
    
    print("Sending request to ChatGPT API...")
    response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=data)
    print(f"Response status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    
    if response.status_code == 200:
        response_json = response.json()
        print(f"Full API response: {json.dumps(response_json, indent=2)}")
        return response_json
    else:
        print(f"Error: {response.status_code}")
        print(f"Error response: {response.text}")
        return None

# Function to send the podcast audio file to Gemini Flash API for analysis
def analyze_podcast(audio_file_path):
    headers = {
        'Content-Type': 'application/json',
    }
    
    with open(audio_file_path, 'rb') as audio_file:
        audio_content = audio_file.read()

    data = {
        "contents": [{
            "parts": [{
                "text": get_prompt()
            }, {
                "inline_data": {
                    "mime_type": "audio/mpeg",
                    "data": base64.b64encode(audio_content).decode('utf-8')
                }
            }]
        }]
    }
    
    params = {
        'key': API_KEY
    }
    print("Sending request to Gemini API...")
    response = requests.post(GEMINI_API_URL, headers=headers, json=data, params=params)
    
    print(f"Response status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    
    if response.status_code == 200:
        response_json = response.json()
        print(f"Full API response: {json.dumps(response_json, indent=2)}")
        return response_json
    else:
        print(f"Error: {response.status_code}")
        print(f"Error response: {response.text}")
        return None

# Function to extract timecodes from the API response
def extract_timecodes(api_response):
    if not api_response or 'candidates' not in api_response:
        return []

    text_content = api_response['candidates'][0]['content']['parts'][0]['text']
    
    # Try to find a JSON array in the text
    json_match = re.search(r'\[.*\]', text_content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            print("Found JSON-like structure, but couldn't parse it.")
    
    # If no JSON found, try to extract time ranges
    time_ranges = re.findall(r'(\d+:\d+:\d+)\s*-\s*(\d+:\d+:\d+)', text_content)
    if time_ranges:
        return [{'start': time_to_seconds(start), 'end': time_to_seconds(end)} 
                for start, end in time_ranges]
    
    print("Couldn't extract timecodes from the response.")
    return []

# Helper function to convert time string to seconds
def time_to_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

# Function to clip the audio using FFMPEG
def clip_audio(input_file, output_file, start_time, end_time):
    command = [
        'ffmpeg', '-i', input_file,
        '-ss', str(start_time),
        '-to', str(end_time),
        '-c', 'copy', output_file
    ]
    subprocess.run(command)

# Main function to analyze and create audio clips
def process_podcast(audio_file_path):
    # Analyze the podcast using Gemini Flash API
    print(API_KEY)
    print(CHATGPT_API_KEY)
    analysis_result = analyze_podcast(audio_file_path)
    
    if not analysis_result:
        print("Analysis failed.")
        return

    best_moments = extract_timecodes(analysis_result)
    
    if not best_moments:
        print("No significant moments found.")
        print("API response structure:")
        print(json.dumps(analysis_result, indent=2))
        return
    
    # Clip the audio for each timecode
    # Get today's date
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # Extract the base filename without extension
    base_filename = os.path.splitext(os.path.basename(audio_file_path))[0]
    
    for idx, moment in enumerate(best_moments):
        start_time = moment['start']
        end_time = moment['end']
        output_file = f"{today}_{base_filename}_clip_{idx+1}.mp3"
        print(f"Clipping from {start_time} to {end_time}, output file: {output_file}")
        
        # Clip the audio
        clip_audio(audio_file_path, output_file, start_time, end_time)

        # Delay to avoid overloading the system (optional)
        time.sleep(2)

# Example usage
if __name__ == "__main__":
    podcast_file = 'Mark Rober & MrBeast are Trying to Save the Ocean One Pound of Trash at a Time.mp3'
    print(podcast_file)
    process_podcast(podcast_file)
