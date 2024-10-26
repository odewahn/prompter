VERSION = "0.6.0"
DEFAULT_DB_URL = "sqlite+aiosqlite:///mydatabase.db"

# ******************************************************************************
# Error messages
# ******************************************************************************
OPENAI_KEY_NOT_SET = """
[red]
OPENAI_API_KEY environment variable is not set. \n 
Features like COMPLETE and SPEAK will not work. \n
Exit prompter, type the following command in your shell, and then restart:\n
   export OPENAI_API_KEY=[italic]your-api-key[/italic]\n
"""
