#!/usr/bin/env python3
"""
Vidéo Titelli V5 - Version Premium
Approche: Vrais écrans Titelli + Clips AI humains séparés
"""
import os
import subprocess
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv('/app/backend/.env')

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration

UPLOADS_DIR = '/app/backend/uploads'
V5_DIR = f'{UPLOADS_DIR}/v5'

# Créer le dossier V5
os.makedirs(V5_DIR, exist_ok=True)

def capture_titelli_screenshots():
    """Capture de vrais screenshots HD de Titelli.com"""
    print("\n📸 Capture des écrans Titelli.com...")
    
    screenshots = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=2  # Retina pour HD
        )
        page = context.new_page()
        
        # Pages à capturer - utiliser l'URL preview
        BASE_URL = 'https://image-fix-demo.preview.emergentagent.com'
        pages_to_capture = [
            (f'{BASE_URL}', 'home', 'Page d\'accueil'),
            (f'{BASE_URL}/prestataires', 'prestataires', 'Liste prestataires'),
            (f'{BASE_URL}/boutiques', 'boutiques', 'Boutiques'),
        ]
        
        for url, name, desc in pages_to_capture:
            try:
                print(f"  📷 {desc}...")
                page.goto(url, wait_until='networkidle', timeout=30000)
                time.sleep(2)
                
                # Screenshot pleine page
                screenshot_path = f'{V5_DIR}/screen_{name}.png'
                page.screenshot(path=screenshot_path, full_page=False)
                screenshots.append((screenshot_path, name, desc))
                print(f"    ✅ {screenshot_path}")
                
            except Exception as e:
                print(f"    ❌ Erreur: {e}")
        
        browser.close()
    
    return screenshots


def generate_ai_clips():
    """Génère les clips AI pour les scènes humaines uniquement"""
    print("\n🎬 Génération des clips AI (scènes humaines)...")
    
    video_gen = OpenAIVideoGeneration(api_key=os.environ['EMERGENT_LLM_KEY'])
    
    # MÊME personnage pour avant/après
    person = "a young Swiss woman with medium-length brown hair, wearing a white blouse, professional look"
    
    clips = [
        {
            "name": "v5_human_before",
            "prompt": f"POV first-person shot looking down at hands on a cluttered desk with papers, sticky notes, receipts scattered everywhere. {person}'s reflection visible in a dark computer screen showing spreadsheets. She sighs and rubs her temples in frustration. Dim office lighting. Documentary style. 4K cinematic.",
            "duration": 8
        },
        {
            "name": "v5_human_after",
            "prompt": f"POV first-person shot of {person} sitting relaxed in a bright modern office with plants. She smiles contentedly while holding a coffee cup, occasionally glancing at her MacBook. Bright natural sunlight streaming through windows. She gives a satisfied thumbs up. Professional commercial style. 4K.",
            "duration": 8
        },
        {
            "name": "v5_transition",
            "prompt": f"Smooth transition effect: Screen showing confusing spreadsheet data transforms into a clean modern dark dashboard interface with colorful charts and analytics. Glowing blue particles and light rays. Professional tech commercial aesthetic. 4K quality.",
            "duration": 4
        }
    ]
    
    generated = []
    
    for clip in clips:
        output_path = f'{V5_DIR}/{clip["name"]}.mp4'
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 200000:
            print(f"  ⏭️ Existe: {clip['name']}")
            generated.append(output_path)
            continue
        
        print(f"  🎥 {clip['name']}...")
        try:
            video_bytes = video_gen.text_to_video(
                prompt=clip['prompt'],
                model="sora-2",
                size="1280x720",
                duration=clip['duration'],
                max_wait_time=600
            )
            
            if video_bytes:
                video_gen.save_video(video_bytes, output_path)
                generated.append(output_path)
                print(f"    ✅ Généré!")
            else:
                print(f"    ❌ Échec génération")
        except Exception as e:
            print(f"    ❌ Erreur: {e}")
    
    return generated


