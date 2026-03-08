#!/usr/bin/env python3
"""
Titelli - Generate presentation video for providers (Before/After Titelli)
30 seconds video showcasing the transformation
"""

import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration

OUTPUT_DIR = "/app/backend/uploads/media_titelli"

def generate_video(prompt, output_filename, duration=12, size="1280x720"):
    """Generate a single video with Sora 2"""
    print(f"\n🎬 Generating: {output_filename}")
    print(f"   Prompt: {prompt[:100]}...")
    print(f"   Duration: {duration}s, Size: {size}")
    
    try:
        video_gen = OpenAIVideoGeneration(api_key=os.environ['EMERGENT_LLM_KEY'])
        
        video_bytes = video_gen.text_to_video(
            prompt=prompt,
            model="sora-2",
            size=size,
            duration=duration,
            max_wait_time=900
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
    
    # Video presentation before/after - split into 3 parts (12s each = 36s total, we'll trim to 30s)
    videos = [
        {
            "prompt": "Cinematic opening shot of a small struggling local business storefront in Lausanne Switzerland, empty street, cloudy day, sad atmosphere, then camera slowly pans to reveal smartphone with 'Titelli' logo glowing in deep blue (#0047AB) and gold (#D4AF37), hope emerging, professional cinematography",
            "filename": "video_presentation_part1.mp4",
            "duration": 12,
            "size": "1280x720"
        },
        {
            "prompt": "Cinematic transformation sequence showing local business becoming successful with Titelli platform, customers flowing in, golden warm lighting, busy happy atmosphere, notifications appearing on smartphone with orders, professional business growth visualization, deep blue and gold color theme",
            "filename": "video_presentation_part2.mp4",
            "duration": 12,
            "size": "1280x720"
        },
        {
            "prompt": "Triumphant finale shot of thriving local business in Lausanne, happy entrepreneur checking Titelli dashboard showing growth metrics, golden hour lighting, deep blue (#0047AB) and gold (#D4AF37) color accents, premium success story cinematography, ending with Titelli logo reveal",
            "filename": "video_presentation_part3.mp4",
            "duration": 8,
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
    print("PRESENTATION VIDEOS COMPLETE")
    print("="*60)
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['filename']}")


if __name__ == "__main__":
    main()
