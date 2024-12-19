import os
import re
from dotenv import load_dotenv


def load_env():
    """Loads environment variables from a .env file."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    print(f'Loading environment variables from {env_path}')
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)  # Load the .env file
    else:
        raise FileNotFoundError(f".env file not found at {env_path}")


def save_env(env_variables):
    """Saves the environment variables to the .env file while preserving formatting, quotes, and comments."""
    # Path to the .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')

    # Read the existing .env file to preserve formatting and comments
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as file:
            lines = file.readlines()

    updated_lines = []
    keys_to_update = set(env_variables.keys())
    seen_keys = set()

    # Regex to match variable assignments
    pattern = re.compile(r'^(\s*[\w]+)(\s*=\s*)(["\']?.*?["\']?)(\s*#.*)?$')

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith('#'):  # Preserve blank lines and comments
            updated_lines.append(line)
            continue

        match = pattern.match(line)
        if match:
            key = match.group(1).strip()
            if key in keys_to_update:
                # Update the value while preserving formatting and quotes
                new_value = env_variables[key]
                if match.group(3).startswith('"') or match.group(3).startswith("'"):
                    new_value = f'"{new_value}"'  # Add quotes if the original value was quoted
                updated_line = f"{match.group(1)}{match.group(2)}{new_value}{match.group(4) or ''}\n"
                updated_lines.append(updated_line)
                seen_keys.add(key)
                print(f"Updating: {key} with \"{new_value}\"")
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

    # Add new variables that were not in the original file
    for key in keys_to_update - seen_keys:
        new_value = env_variables[key]
        if isinstance(new_value, str) and not new_value.isnumeric():
            new_value = f'"{new_value}"'  # Add quotes for new string values
        updated_lines.append(f"{key} = {new_value} # Added by save_env\n")
        print(f"Adding: {key} with \"{new_value}\"")

    # Save the updated lines back to the .env file
    with open(env_path, 'w') as file:
        file.writelines(updated_lines)

    print(f'Environment variables saved to {env_path}')

    # Reload the environment variables after saving
    load_env()

    # Update os.environ to reflect the changes
    for key, value in env_variables.items():
        os.environ[key] = value
        print(f"os.environ updated: {key}={value}")

    # Verify changes
    for key in env_variables.keys():
        reloaded_value = os.getenv(key)
        print(f"Verified {key}: {reloaded_value}")
