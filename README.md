# Claude Vision CLI

Claude Vision CLI is an advanced command-line tool for image analysis using the Claude 3.5 Sonnet vision model. This tool allows you to process one or more images, including images from URLs, and receive detailed descriptions or structured output based on the content of the images.

![Visual Judge Demo](visual-judge-demo.jpg)


## Installation

To install Claude Vision CLI, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/irthomasthomas/claude-vision-cli.git
   cd claude-vision-cli
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

Claude Vision CLI now offers several advanced features:

### Basic Analysis
```
claude-vision analyze [OPTIONS] [IMAGE_PATHS]...
```

### Visual Decider
Compare and rank multiple images based on given criteria:
```
claude-vision decide [IMAGE_PATHS]... --criteria "sharpness,color,composition" --weights "0.3,0.3,0.4"
```

### Image Evolution Analyzer
Analyze a series of images to describe changes over time:
```
claude-vision evolution [IMAGE_PATHS]... --time-points "2023-01,2023-06,2023-12"
```

### Persona-Based Analysis
Analyze an image using a specified professional and stylistic persona:
```
claude-vision persona-analysis IMAGE_PATH --persona art_critic --style noir_detective
```

### Comparative Time-Series Analysis
Perform comparative time-series analysis on multiple images:
```
claude-vision time-series [IMAGE_PATHS]... --time-points "2023-Q1,2023-Q2,2023-Q3,2023-Q4" --metrics "sales,customer_satisfaction"
```

### Generate Alt-Text
Generate detailed, context-aware alt-text for an image:
```
claude-vision alt-text IMAGE_PATH
```

## Features

- Analyze multiple local images or images from URLs
- Compare and rank images based on custom criteria
- Analyze image evolution over time
- Perform persona-based analysis with professional and stylistic personas
- Conduct comparative time-series analysis
- Generate detailed alt-text for web accessibility
- Choose between text, JSON, or Markdown output formats
- Automatic image resizing to meet API requirements

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.