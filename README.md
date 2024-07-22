# Claude Vision CLI

https://github.com/user-attachments/assets/489a8dae-4366-4ff4-aa41-fb81a71160a1


```
claude-vision judge [IMAGE_PATHS]... --criteria "sharpness,color,composition" --weights "0.3,0.3,0.4" --output md
```

![Visual Judge Demo](visual-judge-demo.jpg)

Claude Vision CLI is an advanced command-line tool for image analysis using the Claude 3.5 Sonnet vision model. This tool allows you to process one or more images, including images from URLs, and receive detailed descriptions or structured output based on the content of the images. It can be used as part of pipeline to support advanced analysis and automation. It features a markdown mode and JSON mode to guarantee structured output.

## Examples:
More examples available in [Lighthouse Analysis Demo](demo/lighthouse.md)

## Installation

To install Claude Vision CLI, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/irthomasthomas/claude-vision.git
   cd claude-vision
   ```

2. Install the package:
   ```
   pip install -e .
   ```

3. Set up your Anthropic API key:
   ```
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

Claude Vision CLI offers several advanced features:

### Basic Analysis
```
claude-vision analyze [IMAGE_PATHS]... [OPTIONS]
```

Example:
```
claude-vision analyze image1.jpg image2.png -p "Describe the contents of these images"
```

### Using stdin and stdout
You can pipe images into Claude Vision CLI:
```
cat image.jpg | claude-vision --output json > result.json
```

### Visual Judge
Compare and rank multiple images based on given criteria:
```
claude-vision judge [IMAGE_PATHS]... --criteria "sharpness,color,composition" --weights "0.3,0.3,0.4" --output md
```

### Image Evolution Analyzer
Analyze a series of images to describe changes over time:
```
claude-vision evolution [IMAGE_PATHS]... --time-points "2023-01,2023-06,2023-12" --output json
```

### Persona-Based Analysis
Analyze an image using a specified professional and stylistic persona:
```
claude-vision persona IMAGE_PATH --persona art_critic --style victorian_gent
```

### Comparative Time-Series Analysis
Perform comparative time-series analysis on multiple images:
```
claude-vision time-series [IMAGE_PATHS]... --time-points "2023-Q1,2023-Q2,2023-Q3,2023-Q4" --metrics "sales,customer_satisfaction"
```

### Generate Alt-Text
Generate detailed, context-aware alt-text for an image:
```
claude-vision alt-text IMAGE_PATH --output md
```

## Features

- Analyze multiple local images or images from URLs
- Compare and rank images based on custom criteria
- Analyze image evolution over time
- Perform persona-based analysis with professional and stylistic personas
- Conduct comparative time-series analysis
- Generate detailed alt-text for web accessibility
- Choose between text, JSON, or Markdown output formats
- JSON output with automatic structure enforcement
- Automatic image resizing to meet API requirements
- Support for stdin and stdout, enabling integration with other tools

## Imaginative Use Cases
<!-- Todo: Use judge to place image sets on trial and delete the junkers. -->

1. **Automated Visual Inspection**: Use Claude Vision CLI in manufacturing to analyze product images for defects:
   ```
   find /path/to/product/images -type f -name "*.jpg" | xargs claude-vision compare --criteria "defects,alignment,color" --weights "0.5,0.3,0.2" --output json | jq '.defective_items[]' > defective_items.txt
   ```

2. **Real Estate Photo Enhancement**: Improve real estate listing photos by analyzing and generating suggestions:
   ```
   claude-vision persona listing_photo.jpg --persona interior_designer --style modern_minimalist --output json | jq '.suggestions[]' > photo_improvement_tips.txt

3. **Satellite Imagery Analysis**: Track environmental changes over time using satellite images:
   ```
   claude-vision evolution satellite_images/*.tif --time-points "2020,2021,2022,2023" --output md > environmental_report.md
   ```
4. **Art Style Transfer Guidance**: Use Claude Vision to analyze artworks and guide style transfer algorithms:
   ```
   claude-vision persona artwork.jpg --persona art_historian --style analytical | python style_transfer.py --guidance - --input photo.jpg --output stylized_photo.jpg
   ```

## Contributing

Contributions greatfully received...

## License

This project is licensed under the MIT License.
