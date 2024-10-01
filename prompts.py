import random

def get_prompt():
    base_prompt = (
        "You are an AI designed to analyze podcasts and provide timecodes. Unzip the included file and analyze the podcast. "
        "If the file is too large, please analyze it by segments."
        "Analyze this podcast and provide timecodes for the best moments. The ranking is based on this order: quality, entertainment, learning, length, and uniqueness."
        "There should be clips based on the length of the podcast with the max length of 3/10 of the podcast length and the min length of 1/10 of the podcast length." 
        # "For each best moment segment, provide a brief description of the topic and the main points discussed."
        "The best moments should be unique and not overlapping. They should also be interesting and engaging. "
        "Each moment should not include intro music or outro music. Try not to end the segment on a cliffhanger or mid sentence. "
        "Do not include the first 20 seconds and last 20 seconds of the podcast as part of the analysis."
        "Format the response as a JSON array of objects, each with 'start' and 'end' keys in seconds. "

    )
    
    # List of additional instructions or variations
    variations = [
        "Focus on humorous moments.",
        "Identify key insights or learnings.",
        "Look for emotional or inspiring segments.",
        "Find controversial or debate-worthy discussions.",
        "Highlight any surprising facts or revelations.",
    ]
    
    # Randomly choose whether to add a variation
    if random.choice([True, False]):
        selected_variation = random.choice(variations)
        prompt = f"{base_prompt} {selected_variation}"
    else:
        prompt = base_prompt
    
    return prompt

# Test the function
if __name__ == "__main__":
    for _ in range(5):
        print(get_prompt())
        print("---")