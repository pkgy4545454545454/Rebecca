#!/usr/bin/env python3
"""
Titelli Media Generator - Sora 2 Video Generation
Generates promotional videos for Titelli platform
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration

OUTPUT_DIR = "/app/backend/uploads/media_titelli"

def generate_video(prompt, output_filename, duration=4, size="1280x720"):
    """Generate a single video with Sora 2"""
    print(f"\n🎬 Generating: {output_filename}")
    print(f"   Prompt: {prompt[:80]}...")
    print(f"   Duration: {duration}s, Size: {size}")
    
    try:
        video_gen = OpenAIVideoGeneration(api_key=os.environ['EMERGENT_LLM_KEY'])
        
        video_bytes = video_gen.text_to_video(
            prompt=prompt,
            model="sora-2",
            size=size,
            duration=duration,
            max_wait_time=600
        )
        
        if video_bytes:
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            video_gen.save_video(video_bytes, output_path)
            print(f"   ✅ Saved: {output_path}")
            return output_path
        else:
            print(f"   ❌ Failed: No video bytes returned")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Videos to generate
    videos = [
        # 5 Product promo videos (4 seconds each)
        {
            "prompt": "Elegant slow-motion shot of a luxury Swiss watch rotating on a deep blue (#0047AB) velvet surface with golden (#D4AF37) light reflections, premium product cinematography, dramatic lighting, high-end advertising quality",
            "filename": "video_produit_montre.mp4",
            "duration": 4,
            "size": "1280x720"
        },
        {
            "prompt": "Cinematic close-up of premium chocolate being unwrapped, revealing artisan Swiss confectionery with gold foil, deep blue background, luxurious atmosphere, smooth slow motion, professional food advertising",
            "filename": "video_produit_chocolat.mp4",
            "duration": 4,
            "size": "1280x720"
        },
        {
            "prompt": "Elegant luxury skincare serum drop falling in slow motion onto premium glass bottle with gold cap, deep blue marble background, beauty product cinematography, soft lighting, high-end cosmetics advertising",
            "filename": "video_produit_beaute.mp4",
            "duration": 4,
            "size": "1280x720"
        },
        {
            "prompt": "Premium wine being poured into crystal glass in slow motion, elegant golden lighting, professional beverage cinematography, luxury atmosphere, deep blue background with gold accents",
            "filename": "video_produit_vin.mp4",
            "duration": 4,
            "size": "1280x720"
        },
        {
            "prompt": "Elegant jewelry display with diamond ring rotating slowly on midnight blue (#0047AB) velvet, golden spotlight reflections, luxury product cinematography, professional advertising quality",
            "filename": "video_produit_bijou.mp4",
            "duration": 4,
            "size": "1280x720"
        },
    ]
    
    results = []
    for video in videos:
        result = generate_video(
            video["prompt"],
            video["filename"],
            video["duration"],
            video["size"]
        )
        results.append({"filename": video["filename"], "success": result is not None})
    
    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['filename']}")
    
    return results


if __name__ == "__main__":
    main()
