# AI_NewsBot_Aladdin MVP

This is the Minimum Viable Product (MVP) for the AI_NewsBot_Aladdin, designed to monitor various sources, detect changes, generate social media posts in Persian using AI, and save them locally.

## Features

*   **Source Monitoring:** Fetches content from configured websites and local documents.
*   **Change Detection:** Uses SHA256 hashing to detect new or modified content.
*   **AI Post Generation:** Integrates with OpenAI API to summarize content and generate Persian posts for LinkedIn, Instagram, and Twitter (X).
*   **Local Storage:** Saves generated posts to a structured local file system.
*   **Basic Scheduling:** Periodically triggers checks for updates.

## Project Structure

```
/aladdin-sandbox/apps/ai_newsbot/
├── src/
│   ├── main.py             # Main orchestration logic and scheduler setup
│   ├── database.py         # SQLAlchemy models and SQLite database initialization
│   ├── crawler.py          # Functions for fetching content from web/documents
│   ├── change_detector.py  # Functions for calculating hashes and detecting changes
│   ├── summarizer_generator.py # AI integration for summarization and post generation
│   └── publisher.py        # Functions for saving generated posts locally
├── config/                 # Configuration files (e.g., config.json - currently not used, but for future)
├── tests/                  # Unit and integration tests
├── output/                 # Directory for locally saved posts
│   ├── linkedin/
│   ├── instagram/
│   └── twitter/
├── .env.example            # Example environment variables file
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

## Setup and Installation

1.  **Navigate to the project directory:**
    ```bash
    cd aladdin-sandbox/apps/ai_newsbot
    ```

2.  **Create a Python Virtual Environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the `aladdin-sandbox/apps/ai_newsbot/` directory based on `.env.example`:
    ```dotenv
    # .env
    OPENAI_API_KEY="your_openai_api_key_here"
    OPENAI_MODEL="gpt-4.1-mini" # or gpt-4.1-nano, gemini-2.5-flash
    DB_PATH="aladdin-sandbox/apps/ai_newsbot/data/newsbot.db"
    MONITORING_INTERVAL_SECONDS=3600 # Check every 1 hour (3600 seconds)
    USE_MOCK_AI="True" # Set to "False" to use actual OpenAI API
    ```
    *   Replace `your_openai_api_key_here` with your actual OpenAI API key if `USE_MOCK_AI` is set to `False`.
    *   `USE_MOCK_AI=True` will use mock responses for AI generation, which is useful for testing without incurring API costs.

## Running the Bot

1.  **Ensure your virtual environment is activated.**

2.  **Run the main script:**
    ```bash
    python3 src/main.py
    ```

    The bot will start, initialize the SQLite database (if it doesn't exist), and begin monitoring sources at the specified interval. It will print messages to the console indicating its activity.

## Expected Output

When the bot detects a change and generates posts, you will see output similar to this in your console:

```
Starting AI_NewsBot_Aladdin MVP...
Scheduler started.
--- Running AI_NewsBot_Aladdin job at 2025-10-14 10:00:00.123456 ---
🔍 Checking https://homecouver.com ...
🆕 Change detected for https://homecouver.com → Generating posts...
Using mock OpenAI API response. (if USE_MOCK_AI is True)
Post saved to: aladdin-sandbox/apps/ai_newsbot/output/linkedin/20251014_100000.md
Post saved to: aladdin-sandbox/apps/ai_newsbot/output/instagram/20251014_100000.md
Post saved to: aladdin-sandbox/apps/ai_newsbot/output/twitter/20251014_100000.md
✅ Posts saved and source updated for https://homecouver.com
⏳ Sleeping 3600 seconds...
```

Generated posts will be saved in the `aladdin-sandbox/apps/ai_newsbot/output/` directory, organized by platform:

```
/aladdin-sandbox/apps/ai_newsbot/output/
├── linkedin/
│   └── 20251014_100000.md
├── instagram/
│   └── 20251014_100000.md
└── twitter/
    └── 20251014_100000.md
```

## Database

The SQLite database `newsbot.db` will be created in `aladdin-sandbox/apps/ai_newsbot/data/`. This database stores information about monitored sources and generated posts.

## Next Steps (Phase 3 Automation)

This MVP focuses on local generation and storage. Future phases will involve:

*   Integration with social media APIs for automated publishing.
*   Advanced scheduling with Celery/Redis.
*   User interface for configuration and post management.
*   Integration with Aladdin Docs & Dashboard.

