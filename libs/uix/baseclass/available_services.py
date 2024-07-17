import os
import requests
from anvil.tables import app_tables, query as q
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy_garden.mapview import MapMarker, MapView, MapSource, MapLayer
from kivymd.uix.fitimage import FitImage
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from googlemaps import Client as GoogleMapsClient


class CustomMapMarker(MDBoxLayout, MapMarker):
    def __init__(self, lat, lon, name, **kwargs):
        super().__init__(**kwargs)
        self.lat = lat
        self.lon = lon

        label = MDLabel(
            text=name,
            theme_text_color="Secondary",
            size_hint=(None, None),
            size=(100, 30),
            valign="top",
            halign="center"
        )
        self.add_widget(label)


class StaticMapMarker(MapMarker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lat = kwargs.get('lat', 0)
        self.lon = kwargs.get('lon', 0)
        self.color = 'blue'


class CustomMapView2(MapView):
    manager = ObjectProperty()
    API_KEY = "AIzaSyA8GzhJLPK0Hfryi5zHbg3RMDSMCukmQCw"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.static_marker = StaticMapMarker()
        self.add_widget(self.static_marker)
        self.geocoder = GoogleMapsClient(key=self.API_KEY)
        self.init_cache()
        Clock.schedule_once(self.setup_map, 0)

    def init_cache(self):
        if not os.path.exists('map_cache.sqlite'):
            open('map_cache.sqlite', 'a').close()

    def setup_map(self, dt):
        # Set up the map source to use Google Maps with the 'roadmap' type
        self.map_source = MapSource(
            url="https://mt0.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",  # URL for Google 'roadmap' tiles
            attribution="Google Maps",
            max_zoom=10,
            min_zoom=10
        )
        self.center_marker()

    def center_marker(self):
        self.static_marker.lat = self.lat if hasattr(self, 'lat') else 0
        self.static_marker.lon = self.lon if hasattr(self, 'lon') else 0
        self.update_marker_position()

    def on_map_relocated(self, zoom, coord):
        super().on_map_relocated(zoom, coord)
        self.update_marker_position()

    def update_marker_position(self):
        scatter = self._scatter
        map_source = self.map_source
        zoom = self._zoom
        scale = self._scale

        x = self.width / 2
        y = self.height / 2

        lon = map_source.get_lon(zoom, (x - scatter.x) / scale - self.delta_x)
        lat = map_source.get_lat(zoom, (y - scatter.y) / scale - self.delta_y)

        self.static_marker.lat = lat
        self.static_marker.lon = lon

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            return True  # Block panning by returning True

        return super().on_touch_move(touch)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            return True  # Block zooming by returning True

        return super().on_touch_down(touch)


class SliverToolbar(MDTopAppBar):
    manager = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.left_action_items = [["arrow-left", lambda x: self.back_screen(), "color", (1, 0, 0, 1)]]

    def back_screen(self):
        screen = self.manager.get_screen('available_services')
        screen.remove_all_markers()
        self.manager.push_replacement('client_location')


class AvailableService(MDScreen):
    silver_tool_bar = SliverToolbar()
    location = None
    API_KEY = "AIzaSyA8GzhJLPK0Hfryi5zHbg3RMDSMCukmQCw"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.longitude = None
        self.latitude = None
        Window.bind(on_keyboard=self.on_keyboard)
        self.pincodes = None
        self.markers = []

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
        #self.fetch_list_of_pincodes()

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

        results_oxiclinics = app_tables.oxiclinics.search(oxiclinics_pincode=q.any_of(*pincodes))
        results_oxigyms = app_tables.oxigyms.search(oxigyms_pincode=q.any_of(*pincodes))
        results_oxiwheels = app_tables.oxiwheels.search(oxiwheels_pincode=q.any_of(*pincodes))

        all_results = list(results_oxiclinics) + list(results_oxigyms) + list(results_oxiwheels)

        self.ids.content.clear_widgets()

        if not all_results:
            self.show_no_service_popup()
            return

        # Add markers to the map
        services = []
        for service in all_results:
            service_dict = dict(service)
            print(f"Service: {service_dict}")

            # Fetch latitude and longitude based on pincode
            pincode = service_dict.get('oxiclinics_pincode') or service_dict.get('oxigyms_pincode') or service_dict.get(
                'oxiwheels_pincode')
            lat, lon = self.fetch_coordinates(pincode)
            name = service_dict.get('oxiclinics_Name') or service_dict.get('oxigyms_Name') or service_dict.get(
                'oxiwheels_Name')

            if lat is not None and lon is not None:
                services.append({
                    'lat': lat,
                    'lon': lon,
                    'name': name,
                })

            card = MDCard(
                orientation="vertical",
                size_hint=(None, None),
                size=("280dp", "100dp"),
                pos_hint={"center_x": 0.5, "center_y": 0.3},
                ripple_behavior=True,
            )

            box_layout = MDBoxLayout(orientation="horizontal", padding="8dp")

            service_name = ""
            service_district = ""
            image_source = ""
            if 'oxiclinics_Name' in service_dict:
                service_name = service_dict['oxiclinics_Name']
                service_district = service_dict['oxiclinics_District']
                image_source = "images/2.png"
            elif 'oxigyms_Name' in service_dict:
                service_name = service_dict['oxigyms_Name']
                service_district = service_dict['oxigyms_District']
                image_source = "images/3.png"
            elif 'oxiwheels_Name' in service_dict:
                service_name = service_dict['oxiwheels_Name']
                service_district = service_dict['oxiwheels_District']
                image_source = "images/1.png"
            else:
                print("Unknown service type or missing attribute")
                continue

            image = FitImage(
                source=image_source,
            )
            box_layout.add_widget(image)

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

        # Call the method to add service markers on the map
        self.update_map_location()
        map_view = self.ids.map_view2
        print(services)
        for location in services:
            marker = MapMarker(lat=location['lat'], lon=location['lon'])
            map_view.add_widget(marker)
            self.markers.append(marker)

    def remove_all_markers(self):
        map_view = self.ids.map_view2
        for marker in self.markers:
            map_view.remove_widget(marker)
        self.markers.clear()

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
        self.remove_all_markers()

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
                lat = data['results'][0]['geometry']['location']['lat']
                lng = data['results'][0]['geometry']['location']['lng']
                print(f'Latitude: {lat}, Longitude: {lng}')
                self.latitude = lat
                self.longitude = lng
            else:
                print('No results found')
                return []

        else:
            print(f'Error: {response.status_code}')
            return []

        pincodes_list = set()

        try:
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

            nearby_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
            nearby_params = {
                'location': f'{lat},{lng}',
                'radius': 30000,
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
            pincodes_list = [int(pincode) for pincode in pincodes_list]
            print(pincodes_list)

        except requests.exceptions.RequestException as e:
            print(e)
        except KeyError:
            print("Unexpected response format.")
        except Exception as e:
            print(e)

        self.pincodes = pincodes_list
        return pincodes_list

    def fetch_coordinates(self, pincode):
        geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={pincode}&key={self.API_KEY}'
        response = requests.get(geocode_url)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                location = data['results'][0]['geometry']['location']
                return location['lat'], location['lng']
        return None, None

    def update_map_location(self):
        if self.latitude is not None and self.longitude is not None:
            map_view = self.ids.map_view2
            map_view.center_on(self.latitude, self.longitude)
            map_view.static_marker.lat = self.latitude
            map_view.static_marker.lon = self.longitude
            map_view.zoom = 10
            map_view.update_marker_position()
