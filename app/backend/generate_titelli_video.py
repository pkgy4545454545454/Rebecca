import os
import sys
import time

os.environ['EMERGENT_LLM_KEY'] = 'sk-emergent-f7b660f6d3b5fA5846'

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration

# Scènes complètes pour "Le Monde Après Titelli"
scenes = [
    {
        "name": "scene3_chauffeur",
        "prompt": """Cinematic scene: Professional chauffeur in elegant dark uniform opens the door of a luxury black sedan for a well-dressed businesswoman. 
Beautiful European city street with historic buildings in golden morning light. 
She smiles and enters gracefully. Premium lifestyle, high-end service advertisement. Photorealistic 4K quality."""
    },
    {
        "name": "scene4_formation",
        "prompt": """Cinematic scene: Young professional woman happily attending an online video course on her laptop in a bright modern coworking space. 
She takes notes, looks inspired and engaged. Natural daylight, plants, modern furniture.
Education and personal development concept. Photorealistic 4K quality."""
    },
    {
        "name": "scene5_artisan",
        "prompt": """Cinematic scene: Skilled artisan craftsman carefully packaging beautiful handmade ceramic products in elegant gift boxes. 
Warm workshop with natural light, wooden shelves with creations. Preparing orders for delivery.
Small business, local craftsmanship. Photorealistic 4K quality."""
    },
    {
        "name": "scene6_livraison_panier",
        "prompt": """Cinematic scene: Smiling mother at her home doorstep receiving a beautiful wicker basket full of fresh groceries and gourmet food from a friendly delivery person.
She pays with her smartphone contactless. Warm family home exterior.
Premium food delivery service. Photorealistic 4K quality."""
    },
    {
        "name": "scene7_soiree_copines",
        "prompt": """Cinematic scene: Group of four elegant women friends enjoying a spa evening at home with professional beauticians. 
Face masks, manicures, champagne glasses, candles. Luxurious modern living room at night.
Girls night wellness party. Photorealistic 4K quality."""
    },
    {
        "name": "scene8_shopping_minuit",
        "prompt": """Cinematic scene: Young couple shopping online on tablets in their cozy modern apartment at midnight. 
Warm ambient lighting, comfortable sofa, city lights through window. Relaxed evening shopping.
E-commerce convenience lifestyle. Photorealistic 4K quality."""
    },
    {
        "name": "scene9_theatre_maison",
        "prompt": """Cinematic scene: Professional musicians playing violin and cello in an elegant living room for a small private audience of a family.
Dramatic warm lighting, captivated listeners on sofas. Intimate classical music performance.
Premium home entertainment. Photorealistic 4K quality."""
    },
    {
        "name": "scene10_medecin",
        "prompt": """Cinematic scene: Caring professional doctor in white coat making a house call, gently checking blood pressure of an elderly patient at home.
Modern medical equipment, family members watching gratefully. Warm interior lighting.
Premium home healthcare. Photorealistic 4K quality."""
    },
    {
        "name": "scene11_chef",
        "prompt": """Cinematic scene: Professional chef in pristine white uniform cooking a gourmet meal in a beautiful modern home kitchen.
Flames rising from pan, fresh colorful ingredients, family watching excitedly in background.
Private chef experience. Photorealistic 4K quality."""
    },
    {
        "name": "scene12_personnes_agees",
        "prompt": """Cinematic scene: Kind professional caregiver helping an elegant elderly woman walk through a beautiful garden path.
Gentle supportive assistance, peaceful outdoor setting with flowers and trees. Sunny day.
Premium elderly care service. Photorealistic 4K quality."""
    },
    {
        "name": "scene13_travaux",
        "prompt": """Cinematic scene: Professional handyman in clean uniform carefully fixing cabinet details in a beautiful modern kitchen.
Homeowner watching satisfied. Quality tools, attention to detail, natural daylight.
Home improvement specialist. Photorealistic 4K quality."""
    },
    {
        "name": "scene14_finale",
        "prompt": """Cinematic scene: Diverse happy people enjoying a beautiful day in a Swiss city. Couples walking, families in parks, people at cafes.
Everyone well-dressed, relaxed, smiling. Golden hour sunlight, mountains in background.
Life made easier, premium lifestyle for all. Photorealistic 4K quality."""
    }
]

print("🎬 GÉNÉRATION VIDÉO 'LE MONDE APRÈS TITELLI'", flush=True)
print(f"   Total: {len(scenes)} scènes à générer", flush=True)
print("   Durée estimée: 15-25 minutes", flush=True)
print("", flush=True)

generated_count = 0
failed_scenes = []

for i, scene in enumerate(scenes):
    print(f"🎬 [{i+1}/{len(scenes)}] {scene['name']}...", flush=True)
    start_time = time.time()
    
    try:
        video_gen = OpenAIVideoGeneration(api_key=os.environ['EMERGENT_LLM_KEY'])
        video_bytes = video_gen.text_to_video(
            prompt=scene['prompt'],
            model="sora-2",
            size="1280x720",
            duration=4,
            max_wait_time=600
        )
        
        if video_bytes:
            output_path = f"/app/backend/uploads/titelli_monde_{scene['name']}.mp4"
            video_gen.save_video(video_bytes, output_path)
            elapsed = time.time() - start_time
            print(f"   ✅ OK ({elapsed:.0f}s)", flush=True)
            generated_count += 1
        else:
            print(f"   ❌ Échec", flush=True)
            failed_scenes.append(scene['name'])
    except Exception as e:
        error_msg = str(e)
        if "insufficient_balance" in error_msg:
            print(f"   ❌ Balance insuffisante - STOP", flush=True)
            failed_scenes.append(scene['name'])
            break
        else:
            print(f"   ❌ {error_msg[:50]}", flush=True)
            failed_scenes.append(scene['name'])
    
    print("", flush=True)

print("", flush=True)
print("=" * 60, flush=True)
print(f"🎬 RÉSULTAT: {generated_count}/{len(scenes)} scènes générées", flush=True)
if failed_scenes:
    print(f"   Échecs: {', '.join(failed_scenes)}", flush=True)
print("=" * 60, flush=True)
