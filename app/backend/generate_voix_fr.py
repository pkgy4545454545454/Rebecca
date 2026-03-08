#!/usr/bin/env python3
"""
Génère la voix française pour la vidéo Titelli avec OpenAI TTS
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('/app/backend/.env')

UPLOADS_DIR = '/app/backend/uploads'

# Narrations pour chaque partie
NARRATIONS = {
    "avant": "Avant Titelli... la gestion de votre entreprise était un véritable casse-tête. Des papiers partout, des heures perdues à chercher des informations, des clients qui attendent...",
    "transition": "Découvrez Titelli, votre solution tout-en-un pour gérer votre entreprise facilement.",
    "apres": "Après Titelli, tout change ! Un tableau de bord intuitif, des données organisées, et enfin du temps pour ce qui compte vraiment : vos clients et votre succès."
}

def generate_audio(text, output_path, voice="nova"):
    """Génère un fichier audio avec OpenAI TTS"""
    print(f"🎤 Génération audio: {output_path}")
    
    client = OpenAI(
        api_key=os.environ['EMERGENT_LLM_KEY'],
        base_url="https://integrations.emergentagent.com/llm/openai/v1"
    )
    
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,  # nova est une voix féminine naturelle
        input=text,
        response_format="mp3"
    )
    
    response.stream_to_file(output_path)
    print(f"✅ Audio sauvegardé: {output_path}")
    return output_path


def main():
    print("=" * 70)
    print("   GÉNÉRATION VOIX FRANÇAISE - TITELLI")
    print("=" * 70)
    
    # Générer les audios
    audio_avant = generate_audio(NARRATIONS["avant"], f"{UPLOADS_DIR}/titelli_voix_avant.mp3")
    audio_transition = generate_audio(NARRATIONS["transition"], f"{UPLOADS_DIR}/titelli_voix_transition.mp3")
    audio_apres = generate_audio(NARRATIONS["apres"], f"{UPLOADS_DIR}/titelli_voix_apres.mp3")
    
    print("\n✅ Tous les audios générés!")
    return [audio_avant, audio_transition, audio_apres]


if __name__ == "__main__":
    main()
