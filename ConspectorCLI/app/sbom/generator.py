import subprocess
import os
from flask import current_app as app
from datetime import datetime
import sys

def generate_sbom(repo_url, branch):
    try:
        # Ensure the application context is set
        with app.app_context():
            # Clean the repo URL by removing '/tree/<branch>' if present
            clean_repo_url = repo_url.split("/tree")[0]

            # Define paths and command components
            sbom_tool_path = os.getenv("SBOM_TOOL_PATH")
            report_output_dir = os.getenv("REPORT_OUTPUT_DIR")
            if not report_output_dir:
                raise ValueError("REPORT_OUTPUT_DIR environment variable is not set.")

            # Ensure REPORT_OUTPUT_DIR is an absolute path
            report_output_dir = os.path.abspath(report_output_dir)

            # Extract the repo name (from the URL) and generate the timestamp
            repo_name = clean_repo_url.split("/")[-1]
            timestamp = datetime.now().strftime("%Y-%d-%b-%H-%M-%S")

            # Define the full output path (repo_name/branch/timestamp)
            sbom_output_path = os.path.join(report_output_dir, repo_name, branch, timestamp)
            target_dir = os.path.join(sbom_output_path, repo_name)

            app.logger.info(f"Report Output Directory: {report_output_dir}")
            app.logger.info(f"Target Directory for Cloning: {target_dir}")

            # Create the new folder for this SBOM generation (repo_name/branch/timestamp)
            if not os.path.exists(sbom_output_path):
                os.makedirs(sbom_output_path)
                app.logger.info(f"Created new directory: {sbom_output_path}")
            else:
                app.logger.info(f"Directory already exists: {sbom_output_path}")

            # Clone the repo to a local directory if it doesn't already exist
            if not os.path.exists(target_dir):
                app.logger.info(f"Cloning repository {clean_repo_url} into {target_dir}")
                subprocess.run(
                    ["git", "clone", "-b", branch, "--depth", "1", clean_repo_url, target_dir],
                    check=True
                )
            else:
                app.logger.info(f"Repository already cloned at {target_dir}, skipping clone.")

            # Check if requirements.txt exists and is valid
            repo_path = target_dir
            requirements_path = os.path.join(repo_path, "requirements.txt")

            if os.path.exists(requirements_path):
                try:
                    with open(requirements_path, "r", encoding="utf-8") as f:
                        # Try reading the file to check if it's valid
                        contents = f.read()
                        if contents.strip():  # If the file is not empty
                            app.logger.info(f"Valid requirements.txt found at {requirements_path}. Using the original file.")
                            use_original_requirements = True
                        else:
                            raise ValueError("requirements.txt is empty.")
                except (UnicodeDecodeError, ValueError) as e:
                    # Log the error and regenerate the requirements.txt
                    app.logger.warning(f"Failed to parse requirements.txt at {requirements_path}. Error: {e}")
                    app.logger.info("Regenerating a curated requirements.txt using pipreqs.")
                    use_original_requirements = False
            else:
                app.logger.warning(f"Missing requirements.txt at {requirements_path}.")
                app.logger.info("Regenerating a curated requirements.txt using pipreqs.")
                use_original_requirements = False

            # Regenerate the requirements.txt with pipreqs if necessary
            if not use_original_requirements:
                try:
                    subprocess.run(
                        ["pipreqs", repo_path, "--force"], check=True
                    )
                    app.logger.info("Successfully regenerated requirements.txt using pipreqs.")
                except subprocess.CalledProcessError as e:
                    app.logger.error(f"Error while regenerating requirements.txt with pipreqs: {e}")
                    app.logger.info("Attempting to generate requirements.txt using pip freeze.")
                    generate_pip_freeze_requirements(requirements_path)

            # Construct the Syft command
            sbom_output_file = f"sbom-{branch}.json"
            sbom_output_file_path = os.path.join(sbom_output_path, sbom_output_file)

            command = [
                sbom_tool_path,
                "scan",
                f"dir:{target_dir}",
                "-o",
                f"syft-json={sbom_output_file_path}"
            ]

            # Log and execute the command
            app.logger.info(f"Running Syft command: {' '.join(command)}")
            subprocess.run(command, check=True)

            # Return the path of the generated SBOM
            return sbom_output_file_path

    except subprocess.CalledProcessError as e:
        app.logger.error(f"Failed to generate SBOM. Error: {e}")
        return None
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return None

def generate_pip_freeze_requirements(requirements_path):
    """Generates the requirements.txt using pip freeze."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=True
        )
        with open(requirements_path, "w") as f:
            f.write(result.stdout)
        app.logger.info(f"Successfully generated requirements.txt using pip freeze.")
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Error while generating requirements.txt with pip freeze: {e}")
