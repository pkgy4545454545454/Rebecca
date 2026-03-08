#!/usr/bin/env python3
"""
Vidéo Titelli Avant/Après V2 - POV Style avec même personnage
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
    print("   VIDÉO TITELLI V2 - POV STYLE")
    print("=" * 70)
    
    # IMPORTANT: Même personnage (femme brune, 30 ans, chemise bleue) pour la continuité
    character = "a brunette woman in her 30s wearing a blue blouse"
    
    scenes = [
        # AVANT - POV du bureau désorganisé
        {
            "name": "v2_avant_pov_bureau",
            "prompt": f"POV first-person view of hands typing on a laptop keyboard in a messy cluttered office. Papers and invoices scattered everywhere on the desk. The laptop screen shows confusing spreadsheets with errors. Stressed atmosphere, dim lighting. Realistic office footage. The hands belong to {character}.",
            "duration": 4
        },
        {
            "name": "v2_avant_stress",
            "prompt": f"Medium shot of {character} sitting at a messy desk looking stressed and overwhelmed. She is rubbing her temples with her hands, papers everywhere. Old computer with error messages. Swiss office interior. Realistic documentary style.",
            "duration": 4
        },
        
        # TRANSITION - Découverte de Titelli
        {
            "name": "v2_transition_decouverte",
            "prompt": f"POV first-person view of hands holding a smartphone, the screen shows a modern blue and gold app interface with the letter T logo. The person is in a bright modern office. Clean professional look. The fingers scroll through a sleek dashboard. Tech commercial style.",
            "duration": 4
        },
        
        # APRÈS - POV organisé avec Titelli
        {
            "name": "v2_apres_pov_dashboard",
            "prompt": f"POV first-person view of hands using a laptop showing a modern dark dashboard with colorful charts and graphs. Clean organized desk with just a coffee cup and plant. Bright natural lighting. Professional business software interface. The hands belong to {character}.",
            "duration": 4
        },
        {
            "name": "v2_apres_sourire",
            "prompt": f"Medium shot of {character} sitting at a clean organized modern desk, smiling confidently while looking at her laptop screen. The screen shows growth charts. Bright office with plants. She looks relaxed and successful. Professional corporate style.",
            "duration": 4
        }
    ]
    
    generated = []
    
    for scene in scenes:
        output_path = f"{UPLOADS_DIR}/titelli_{scene['name']}.mp4"
        
        # Skip si existe déjà
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
