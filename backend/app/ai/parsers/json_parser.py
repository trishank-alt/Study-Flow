import json
import re


def parse_json_markdown(text: str) -> dict:
    text = text.strip()

    # Try searching for a JSON code block
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        json_content = match.group(1).strip()
    else:
        # Try to find the first '{' and last '}'
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1:
            json_content = text[start_idx:end_idx + 1]
        else:
            json_content = text

    # Remove single line comments
    json_content = re.sub(r"//.*", "", json_content)

    # Load JSON
    try:
        return json.loads(json_content)
    except json.JSONDecodeError as e:
        try:
            # Fallback cleanup: replace single quotes with double quotes
            cleaned = json_content.replace("'", '"')
            return json.loads(cleaned)
        except Exception:
            raise ValueError(f"Failed to parse JSON: {str(e)}")
