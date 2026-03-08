#!/usr/bin/env python3
"""
Vidéo Titelli V4 - Haute Qualité - Avant/Après avec même personnage
Focus sur les vrais écrans Titelli
"""
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration

UPLOADS_DIR = '/app/backend/uploads'

def generate_video(prompt, output_path, duration=8):
    """Génère une vidéo HD avec Sora 2"""
    print(f"\n🎬 Génération HQ: {output_path}")
    print(f"📝 {prompt[:80]}...")
    
    video_gen = OpenAIVideoGeneration(api_key=os.environ['EMERGENT_LLM_KEY'])
    
    video_bytes = video_gen.text_to_video(
        prompt=prompt,
        model="sora-2",
        size="1280x720",
        duration=duration,
        max_wait_time=900
    )
    
    if video_bytes:
        video_gen.save_video(video_bytes, output_path)
        print(f"✅ Vidéo HQ sauvegardée!")
        return output_path
    return None


def main():
    print("=" * 70)
    print("   VIDÉO TITELLI V4 - HAUTE QUALITÉ")
    print("=" * 70)
    
    # MÊME personnage pour continuité avant/après
    person = "a young professional Swiss woman with brown hair, wearing a white shirt"
    
    scenes = [
        # AVANT - Bureau désorganisé, stress
        {
            "name": "v4_avant",
            "prompt": f"Cinematic shot of {person} sitting at a messy cluttered desk in a dim office. She looks stressed, rubbing her eyes, surrounded by papers and sticky notes. Old computer screen shows spreadsheets with red numbers. She sighs in frustration. Realistic corporate documentary style. 4K quality.",
            "duration": 8
        },
        
        # APRÈS - Bureau moderne, succès avec Titelli
        {
            "name": "v4_apres", 
            "prompt": f"Cinematic shot of {person} sitting at a clean modern white desk in a bright office with plants. She smiles confidently while looking at her MacBook screen showing a dark professional dashboard with colorful charts. She nods with satisfaction and picks up her coffee cup. Bright natural sunlight. Professional corporate commercial style. 4K quality.",
            "duration": 8
        }
    ]
    
    generated = []
    
    for scene in scenes:
        output_path = f"{UPLOADS_DIR}/titelli_{scene['name']}.mp4"
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 200000:
            print(f"⏭️ Existe déjà: {output_path}")
            generated.append(output_path)
            continue
        
        result = generate_video(scene['prompt'], output_path, scene['duration'])
        if result:
            generated.append(result)
    
    print(f"\n{'=' * 70}")
    print(f"   {len(generated)} vidéos HQ générées")
    for v in generated:
        print(f"   - {v}")
    print("=" * 70)
    
    return generated


if __name__ == "__main__":
    main()
