import pytest
from click.testing import CliRunner
from claude_vision.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_analyze_command(runner):
    result = runner.invoke(cli, ['analyze', 'tests/mona-lisa.jpg'])
    assert result.exit_code == 0
    assert 'Describe this image in detail' in result.output

def test_judge_command(runner):
    result = runner.invoke(cli, ['judge', 'tests/lighthouse-1.jpg', 'tests/lighthouse-2.png', '--criteria', 'composition,color', '--weights', '0.6,0.4'])
    assert result.exit_code == 0
    assert 'Judge the following images' in result.output

def test_evolution_command(runner):
    result = runner.invoke(cli, ['evolution', 'tests/IMG20240510235144.jpg', 'tests/IMG20240510235307.jpg', '--time-points', '23:51,23:53'])
    assert result.exit_code == 0
    assert 'Analyze the following series of images' in result.output

def test_persona_command(runner):
    result = runner.invoke(cli, ['persona', 'tests/mona-lisa.jpg', '--persona', 'art_critic', '--style', 'noir_detective'])
    assert result.exit_code == 0
    assert 'Analyze the following image in character' in result.output

def test_time_series_command(runner):
    result = runner.invoke(cli, ['time-series',  'tests/IMG20240510235144.jpg', 'tests/IMG20240510235307.jpg', '--time-points', '2022,2023', '--metrics', 'growth,color'])
    assert result.exit_code == 0
    assert 'Analyze the following series of images' in result.output

def test_alt_text_command(runner):
    result = runner.invoke(cli, ['alt-text', 'tests/aurora-moon.jpg'])
    assert result.exit_code == 0
    assert 'Generate a detailed, context-aware alt-text' in result.output

def test_config_command(runner):
    result = runner.invoke(cli, ['config'])
    assert result.exit_code == 0
    assert 'ANTHROPIC_API_KEY' in result.output