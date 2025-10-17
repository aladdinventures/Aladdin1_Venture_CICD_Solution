
import time
import os
from datetime import datetime
from dotenv import load_dotenv
import json

from database import init_db, Source, GeneratedPost
from crawler import fetch_content
from change_detector import detect_change, calculate_sha256
from summarizer_generator import SummarizerGenerator
from publisher import save_post_locally
from scheduler import NewsBotScheduler

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Use SQLite for MVP as per prompt
DB_PATH = os.getenv("DB_PATH", "aladdin-sandbox/apps/ai_newsbot/data/newsbot.db")
MONITORING_INTERVAL_SECONDS = int(os.getenv("MONITORING_INTERVAL_SECONDS", 3600)) # Default to 1 hour
USE_MOCK_AI = os.getenv("USE_MOCK_AI", "True").lower() == "true"

# Initialize DB Session
Session = init_db(DB_PATH)

def process_source(source_id, source_url, source_type, last_hash):
    """Fetches content, detects changes, generates posts, and saves them locally."""
    print(f"🔍 Checking {source_url} ...")
    current_content = fetch_content(source_url, source_type)

    if current_content:
        changed, new_hash = detect_change(current_content, last_hash)

        if changed:
            print(f"🆕 Change detected for {source_url} → Generating posts...")
            generator = SummarizerGenerator(use_mock=USE_MOCK_AI)
            generated_posts = generator.generate_posts(current_content, source_url)

            if generated_posts:
                session = Session()
                try:
                    for platform, post_content in generated_posts.items():
                        generated_at = datetime.now()
                        metadata = {"source_id": source_id, "source_url": source_url, "ai_model": generator.model}
                        file_path = save_post_locally(
                            platform=platform,
                            post_content=post_content,
                            source_id=source_id,
                            generated_at=generated_at,
                            metadata_json=json.dumps(metadata)
                        )
                        if file_path:
                            new_post = GeneratedPost(
                                id=f"{source_id}_{platform}_{generated_at.strftime("%Y%m%d%H%M%S")}",
                                source_id=source_id,
                                platform=platform,
                                content=post_content,
                                metadata_json=json.dumps(metadata),
                                generated_at=generated_at,
                                status=\'pending_review\'
                            )
                            session.add(new_post)
                    
                    # Update source with new hash and last checked time
                    source = session.query(Source).filter_by(id=source_id).first()
                    if source:
                        source.last_hash = new_hash
                        source.last_checked = datetime.now()
                    session.commit()
                    print(f"✅ Posts saved and source updated for {source_url}")
                except Exception as e:
                    session.rollback()
                    print(f"Error during post generation/saving for {source_url}: {e}")
                finally:
                    session.close()
            else:
                print(f"❌ No posts generated for {source_url}")
        else:
            print(f"No significant change detected for {source_url}.")
    else:
        print(f"Skipping {source_url} due to content fetching error.")

def main_job():
    """The main job executed by the scheduler."""
    print(f"\n--- Running AI_NewsBot_Aladdin job at {datetime.now()} ---")
    session = Session()
    try:
        sources = session.query(Source).filter_by(is_active=True).all()
        if not sources:
            print("No active sources configured. Please add sources to the database.")
            # Add a default sample source if none exist
            sample_url = "https://homecouver.com"
            if not session.query(Source).filter_by(url=sample_url).first():
                sample_source = Source(
                    id="homecouver_website",
                    url=sample_url,
                    source_type="website",
                    monitoring_frequency_seconds=MONITORING_INTERVAL_SECONDS
                )
                session.add(sample_source)
                session.commit()
                print(f"Added default sample source: {sample_source.url}")
                sources = [sample_source] # Process the newly added source
            else:
                print("Default sample source already exists.")

        for source in sources:
            # Check if enough time has passed since last check
            if (datetime.now() - source.last_checked).total_seconds() >= source.monitoring_frequency_seconds:
                process_source(source.id, source.url, source.source_type, source.last_hash)
            else:
                print(f"Skipping {source.url}. Next check in {int(source.monitoring_frequency_seconds - (datetime.now() - source.last_checked).total_seconds())} seconds.")
    except Exception as e:
        print(f"Error in main_job: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    print("Starting AI_NewsBot_Aladdin MVP...")
    
    # Ensure data directory exists for SQLite DB
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Initialize the database and create tables if they don't exist
    init_db(DB_PATH)

    scheduler = NewsBotScheduler()
    scheduler.add_job(main_job, 'interval', seconds=MONITORING_INTERVAL_SECONDS, id='newsbot_main_job')
    scheduler.start()

    try:
        # Keep the main thread alive
        while True:
            time.sleep(2) # Sleep for a short duration to allow scheduler to run
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("AI_NewsBot_Aladdin MVP stopped.")


