import json
from typing import Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from jsonschema import validate, ValidationError

class AnalysisType(Enum):
    DESCRIPTION = "description"
    OBJECT_DETECTION = "object_detection"
    SCENE_CLASSIFICATION = "scene_classification"
    VIDEO_DESCRIPTION = "video_description"
    VIDEO_OBJECT_DETECTION = "video_object_detection"
    VIDEO_SCENE_CLASSIFICATION = "video_scene_classification"

@dataclass
class InputSchema:
    FILE_PATH: str = "file_path"
    PERSONA: str = "persona"
    ANALYSIS_TYPE: str = "analysis_type"
    FRAME_INTERVAL: str = "frame_interval"

@dataclass
class OutputSchema:
    RESULT: str = "result"
    CONFIDENCE: str = "confidence"
    ANALYSIS_TYPE: str = "analysis_type"
    VIDEO_METADATA: str = "video_metadata"
    FRAME_RESULTS: str = "frame_results"
    FRAME_NUMBER: str = "frame_number"
    TIMESTAMP: str = "timestamp"

INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        InputSchema.FILE_PATH: {"type": "string"},
        InputSchema.PERSONA: {"type": "string"},
        InputSchema.ANALYSIS_TYPE: {"type": "string", "enum": [e.value for e in AnalysisType]}
    },
    "required": [InputSchema.FILE_PATH, InputSchema.ANALYSIS_TYPE]
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        OutputSchema.RESULT: {
            "oneOf": [
                {"type": "string"},
                {"type": "object"}
            ]
        },
        OutputSchema.CONFIDENCE: {"type": "number"},
        OutputSchema.ANALYSIS_TYPE: {"type": "string"}
    },
    "required": [OutputSchema.RESULT, OutputSchema.ANALYSIS_TYPE]
}

VIDEO_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        InputSchema.FILE_PATH: {"type": "string"},
        InputSchema.PERSONA: {"type": "string"},
        InputSchema.ANALYSIS_TYPE: {"type": "string", "enum": [e.value for e in AnalysisType if e.value.startswith("video_")]},
        InputSchema.FRAME_INTERVAL: {"type": "integer", "minimum": 1}
    },
    "required": [InputSchema.FILE_PATH, InputSchema.ANALYSIS_TYPE]
}

VIDEO_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        OutputSchema.VIDEO_METADATA: {
            "type": "object",
            "properties": {
                "fps": {"type": "number"},
                "frame_count": {"type": "integer"},
                "duration": {"type": "number"},
                "width": {"type": "integer"},
                "height": {"type": "integer"}
            }
        },
        OutputSchema.FRAME_RESULTS: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    OutputSchema.FRAME_NUMBER: {"type": "integer"},
                    OutputSchema.TIMESTAMP: {"type": "number"},
                    OutputSchema.RESULT: {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "object"}
                        ]
                    }
                }
            }
        },
        OutputSchema.ANALYSIS_TYPE: {"type": "string"}
    },
    "required": [OutputSchema.VIDEO_METADATA, OutputSchema.FRAME_RESULTS, OutputSchema.ANALYSIS_TYPE]
}

class JsonSchemaValidator:
    @staticmethod
    def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> None:
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            raise ValueError(f"JSON data does not match schema: {e}")

class JsonParser:
    @staticmethod
    def parse_json(json_input: str) -> Dict[str, Any]:
        try:
            return json.loads(json_input)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input")

    @staticmethod
    def parse_and_validate(json_input: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        data = JsonParser.parse_json(json_input)
        JsonSchemaValidator.validate_schema(data, schema)
        return data

def parse_json_input(json_input: str) -> Dict[str, Any]:
    return JsonParser.parse_and_validate(json_input, INPUT_SCHEMA)

def parse_video_json_input(json_input: str) -> Dict[str, Any]:
    return JsonParser.parse_and_validate(json_input, VIDEO_INPUT_SCHEMA)

def format_json_output(result: Any, analysis_type: str) -> Dict[str, Any]:
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            pass
    
    output = {
        OutputSchema.RESULT: result if isinstance(result, dict) else {"description": result},
        OutputSchema.ANALYSIS_TYPE: analysis_type
    }
    
    JsonSchemaValidator.validate_schema(output, OUTPUT_SCHEMA)
    return output

def format_video_json_output(video_metadata: Dict[str, Any], frame_results: List[Dict[str, Any]], analysis_type: str) -> Dict[str, Any]:
    output = {
        OutputSchema.VIDEO_METADATA: video_metadata,
        OutputSchema.FRAME_RESULTS: [],
        OutputSchema.ANALYSIS_TYPE: analysis_type
    }
    
    for frame in frame_results:
        formatted_frame = {
            OutputSchema.FRAME_NUMBER: frame[OutputSchema.FRAME_NUMBER],
            OutputSchema.TIMESTAMP: frame[OutputSchema.TIMESTAMP],
            OutputSchema.RESULT: frame[OutputSchema.RESULT]
        }
        
        if isinstance(formatted_frame[OutputSchema.RESULT], str):
            try:
                formatted_frame[OutputSchema.RESULT] = json.loads(formatted_frame[OutputSchema.RESULT])
            except json.JSONDecodeError:
                pass
        
        output[OutputSchema.FRAME_RESULTS].append(formatted_frame)
    
    JsonSchemaValidator.validate_schema(output, VIDEO_OUTPUT_SCHEMA)
    return output