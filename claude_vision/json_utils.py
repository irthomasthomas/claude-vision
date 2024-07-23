
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
        "result": {
            "oneOf": [
                {"type": "string"},
                {"type": "object"}
            ]
        },
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
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            # If it's not valid JSON, keep it as is
            pass
    
    output = {
        "result": result if isinstance(result, dict) else {"description": result},
        "analysis_type": analysis_type
    }
    
    try:
        validate(instance=output, schema=OUTPUT_SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        raise ValueError(f"Output does not match schema: {e}")
    
    return output

# Video-specific schemas and functions

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
                    "result": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "object"}
                        ]
                    }
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
        "frame_results": [],
        "analysis_type": analysis_type
    }
    
    for frame in frame_results:
        formatted_frame = {
            "frame_number": frame["frame_number"],
            "timestamp": frame["timestamp"],
            "result": frame["result"]
        }
        
        # Parse the nested JSON string in the result
        if isinstance(formatted_frame["result"], str):
            try:
                formatted_frame["result"] = json.loads(formatted_frame["result"])
            except json.JSONDecodeError:
                # If it's not valid JSON, keep it as is
                pass
        
        output["frame_results"].append(formatted_frame)
    
    try:
        validate(instance=output, schema=VIDEO_OUTPUT_SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        raise ValueError(f"Output does not match schema: {e}")
    
    return output