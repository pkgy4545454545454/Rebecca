#!/usr/bin/env python3
"""
Génération de la vidéo Titelli "Avant/Après" - Scènes restantes
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
    print(f"📝 Prompt: {prompt[:80]}...")
    
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
    print("   GÉNÉRATION VIDÉO TITELLI - AVANT/APRÈS (SUITE)")
    print("=" * 70)
    
    # Scènes restantes à générer
    scenes = [
        # AVANT - Clients frustrés
        {
            "name": "avant_clients_attente",
            "prompt": "Frustrated customers waiting in a long line at a small business counter. The owner is struggling with an old cash register. People checking their watches impatiently. Retail shop in Switzerland. Realistic commercial style.",
            "duration": 4
        },
        
        # TRANSITION - Titelli arrive
        {
            "name": "transition_titelli",
            "prompt": "A modern tablet screen showing a sleek blue dashboard interface with graphs, charts and management tools. Clean modern UI design. The screen glows with professional business software. Close-up shot. Tech commercial style.",
            "duration": 4
        },
        
        # APRÈS - La solution
        {
            "name": "apres_organise",
            "prompt": "A happy business owner in a clean modern office using a tablet with a dashboard. Everything is organized and tidy. The person is smiling confidently. Clean desk, natural bright lighting. Swiss office. Commercial advertisement style.",
            "duration": 4
        },
        {
            "name": "apres_clients_heureux",
            "prompt": "Happy customers being served quickly and efficiently at a modern store. The shop owner is smiling, customers are satisfied and happy. Fast smooth transactions. Modern Swiss retail store. Bright commercial footage.",
            "duration": 4
        },
        {
            "name": "apres_succes",
            "prompt": "A successful business owner looking at growth charts on a laptop showing upward trends. The person is relaxed, smiling with satisfaction. Modern clean office with plants. Professional corporate video style. Success and achievement.",
            "duration": 4
        }
    ]
    
    generated = []
    
    # Ajouter les vidéos déjà générées
    existing = [
        f"{UPLOADS_DIR}/titelli_avant_stress.mp4",
        f"{UPLOADS_DIR}/titelli_avant_desorganise.mp4"
    ]
    for e in existing:
        if os.path.exists(e):
            generated.append(e)
            print(f"✅ Déjà généré: {e}")
    
    for scene in scenes:
        output_path = f"{UPLOADS_DIR}/titelli_{scene['name']}.mp4"
        
        # Skip si déjà généré
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
            print(f"⏭️ Existe déjà: {output_path}")
            generated.append(output_path)
            continue
        
        result = generate_video(scene['prompt'], output_path, scene['duration'])
        if result:
            generated.append(result)
    
    print(f"\n{'=' * 70}")
    print(f"   TERMINÉ! {len(generated)} vidéos au total")
    print(f"{'=' * 70}")
    
    for vid in generated:
        print(f"  - {vid}")
    
    return generated


if __name__ == "__main__":
    main()
