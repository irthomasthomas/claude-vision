import json
import jsonschema
from jsonschema import validate

INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "file_path": {"type": "string"},
        "persona": {"type": "string"},
        "analysis_type": {"type": "string", "enum": ["description", "object_detection", "scene_classification"]}
    },
    "required": ["file_path", "analysis_type"]
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "result": {"type": "string"},
        "confidence": {"type": "number"},
        "analysis_type": {"type": "string"}
    },
    "required": ["result", "analysis_type"]
}

def parse_json_input(json_input):
    try:
        data = json.load(json_input)
        validate(instance=data, schema=INPUT_SCHEMA)
        return data
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON input")
    except jsonschema.exceptions.ValidationError as e:
        raise ValueError(f"JSON input does not match schema: {e}")

def format_json_output(result, analysis_type):
    output = {
        "result": result,
        "analysis_type": analysis_type
    }
    validate(instance=output, schema=OUTPUT_SCHEMA)
    return output