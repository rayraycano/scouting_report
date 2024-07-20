import cv2
import argparse
from openai import OpenAI
from os import path
import base64

user_msg = """
the following images are of a basketball play. 
how many images are there? 
what is happening in the play?
is there a name for this type of play? 
does anyone score? 
"""


def create_image_content(image: str, maxdim, detail_threshold):
    # detail = "low" if maxdim < detail_threshold else "high"
    return {
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{image}"},
    }


MAX_DIM = 1024


def process_image(image: cv2.typing.MatLike) -> str:
    base64_image = base64.b64encode(image).decode("utf-8")
    return base64_image


def analyze_stills(filename: str):
    filepath = path.join("data", "video", "stills", filename)
    im = cv2.imread(filepath)
    base64_image = process_image(im)
    client = OpenAI()
    result = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": "you are analyzing basketball film. the film is delivered as a series of images. be precise and concise with your answers",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_msg,
                    },
                    create_image_content(base64_image, None, None),
                ],
            },
        ],
    )
    print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    analyze_stills(args.filename)
