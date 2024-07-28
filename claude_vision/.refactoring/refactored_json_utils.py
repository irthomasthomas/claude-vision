import json
from typing import Any, Dict, List, Union
from jsonschema import validate, ValidationError

class JSONSchemas:
    INPUT = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string"},
            "persona": {"type": "string"},
            "analysis_type": {"type": "string", "enum": ["description", "object_detection", "scene_classification"]}
        },
        "required": ["file_path", "analysis_type"]
    }

    OUTPUT = {
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

    VIDEO_INPUT = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string"},
            "persona": {"type": "string"},
            "analysis_type": {"type": "string", "enum": ["video_description", "video_object_detection", "video_scene_classification"]},
            "frame_interval": {"type": "integer", "minimum": 1}
        },
        "required": ["file_path", "analysis_type"]
    }

    VIDEO_OUTPUT = {
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

class JSONValidator:
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
            JSONValidator.validate_schema(data, JSONSchemas.INPUT)
            return data
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input")

    @staticmethod
    def parse_video_json_input(json_input: str) -> Dict[str, Any]:
        try:
            data = json.loads(json_input)
            JSONValidator.validate_schema(data, JSONSchemas.VIDEO_INPUT)
            return data
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input")

class JSONFormatter:
    @staticmethod
    def format_json_output(result: Union[str, Dict[str, Any]], analysis_type: str) -> Dict[str, Any]:
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                pass
        
        output = {
            "result": result if isinstance(result, dict) else {"description": result},
            "analysis_type": analysis_type
        }
        
        JSONValidator.validate_schema(output, JSONSchemas.OUTPUT)
        return output

    @staticmethod
    def format_video_json_output(video_metadata: Dict[str, Any], frame_results: List[Dict[str, Any]], analysis_type: str) -> Dict[str, Any]:
        output = {
            "video_metadata": video_metadata,
            "frame_results": [JSONFormatter._format_frame_result(frame) for frame in frame_results],
            "analysis_type": analysis_type
        }
        
        JSONValidator.validate_schema(output, JSONSchemas.VIDEO_OUTPUT)
        return output

    @staticmethod
    def _format_frame_result(frame: Dict[str, Any]) -> Dict[str, Any]:
        formatted_frame = {
            "frame_number": frame["frame_number"],
            "timestamp": frame["timestamp"],
            "result": frame["result"]
        }
        
        if isinstance(formatted_frame["result"], str):
            try:
                formatted_frame["result"] = json.loads(formatted_frame["result"])
            except json.JSONDecodeError:
                pass
        
        return formatted_frame