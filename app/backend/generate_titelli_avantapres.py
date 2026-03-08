#!/usr/bin/env python3
"""
Génération de la vidéo Titelli "Avant/Après" - Style équipe au bureau
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration

UPLOADS_DIR = '/app/backend/uploads'

def generate_video(prompt, output_path, duration=4):
    """Génère une vidéo avec Sora 2"""
    print(f"\n🎬 Génération: {output_path}")
    print(f"📝 Prompt: {prompt[:100]}...")
    
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
        print(f"❌ Échec génération")
        return None


def main():
    print("=" * 70)
    print("   GÉNÉRATION VIDÉO TITELLI - AVANT/APRÈS")
    print("=" * 70)
    
    scenes = [
        # AVANT - Les problèmes
        {
            "name": "avant_stress",
            "prompt": "A stressed small business owner in a messy office in Switzerland, papers everywhere, looking at a laptop with worried expression. The person is overwhelmed by paperwork and invoices scattered on the desk. Natural lighting, office environment in Lausanne. Realistic footage style.",
            "duration": 4
        },
        {
            "name": "avant_desorganise",
            "prompt": "A small shop owner manually writing in a paper notebook, surrounded by receipts and unorganized files. The counter is cluttered. Stressed expression on face. Swiss bakery or small store interior. Documentary style footage.",
            "duration": 4
        },
        {
            "name": "avant_clients_attente",
            "prompt": "Frustrated customers waiting in a long line at a small business counter. The owner is struggling with an old cash register. People checking their watches impatiently. Retail shop in Switzerland. Realistic commercial style.",
            "duration": 4
        },
        
        # TRANSITION - Titelli arrive
        {
            "name": "transition_titelli",
            "prompt": "A modern tablet or laptop screen showing a sleek dashboard interface with graphs and management tools. The screen transitions from chaotic data to organized clean interface. Blue and white color scheme. Close-up shot of the screen. Professional tech commercial style.",
            "duration": 4
        },
        
        # APRÈS - La solution
        {
            "name": "apres_organise",
            "prompt": "A happy business owner in a clean, modern office using a tablet with a modern dashboard. Everything is organized. The person is smiling and confident. Clean desk with just essential items. Swiss office interior. Bright natural lighting. Commercial advertisement style.",
            "duration": 4
        },
        {
            "name": "apres_clients_heureux",
            "prompt": "Happy customers being served efficiently at a modern point-of-sale system. The shop owner is smiling, customers are satisfied. Quick transactions. Modern Swiss retail store. Bright commercial footage style.",
            "duration": 4
        },
        {
            "name": "apres_succes",
            "prompt": "A business owner looking at growth charts on a laptop, smiling with satisfaction. The graphs show upward trends. Modern clean office in Switzerland. The person is relaxed and successful. Professional corporate video style.",
            "duration": 4
        }
    ]
    
    generated = []
    
    for scene in scenes:
        output_path = f"{UPLOADS_DIR}/titelli_{scene['name']}.mp4"
        result = generate_video(scene['prompt'], output_path, scene['duration'])
        if result:
            generated.append(result)
    
    print(f"\n{'=' * 70}")
    print(f"   TERMINÉ! {len(generated)}/{len(scenes)} vidéos générées")
    print(f"{'=' * 70}")
    
    for vid in generated:
        print(f"  - {vid}")
    
    return generated


if __name__ == "__main__":
    main()
