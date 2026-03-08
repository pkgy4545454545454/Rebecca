#!/usr/bin/env python3
"""
Script to fix broken logo URLs in the production database.
Converts absolute URLs (pointing to old preview domains) to relative paths.
"""

from pymongo import MongoClient
import re

# Connect to MongoDB
MONGO_URL = "mongodb+srv://prankgy:Minijetaime1996@cluster0.kwjifsg.mongodb.net/secondevie?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URL)
db = client["secondevie"]

def fix_logo_url(logo_url):
    """
    Convert absolute URLs to relative paths.
    Example: https://image-fix-demo.preview.emergentagent.com/api/uploads/enterprises/xxx
    Becomes: /api/uploads/enterprises/xxx
    """
    if not logo_url:
        return None
    
    # Pattern to match preview domain URLs
    patterns = [
        r"https?://[a-zA-Z0-9-]+\.preview\.emergentagent\.com(/api/uploads/.*)",
        r"https?://localhost:\d+(/api/uploads/.*)",
    ]
    
    for pattern in patterns:
        match = re.match(pattern, logo_url)
        if match:
            return match.group(1)
    
    # If it's already a relative path, keep it
    if logo_url.startswith("/api/uploads/"):
        return logo_url
    
    return logo_url

def main():
    print("=" * 60)
    print("FIXING BROKEN LOGO URLs IN DATABASE")
    print("=" * 60)
    
    # Find all enterprises with broken logos
    broken_count = 0
    fixed_count = 0
    skipped_count = 0
    
    # Get all enterprises with a logo field
    enterprises = list(db.enterprises.find({"logo": {"$exists": True, "$ne": ""}}))
    print(f"\nTotal enterprises with logos: {len(enterprises)}")
    
    for enterprise in enterprises:
        logo = enterprise.get("logo", "")
        eid = enterprise["_id"]
        name = enterprise.get("business_name", enterprise.get("name", "Unknown"))
        
        # Check if the logo URL is broken
        if logo and "preview.emergentagent.com" in logo and "urgent-ui-polish" not in logo:
            broken_count += 1
            fixed_url = fix_logo_url(logo)
            
            if fixed_url != logo:
                # Update the document
                result = db.enterprises.update_one(
                    {"_id": eid},
                    {"$set": {"logo": fixed_url}}
                )
                if result.modified_count > 0:
                    fixed_count += 1
                    print(f"  ✓ Fixed: {name}")
                    print(f"    Old: {logo[:70]}...")
                    print(f"    New: {fixed_url}")
                else:
                    skipped_count += 1
                    print(f"  - Skipped (no change): {name}")
            else:
                skipped_count += 1
                print(f"  - Skipped (same URL): {name}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total broken URLs found: {broken_count}")
    print(f"Successfully fixed: {fixed_count}")
    print(f"Skipped: {skipped_count}")
    
    client.close()
    print("\nDone!")

if __name__ == "__main__":
    main()
