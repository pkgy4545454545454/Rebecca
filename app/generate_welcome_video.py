#!/usr/bin/env python3
"""
Génération vidéo d'accueil Titelli - Couple marchant à Lausanne
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(''))

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration

load_dotenv('/app/backend/.env')

def generate_welcome_video():
    """Génère la vidéo d'accueil - Lausanne avec couple qui marche"""
    
    prompt = """Cinematic aerial establishing shot of Lausanne city waterfront promenade along Lake Geneva. 

A romantic couple walks hand in hand FROM BEHIND, walking AWAY from the camera along the lakeside path, passing by local shops and cafes with terraces. The man is wearing an elegant dark coat. We see their backs as they stroll together towards the beautiful view of the Swiss Alps mountains in the background across the shimmering blue lake water.

Local merchants and shop owners visible in their storefronts. Warm golden hour sunlight, European charm atmosphere. The couple walks away from the camera into the scenic landscape.

Smooth dolly camera movement following them from behind. Premium lifestyle advertisement quality. Photorealistic 4K cinematic footage. Swiss lakeside city ambiance."""
    
    output_path = '/app/backend/uploads/video_accueil_couple_lausanne.mp4'
    
    print("🎬 Génération de la vidéo d'accueil...")
    print(f"📍 Lausanne - Couple marchant au bord du lac avec vue montagnes")
    
    video_gen = OpenAIVideoGeneration(api_key=os.environ['EMERGENT_LLM_KEY'])
    
    video_bytes = video_gen.text_to_video(
        prompt=prompt,
        model="sora-2",
        size="1280x720",
        duration=8,
        max_wait_time=900
    )
    
    if video_bytes:
        video_gen.save_video(video_bytes, output_path)
        print(f"✅ Vidéo générée avec succès: {output_path}")
        return output_path
    else:
        print("❌ Échec de la génération vidéo")
        return None


if __name__ == "__main__":
    result = generate_welcome_video()
    if result:
        print(f"\n🔗 Lien: https://image-fix-demo.preview.emergentagent.com/api/uploads/video_accueil_couple_lausanne.mp4")
