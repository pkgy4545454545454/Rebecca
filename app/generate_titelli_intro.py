#!/usr/bin/env python3
"""
Génération de la vidéo d'animation Titelli avec Sora 2
Style: Picsart typing effect + Logo œil qui saute + Fermeture des aiguilles
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(''))
load_dotenv('/app/backend/.env')

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration


def generate_titelli_intro():
    """Génère la vidéo intro Titelli"""
    
    # Prompt ultra-détaillé pour l'animation
    prompt = """Cinematic logo animation on pure black background. 

Scene 1 (0-4s): The word "Titelli" appears letter by letter with elegant typing effect. Each white letter materializes with a subtle glow and soft bounce. The letters are in classic serif font (like Georgia), white with subtle luminous glow effect. A blinking cursor follows each letter appearing.

Scene 2 (4-8s): After "Titell" is typed, pause. Then a stylized eye logo (circular, with blue-brown iris gradient and black clock hands inside) drops from above with playful bouncing animation. It lands perfectly on top of the letter "i", replacing its dot. The eye has a magical sparkle effect when it lands.

Scene 3 (8-12s): The two clock hands inside the eye slowly rotate and meet at the 12 o'clock position, creating a closing eye effect. The iris seems to close like eyelids meeting. A soft blue glow pulses around the eye logo.

Final: The complete "Titelli" logo with the eye as the dot of final "i" stays centered. Elegant, minimalist, professional luxury brand aesthetic. Colors: white text, black background, blue accent glow. Smooth 60fps animation, premium quality."""

    output_path = "/app/backend/uploads/TITELLI_INTRO_ANIMATION.mp4"
    
    print("=" * 60)
    print("🎬 GÉNÉRATION VIDÉO INTRO TITELLI")
    print("=" * 60)
    print(f"📝 Durée: 12 secondes")
    print(f"📐 Résolution: 1280x720 HD")
    print("⏳ Cela peut prendre 3-5 minutes...")
    print("")
    
    try:
        video_gen = OpenAIVideoGeneration(api_key=os.environ['EMERGENT_LLM_KEY'])
        
        video_bytes = video_gen.text_to_video(
            prompt=prompt,
            model="sora-2",
            size="1280x720",
            duration=12,
            max_wait_time=600
        )
        
        if video_bytes:
            video_gen.save_video(video_bytes, output_path)
            print(f"✅ Vidéo sauvegardée: {output_path}")
            return output_path
        else:
            print("❌ Échec de la génération")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return None


if __name__ == "__main__":
    result = generate_titelli_intro()
    if result:
        print(f"\n🎉 Animation créée avec succès!")
        print(f"📥 Téléchargez: https://image-fix-demo.preview.emergentagent.com/api/uploads/TITELLI_INTRO_ANIMATION.mp4")
