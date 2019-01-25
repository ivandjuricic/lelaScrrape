import time
from threading import Thread

from bs4 import BeautifulSoup
import requests
from utils import str_to_int
from models import Apartment


class NekretnineScraper(Thread):

    def __init__(self, client, timeout=60, should_skip=True):
        super().__init__()
        self.should_skip = should_skip
        self.timeout = timeout
        self.base_url = 'https://www.nekretnine.rs/stambeni-objekti/stanovi/'
        self.other_params = 'jednosoban-stan/izdavanje-prodaja/izdavanje/grad/beograd/cena/100_250/lista/po_stranici/20/?search%5Bcategory%5D%5B0%5D=12&search%5Bcategory%5D%5B1%5D=9'
        self.client = client
        print(self.full_url)

    @property
    def full_url(self):
        return f"{self.base_url}{self.other_params}"

    def get_apartment_div_list(self):
        response = requests.get(self.full_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.findAll("div", {"class": "row offer"})
        return divs

    def parse_apartment_div(self, apt_div):
        title_element = apt_div.find("h2")
        title = title_element.find("a").text.strip()
        external_id_string = title_element.find("a").attrs['href']
        external_id = external_id_string.split("/")[3]
        url = title_element.find("a")
        base_url = 'https://www.nekretnine.rs'
        add_url = "".join([base_url, url.attrs['href']])
        image_parent_element = apt_div.find("picture")
        image_element = image_parent_element.find("img")
        image_url = image_element.attrs['src']
        multi_element = apt_div.find("p", {"class": "offer-price"})
        price_string = multi_element.find("span").text
        price = str_to_int(price_string.split(" ")[0])

        region = apt_div.find("p", {"class": "offer-location"}).text.strip()
        data = {
            "add_url": add_url,
            "title": title,
            "price": price,
            "external_id": external_id,
            "image_url": image_url,
            "region": region
        }
        return data

    def build_slack_bot_data(self, apt):
        return {
            "attachments": [
                {
                    "fallback": "NEW APPARTMENT",
                    "color": "#36a64f",
                    "pretext": "Hey <@UFLS66H8X>, I found new appartment for you!",
                    "title": f"{apt['title']}",
                    "title_link": f"{apt['add_url']}",
                    "text": f"Price: {apt['price']}e\n",
                    "image_url": f"{apt['image_url']}",
                    "footer": f"{apt['region']}",
                }
            ]
        }

    def run(self):
        while True:
            apt_divs = self.get_apartment_div_list()
            for apt in apt_divs:
                apt = self.parse_apartment_div(apt)
                current = Apartment.select().where(Apartment.external_id == apt['external_id'])
                if not current.exists():
                    Apartment(**apt).save()
                    if self.should_skip:
                        continue
                    self.client.notify(apartment_dict=apt)
                else:
                    continue
            self.should_skip = False
            time.sleep(self.timeout)
