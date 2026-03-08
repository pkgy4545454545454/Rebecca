#!/usr/bin/env python3
"""
Generate remaining product videos - One at a time
"""
import os
import sys
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.abspath(''))
from dotenv import load_dotenv
load_dotenv()

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration

OUTPUT_DIR = "/app/backend/uploads/media_titelli/v2"

# Videos that need to be generated
REMAINING_VIDEOS = [
    {
        "name": "soins_beaute",
        "prompt": "Elegant spa treatment scene with woman receiving relaxing facial massage, soft natural lighting through windows, white fluffy towels, fresh flowers, steam rising gently, serene wellness atmosphere, professional beauty salon advertisement"
    },
    {
        "name": "restaurant_gourmet",
        "prompt": "Professional chef carefully plating an artistic gourmet dish, warm kitchen lighting, fresh colorful ingredients, precision knife work, steam rising, sophisticated culinary presentation, fine dining restaurant scene"
    },
    {
        "name": "vin_premium",
        "prompt": "Premium red wine being poured elegantly into crystal wine glass, Swiss vineyard sunset in background, golden light reflections, sophisticated wine tasting atmosphere, luxury lifestyle"
    },
    {
        "name": "presentation_app",
        "prompt": "Modern elegant mobile application interface showing business directory with gold and dark theme, smooth scrolling animation, professional UI design, app demonstration mockup style"
    },
    {
        "name": "presentation_services",
        "prompt": "Montage of premium local services in action: hair salon stylist working, massage therapist, chef cooking, watchmaker at work, warm professional lighting, quick dynamic cuts"
    },
    {
        "name": "presentation_booking",
        "prompt": "Customer hand using elegant smartphone app to book appointment, finger tapping confirm button, happy confirmation animation, modern dark themed UI, success moment celebration"
    }
]

def generate_single_video(name, prompt):
    """Generate a single video"""
    logger.info(f"🎬 Starting generation: {name}")
    logger.info(f"   Prompt: {prompt[:80]}...")
    
    try:
        # Create new instance for each video
        video_gen = OpenAIVideoGeneration(api_key=os.environ['EMERGENT_LLM_KEY'])
        
        video_bytes = video_gen.text_to_video(
            prompt=prompt,
            model="sora-2",
            size="1280x720",
            duration=4,
            max_wait_time=900  # 15 minutes max
        )
        
        if video_bytes:
            output_path = f"{OUTPUT_DIR}/produit_{name}_v2.mp4"
            video_gen.save_video(video_bytes, output_path)
            logger.info(f"✅ SUCCESS: {output_path}")
            return output_path
        else:
            logger.error(f"❌ FAILED: No video bytes for {name}")
            return None
            
    except Exception as e:
        logger.error(f"❌ ERROR for {name}: {str(e)}")
        return None

if __name__ == "__main__":
    import sys
    
    # Allow selecting specific video by index
    if len(sys.argv) > 1:
        idx = int(sys.argv[1])
        if 0 <= idx < len(REMAINING_VIDEOS):
            video = REMAINING_VIDEOS[idx]
            generate_single_video(video['name'], video['prompt'])
        else:
            print(f"Index out of range. Valid: 0-{len(REMAINING_VIDEOS)-1}")
    else:
        # Generate all
        for i, video in enumerate(REMAINING_VIDEOS):
            logger.info(f"\n{'='*60}")
            logger.info(f"Video {i+1}/{len(REMAINING_VIDEOS)}")
            generate_single_video(video['name'], video['prompt'])
