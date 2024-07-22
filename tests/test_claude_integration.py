import pytest
from unittest.mock import patch, MagicMock
from claude_vision.claude_integration import claude_vision_analysis
from claude_vision.exceptions import APIError

@pytest.mark.asyncio
async def test_claude_vision_analysis():
    with patch('claude_vision.claude_integration.httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'content': [{'text': 'Test response'}]
        }
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

        result = await claude_vision_analysis(['base64_image'], 'Describe the image', 'text')
        assert result == 'Test response'

@pytest.mark.asyncio
async def test_claude_vision_analysis_error():
    with patch('claude_vision.claude_integration.httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = APIError('API Error')
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

        with pytest.raises(APIError):
            await claude_vision_analysis(['base64_image'], 'Describe the image', 'text')

@pytest.mark.asyncio
async def test_claude_vision_analysis_stream():
    with patch('claude_vision.claude_integration.httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.aiter_lines.return_value = [
            'data: {"type": "content_block_delta", "delta": {"text": "Chunk 1"}}',
            'data: {"type": "content_block_delta", "delta": {"text": "Chunk 2"}}',
            'data: {"type": "message_stop"}'
        ]
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

        result = await claude_vision_analysis(['base64_image'], 'Describe the image', 'text', stream=True)
        chunks = [chunk async for chunk in result]
        assert chunks == ['Chunk 1', 'Chunk 2']