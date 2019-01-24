import time
from threading import Thread

from bs4 import BeautifulSoup
import requests

from utils import str_to_int
from models import Apartment


class HaloScraper(Thread):

    def __init__(self, client, timeout=60, should_skip=False):
        super().__init__()
        self.should_skip = should_skip
        self.timeout = timeout
        self.base_url = 'https://www.halooglasi.com/nekretnine/izdavanje-stanova?'
        self.city_param = 'grad_id_l-lokacija_id_l-mikrolokacija_id_l=51698%2C52154%2C52155%2C52157%2C52158%2C52159%2C52161%2C52308%2C52684%2C53061%2C54310%2C54331%2C54618%2C54817%2C54936%2C55487%2C56358%2C56360%2C56489%2C57488%2C57809%2C57836%2C57869%2C58198%2C58352%2C58376%2C58426%2C58481%2C58482%2C59215%2C321934%2C346532%2C346533%2C346534%2C346980%2C346982%2C346983%2C346984%2C346986%2C347240%2C347241%2C347242%2C347244%2C347250%2C347251%2C347626%2C347627%2C347628%2C347629%2C347630%2C347631%2C347632%2C531370%2C531372%2C537333%2C538172%2C538174'
        self.other_params = '&cena_d_from=100&cena_d_to=250&cena_d_unit=4&broj_soba_order_i_from=3&broj_soba_order_i_to=4&sa_fotografijom=true&sort=ValidFromForDisplay%2Cdesc'
        self.client = client

    @property
    def full_url(self):
        return f"{self.base_url}{self.city_param}{self.other_params}"

    def get_apartment_div_list(self):
        response = requests.get(self.full_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        main = soup.find(id='ad-list-3')
        divs = main.findAll("div", {"class": "col-md-12 col-sm-12 col-xs-12 col-lg-12"})
        return divs

    def parse_apartment_div(self, apt_div):
        external_id_element = apt_div.find("button", {"class": "fav-cmd"})
        external_id = external_id_element.attrs['data-id']
        title = apt_div.find("h3")
        url = title.find("a")
        base_url = 'https://www.halooglasi.com'
        add_url = "".join([base_url, url.attrs['href']])

        image_parent_element = apt_div.find("figure")
        image_element = image_parent_element.find("img")
        image_url = image_element.attrs['src']

        price = str_to_int(apt_div.find("span").attrs['data-value'])
        region_elements = apt_div.find("ul", {"class": "subtitle-places"})
        region_strings = [el.text.strip() for el in region_elements.findAll("li")]
        region = ", ".join(region_strings)
        return {
            "add_url": add_url,
            "title": title.text,
            "price": price,
            "external_id": external_id,
            "image_url": image_url,
            "region": region
        }

    def run(self):
        while True:
            apt_divs = self.get_apartment_div_list()
            for apt in apt_divs:
                self.parse_apartment_div(apt)
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
