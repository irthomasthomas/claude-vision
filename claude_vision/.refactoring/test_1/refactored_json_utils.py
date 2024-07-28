import json
from typing import Any, Dict, List
from jsonschema import validate, ValidationError

class JSONSchemaValidator:
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

    @staticmethod
    def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> None:
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            raise ValueError(f"JSON does not match schema: {e}")

class JSONParser:
    @staticmethod
    def parse_json_input(json_input: str) -> Dict[str, Any]:
        try:
            data = json.loads(json_input)
            JSONSchemaValidator.validate_schema(data, JSONSchemaValidator.INPUT_SCHEMA)
            return data
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input")

    @staticmethod
    def parse_video_json_input(json_input: str) -> Dict[str, Any]:
        try:
            data = json.loads(json_input)
            JSONSchemaValidator.validate_schema(data, JSONSchemaValidator.VIDEO_INPUT_SCHEMA)
            return data
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input")

class JSONFormatter:
    @staticmethod
    def format_json_output(result: Any, analysis_type: str) -> Dict[str, Any]:
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                pass
        
        output = {
            "result": result if isinstance(result, dict) else {"description": result},
            "analysis_type": analysis_type
        }
        
        JSONSchemaValidator.validate_schema(output, JSONSchemaValidator.OUTPUT_SCHEMA)
        return output

    @staticmethod
    def format_video_json_output(video_metadata: Dict[str, Any], frame_results: List[Dict[str, Any]], analysis_type: str) -> Dict[str, Any]:
        output = {
            "video_metadata": video_metadata,
            "frame_results": [],
            "analysis_type": analysis_type
        }
        
        for frame in frame_results:
            formatted_frame = {
                "frame_number": frame["frame_number"],
                "timestamp": frame["timestamp"],
                "result": JSONFormatter._parse_frame_result(frame["result"])
            }
            output["frame_results"].append(formatted_frame)
        
        JSONSchemaValidator.validate_schema(output, JSONSchemaValidator.VIDEO_OUTPUT_SCHEMA)
        return output

    @staticmethod
    def _parse_frame_result(result: Any) -> Any:
        if isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return result
        return result