#!/usr/bin/env python3
"""
Vidéo Titelli V3 - Avec vrais écrans du site
Génère des vidéos POV puis overlay les vrais screenshots Titelli
"""
import os
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
    print("   VIDÉO TITELLI V3 - VRAIS ÉCRANS")
    print("=" * 70)
    
    # Personnage: même femme brune 30 ans chemise bleue
    character = "a brunette businesswoman in her 30s with blue blouse"
    
    scenes = [
        # AVANT - Vue sur écran chaotique (on remplacera l'écran par un vrai)
        {
            "name": "v3_avant_ecran",
            "prompt": f"POV first-person view looking at a laptop screen in a dark messy office. The screen is bright and glowing, showing a spreadsheet interface. Papers scattered on desk. Dim lighting, stressed atmosphere. The view slightly shakes as if frustrated. Realistic office footage.",
            "duration": 4
        },
        {
            "name": "v3_avant_personne", 
            "prompt": f"Close-up of {character} looking frustrated at her laptop screen in a messy office. She sighs and rubs her forehead. Papers everywhere. The laptop screen reflects on her face. Documentary style realistic footage.",
            "duration": 4
        },
        
        # APRÈS - Vue sur écran Titelli (on remplacera par le vrai dashboard)
        {
            "name": "v3_apres_ecran",
            "prompt": f"POV first-person view looking at a modern laptop screen in a bright clean office. The screen shows a dark professional dashboard with colorful charts and graphs. Clean desk with coffee cup. Natural daylight. Smooth slight camera movement. Tech commercial style.",
            "duration": 4
        },
        {
            "name": "v3_apres_personne",
            "prompt": f"Close-up of {character} smiling confidently while looking at her laptop screen in a clean modern office. She nods approvingly and takes a sip of coffee. The colorful dashboard reflects on her face. Professional corporate video style. Bright natural lighting.",
            "duration": 4
        },
        
        # Transition - Scroll sur le vrai site
        {
            "name": "v3_scroll_site",
            "prompt": f"Screen recording style video of a modern dark website with gold accents. The cursor moves smoothly, clicking on navigation menu items. The website shows cards with images and ratings. Smooth scrolling animation. Professional web demo style.",
            "duration": 4
        }
    ]
    
    generated = []
    
    for scene in scenes:
        output_path = f"{UPLOADS_DIR}/titelli_{scene['name']}.mp4"
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
            print(f"⏭️ Existe: {output_path}")
            generated.append(output_path)
            continue
        
        result = generate_video(scene['prompt'], output_path, scene['duration'])
        if result:
            generated.append(result)
    
    print(f"\n{'=' * 70}")
    print(f"   {len(generated)} vidéos générées")
    print(f"{'=' * 70}")
    
    return generated


if __name__ == "__main__":
    main()
