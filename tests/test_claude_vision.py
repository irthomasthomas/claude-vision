import pytest
from click.testing import CliRunner
from claude_vision.cli import cli
from claude_vision.json_utils import parse_json_input, format_json_output
import json

def test_claude_vision_analyze():
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', 'test_image.jpg'])
    assert result.exit_code == 0
    assert "Analysis result" in result.output

def test_json_input_parsing():
    valid_json = '{"file_path": "test.jpg", "analysis_type": "description"}'
    assert parse_json_input(json.loads(valid_json)) == {"file_path": "test.jpg", "analysis_type": "description"}

    with pytest.raises(ValueError):
        parse_json_input(json.loads('{"invalid": "json"}'))

def test_json_output_formatting():
    result = "This is a test result"
    output = format_json_output(result, "description")
    assert output["result"] == result
    assert output["analysis_type"] == "description"

def test_claude_vision_with_persona():
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', 'test_image.jpg', '--persona', 'art_critic'])
    assert result.exit_code == 0
    assert "As an art critic" in result.output

def test_claude_vision_with_json_output():
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', 'test_image.jpg', '--json-output'])
    assert result.exit_code == 0
    assert json.loads(result.output)["analysis_type"] == "description"

def test_claude_vision_with_json_input(tmp_path):
    input_file = tmp_path / "input.json"
    input_file.write_text('{"file_path": "test_image.jpg", "analysis_type": "description"}')
    
    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', '--json-input', str(input_file)])
    assert result.exit_code == 0
    assert "Analysis result" in result.output

def test_claude_vision_judge():
    runner = CliRunner()
    result = runner.invoke(cli, ['judge', 'image1.jpg', 'image2.jpg', '--criteria', 'composition,color', '--weights', '0.6,0.4'])
    assert result.exit_code == 0
    assert "Judging result" in result.output

def test_claude_vision_evolution():
    runner = CliRunner()
    result = runner.invoke(cli, ['evolution', 'image1.jpg', 'image2.jpg', '--time-points', '2022-01,2023-01'])
    assert result.exit_code == 0
    assert "Evolution analysis" in result.output

def test_claude_vision_time_series():
    runner = CliRunner()
    result = runner.invoke(cli, ['time-series', 'image1.jpg', 'image2.jpg', '--time-points', 'Q1,Q2', '--metrics', 'sales,satisfaction'])
    assert result.exit_code == 0
    assert "Time series analysis" in result.output