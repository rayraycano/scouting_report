import urllib3
import os

model_id = "232znyv3"
# Read secrets from environment variables
baseten_api_key = os.environ["BASETEN_API_KEY"]

resp = urllib3.request(
    "POST",
    f"https://model-{model_id}.api.baseten.co/production/predict",
    headers={"Authorization": f"Api-Key {baseten_api_key}"},
    json={
        "messages": [
            {
                "role": "user",
                "content": "what color would make the best for a summer t shirt",
            },
        ],
    },
)

print(resp.read())
# print(resp.json(json))
import requests

resp = requests.post(
    "https://model-232znyv3.api.baseten.co/production/predict",
    headers={"Authorization": f"Api-Key {baseten_api_key}"},
    json={
        "messages": [
            {"role": "user", "content": "What is your favourite condiment?"},
            {
                "role": "assistant",
                "content": "Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!",
            },
            {"role": "user", "content": "Do you have mayonnaise recipes?"},
        ],
        "max_tokens": 512,
    },
)

print(resp.ok)
