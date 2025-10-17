
import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

class SummarizerGenerator:
    def __init__(self, use_mock=True):
        self.use_mock = use_mock
        if not self.use_mock:
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini") # Using gpt-4.1-mini as per environment variable hint

    def generate_posts(self, content, source_url):
        """Summarizes content and generates social media posts in Persian."""
        if self.use_mock:
            print("Using mock OpenAI API response.")
            return self._mock_generate_posts(content, source_url)
        else:
            return self._real_generate_posts(content, source_url)

    def _mock_generate_posts(self, content, source_url):
        """Generates mock social media posts for testing."""
        mock_summary = f"خلاصه ساختگی از محتوای {source_url}: این یک تغییر مهم است که باید در رسانه های اجتماعی به اشتراک گذاشته شود."
        mock_posts = {
            "linkedin": f"[لینکدین] {mock_summary} #اخبار #تکنولوژی #هوش_مصنوعی",
            "instagram": f"[اینستاگرام] {mock_summary} \n\nبرای جزئیات بیشتر به لینک در بیو مراجعه کنید! #اخبار_فوری #هوش_مصنوعی #فناوری",
            "twitter": f"[توییتر] {mock_summary} \n\nمنبع: {source_url} #AI_NewsBot #اخبار"
        }
        return mock_posts

    def _real_generate_posts(self, content, source_url):
        """Generates social media posts using the OpenAI API."""
        prompt = f"""You are an AI assistant for a news bot. Your task is to summarize the following content and generate three short, engaging social media posts in Persian. Each post should be tailored for a specific platform: LinkedIn, Instagram, and Twitter (X). The posts should highlight the key information from the content. The output should be a JSON object with keys 'linkedin', 'instagram', and 'twitter'.

Content from {source_url}:
{content}

Example Output Format:
{{
  "linkedin": "[LinkedIn Post in Persian]",
  "instagram": "[Instagram Post in Persian]",
  "twitter": "[Twitter Post in Persian]"
}}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates social media posts in Persian."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" },
                temperature=0.7,
                max_tokens=500
            )
            generated_text = response.choices[0].message.content
            return json.loads(generated_text)
        except Exception as e:
            print(f"Error generating posts with OpenAI API: {e}")
            return None

if __name__ == '__main__':
    # Example usage with mock responses
    generator_mock = SummarizerGenerator(use_mock=True)
    sample_content = "یک مقاله جدید در مورد پیشرفت های هوش مصنوعی منتشر شده است که به بررسی تاثیر آن بر صنایع مختلف می پردازد."
    sample_url = "https://example.com/ai-article"
    mock_generated_posts = generator_mock.generate_posts(sample_content, sample_url)
    if mock_generated_posts:
        print("\nMock Generated Posts:")
        for platform, post in mock_generated_posts.items():
            print(f"  {platform.capitalize()}: {post}")

    # Example usage with real API (requires OPENAI_API_KEY in .env)
    # To run this, create a .env file in the root of the project with OPENAI_API_KEY='your_key'
    # and set use_mock=False
    # generator_real = SummarizerGenerator(use_mock=False)
    # real_generated_posts = generator_real.generate_posts(sample_content, sample_url)
    # if real_generated_posts:
    #     print("\nReal Generated Posts:")
    #     for platform, post in real_generated_posts.items():
    #         print(f"  {platform.capitalize()}: {post}")

