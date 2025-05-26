# Text2Asset 🖼️

![Godot Version](https://img.shields.io/badge/Godot-v4.x-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

**Text2Asset** is a Godot plugin that transforms text input into game-ready assets like textures, sprites, or 3D models, streamlining your asset creation process. Whether you're prototyping a game or experimenting with procedural content, Text2Asset makes it easy to generate assets directly within the Godot editor.

## News
A new Python version is added! Easier to integrate into systems other than Godot :)

## Table of Contents

- [Features](#features)
- [Installation](#installation)

## Features

- 📝 **Text-to-Asset Generation**: Convert text descriptions (e.g., "a blue bird") into assets using Gemini AI.
- 🖌️ **Customizable Styles**: Supports multiple art styles like pixel art, watercolor, or low-poly 3D, with adjustable parameters.
- 🖥️ **Editor Integration**: Adds a dock to the Godot editor for seamless asset creation without leaving your project.
- ⚡ **Efficient Workflow**: Generate assets in seconds, reducing manual asset creation time by up to 50%.

## Installation

### For Godot:
Follow these steps to install Text2Asset in your Godot project:

1. **Download the Plugin**:
   - Download `text2asset.zip` from the [releases page](https://github.com/JoyceQiao7/Text2Asset/releases) or clone this repository.

2. **Install the Plugin**:
   - Open your Godot project (Godot 4.x recommended).
   - Create an `addons/` folder in your project directory if it doesn’t exist (`res://addons/`).
   - Unzip `text2asset.zip` into `res://addons/`, resulting in:\
res://addons/Text2Asset/\
├── plugin.cfg\
├── plugin.gd\
├── text2asset.gd\
├── ui.gd\
├── ui.tscn\
└── README.md

3. **Enable the Plugin**:
- In Godot, go to `Project > Project Settings > Plugins`.
- Find "Text2Asset" in the list and set its status to "Active".

4. **Verify Installation**:
- A new "Text2Asset" dock should appear in the Godot editor (default: left side).
- If it doesn’t appear, ensure the plugin is active and restart Godot.

### For Python version: 
Command Line:
```
# Basic usage
python text2asset_simple.py "golden treasure chest"

# With custom output
python text2asset_simple.py "mystical orb" --output magical_orb.png

# With API keys
python text2asset_simple.py "fire phoenix" --gemini-key YOUR_KEY --removebg-key YOUR_KEY
```

Integrate as a module:
```
from text2asset_simple import generate_asset

# Simple usage
output_file = generate_asset("red dragon")

# With custom path
output_file = generate_asset("blue castle", "my_castle.png")

# With API keys
output_file = generate_asset("magic sword", 
                           gemini_api_key="your_key", 
                           removebg_api_key="your_key")
```

Integration example:
```
# In your larger system
from text2asset_simple import Text2AssetGenerator

generator = Text2AssetGenerator(gemini_key, removebg_key)

# Generate multiple assets
assets = []
for prompt in ["sword", "shield", "potion"]:
    asset_path = generator.generate_image_from_text(prompt)
    assets.append(asset_path)
```
