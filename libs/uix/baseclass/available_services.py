import requests
from anvil.tables import app_tables, query as q
from kivy.properties import ObjectProperty, StringProperty

from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar


class CardItem(MDCard):
    manager = ObjectProperty()
    image_path = StringProperty()
    servicer_name = StringProperty()
    subtitle = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elevation = 3

    def schedule_screen(self):
        self.manager.push_replacement("slot_booking")


class SliverToolbar(MDTopAppBar):
    manager = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shadow_color = (0, 0, 0, 0)
        self.type_height = "medium"
        self.headline_text = "Available Services"
        self.left_action_items = [["arrow-left", lambda x: self.back_screen()]]

    def back_screen(self):
        self.manager.push_replacement('client_location')


class AvailableService(MDScreen):
    silver_tool_bar = SliverToolbar()
    location = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pincodes = None

    def on_enter(self, *args):
        self.populate_cards()
        self.silver_tool_bar.manager = self.manager
        self.fetch_list_of_pincodes()

    def populate_cards(self):
        pincodes = self.fetch_list_of_pincodes()
        results = app_tables.oxiclinics.search(oxiclinics_pincode=q.any_of(*pincodes))
        results = (list(results))
        self.ids.content.clear_widgets()
        for service in results:
            self.ids.content.add_widget(CardItem(manager=self.manager, servicer_name=service['oxiclinics_Name'],
                                                 subtitle=service['oxiclinics_District']))

    def fetch_list_of_pincodes(self):
        global lat, lng, pincodes, pincodes_list
        api_key = "7060ef7890c44bb48d75f2d12c66a466"
        username = 'mhpraveen1997'
        address = self.location
        base_url = 'https://api.opencagedata.com/geocode/v1/json'
        params = {
            'q': address,
            'key': api_key,
            'pretty': 1,  # Pretty print the result
            'no_annotations': 1  # Do not include additional information
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            if data['results']:
                # Extracting latitude and longitude
                lat = data['results'][0]['geometry']['lat']
                lng = data['results'][0]['geometry']['lng']
                print(f'Latitude: {lat}, Longitude: {lng}')
            else:
                print('No results found')
        else:
            print(f'Error: {response.status_code}')

        try:
            url = f"http://api.geonames.org/findNearbyPostalCodesJSON?lat={lat}&lng={lng}&radius=30&username={username}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if 'postalCodes' in data:
                pincodes_list = [item['postalCode'] for item in data['postalCodes']]
                print(pincodes_list)
            else:
                print('No pincodes found.')
        except requests.exceptions.RequestException as e:
            print(e)
        except KeyError:
            print("Unexpected response format.")
        except Exception as e:
            print(e)
        pincodes = list(map(int, pincodes_list))
        self.pincodes = pincodes
        return pincodes
