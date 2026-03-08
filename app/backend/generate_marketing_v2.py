#!/usr/bin/env python3
"""
Titelli Marketing Media Generator v2
- Generates 30-second presentation video with French voiceover
- Generates 5 cool product advertisement videos
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/backend/marketing_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add path and load env
sys.path.insert(0, os.path.abspath(''))
from dotenv import load_dotenv
load_dotenv()

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration
from emergentintegrations.llm.openai import OpenAITextToSpeech

# Output directory
OUTPUT_DIR = "/app/backend/uploads/media_titelli/v2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# French voiceover text for the 30-second presentation
PRESENTATION_TEXT = """
Bienvenue sur Titelli, votre plateforme de référence pour découvrir les meilleurs prestataires de Lausanne.
Avec plus de six mille entreprises certifiées, trouvez facilement des services de beauté, bien-être, restauration et artisanat.
Réservez en quelques clics et profitez d'offres exclusives.
Titelli, l'excellence à portée de main.
"""

# Product video prompts - More dynamic and engaging
PRODUCT_VIDEOS = [
    {
        "name": "chocolat_suisse",
        "prompt": "Cinematic close-up shot of premium Swiss chocolate being crafted by artisan hands, golden lighting, melted chocolate dripping elegantly, luxurious atmosphere, slow motion, warm brown tones, professional food photography style, 4K quality",
        "duration": 4
    },
    {
        "name": "montre_luxe", 
        "prompt": "Dramatic reveal of a luxury Swiss watch rotating slowly on black velvet, golden hour lighting reflecting on polished metal, precision craftsmanship visible, macro lens detail on gears, cinematic slow motion, premium advertising style",
        "duration": 4
    },
    {
        "name": "soins_beaute",
        "prompt": "Elegant spa treatment scene with woman receiving facial massage, soft natural lighting, rose petals and candles, steam rising gently, serene atmosphere, professional beauty advertisement style, calming pastel colors",
        "duration": 4
    },
    {
        "name": "restaurant_gourmet",
        "prompt": "Chef plating an exquisite gourmet dish in upscale restaurant kitchen, dramatic top-down shot, steam rising from fresh ingredients, precise movements, warm kitchen lighting, professional culinary video style, appetizing presentation",
        "duration": 4
    },
    {
        "name": "vin_premium",
        "prompt": "Elegant wine tasting scene in Swiss vineyard at golden hour, burgundy wine being poured into crystal glass, vineyard landscape in background, sophisticated atmosphere, slow motion liquid pour, luxury lifestyle advertising style",
        "duration": 4
    }
]

# Presentation video segments prompts
PRESENTATION_SEGMENTS = [
    {
        "name": "segment_1_intro",
        "prompt": "Modern smartphone displaying elegant dark-themed mobile app interface with golden accents, user scrolling through business listings, clean UI design, professional app demonstration style, soft lighting",
        "duration": 4
    },
    {
        "name": "segment_2_explore",
        "prompt": "Split screen montage showing diverse Lausanne businesses: cozy cafe interior, modern beauty salon, artisan workshop, professional service scenes, warm natural lighting, dynamic transitions feel",
        "duration": 4
    },
    {
        "name": "segment_3_booking",
        "prompt": "Close-up of finger tapping reservation button on elegant mobile app interface, confirmation animation appearing, satisfied customer smile in background, modern clean design, success moment",
        "duration": 4
    }
]


async def generate_french_voiceover():
    """Generate French voiceover using OpenAI TTS"""
    logger.info("🎙️ Generating French voiceover...")
    
    try:
        tts = OpenAITextToSpeech(api_key=os.environ['EMERGENT_LLM_KEY'])
        
        audio_bytes = await tts.generate_speech(
            text=PRESENTATION_TEXT.strip(),
            model="tts-1-hd",
            voice="nova",  # Energetic and professional
            speed=0.95,    # Slightly slower for French clarity
            response_format="mp3"
        )
        
        output_path = f"{OUTPUT_DIR}/voiceover_french.mp3"
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        
        logger.info(f"✅ Voiceover saved: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"❌ Voiceover generation failed: {e}")
        return None


def generate_video(prompt, output_name, duration=4):
    """Generate a single video using Sora 2"""
    logger.info(f"🎬 Generating video: {output_name}")
    
    try:
        video_gen = OpenAIVideoGeneration(api_key=os.environ['EMERGENT_LLM_KEY'])
        
        video_bytes = video_gen.text_to_video(
            prompt=prompt,
            model="sora-2",
            size="1280x720",
            duration=duration,
            max_wait_time=900
        )
        
        if video_bytes:
            output_path = f"{OUTPUT_DIR}/{output_name}.mp4"
            video_gen.save_video(video_bytes, output_path)
            logger.info(f"✅ Video saved: {output_path}")
            return output_path
        else:
            logger.error(f"❌ No video bytes returned for {output_name}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Video generation failed for {output_name}: {e}")
        return None


async def generate_all_product_videos():
    """Generate all 5 product videos"""
    logger.info("=" * 60)
    logger.info("🎥 GENERATING PRODUCT VIDEOS (v2 - More Dynamic)")
    logger.info("=" * 60)
    
    results = []
    for i, video in enumerate(PRODUCT_VIDEOS, 1):
        logger.info(f"\n📹 Video {i}/5: {video['name']}")
        result = generate_video(
            prompt=video['prompt'],
            output_name=f"produit_{video['name']}_v2",
            duration=video['duration']
        )
        results.append((video['name'], result))
        
    return results


async def generate_presentation_segments():
    """Generate presentation video segments"""
    logger.info("=" * 60)
    logger.info("🎬 GENERATING PRESENTATION SEGMENTS")
    logger.info("=" * 60)
    
    results = []
    for i, segment in enumerate(PRESENTATION_SEGMENTS, 1):
        logger.info(f"\n📹 Segment {i}/3: {segment['name']}")
        result = generate_video(
            prompt=segment['prompt'],
            output_name=f"presentation_{segment['name']}_v2",
            duration=segment['duration']
        )
        results.append((segment['name'], result))
        
    return results


async def main():
    """Main function to generate all marketing materials"""
    logger.info("=" * 60)
    logger.info("🚀 TITELLI MARKETING MEDIA GENERATOR v2")
    logger.info(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Step 1: Generate French voiceover
    voiceover_path = await generate_french_voiceover()
    
    # Step 2: Generate product videos
    product_results = await generate_all_product_videos()
    
    # Step 3: Generate presentation segments
    presentation_results = await generate_presentation_segments()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 GENERATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Voiceover: {'✅' if voiceover_path else '❌'}")
    
    logger.info("\nProduct Videos:")
    for name, path in product_results:
        logger.info(f"  - {name}: {'✅' if path else '❌'}")
    
    logger.info("\nPresentation Segments:")
    for name, path in presentation_results:
        logger.info(f"  - {name}: {'✅' if path else '❌'}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"✅ Generation completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