def create_screen_animations(screenshots):
    """Crée des animations fluides des screenshots avec FFmpeg"""
    print("\n🎞️ Création des animations d'écran...")
    
    animations = []
    
    for screenshot_path, name, desc in screenshots:
        if not os.path.exists(screenshot_path):
            continue
            
        output_path = f'{V5_DIR}/anim_{name}.mp4'
        
        # Animation zoom-in fluide avec Ken Burns effect
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', screenshot_path,
            '-vf', (
                'scale=3840:2160,'  # Upscale pour zoom
                'zoompan=z=\'min(zoom+0.0008,1.3)\':'  # Zoom progressif
                's=1920x1080:d=180:'  # 6 sec @ 30fps
                'x=\'iw/2-(iw/zoom/2)\':'
                'y=\'ih/2-(ih/zoom/2)\','
                'format=yuv420p'
            ),
            '-t', '6',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '18',
            '-r', '30',
            output_path
        ]
        
        print(f"  🎬 Animation {name}...")
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            animations.append(output_path)
            print(f"    ✅ {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"    ❌ Erreur FFmpeg: {e.stderr.decode()[:200]}")
    
    return animations


def generate_voiceover():
    """Génère la voix-off française avec OpenAI TTS"""
    print("\n🎙️ Génération voix-off française...")
    
    voiceover_path = f'{V5_DIR}/voiceover_v5.mp3'
    
    if os.path.exists(voiceover_path) and os.path.getsize(voiceover_path) > 10000:
        print("  ⏭️ Voix-off existe déjà")
        return voiceover_path
    
    text = """
    Avant Titelli...
    Des heures perdues à gérer vos rendez-vous.
    Des clients qui attendent, de la frustration.
    
    Avec Titelli...
    Tout est simplifié.
    Réservation en ligne, gestion automatique, clients satisfaits.
    
    Titelli. La solution suisse pour les professionnels.
    Rejoignez-nous sur titelli point com.
    """
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ['EMERGENT_LLM_KEY'])
        
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",  # Voix féminine professionnelle
            input=text.strip(),
            speed=0.95
        )
        
        response.stream_to_file(voiceover_path)
        print(f"  ✅ Voix-off générée: {voiceover_path}")
        return voiceover_path
        
    except Exception as e:
        print(f"  ❌ Erreur TTS: {e}")
        return None


