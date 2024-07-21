import pytest
from unittest.mock import patch
from claude_vision.advanced_features import (
    visual_judge,
    image_evolution_analyzer,
    persona_based_analysis,
    comparative_time_series_analysis,
    generate_alt_text
)

@pytest.mark.asyncio
async def test_visual_judge():
    with patch('claude_vision.advanced_features.claude_vision_analysis') as mock_analysis:
        mock_analysis.return_value = 'Visual judge result'
        result = await visual_judge(['base64_image1', 'base64_image2'], ['criteria1', 'criteria2'], [0.5, 0.5], 'text', False)
        assert result == 'Visual judge result'

@pytest.mark.asyncio
async def test_image_evolution_analyzer():
    with patch('claude_vision.advanced_features.claude_vision_analysis') as mock_analysis:
        mock_analysis.return_value = 'Evolution analysis result'
        result = await image_evolution_analyzer(['base64_image1', 'base64_image2'], ['2022', '2023'], 'text', False)
        assert result == 'Evolution analysis result'

@pytest.mark.asyncio
async def test_persona_based_analysis():
    with patch('claude_vision.advanced_features.claude_vision_analysis') as mock_analysis:
        mock_analysis.return_value = 'Persona-based analysis result'
        result = await persona_based_analysis('base64_image', 'art_critic', 'noir_detective', 'text', False)
        assert result == 'Persona-based analysis result'

@pytest.mark.asyncio
async def test_comparative_time_series_analysis():
    with patch('claude_vision.advanced_features.claude_vision_analysis') as mock_analysis:
        mock_analysis.return_value = 'Time series analysis result'
        result = await comparative_time_series_analysis(['base64_image1', 'base64_image2'], ['2022', '2023'], ['metric1', 'metric2'], 'text', False)
        assert result == 'Time series analysis result'

@pytest.mark.asyncio
async def test_generate_alt_text():
    with patch('claude_vision.advanced_features.claude_vision_analysis') as mock_analysis:
        mock_analysis.return_value = 'Generated alt text'
        result = await generate_alt_text('base64_image', 'text', False)
        assert result == 'Generated alt text'