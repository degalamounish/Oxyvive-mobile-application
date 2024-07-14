import requests
from anvil.tables import app_tables, query as q
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

class SliverToolbar(MDTopAppBar):
    manager = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.left_action_items = [["arrow-left", lambda x: self.back_screen(), "color", (1, 0, 0, 1)]]

    def back_screen(self):
        self.manager.push_replacement('client_location')


class AvailableService(MDScreen):
    silver_tool_bar = SliverToolbar()
    location = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)
        self.pincodes = None

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.go_back()
            return True
        return False

    def go_back(self):
        self.manager.push_replacement('client_location')

    def on_enter(self, *args):
        self.populate_cards()
        self.silver_tool_bar.manager = self.manager
        self.fetch_list_of_pincodes()

    def show_no_service_popup(self):
        dialog = MDDialog(
            title="Service Unavailable",
            text="We are not available in your area yet. Please search another location or select one with the help of the map.",
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.close_dialog()
                )
            ],
        )
        self.dialog = dialog
        dialog.open()

    def close_dialog(self):
        if hasattr(self, 'dialog'):
            self.dialog.dismiss()
            self.dialog = None
            self.manager.current = 'client_location'

    def populate_cards(self, service=None):
        pincodes = self.fetch_list_of_pincodes()

        # Fetch data from all three tables
        results_oxiclinics = app_tables.oxiclinics.search(oxiclinics_pincode=q.any_of(*pincodes))
        results_oxigyms = app_tables.oxigyms.search(oxigyms_pincode=q.any_of(*pincodes))
        results_oxiwheels = app_tables.oxiwheels.search(oxiwheels_pincode=q.any_of(*pincodes))

        # Combine all results
        all_results = list(results_oxiclinics) + list(results_oxigyms) + list(results_oxiwheels)

        # Clear existing widgets
        self.ids.content.clear_widgets()

        # Check if no services are available
        if not all_results:
            self.show_no_service_popup()
            return

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
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                size=("80dp", "36dp"),
                on_release=lambda x, s=service: self.book_service(s)
            )
            button_box.add_widget(button)

            content_layout.add_widget(button_box)
            box_layout.add_widget(content_layout)
            card.add_widget(box_layout)

            self.ids.content.add_widget(card)

    def book_service(self, service):
        servicer = dict(service)
        self.manager.load_screen('slot_booking')
        screen = self.manager.get_screen('slot_booking')
        if 'oxiclinics_id' in servicer:
            screen.servicer_id = servicer.get('oxiclinics_id')


        elif 'oxiwheels_id' in servicer:
            screen.servicer_id = servicer.get('oxiwheels_id')

        elif 'oxigyms_id' in servicer:
            screen.servicer_id = servicer.get('oxigyms_id')

        else:
            print('Please select service')

        self.manager.push_replacement('slot_booking')
        print(f"Booking service: {dict(service)}")

    def fetch_list_of_pincodes(self):
        global lat, lng
        api_key = "AIzaSyA8GzhJLPK0Hfryi5zHbg3RMDSMCukmQCw"
        base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {
            'address': self.location,
            'key': api_key,
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            if data['results']:
                # Extracting latitude and longitude of the first result
                lat = data['results'][0]['geometry']['location']['lat']
                lng = data['results'][0]['geometry']['location']['lng']
                print(f'Latitude: {lat}, Longitude: {lng}')
            else:
                print('No results found')
                return []

        else:
            print(f'Error: {response.status_code}')
            return []

        pincodes_list = set()  # Initialize pincodes_list as a set to avoid duplicates

        try:
            # Fetch postal codes using Place Details API
            details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
            details_params = {
                'place_id': data['results'][0]['place_id'],
                'fields': 'address_components',
                'key': api_key,
            }
            details_response = requests.get(details_url, params=details_params)
            details_response.raise_for_status()
            details_data = details_response.json()

            if 'result' in details_data:
                address_components = details_data['result']['address_components']
                for component in address_components:
                    if 'postal_code' in component['types']:
                        pincodes_list.add(component['long_name'])

            # Fetch nearby places postal codes using Nearby Search API
            nearby_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
            nearby_params = {
                'location': f'{lat},{lng}',
                'radius': 30000,  # 30 km radius
                'key': api_key,
            }
            nearby_response = requests.get(nearby_url, params=nearby_params)
            nearby_response.raise_for_status()
            nearby_data = nearby_response.json()

            if 'results' in nearby_data:
                for place in nearby_data['results']:
                    place_id = place['place_id']
                    place_details_response = requests.get(details_url, params={
                        'place_id': place_id,
                        'fields': 'address_components',
                        'key': api_key,
                    })
                    place_details_response.raise_for_status()
                    place_details_data = place_details_response.json()

                    if 'result' in place_details_data:
                        print(place_details_data)
                        address_components = place_details_data['result']['address_components']
                        for component in address_components:
                            if 'postal_code' in component['types']:
                                pincodes_list.add(component['long_name'])

            pincodes_list = list(pincodes_list)
            pincodes_list = [int(pincode) for pincode in pincodes_list]  # Convert to integers
            print(pincodes_list)

        except requests.exceptions.RequestException as e:
            print(e)
        except KeyError:
            print("Unexpected response format.")
        except Exception as e:
            print(e)

        self.pincodes = pincodes_list
        return pincodes_list
