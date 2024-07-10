import unittest
from unittest.mock import patch, MagicMock
from PIL import Image
import io
import base64
from claude_vision_cli.image_processing import convert_image_to_base64, resize_image, fetch_image_from_url

class TestImageProcessing(unittest.TestCase):
    def setUp(self):
        self.test_image = Image.new('RGB', (100, 100), color='red')

    def test_convert_image_to_base64(self):
        base64_string = convert_image_to_base64(self.test_image)
        self.assertTrue(isinstance(base64_string, str))
        self.assertTrue(base64_string.startswith('iVBORw0KGgo'))

    def test_resize_image(self):
        resized_image = resize_image(self.test_image, max_size=(50, 50))
        self.assertEqual(resized_image.size, (50, 50))

    @patch('requests.get')
    def test_fetch_image_from_url(self, mock_get):
        # Create a valid image for the mock response
        img_byte_arr = io.BytesIO()
        self.test_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        mock_response = MagicMock()
        mock_response.content = img_byte_arr
        mock_get.return_value = mock_response

        fetched_image = fetch_image_from_url('https://example.com/image.jpg')
        self.assertIsInstance(fetched_image, Image.Image)
        self.assertEqual(fetched_image.size, (100, 100))

    @patch('requests.get')
    def test_fetch_image_from_wikipedia(self, mock_get):
        # Famous Wikipedia image: Mona Lisa
        mona_lisa_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/687px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg"
        
        # Use the actual Mona Lisa sample image for the test
        with open('tests/mona_lisa_sample.jpg', 'rb') as f:
            mock_response = MagicMock()
            mock_response.content = f.read()
        mock_get.return_value = mock_response

        fetched_image = fetch_image_from_url(mona_lisa_url)
        self.assertIsInstance(fetched_image, Image.Image)
        self.assertTrue(fetched_image.width > 0 and fetched_image.height > 0)

if __name__ == '__main__':
    unittest.main()