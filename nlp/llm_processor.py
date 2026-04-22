import json
from typing import Any, cast

from openai import OpenAI
from core.settings import settings
from db.connection import get_db_connection


class LLMProcessor:
    def __init__(self, client: OpenAI | None = None):
        self.client = client or OpenAI(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY,
        )

    def generate_insights(self, title: str, summary: str) -> dict:
        """Uses LLM to generate bullet points and extract keywords."""
        prompt = f"""
        Analyze the following financial news article.
        Title: {title}
        Content: {summary}
        
        Provide the output STRICTLY as a JSON object with two keys:
        1. "bullets": An array of 2 to 3 short bullet points summarizing the key facts.
        2. "keywords": An array of 3 to 5 highly relevant financial/tech keywords or tags.
        
        Do not include any markdown formatting, preamble, or explanation. Just return the raw JSON.
        """

        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )

            content = response.choices[0].message.content or ""
            raw_output = content.strip()

            if raw_output.startswith("```json"):
                raw_output = raw_output[7:-3]

            return json.loads(raw_output)
        except Exception as exc:
            print(f"Error generating insights: {exc}")
            return {"bullets": [], "keywords": []}

    def process_unsummarized_articles(self) -> None:
        """Finds articles without LLM insights and processes them."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("ALTER TABLE articles ADD COLUMN IF NOT EXISTS bullets TEXT")
            cursor.execute(
                "ALTER TABLE articles ADD COLUMN IF NOT EXISTS keywords TEXT"
            )
        except Exception:
            pass

        cursor.execute(
            "SELECT id, title, summary FROM articles WHERE bullets IS NULL LIMIT 20"
        )
        unsummarized = cursor.fetchall()

        if not unsummarized:
            print("No unsummarized articles found.")
            conn.close()
            return

        print(f"Summarizing {len(unsummarized)} articles...")

        update_count = 0
        for article in unsummarized:
            row = cast(dict[str, Any], article)
            insights = self.generate_insights(row["title"], row["summary"])

            if insights["bullets"] and insights["keywords"]:
                bullets_json = json.dumps(insights["bullets"])
                keywords_json = json.dumps(insights["keywords"])

                cursor.execute(
                    """
                    UPDATE articles 
                    SET bullets = %s, keywords = %s 
                    WHERE id = %s
                """,
                    (bullets_json, keywords_json, row["id"]),
                )
                update_count += 1

        conn.commit()
        conn.close()
        print(f"Successfully generated insights for {update_count} articles.")


def generate_insights(title: str, summary: str) -> dict:
    return LLMProcessor().generate_insights(title, summary)


def process_unsummarized_articles() -> None:
    LLMProcessor().process_unsummarized_articles()
