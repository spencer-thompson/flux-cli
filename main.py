"""
This is just a cli to generate images using the API
"""

import argparse
import base64
import os
import time

import requests


def get_result(querystring, model: str):
    """
    Get the image after it has finished generating.
    """
    spinner = ["-", "\\", "|", "/"]
    url = "https://api.bfl.ml/v1/get_result"
    idx = 0
    while True:
        r = requests.get(url, params=querystring)
        time.sleep(0.05)
        if r.json()["status"] == "Ready":
            break

        else:
            idx = (idx + 1) % len(spinner)
            print(f"\rUsing {model} | Generating [ {spinner[idx]} ]", end="", flush=True)

    print(" | Downloading...", end="")
    response = requests.get(r.json()["result"]["sample"])
    if response.status_code == 200:
        with open("/home/sthom/pics/flux-gen.png", "wb") as f:
            f.write(response.content)

    print(" | Done!")


def aspect_ratio():
    pass


def main():
    parser = argparse.ArgumentParser(description="A simple script to generate images with flux.")

    parser.add_argument(
        "--model",
        "-m",
        choices=["dev", "d", "pro", "p", "ultra", "u", "fill", "f", "canny", "c"],
        default="ultra",
        help="Choose a model.",
    )
    parser.add_argument("-u", "--upsampling", action="store_true", help="Prompt AI Upsampling")
    parser.add_argument("-H", "--height", type=int, default=1440, help="Height of Image")
    parser.add_argument("-W", "--width", type=int, default=1440, help="Width of Image")
    parser.add_argument("-S", "--safety", type=int, default=6, help="Safety Tolerance 1 to 6")
    parser.add_argument("-i", "--image", type=str, default="", help="Image to use")
    parser.add_argument("-s", "--steps", type=int, default=40, help="Number of steps 1-50")
    parser.add_argument("-g", "--guidance", type=float, default=2.5, help="Guidance to prompt 1.5 to 5")
    parser.add_argument("-a", "--aspect", type=str, default="2:1", help="Aspect Ratio")
    parser.add_argument("-r", "--raw", action="store_true", help="Raw Mode [Ultra]")
    parser.add_argument("prompt", type=str, help="The image to generate")

    args, other = parser.parse_known_args()

    payload = {
        "prompt": args.prompt + " ".join(other),
        "prompt_upsampling": args.upsampling,
        "safety_tolerance": args.safety,
        "output_format": "png",
    }

    if args.image:
        with open(args.image, "rb") as f:
            image_data = f.read()

        # Encode the binary data to base64
        base64_encoded = base64.b64encode(image_data)

        # Convert the base64 bytes to a string
        base64_string = base64_encoded.decode("utf-8")

        payload["image_prompt"] = base64_string

    if args.model.startswith("u"):
        model = "Ultra"
    elif args.model.startswith("p"):
        model = "Pro"
    elif args.model.startswith("d"):
        model = "Dev"

    print(f"Using {model} | ", end="")
    if args.model.startswith("u"):  # Ultra
        url = "https://api.bfl.ml/v1/flux-pro-1.1-ultra"

        payload["aspect_ratio"] = args.aspect
        payload["image_prompt_strength"] = 0.2
        if args.raw:
            payload["raw"] = False

    if args.model.startswith(("d", "p")):  # Dev and Pro
        if args.model.startswith("p"):
            url = "https://api.bfl.ml/v1/flux-pro"
        if args.model.startswith("d"):
            url = "https://api.bfl.ml/v1/flux-dev"

        payload["width"] = args.width
        payload["height"] = args.height
        payload["steps"] = args.steps
        payload["guidance"] = args.guidance

    headers = {"Content-Type": "application/json", "X-Key": os.getenv("BFL_API_KEY")}

    r = requests.post(url, json=payload, headers=headers)

    querystring = {"id": r.json()["id"]}
    get_result(querystring, model)


if __name__ == "__main__":
    main()
