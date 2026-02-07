import requests
import json

AI_SYSTEM_PROMPT = """
You are Barack Obama, the 44th President of the United States. Respond in your distinct speaking style, 
using phrases like "Let me be clear" and "folks." Maintain a thoughtful, measured tone while being 
inspirational and optimistic. Draw on your experiences as President when relevant, and reference Michelle, 
Malia, and Sasha naturally. Avoid policy specifics from after your presidency ended in January 2017.
"""
# response = requests.post(
#     "http://192.168.50.38:11434/api/generate",
#     json={
#         "model": "gemma3:1b",
#         "prompt": "Tell me a joke",
#         "system": AI_SYSTEM_PROMPT,
#     },
#     stream=True,
#     timeout=10,
# )


def generate_with_progress(prompt):
    response = requests.post(
        "http://192.168.50.38:11434/api/generate",
        json={
            "model": "gemma3:1b",
            "prompt": prompt,
            "system": AI_SYSTEM_PROMPT,
        },
        stream=True,
    )

    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode("utf-8"))
            if "response" in chunk:
                # Print immediately without newline for smooth output
                print(chunk["response"], end="", flush=True)
    print()  # Final newline


generate_with_progress(
    "briefly explain to me what the difference between a pen and pencil is"
)
