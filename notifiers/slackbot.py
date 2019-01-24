import requests


class SlackBot:

    def __init__(self, slack_hook_url, slack_user_id):
        self.slack_hook_url = slack_hook_url
        self.slack_user_id = slack_user_id

    def build_slack_bot_data(self, apt):
        return {
            "attachments": [
                {
                    "fallback": "NEW APPARTMENT",
                    "color": "#36a64f",
                    "pretext": f"Hey <@{self.slack_user_id}>, I found new appartment for you!",
                    "title": f"{apt['title']}",
                    "title_link": f"{apt['add_url']}",
                    "text": f"Price: {apt['price']}e\n",
                    "image_url": f"{apt['image_url']}",
                    "footer": f"{apt['region']}",
                }
            ]
        }

    def notify(self, apartment_dict):
        requests.post(
            self.slack_hook_url,
            json=self.build_slack_bot_data(apartment_dict))