import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(''))

from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration

# Load environment variables
load_dotenv()

def generateVideo(prompt, output_path='/app/backend/uploads/video_accueil_couple_lausanne.mp4', model="sora-2", size="1280x720", duration=8):
    """Generate video with Sora 2"""
    video_gen = OpenAIVideoGeneration(api_key=os.environ['EMERGENT_LLM_KEY'])
    
    video_bytes = video_gen.text_to_video(
        prompt=prompt,
        model=model,
        size=size,
        duration=duration,
        max_wait_time=900
    )
    
    if video_bytes:
        video_gen.save_video(video_bytes, output_path)
        return output_path
    return None


def main():
    prompt = """Cinematic romantic scene in Lausanne, Switzerland. A distinguished older man in his 50s with gray hair, wearing an elegant dark coat, walks hand in hand with a beautiful woman with long curly brown hair. They stroll along the shores of Lake Geneva at sunset, with the Alps visible in the background. The golden hour light illuminates their faces as they share a tender moment. Smooth camera movement following them, romantic and warm atmosphere. High quality, 4K cinematic look."""
    
    print("Starting video generation with Sora 2...")
    print(f"Prompt: {prompt}")
    print("This may take 5-10 minutes...")
    
    result = generateVideo(prompt)
    
    if result:
        print(f'Video saved to: {result}')
    else:
        print('Video generation failed')

if __name__ == "__main__":
    main()
