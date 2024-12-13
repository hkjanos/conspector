from dotenv import load_dotenv
import os

def load_env():
    """Loads environment variables from a .env file."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
    else:
        raise FileNotFoundError(f".env file not found at {env_path}")
