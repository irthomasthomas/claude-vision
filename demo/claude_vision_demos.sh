#!/bin/zsh

# Global variables for local image paths
IMAGE1="path/to/local/image1.jpg"
IMAGE2="path/to/local/image2.png"
IMAGE3="path/to/local/image3.jpg"
IMAGE4="path/to/local/image4.png"

# Real image URLs
boringURL1="https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
boringURL2="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Image_created_with_a_mobile_phone.png/1200px-Image_created_with_a_mobile_phone.png"


# Interesting real image URLs
URL1="https://apod.nasa.gov/apod/image/2403/NGC1232_vlt_960.jpg"
URL2="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/1200px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg"
URL3="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Felis_catus-cat_on_snow.jpg/2560px-Felis_catus-cat_on_snow.jpg"
URL4="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Hydrogen_Explosion.jpg/1280px-Hydrogen_Explosion.jpg"
URL5="https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Starry_Night_Over_the_Rhone.jpg/2560px-Starry_Night_Over_the_Rhone.jpg"



# Basic Analysis
claude-vision analyze $IMAGE1 $IMAGE2 -p "Describe the contents of these images"

# Using stdin and stdout
cat $IMAGE1 | claude-vision analyze - --output json > result.json

# Visual Judge
claude-vision judge $IMAGE1 $IMAGE2 $IMAGE3 --criteria "sharpness,color,composition" --weights "0.3,0.3,0.4" --output md

# Image Evolution Analyzer
claude-vision evolution $IMAGE1 $IMAGE2 $IMAGE3 --time-points "2023-01,2023-06,2023-12" --output json

# Persona-Based Analysis
claude-vision persona $IMAGE1 --persona art_critic --style victorian_gent

# Comparative Time-Series Analysis
claude-vision time-series $IMAGE1 $IMAGE2 $IMAGE3 $IMAGE4 --time-points "2023-Q1,2023-Q2,2023-Q3,2023-Q4" --metrics "sales,customer_satisfaction"

# Generate Alt-Text
claude-vision alt-text $IMAGE1 --output md

# Streaming Responses
claude-vision analyze $IMAGE1 --stream

# Custom System Prompts
claude-vision analyze $IMAGE2 --system-prompt "You are an expert in identifying rare plants."

# Prefilling Responses
claude-vision analyze $IMAGE3 --prefill "The image shows a"

# Using Tools
claude-vision analyze $IMAGE4 --tools get_weather --tools image_metadata

# Analyzing URL images
claude-vision analyze $URL1 $URL2 -p "Compare and contrast these two images"
