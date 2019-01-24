from notifiers import SlackBot
from scrapers import HaloScraper, NekretnineScraper
from dotenv import load_dotenv
import os

load_dotenv()


if __name__ == "__main__":
    slack_hook_url = os.getenv('SLACK_HOOK_URL')
    slack_user_id = os.getenv('SLACK_USER_ID')
    client = SlackBot(slack_hook_url, slack_user_id)
    thread1 = HaloScraper(client, should_skip=True, timeout=10)
    thread2 = NekretnineScraper(client, should_skip=True, timeout=10)
    thread1.start()
    thread2.start()
