from pathlib import Path
from openai import OpenAI
import os
import yaml
import warnings
import sys

sys.path.append("../../")
from completions_common import load_config

ENV_FILENAME = ".prompter"


config = load_config()

client = OpenAI(api_key=config["openai"])

warnings.filterwarnings("ignore", category=DeprecationWarning)


TXT = """
Today, we're going to talk about O'Reilly's AI Use Policy for Employees. 
This policy is designed to help us harness the power of generative AI technologies while 
mitigating risks like data security vulnerabilities, privacy concerns, and intellectual 
property issues.
"""

speech_file_path = "speech.mp3"
response = client.audio.speech.create(model="tts-1", voice="alloy", input=TXT)

response.stream_to_file(speech_file_path)
