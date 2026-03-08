import sys
import os
from dotenv import load_dotenv

load_dotenv()

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration

def generateVideo(prompt, output_path, model="sora-2", size="1280x720", duration=8):
    video_gen = OpenAIVideoGeneration(api_key=os.environ['EMERGENT_LLM_KEY'])
    
    print(f"🎬 Génération vidéo en cours...")
    print(f"   Durée: {duration}s | Taille: {size}")
    
    video_bytes = video_gen.text_to_video(
        prompt=prompt,
        model=model,
        size=size,
        duration=duration,
        max_wait_time=600
    )
    
    if video_bytes:
        video_gen.save_video(video_bytes, output_path)
        return output_path
    return None


def main():
    # Prompt simplifié et safe
    prompt = """
    Abstract art animation on black background.
    
    Scene starts with golden sparkles floating gently in darkness.
    
    Smooth transition to colorful light ribbons - pink, purple, blue, cyan - 
    gracefully swirling and dancing in circular motion like aurora borealis.
    
    The colorful lights slowly spiral toward the center, getting brighter.
    
    Final frame: The colors fade to reveal a simple white letter T inside 
    a thin white circle, centered on black background. Clean minimalist logo.
    
    Style: Elegant, smooth motion, cinematic quality, relaxing ambient mood.
    """
    
    output_path = '/app/backend/uploads/titelli_presentation_v2.mp4'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    result = generateVideo(prompt, output_path, model="sora-2", size="1280x720", duration=8)
    
    if result:
        print(f'✅ Vidéo sauvegardée: {result}')
        print(f'📁 Taille: {os.path.getsize(result) / 1024 / 1024:.2f} MB')
    else:
        print('❌ Échec de la génération vidéo')


if __name__ == "__main__":
    main()
