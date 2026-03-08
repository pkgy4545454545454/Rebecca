#!/usr/bin/env python3
"""
Générateur de vidéo publicitaire Titelli - Avant/Après
Structure: 
- 20s AVANT: Prestataire qui galère (4 scènes x 5s)
- 5s TRANSITION: "Et un jour Titelli arriva..."
- 20s APRÈS: Prestataire heureux avec Titelli (4 scènes x 5s)
- 5s SLOGAN: "Avec Titelli tout est eazy"
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add path for emergentintegrations
sys.path.insert(0, os.path.abspath(''))

load_dotenv('/app/backend/.env')

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration

# Output directory
OUTPUT_DIR = "/app/backend/uploads"

# Scene definitions for the video
SCENES = [
    # ============ AVANT TITELLI (chaos, stress) ============
    {
        "id": "avant_1_stress",
        "name": "Avant 1 - Prestataire stressé",
        "prompt": "A stressed middle-aged male clothing store owner with dark hair and beard, wearing a casual shirt, sitting at a messy desk in his boutique. He's holding his head in frustration, papers and missed order notifications scattered everywhere. Warm indoor lighting, realistic cinematic style. The man looks overwhelmed and exhausted.",
        "duration": 5,
        "phase": "avant"
    },
    {
        "id": "avant_2_stock",
        "name": "Avant 2 - Stock désorganisé",
        "prompt": "Same middle-aged male store owner with dark hair and beard walking through his clothing boutique. Clothes are piled messily on shelves, boxes everywhere, disorganized inventory visible. He looks frustrated trying to find items. Messy retail environment, warm lighting, cinematic style.",
        "duration": 5,
        "phase": "avant"
    },
    {
        "id": "avant_3_clients",
        "name": "Avant 3 - Clients qui attendent",
        "prompt": "Inside a clothing boutique, three impatient customers waiting in line. The same middle-aged male store owner with dark hair and beard is searching through messy papers, looking stressed. Customers checking their watches and looking annoyed. Warm retail lighting, realistic style.",
        "duration": 5,
        "phase": "avant"
    },
    {
        "id": "avant_4_echec",
        "name": "Avant 4 - Commande ratée",
        "prompt": "The same middle-aged male store owner with dark hair and beard looking at his old computer screen showing error messages. He's shaking his head in disappointment. A customer in the background leaving the store unhappy. Warm indoor lighting, cinematic documentary style.",
        "duration": 5,
        "phase": "avant"
    },
    
    # ============ APRÈS TITELLI (succès, joie) ============
    {
        "id": "apres_1_sourire",
        "name": "Après 1 - Prestataire souriant",
        "prompt": "The same middle-aged male store owner with dark hair and beard, now smiling confidently as he walks towards his modern computer setup. The boutique is now clean and well-organized. Bright, warm lighting. He looks happy and relieved. Professional retail environment.",
        "duration": 5,
        "phase": "apres"
    },
    {
        "id": "apres_2_dashboard",
        "name": "Après 2 - Dashboard Titelli",
        "prompt": "Close-up of the same middle-aged male store owner with dark hair and beard looking at a modern dark-themed dashboard on his computer screen. Green notification badges, order confirmations, and positive metrics visible. He's smiling with satisfaction. Professional office lighting.",
        "duration": 5,
        "phase": "apres"
    },
    {
        "id": "apres_3_stock_organise",
        "name": "Après 3 - Stock bien organisé",
        "prompt": "The same clothing boutique now perfectly organized. The middle-aged male store owner with dark hair and beard proudly showing neatly arranged clothes on shelves, labeled boxes, everything in order. Clean modern retail aesthetic, bright warm lighting, satisfied expression.",
        "duration": 5,
        "phase": "apres"
    },
    {
        "id": "apres_4_cliente_heureuse",
        "name": "Après 4 - Cliente heureuse",
        "prompt": "A happy young woman customer entering the boutique, greeted by the smiling middle-aged male store owner with dark hair and beard. He hands her a beautifully packaged order that was ready early. Both smiling warmly. Bright, welcoming retail environment. Success and satisfaction.",
        "duration": 5,
        "phase": "apres"
    }
]


def generate_single_video(prompt: str, output_path: str, duration: int = 5) -> bool:
    """Generate a single video scene"""
    try:
        video_gen = OpenAIVideoGeneration(api_key=os.environ['EMERGENT_LLM_KEY'])
        
        print(f"  Generating ({duration}s)...")
        video_bytes = video_gen.text_to_video(
            prompt=prompt,
            model="sora-2",
            size="1280x720",
            duration=duration,
            max_wait_time=600
        )
        
        if video_bytes:
            video_gen.save_video(video_bytes, output_path)
            print(f"  ✅ Saved: {output_path}")
            return True
        else:
            print(f"  ❌ No video data returned")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("🎬 GÉNÉRATION VIDÉO PUB TITELLI - AVANT/APRÈS")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Scènes à générer: {len(SCENES)}")
    print()
    
    generated = []
    failed = []
    
    for i, scene in enumerate(SCENES, 1):
        print(f"\n[{i}/{len(SCENES)}] {scene['name']}")
        print(f"  Phase: {scene['phase'].upper()}")
        
        output_path = f"{OUTPUT_DIR}/pub_titelli_{scene['id']}.mp4"
        
        # Check if already exists
        if os.path.exists(output_path):
            print(f"  ⏭️ Already exists, skipping")
            generated.append(scene['id'])
            continue
        
        success = generate_single_video(
            prompt=scene['prompt'],
            output_path=output_path,
            duration=scene['duration']
        )
        
        if success:
            generated.append(scene['id'])
        else:
            failed.append(scene['id'])
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE GÉNÉRATION")
    print("=" * 60)
    print(f"✅ Générées: {len(generated)}/{len(SCENES)}")
    if failed:
        print(f"❌ Échouées: {len(failed)} - {failed}")
    
    # List generated files
    print("\n📁 Fichiers générés:")
    for scene_id in generated:
        filepath = f"{OUTPUT_DIR}/pub_titelli_{scene_id}.mp4"
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  - pub_titelli_{scene_id}.mp4 ({size_mb:.2f} MB)")
    
    return len(generated), len(failed)


if __name__ == "__main__":
    main()
