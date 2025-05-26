#!/usr/bin/env python3
"""
Takes text prompt as input and outputs an image with background removed
"""
from google import genai
from google.genai import types
from PIL import Image
import io
from io import BytesIO
import base64
import os
import json
import requests
import time
from typing import Optional

class Text2AssetGenerator:
    def __init__(self, gemini_api_key: str = None, removebg_api_key: str = None):
        """
        Initialize the Text2Asset generator
        
        Args:
            gemini_api_key: Google Gemini API key for image generation
            removebg_api_key: Remove.bg API key for background removal
        """
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        self.removebg_api_key = removebg_api_key or os.getenv('REMOVEBG_API_KEY')
        
        # Load API keys from config if not provided
        if not self.gemini_api_key or not self.removebg_api_key:
            self._load_config()
    
    def _load_config(self):
        """Load API keys from config.json if available"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    if not self.gemini_api_key:
                        self.gemini_api_key = config.get('gemini_api_key', '')
                    if not self.removebg_api_key:
                        self.removebg_api_key = config.get('removebg_api_key', '')
        except Exception as e:
            print(f"Warning: Could not load config.json: {e}")
    
    def generate_image_from_text(self, prompt: str, output_path: str = None) -> str:
        """
        Generate an image from text prompt and automatically remove background
        
        Args:
            prompt: Text description of the desired image
            output_path: Path to save the generated image (optional)
            
        Returns:
            Path to the saved image file
        """
        print(f"Generating image for prompt: '{prompt}'")
        
        # Step 1: Generate image using Gemini API
        generated_image = self._generate_image(prompt)
        if not generated_image:
            raise Exception("Failed to generate image")
        
        # Step 2: Automatically remove background
        if self.removebg_api_key:
            print("Removing background...")
            final_image = self._remove_background(generated_image)
        else:
            print("Warning: No RemoveBG API key provided, skipping background removal")
            final_image = generated_image
        
        # Step 3: Save the final image
        if not output_path:
            timestamp = int(time.time())
            clean_prompt = "".join(c for c in prompt if c.isalnum() or c in (' ', '-', '_')).strip()
            clean_prompt = "_".join(clean_prompt.split())[:30]
            # Replace with output path
            output_path = f"generated_asset_{clean_prompt}_{timestamp}.png"
        
        final_image.save(output_path, format='PNG')
        print(f"Image saved to: {output_path}")
        
        return output_path
    
    def _generate_image(self, prompt: str) -> Optional[Image.Image]:
        """Generate image using Gemini API"""
        if not self.gemini_api_key:
            print("Warning: No Gemini API key provided, using placeholder image")
            return self._create_placeholder_image(prompt)
        
        try:
            client = genai.Client(api_key=self.gemini_api_key)

            contents = (f"Generate a high-quality 2D asset image of: {prompt}. The image should be suitable for use as a game asset or digital artwork, with clear details and good contrast.")

            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=contents,
                config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
                )
            )

            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    print(part.text)
                elif part.inline_data is not None:
                    image = Image.open(BytesIO((part.inline_data.data)))
                    return image

        except Exception as e:
            print(f"Error generating image: {e}")
            return None
    
    def _remove_background(self, image: Image.Image) -> Image.Image:
        """Remove background using RemoveBG API"""
        try:
            # Save the image to a temporary BytesIO object
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            response = requests.post(
                'https://api.remove.bg/v1.0/removebg',
                files={'image_file': img_byte_arr},
                data={'size': 'auto'},
                headers={'X-Api-Key': self.removebg_api_key},
            )
            if response.status_code == requests.codes.ok:
                # Convert the response content back to a PIL Image
                return Image.open(BytesIO(response.content))
            else:
                print("Error:", response.status_code, response.text)
                return image
                
        except Exception as e:
            print(f"Error removing background: {e}. Please use the image without background removal.")
            return image

def generate_asset(prompt: str, output_path: str = None, 
                  gemini_api_key: str = None, removebg_api_key: str = None) -> str:
    """
    Simple function to generate an asset from text prompt
    
    Args:
        prompt: Text description of the desired asset
        output_path: Optional path to save the image
        gemini_api_key: Optional Gemini API key
        removebg_api_key: Optional RemoveBG API key
        
    Returns:
        Path to the generated image file
    """
    generator = Text2AssetGenerator(gemini_api_key, removebg_api_key)
    return generator.generate_image_from_text(prompt, output_path)

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate 2D assets from text prompts")
    parser.add_argument("prompt", help="Text description of the asset to generate")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--gemini-key", help="Gemini API key")
    parser.add_argument("--removebg-key", help="RemoveBG API key")
    
    args = parser.parse_args()
    
    try:
        output_path = generate_asset(
            prompt=args.prompt,
            output_path=args.output,
            gemini_api_key=args.gemini_key,
            removebg_api_key=args.removebg_key
        )
        print(f"Success! Asset generated: {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())