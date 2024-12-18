import json

def export_vulnerabilities_to_json(vuln_data, output_json_path):
    """Exports vulnerability data to a JSON file."""
    try:
        with open(output_json_path, 'w') as json_file:
            json.dump(vuln_data, json_file, indent=4)
        print(f"Vulnerabilities exported to: {output_json_path}")
    except Exception as e:
        print(f"Error exporting vulnerabilities to JSON: {e}")
