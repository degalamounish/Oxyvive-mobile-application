import requests
from anvil.tables import app_tables, query as q
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout

from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.boxlayout import MDBoxLayout

class SliverToolbar(MDTopAppBar):
    manager = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def back_screen(self):
        self.manager.push_replacement('client_location')


class AvailableService(MDScreen):
    silver_tool_bar = SliverToolbar()
    location = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pincodes = None

    def go_back(self):
        self.manager.push_replacement('client_location')

    def on_enter(self, *args):
        self.populate_cards()
        self.silver_tool_bar.manager = self.manager
        self.fetch_list_of_pincodes()

    def populate_cards(self, service=None):
        pincodes = self.fetch_list_of_pincodes()

        # Fetch data from all three tables
        results_oxiclinics = app_tables.oxiclinics.search(oxiclinics_pincode=q.any_of(*pincodes))
        results_oxigyms = app_tables.oxigyms.search(oxigyms_pincode=q.any_of(*pincodes))
        results_oxiwheels = app_tables.oxiwheels.search(oxiwheels_pincode=q.any_of(*pincodes))

        # Combine all results
        all_results = list(results_oxiclinics) + list(results_oxigyms) + list(results_oxiwheels)

        self.ids.content.clear_widgets()
        for service in all_results:
            service_dict = dict(service)
            print(f"Service: {service_dict}")

            card = MDCard(
                orientation="vertical",
                size_hint=(None, None),
                size=("280dp", "100dp"),
                pos_hint={"center_x": 0.5, "center_y": 0.3},
                ripple_behavior=True,
            )

            box_layout = MDBoxLayout(orientation="horizontal", padding="8dp")

            # Determine the source of the service
            service_name = ""
            service_district = ""
            if 'oxiclinics_Name' in service_dict:
                service_name = service_dict['oxiclinics_Name']
                service_district = service_dict['oxiclinics_District']
            elif 'oxigyms_Name' in service_dict:
                service_name = service_dict['oxigyms_Name']
                service_district = service_dict['oxigyms_District']
            elif 'oxiwheels_Name' in service_dict:
                service_name = service_dict['oxiwheels_Name']
                service_district = service_dict['oxiwheels_District']
            else:
                print("Unknown service type or missing attribute")
                continue

            # Set the image source based on the service name
            if service_name == "Oxivive Home":
                image_source = "images/2.png"
            elif service_name == "Oxivive Wheel":
                image_source = "images/3.png"
            elif service_name == "Oxivive Clinic":
                image_source = "images/1.png"
            else:
                image_source = "images/shot.png"  # Default image if none match

            image = Image(
                source=image_source,
                size_hint=(0.3, 1),
                keep_ratio=True,
                allow_stretch=True
            )
            box_layout.add_widget(image)

            # Create a vertical box layout for labels
            content_layout = MDBoxLayout(orientation="vertical", padding="8dp", spacing="8dp")

            label_name = MDLabel(
                text=service_name,
                theme_text_color="Secondary",
                size_hint_y=None,
                height=self.theme_cls.font_styles["H6"][1],
                valign="top",
                halign="center"
            )
            content_layout.add_widget(label_name)

            label_district = MDLabel(
                text=service_district,
                theme_text_color="Secondary",
                size_hint_y=None,
                height=self.theme_cls.font_styles["Caption"][1],
                valign="top",
                halign="center"
            )
            content_layout.add_widget(label_district)

            # Create a horizontal box layout for the button and labels
            button_box = BoxLayout(padding="8dp", spacing="8dp", size_hint_x=1, orientation="horizontal")

            button = MDFillRoundFlatButton(
                text="Book",
                md_bg_color=(1, 0, 0, 1),
                text_color=(1, 1, 1, 1),
                pos_hint={"center_x":0.5, "center_y": 0.5},
                size=("80dp", "36dp"),
                on_release=lambda x, s=service: self.book_service(s)
            )
            button_box.add_widget(button)

            content_layout.add_widget(button_box)
            box_layout.add_widget(content_layout)
            card.add_widget(box_layout)

            self.ids.content.add_widget(card)

    def book_service(self, service):
        self.manager.push_replacement('slot_booking')
        print(f"Booking service: {dict(service)}")

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