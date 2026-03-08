import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'secondevie')

async def fix_broken_urls():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Find all enterprises with broken URLs
    broken_domain = 'enterprise-media.preview.emergentagent.com'
    
    # Fix cover_image
    result_cover = await db.enterprises.update_many(
        {"cover_image": {"$regex": broken_domain}},
        {"$set": {"cover_image": None}}
    )
    print(f"Fixed {result_cover.modified_count} broken cover_image URLs")
    
    # Fix logo
    result_logo = await db.enterprises.update_many(
        {"logo": {"$regex": broken_domain}},
        {"$set": {"logo": None}}
    )
    print(f"Fixed {result_logo.modified_count} broken logo URLs")
    
    # Fix photos array - remove broken URLs
    cursor = db.enterprises.find({"photos": {"$elemMatch": {"$regex": broken_domain}}})
    fixed_photos = 0
    async for enterprise in cursor:
        photos = enterprise.get('photos', [])
        clean_photos = [p for p in photos if broken_domain not in p]
        if len(clean_photos) != len(photos):
            await db.enterprises.update_one(
                {"_id": enterprise["_id"]},
                {"$set": {"photos": clean_photos}}
            )
            fixed_photos += 1
    print(f"Fixed {fixed_photos} enterprises with broken photos arrays")
    
    client.close()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(fix_broken_urls())
