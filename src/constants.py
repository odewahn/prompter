VERSION = "0.7.1"

DEFAULT_DATABASE_NAME = "mydatabase.db"
DEFAULT_DB_URL = f"sqlite+aiosqlite:///{DEFAULT_DATABASE_NAME}"

# ******************************************************************************
# General constants
# ******************************************************************************
DEFAULT_CONTEXT_FN = "metadata.yaml"
PROD_WEB_URL = "http://localhost:8000/static/index.html"
DEV_WEB_URL = "http://localhost:5173"
DEFAULT_ENVIRONMENT = {"DEBUG": "false", "ENV": "prod"}

# ******************************************************************************
# Open AI constants
# ******************************************************************************
OPENAI_DEFAULT_MODEL = "gpt-4o-mini"
OPENAI_DEFAULT_TEMPERATURE = 0.1
MAX_SPEECH_LENGTH = 2000

# ******************************************************************************
# Error messages
# ******************************************************************************
MESSAGE_OPENAI_KEY_NOT_SET = """
[red]
OPENAI_API_KEY environment variable is not set. \n 
Features like COMPLETE and SPEAK will not work. \n
Exit prompter, type the following command in your shell, and then restart:\n
   export OPENAI_API_KEY=[italic]your-api-key[/italic]\n
"""
