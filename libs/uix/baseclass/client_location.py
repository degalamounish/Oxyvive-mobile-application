import logging
import os
import re
import threading
from kivy.clock import Clock
import requests
from PIL import Image
from diskcache import Cache as DiskCache
from googlemaps import Client as GoogleMapsClient
from kivy.animation import Animation
from kivy.config import Config
from kivy.core.image import Texture
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.modalview import ModalView
from kivy.utils import platform
from kivy_garden.mapview import MapView, MapMarker, MapSource
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget, OneLineAvatarIconListItem, OneLineAvatarListItem
from kivymd.uix.screen import MDScreen
from plyer import gps
from plyer.utils import platform

if platform == 'android':
    from kivy.uix.modalview import ModalView
    from kivy.clock import Clock
    from android.permissions import (
        request_permissions, check_permission, Permission
    )

logging.basicConfig(level=logging.DEBUG)


class CustomModalView(DragBehavior, ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drag_start_y = 0
        self.background = 'rgba(0, 0, 0, 0)'
        self.overlay_color = (0, 0, 0, 0)
        self.size_hint = (None, None)
        self.height = Window.height - dp(149)  # Initial height is set to 400dp
        self.update_width()  # Set initial width
        self.update_position()  # Set initial position
        Window.bind(on_resize=self.on_window_resize)  # Bind resize event

    def on_window_resize(self, instance, width, height):
        self.update_width()
        self.update_position()

    def update_width(self):
        self.width = Window.width

    def update_position(self):
        self.pos = (0, 0)  # Position the modal view at the bottom of the screen

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.drag_start_y = touch.y
            return super().on_touch_down(touch)
        return False

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            dy = touch.y - self.drag_start_y
            new_height = self.height + dy
            max_height = Window.height - dp(149)
            if new_height < max_height:
                self.height = max(dp(100), new_height)
            self.drag_start_y = touch.y
            return True
        return False

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            return super().on_touch_up(touch)

    def dismiss_modal(self):
        self.dismiss()

    def open(self, *args):
        self.update_position()
        return super().open(*args)


class CustomButtonMap(MDFloatingActionButton):
    def set_size(self, *args):
        self.size = (dp(40), dp(40))


class StaticMapMarker(MapMarker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lat = kwargs.get('lat', 0)
        self.lon = kwargs.get('lon', 0)


class CustomMapView(MapView):
    manager = ObjectProperty()
    API_KEY = "AIzaSyA8GzhJLPK0Hfryi5zHbg3RMDSMCukmQCw"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.static_marker = StaticMapMarker()
        self.add_widget(self.static_marker)
        self.geocoder = GoogleMapsClient(key=self.API_KEY)
        self.cache_size_limit = 100
        self.cache = {}
        self.tile_cache_limit = 200  # Limit number of tiles to cache
        self.tile_cache = DiskCache('tile_cache')
        self.init_cache()
        self.enable_hardware_acceleration()
        Clock.schedule_once(self.setup_map, 0)

    def init_cache(self):
        if not os.path.exists('map_cache.sqlite'):
            open('map_cache.sqlite', 'a').close()

    def setup_map(self, dt):
        # Set up the map source to use Google Maps with the 'roadmap' type
        self.map_source = MapSource(
            url="https://mt0.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",  # URL for Google 'roadmap' tiles
            attribution="Google Maps",
            max_zoom=15,
            min_zoom=8
        )
        self.center_marker()

    def center_marker(self):
        self.static_marker.lat = self.lat if hasattr(self, 'lat') else 0
        self.static_marker.lon = self.lon if hasattr(self, 'lon') else 0
        self.update_marker_position()
        self.update_text_field()

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            screen = self.manager.get_screen("client_location")
            screen.hide_modal_view()
        return super().on_touch_up(touch)

    def on_map_relocated(self, zoom, coord):
        super().on_map_relocated(zoom, coord)
        self.update_marker_position()
        self.update_text_field()

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

    def update_text_field(self):
        lat = self.static_marker.lat
        lon = self.static_marker.lon
        coord_key = (lat, lon)
        if coord_key in self.cache:
            self.update_coordinate_text_field(lat, lon, self.cache[coord_key])
        else:
            threading.Thread(target=self.fetch_address, args=(lat, lon)).start()

    def fetch_address(self, lat, lon):
        results = self.geocoder.reverse_geocode((lat, lon))
        if results:
            full_address = results[0].get('formatted_address', 'Address not found')
            short_address = self.get_short_address(full_address)
            self.cache[(lat, lon)] = short_address
            Clock.schedule_once(lambda dt: self.update_coordinate_text_field(lat, lon, short_address))
            self.manage_cache_size()

    def get_short_address(self, address):
        # Split the address by commas
        parts = address.split(',')
        filtered_parts = [part.strip() for part in parts if not re.match(r'^[A-Z0-9]+\s+\w+', part.strip())]
        short_address = ', '.join(filtered_parts[:5])

        return short_address

    def update_coordinate_text_field(self, lat, lon, address):
        screen = self.manager.get_screen("client_location")
        if screen:
            screen.ids.autocomplete.text = address

    def manage_cache_size(self):
        if len(self.cache) > self.cache_size_limit:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

    def cache_tile(self, tile_key, tile_data):
        if len(self.tile_cache) > self.tile_cache_limit:
            oldest_tile_key = next(iter(self.tile_cache))
            del self.tile_cache[oldest_tile_key]
        self.tile_cache[tile_key] = tile_data

    def get_cached_tile(self, tile_key):
        return self.tile_cache.get(tile_key)

    def fetch_tile(self, zoom, x, y):
        tile_key = (zoom, x, y)
        cached_tile = self.get_cached_tile(tile_key)
        if cached_tile:
            return cached_tile
        else:
            try:
                # Fetch tile from Google Maps or another tile server
                url = f"https://mt.google.com/vt/lyrs=m&x={x}&y={y}&z={zoom}&key={self.API_KEY}"
                response = requests.get(url)
                response.raise_for_status()
                tile_data = response.content
                self.cache_tile(tile_key, tile_data)
                return tile_data
            except requests.RequestException as e:
                logging.error(f"Error fetching tile: {e}")
                return None

    def optimize_tile_fetching(self):
        try:
            # Use cached tiles if available, fetch new tiles only if necessary
            for tile in self.get_tiles():
                zoom, x, y = tile
                tile_data = self.fetch_tile(zoom, x, y)
                if tile_data:
                    self.display_tile(tile_data, x, y)
        except Exception as e:
            logging.error(f"Error optimizing tile fetching: {e}")

    def get_tiles(self):
        # Returns the list of tiles (zoom, x, y) that should be displayed
        tiles = []
        for child in self._scatter.children:
            zoom = self.zoom
            x, y = child.tile_pos
            tiles.append((zoom, x, y))
        return tiles

    def enable_hardware_acceleration(self):
        Config.set('graphics', 'multisamples', '4')
        Config.set('graphics', 'allow_screensaver', '0')
        Config.set('kivy', 'default_font', ['Roboto', 'data/fonts/Roboto-Regular.ttf', 'data/fonts/Roboto-Italic.ttf',
                                            'data/fonts/Roboto-Bold.ttf', 'data/fonts/Roboto-BoldItalic.ttf'])

    def display_tile(self, tile_data, x, y):
        # Create a texture from the tile data
        tile_texture = Texture.create(size=(256, 256))
        tile_texture.blit_buffer(tile_data, colorfmt='rgb', bufferfmt='ubyte')
        tile_texture.flip_vertical()

        # Create an Image widget to display the texture
        tile_image = Image(texture=tile_texture, size=(256, 256))

        # Calculate the position of the tile
        tile_pos = self.map_source.get_rowcol(self.zoom, self.lat, self.lon)
        tile_x = x - tile_pos[1]
        tile_y = y - tile_pos[0]
        tile_image.pos = (tile_x * 256, tile_y * 256)

        # Add the tile image to the map
        self.add_widget(tile_image)


class Item(OneLineAvatarListItem):
    source = StringProperty()
    manager = ObjectProperty()

    def set_screen(self):
        print('dismiss dialog')
        screen = self.manager.get_screen("client_location")
        screen.hide_dialog()


class ItemConfirm(OneLineAvatarIconListItem):
    manager = ObjectProperty()

    def set_screen(self):
        print('next screen')
        screen = self.manager.get_screen("client_location")


class ClientLocation(MDScreen):
    API_KEY = "AIzaSyA8GzhJLPK0Hfryi5zHbg3RMDSMCukmQCw"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gps = None
        self.search_event = None
        self.dialog = None
        self.longitude = None
        self.latitude = None
        self.geocoder = GoogleMapsClient(key=self.API_KEY)
        self.custom_modal_view = None
        self.fetch_location_details(self)
        self.gps_active = False
        self.places_results = []  # Store the results for place details
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.back_button()
            return True
        return False

    def on_pre_enter(self):
        Clock.schedule_once(self.request_location_permission, 0.5)
        Clock.schedule_once(self.open_modal, 1)

    def request_location_permission(self, *args):
        if platform == 'android':
            if not check_permission(Permission.ACCESS_FINE_LOCATION):
                request_permissions(
                    [Permission.ACCESS_FINE_LOCATION],
                    self.permission_callback
                )
            else:
                self.start_gps()

    def permission_callback(self, permissions_granted):
        if permissions_granted:
            self.start_gps()
        else:
            print("Location permission denied")

    def open_modal(self, _):
        self.custom_modal_view = CustomModalView()
        self.custom_modal_view.open()
        self.show_modal_view()

    def search_location(self, instance, text):
        if self.search_event:
            self.search_event.cancel()
        self.search_event = Clock.schedule_once(lambda dt: self.perform_search(text), 0.2)

    def perform_search(self, text):
        if text:
            threading.Thread(target=self.fetch_location_data, args=(text,)).start()

    def fetch_location_data(self, text):
        results = self.geocoder.places_autocomplete(text)
        self.places_results = results
        self.display_search_results(results)

    def display_search_results(self, results):
        def update_results():
            if self.custom_modal_view:
                self.custom_modal_view.ids.search_results.clear_widgets()
                if results:
                    for result in results:
                        description = result.get("description")
                        if description:
                            item = OneLineIconListItem(IconLeftWidget(icon="map-marker"), text=description)
                            item.bind(on_release=self.on_location_selected)
                            self.custom_modal_view.ids.search_results.add_widget(item)
                else:
                    print("No results found.")

        Clock.schedule_once(lambda dt: update_results())

    def on_location_selected(self, instance):
        selected_description = instance.text
        selected_place = next((place for place in self.places_results if place["description"] == selected_description),
                              None)
        if selected_place:
            place_id = selected_place['place_id']
            threading.Thread(target=self.fetch_place_details, args=(place_id,)).start()

    def fetch_place_details(self, place_id):
        place_details = self.geocoder.place(place_id=place_id)
        location = place_details['result']['geometry']['location']
        self.latitude = location['lat']
        self.longitude = location['lng']
        Clock.schedule_once(lambda dt: self.update_ui_with_place_details(place_details), 0)

    def update_ui_with_place_details(self, place_details):
        self.ids.autocomplete.text = place_details['result']['formatted_address']
        self.update_map_to_current_location()
        self.hide_modal_view()

    def update_map_to_current_location(self):
        if self.latitude is not None and self.longitude is not None:
            map_view = self.ids.map_view
            map_view.center_on(self.latitude, self.longitude)
            map_view.static_marker.lat = self.latitude
            map_view.static_marker.lon = self.longitude
            map_view.zoom = 13
            map_view.update_marker_position()

    def on_text_field_focus(self, instance, value):
        if value:
            self.show_modal_view()
        else:
            pass

    def show_modal_view(self):
        if not self.custom_modal_view:
            self.custom_modal_view = CustomModalView(size=(Window.width, Window.height - dp(150)))
        anim = Animation(opacity=1, duration=0.3)
        anim.start(self.custom_modal_view)
        self.custom_modal_view.open()

    def hide_modal_view(self):
        if self.custom_modal_view:
            anim = Animation(opacity=0, duration=0.3)
            anim.bind(on_complete=lambda *x: self.custom_modal_view.dismiss())
            anim.start(self.custom_modal_view)

    def show_confirmation_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Someone else taking this appointment?",
                type="confirmation",
                items=[
                    Item(text="Myself", source="images/profile.jpg", manager=self.manager),
                    ItemConfirm(text="Choose another contact", manager=self.manager),
                ],
            )
        self.dialog.open()

    def hide_dialog(self):
        if self.dialog:
            self.dialog.dismiss()

    def back_button(self):
        self.hide_modal_view()
        self.manager.push_replacement('client_services')

    def next_screen(self):
        self.manager.load_screen('available_services')
        screen = self.manager.get_screen('available_services')
        screen.location = self.ids.autocomplete.text
        self.manager.push_replacement('available_services')

    def fetch_location_details(self, instance):
        if platform == 'android':
            self.gps = gps
            self.gps.configure(on_location=self.on_location)
            Clock.schedule_once(self.start_gps)
            self.start_gps()
        if platform == 'win':
            self.fetch_location_from_google()

    def start_gps(self, *args):
        gps.start()

    def stop_gps(self):
        gps.stop()

    def on_location(self, **kwargs):
        self.latitude = kwargs.get('lat')
        self.longitude = kwargs.get('lon')
        print(f"Latitude: {self.latitude}, Longitude: {self.longitude}")
        self.update_map_to_current_location()
        self.hide_modal_view()

    def fetch_location_from_google(self):
        url = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + self.API_KEY
        headers = {'Content-Type': 'application/json'}
        data = {}
        try:

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                location_data = response.json()
                self.latitude = location_data['location']['lat']
                self.longitude = location_data['location']['lng']
                print(f"Latitude: {self.latitude}, Longitude: {self.longitude}")
                # Now you can update your UI or perform any other actions with the location data
                self.update_map_to_current_location()
                self.hide_modal_view()
            else:
                print(f"Failed to fetch location: {response.status_code}")
        except Exception:
            pass
