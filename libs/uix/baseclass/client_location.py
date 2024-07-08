import threading

import googlemaps
from googlemaps import Client as GoogleMapsClient
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.modalview import ModalView
from kivy_garden.mapview import MapView, MapMarker, MapSource
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget, OneLineAvatarIconListItem, OneLineAvatarListItem
from kivymd.uix.screen import MDScreen
from plyer import gps


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
    API_KEY = "AIzaSyAQhYOzS2RNq5CQOvCyuLhGqivDombb2Jo"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.static_marker = StaticMapMarker()
        self.add_widget(self.static_marker)
        self.geocoder = GoogleMapsClient(key=self.API_KEY)
        self.search_event = None
        self.cache_size_limit = 100
        self.cache = {}
        Clock.schedule_once(self.setup_map, 0)

    def setup_map(self, dt):
        self.map_source = MapSource(google_maps_api_key=self.API_KEY, source='google', attribution='Google Maps')
        self.center_marker()

    def center_marker(self):
        self.static_marker.lat = self.lat if hasattr(self, 'lat') else 0
        self.static_marker.lon = self.lon if hasattr(self, 'lon') else 0
        self.update_marker_position()
        self.update_text_field()

    def on_map_relocated(self, zoom, coord):
        super().on_map_relocated(zoom, coord)
        self.update_marker_position()
        self.update_text_field()

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            touch.ungrab(self)
            self._touch_count -= 1
            if self._touch_count == 0:
                self.update_marker_position()
                screen = self.manager.get_screen("client_location")
                if screen:
                    screen.hide_modal_view()
                return True
        return super().on_touch_up(touch)

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
            formatted_address = results[0].get('formatted_address', 'Address not found')
            self.cache[(lat, lon)] = formatted_address
            Clock.schedule_once(lambda dt: self.update_coordinate_text_field(lat, lon, formatted_address))
            self.manage_cache_size()

    def update_coordinate_text_field(self, lat, lon, address):
        screen = self.manager.get_screen("client_location")
        if screen:
            screen.ids.autocomplete.text = address

    def manage_cache_size(self):
        if len(self.cache) > self.cache_size_limit:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]


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
    API_KEY = "AIzaSyAQhYOzS2RNq5CQOvCyuLhGqivDombb2Jo"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_event = None
        self.dialog = None
        self.longitude = None
        self.latitude = None
        self.geocoder = GoogleMapsClient(key=self.API_KEY)
        self.custom_modal_view = None
        self.gps_active = False
        self.places_results = []  # Store the results for place details
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.back_button()
            return True
        return False

    def on_pre_enter(self):
        Clock.schedule_once(self.open_modal, 1)

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
        if not self.gps_active:
            self.start_gps()
        else:
            self.stop_gps()

    def start_gps(self):
        try:
            gps.configure(on_location=self.on_location_received)
            gps.start()
            self.gps_active = True
            print("GPS started successfully.")
        except NotImplementedError:
            print("GPS is not available on this platform.")

    def stop_gps(self):
        gps.stop()
        self.gps_active = False
        print("GPS stopped.")

    def on_location_received(self, **kwargs):
        self.latitude = kwargs.get('lat')
        self.longitude = kwargs.get('lon')
        print(f"Latitude: {self.latitude}, Longitude: {self.longitude}")
        self.update_map_to_current_location()
        self.hide_modal_view()