def assemble_final_video(ai_clips, screen_animations, voiceover):
    """Assemble la vidéo finale V5"""
    print("\n🎬 Assemblage de la vidéo finale V5...")
    
    final_output = f'{UPLOADS_DIR}/titelli_v5_final.mp4'
    
    # Ordre des clips:
    # 1. Clip humain "avant" (stress)
    # 2. Animation écran (problème)
    # 3. Transition Titelli
    # 4. Animation dashboard Titelli
    # 5. Clip humain "après" (satisfaction)
    
    # Créer la liste des fichiers à concaténer
    concat_list = f'{V5_DIR}/concat_list.txt'
    
    clips_order = []
    
    # Trouver les clips dans l'ordre
    for name in ['v5_human_before', 'v5_transition', 'v5_human_after']:
        clip_path = f'{V5_DIR}/{name}.mp4'
        if os.path.exists(clip_path):
            clips_order.append(clip_path)
    
    # Ajouter les animations d'écran
    for anim in screen_animations[:2]:  # Max 2 animations
        if os.path.exists(anim):
            clips_order.insert(1, anim)  # Insérer après le premier clip
    
    if len(clips_order) < 2:
        print("  ❌ Pas assez de clips pour assembler")
        return None
    
    # D'abord normaliser tous les clips au même format
    normalized_clips = []
    for i, clip in enumerate(clips_order):
        norm_path = f'{V5_DIR}/norm_{i}.mp4'
        cmd = [
            'ffmpeg', '-y',
            '-i', clip,
            '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2',
            '-shortest',
            norm_path
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            normalized_clips.append(norm_path)
        except:
            pass
    
    # Écrire la liste de concat
    with open(concat_list, 'w') as f:
        for clip in normalized_clips:
            f.write(f"file '{clip}'\n")
    
    # Concaténer
    concat_output = f'{V5_DIR}/v5_concat.mp4'
    cmd_concat = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0',
        '-i', concat_list,
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-c:a', 'aac', '-b:a', '192k',
        concat_output
    ]
    
    try:
        subprocess.run(cmd_concat, capture_output=True, check=True)
        print(f"  ✅ Vidéo concaténée: {concat_output}")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Erreur concat: {e.stderr.decode()[:300]}")
        return None
    
    # Ajouter la voix-off si disponible
    if voiceover and os.path.exists(voiceover):
        cmd_audio = [
            'ffmpeg', '-y',
            '-i', concat_output,
            '-i', voiceover,
            '-filter_complex', '[0:a][1:a]amix=inputs=2:duration=shortest:weights=0.3 1[aout]',
            '-map', '0:v',
            '-map', '[aout]',
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            final_output
        ]
        try:
            subprocess.run(cmd_audio, capture_output=True, check=True)
            print(f"  ✅ Voix-off ajoutée")
        except Exception as e:
            # Si erreur audio, copier juste la vidéo
            subprocess.run(['cp', concat_output, final_output])
    else:
        subprocess.run(['cp', concat_output, final_output])
    
    # Ajouter texte overlay Titelli
    final_with_text = f'{UPLOADS_DIR}/titelli_v5_complete.mp4'
    
    cmd_text = [
        'ffmpeg', '-y',
        '-i', final_output,
        '-vf', (
            "drawtext=text='AVANT':fontsize=60:fontcolor=white:borderw=3:bordercolor=black:"
            "x=(w-text_w)/2:y=h-80:enable='lt(t,8)',"
            "drawtext=text='APRÈS':fontsize=60:fontcolor=white:borderw=3:bordercolor=black:"
            "x=(w-text_w)/2:y=h-80:enable='gt(t,15)',"
            "drawtext=text='TITELLI':fontsize=72:fontcolor=orange:borderw=4:bordercolor=black:"
            "x=(w-text_w)/2:y=50:enable='gt(t,10)*lt(t,25)'"
        ),
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-c:a', 'copy',
        final_with_text
    ]
    
    try:
        subprocess.run(cmd_text, capture_output=True, check=True)
        print(f"\n✅ VIDÉO V5 TERMINÉE: {final_with_text}")
        return final_with_text
    except:
        print(f"\n✅ VIDÉO V5 TERMINÉE: {final_output}")
        return final_output


def main():
    print("=" * 70)
    print("   TITELLI V5 - VERSION PREMIUM")
    print("   Vrais écrans + Clips AI humains")
    print("=" * 70)
    
    # Étape 1: Capturer les screenshots
    screenshots = capture_titelli_screenshots()
    print(f"\n📊 {len(screenshots)} screenshots capturés")
    
    # Étape 2: Créer les animations d'écran
    screen_animations = create_screen_animations(screenshots)
    print(f"📊 {len(screen_animations)} animations créées")
    
    # Étape 3: Générer les clips AI
    ai_clips = generate_ai_clips()
    print(f"📊 {len(ai_clips)} clips AI générés")
    
    # Étape 4: Générer la voix-off
    voiceover = generate_voiceover()
    
    # Étape 5: Assembler la vidéo finale
    final_video = assemble_final_video(ai_clips, screen_animations, voiceover)
    
    print("\n" + "=" * 70)
    if final_video:
        print(f"   ✅ VIDÉO V5 PRÊTE!")
        print(f"   📁 {final_video}")
        
        # Afficher la taille
        size = os.path.getsize(final_video) / (1024 * 1024)
        print(f"   📦 Taille: {size:.1f} MB")
    else:
        print("   ❌ Échec de la génération")
    print("=" * 70)
    
    return final_video


if __name__ == "__main__":
    main()
