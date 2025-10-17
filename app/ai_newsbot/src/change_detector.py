
import hashlib

def calculate_sha256(content):
    """Calculates the SHA256 hash of the given content."""
    if content is None:
        return None
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def detect_change(current_content, last_hash):
    """Detects if the current content has changed compared to the last hash."""
    current_hash = calculate_sha256(current_content)
    if current_hash is None:
        return False, None # Cannot detect change if current content is empty

    if last_hash is None: # First time checking this source
        return True, current_hash
    
    if current_hash != last_hash:
        return True, current_hash
    else:
        return False, current_hash

if __name__ == '__main__':
    # Example usage
    content1 = "This is some sample content."
    content2 = "This is some sample content."
    content3 = "This is some updated content."

    print(f"Hash of content1: {calculate_sha256(content1)}")
    print(f"Hash of content2: {calculate_sha256(content2)}")
    print(f"Hash of content3: {calculate_sha256(content3)}")

    # Test 1: New content (no previous hash)
    changed, new_hash = detect_change(content1, None)
    print(f"\nTest 1 (New content): Changed={changed}, New Hash={new_hash}")

    # Test 2: No change
    changed, new_hash = detect_change(content2, new_hash)
    print(f"Test 2 (No change): Changed={changed}, New Hash={new_hash}")

    # Test 3: Change detected
    changed, new_hash = detect_change(content3, new_hash)
    print(f"Test 3 (Change detected): Changed={changed}, New Hash={new_hash}")

    # Test 4: Empty content
    changed, new_hash = detect_change(None, "some_hash")
    print(f"Test 4 (Empty content): Changed={changed}, New Hash={new_hash}")

