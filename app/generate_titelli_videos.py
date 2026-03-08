#!/usr/bin/env python3
"""
Génération des vidéos Avant/Après pour Titelli
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(''))
load_dotenv('/app/backend/.env')

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration


def generate_video(prompt: str, output_path: str, duration: int = 12):
    """Génère une vidéo avec Sora 2"""
    print(f"\n🎬 Génération vidéo: {output_path}")
    print(f"📝 Prompt: {prompt[:100]}...")
    print(f"⏱️  Durée: {duration} secondes")
    print("⏳ Cela peut prendre 3-5 minutes...")
    
    video_gen = OpenAIVideoGeneration(api_key=os.environ['EMERGENT_LLM_KEY'])
    
    video_bytes = video_gen.text_to_video(
        prompt=prompt,
        model="sora-2",
        size="1280x720",
        duration=duration,
        max_wait_time=600
    )
    
    if video_bytes:
        video_gen.save_video(video_bytes, output_path)
        print(f"✅ Vidéo sauvegardée: {output_path}")
        return output_path
    else:
        print(f"❌ Échec de la génération")
        return None


def main():
    # === VIDÉO 1: AVANT - Commercial stressé ===
    prompt_avant = """Cinematic office scene. A tall brunette businessman in his 30s wearing glasses sits alone at his desk in a commercial office. He looks extremely stressed, disoriented and anxious. He's frantically looking at his computer screen showing declining charts and failed orders with red numbers going down. His desk is messy with scattered papers. He rubs his forehead in despair, loosens his tie nervously. The lighting is cold and harsh fluorescent. His face shows worry and panic. He sighs heavily, puts his head in his hands. Realistic corporate office environment with gray walls. No other people in the scene. Tense atmosphere, documentary style, shallow depth of field focused on the stressed man."""

    # === VIDÉO 2: APRÈS - Commercial heureux ===
    prompt_apres = """Cinematic office scene transformation. The same tall brunette businessman with glasses now sits confidently at his clean organized desk, genuinely smiling and relaxed. His computer screen shows green charts going up, successful orders being completed on time. The office is bright with warm natural sunlight streaming through windows. Happy satisfied customers enter his office to shake his hand and thank him warmly. He stands up proudly, greeting them with a big authentic smile. The atmosphere is upbeat and positive. Modern bright office with plants. Celebratory mood, documentary style. The man looks accomplished, relieved and genuinely happy. Professional success story aesthetic."""

    print("=" * 60)
    print("🎥 GÉNÉRATION VIDÉOS TITELLI - AVANT/APRÈS")
    print("=" * 60)
    
    # Générer vidéo AVANT
    video1 = generate_video(
        prompt=prompt_avant,
        output_path="/app/backend/uploads/TITELLI_VIDEO_AVANT.mp4",
        duration=12
    )
    
    # Générer vidéo APRÈS
    video2 = generate_video(
        prompt=prompt_apres,
        output_path="/app/backend/uploads/TITELLI_VIDEO_APRES.mp4",
        duration=12
    )
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    if video1:
        print(f"✅ Vidéo AVANT: {video1}")
    else:
        print("❌ Vidéo AVANT: Échec")
    
    if video2:
        print(f"✅ Vidéo APRÈS: {video2}")
    else:
        print("❌ Vidéo APRÈS: Échec")


if __name__ == "__main__":
    main()
