
import os
from datetime import datetime
import json

def save_post_locally(platform, post_content, source_id, generated_at, metadata_json=None):
    """Saves a generated social media post to a local file."""
    output_dir = f"aladdin-sandbox/apps/ai_newsbot/output/{platform}"
    os.makedirs(output_dir, exist_ok=True)

    timestamp_str = generated_at.strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp_str}.md" # Using .md for markdown content
    file_path = os.path.join(output_dir, filename)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {platform.capitalize()} Post - {generated_at.isoformat()}\n\n")
            f.write(f"**Source ID:** {source_id}\n\n")
            if metadata_json:
                f.write(f"**Metadata:** {metadata_json}\n\n")
            f.write("---\n\n")
            f.write(post_content)
        print(f"Post saved to: {file_path}")
        return file_path
    except Exception as e:
        print(f"Error saving post to {file_path}: {e}")
        return None

if __name__ == '__main__':
    # Example usage
    current_time = datetime.now()
    sample_metadata = {"ai_model": "gpt-4.1-mini", "version": "1.0"}

    print("Saving sample LinkedIn post...")
    save_post_locally(
        platform="linkedin",
        post_content="این یک پست آزمایشی برای لینکدین است. #تست #AI_NewsBot",
        source_id="test_source_1",
        generated_at=current_time,
        metadata_json=json.dumps(sample_metadata)
    )

    print("\nSaving sample Instagram post...")
    save_post_locally(
        platform="instagram",
        post_content="این یک پست آزمایشی برای اینستاگرام است. \n\n#تست #AI_NewsBot #اینستاگرام",
        source_id="test_source_1",
        generated_at=current_time,
        metadata_json=json.dumps(sample_metadata)
    )

    print("\nSaving sample Twitter post...")
    save_post_locally(
        platform="twitter",
        post_content="این یک پست آزمایشی برای توییتر است. #تست #AI_NewsBot",
        source_id="test_source_1",
        generated_at=current_time,
        metadata_json=json.dumps(sample_metadata)
    )

