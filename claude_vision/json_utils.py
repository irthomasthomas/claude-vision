import json
import jsonschema
from jsonschema import validate

# Existing schemas and functions

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

# New video-specific schemas and functions

VIDEO_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "file_path": {"type": "string"},
        "persona": {"type": "string"},
        "analysis_type": {"type": "string", "enum": ["video_description", "video_object_detection", "video_scene_classification"]},
        "frame_interval": {"type": "integer", "minimum": 1}
    },
    "required": ["file_path", "analysis_type"]
}

VIDEO_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "video_metadata": {
            "type": "object",
            "properties": {
                "fps": {"type": "number"},
                "frame_count": {"type": "integer"},
                "duration": {"type": "number"},
                "width": {"type": "integer"},
                "height": {"type": "integer"}
            }
        },
        "frame_results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "frame_number": {"type": "integer"},
                    "timestamp": {"type": "number"},
                    "result": {"type": "string"}
                }
            }
        },
        "analysis_type": {"type": "string"}
    },
    "required": ["video_metadata", "frame_results", "analysis_type"]
}

def parse_video_json_input(json_input):
    try:
        data = json.load(json_input)
        validate(instance=data, schema=VIDEO_INPUT_SCHEMA)
        return data
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON input")
    except jsonschema.exceptions.ValidationError as e:
        raise ValueError(f"JSON input does not match schema: {e}")

def format_video_json_output(video_metadata, frame_results, analysis_type):
    output = {
        "video_metadata": video_metadata,
        "frame_results": frame_results,
        "analysis_type": analysis_type
    }
    validate(instance=output, schema=VIDEO_OUTPUT_SCHEMA)
    return output