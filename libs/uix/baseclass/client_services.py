import base64
import io
import json
import os
from PIL.Image import Image
from anvil.tables import app_tables
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, DictProperty
from kivy.uix.image import Image as KivyImage
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.hero import MDHeroFrom
from kivymd.uix.imagelist import MDSmartTile
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from server import Server
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty

class Activity(MDBoxLayout):
    manager = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 20
        self.md_bg_color = get_color_from_hex("#FFFFFF")
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.back_btn()
            return True
        return False
    def back_btn(self):
        print("Back button pressed")
        if self.manager:
            screen = self.manager.get_screen('client_services')
            screen.ids.bottom_nav.switch_tab('home screen')
        else:
            print("Manager is not set.")

class BookingDetails(Screen):
    manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager = kwargs.get('manager', None)
        if self.manager is None:
            raise ValueError("Manager must be provided")


        toolbar = MDTopAppBar(
            title="My Bookings",
            elevation=0,
            pos_hint={'top': 1}
        )
        toolbar.left_action_items = [["arrow-left", lambda x: self.back_callback()]]
        toolbar.md_bg_color = get_color_from_hex("#FF0000")
        self.add_widget(toolbar)

        self.bookings_layout = MDBoxLayout(
            orientation='vertical',
            padding=(40, 30, 40, 10),
            spacing=15,
            size_hint_y=None
        )
        self.bookings_layout.bind(minimum_height=self.bookings_layout.setter('height'))

        scroll_view = ScrollView(size_hint=(1, None))
        toolbar_height = toolbar.height
        top_margin = 0.875
        bottom_margin = 0
        window_height = Window.height
        scroll_view_height = window_height * (top_margin - bottom_margin) - toolbar_height
        scroll_view.size = (Window.width, scroll_view_height)
        scroll_view.pos_hint = {'top': top_margin}
        scroll_view.pos = (0, (bottom_margin * window_height) - scroll_view_height)
        scroll_view.add_widget(self.bookings_layout)
        self.add_widget(scroll_view)

        Window.bind(on_keyboard=self.on_keyboard)

    def back_callback(self):
        screen = self.manager.get_screen('client_services')
        screen.ids.bottom_nav.switch_tab('home screen')

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.back_callback()
            return True
        return False

    def display_bookings(self, bookings):
        for booking in bookings:
            book_date = booking['oxi_book_date']
            book_time = booking['oxi_date_time']
            service_type = booking['service_type']
            user_id = booking['oxi_id']
            username = booking['username']
            booking_date_str = book_date.strftime('%d %B %Y')
            day, month, year = booking_date_str.split(' ')

            service_images = {
                "Oxi-Clinic": "images/1.png",
                "Oxi-Wheel": "images/3.png",
                "Oxi-Gym": "images/2.png"
            }
            image_source = service_images.get(service_type, "images/shot.png")

            booking_card = MDCard(
                orientation='horizontal',
                size_hint=(1, None),
                height='130dp',
                elevation=2,
                padding=13,
                spacing=10,
                md_bg_color=get_color_from_hex("#FFFFFF"),
                radius=[15, 15, 15, 15],
                on_release = lambda x, service_type=service_type, book_date=str(book_date),
                                book_time=book_time: self.view_booking_details(service_type, book_date,
                                                                               book_time)
            )

            left_layout = MDBoxLayout(orientation='horizontal', padding=(10, 10, 10, 10), size_hint_x=0.65)
            if image_source:
                left_layout.add_widget(KivyImage(source=image_source, size_hint=(None, None), size=("100dp", "100dp")))

            details_layout = MDBoxLayout(orientation='vertical', padding=(15, 0, 0, 10), spacing=37)
            details_layout.add_widget(
                MDLabel(text=f"Service Type: {service_type}", font_size='10sp', theme_text_color="Custom",
                        text_color=get_color_from_hex("#000000"), size_hint_y=None, height=20))
            details_layout.add_widget(
                MDLabel(text=f"User Name: {username}", font_size='10sp', theme_text_color="Custom",
                        text_color=get_color_from_hex("#000000"), size_hint_y=None, height=20))
            details_layout.add_widget(MDLabel(text=f"Time: {book_time}", font_size='10sp', theme_text_color="Custom",
                                              text_color=get_color_from_hex("#000000"), size_hint_y=None, height=20))
            left_layout.add_widget(details_layout)

            right_layout = MDBoxLayout(orientation='horizontal', size_hint_x=0.28, padding=(15, 0, 0, 5))
            date_layout = MDBoxLayout(orientation='vertical', size_hint=(None, None), size=("90dp", "90dp"),
                                      md_bg_color=get_color_from_hex("#C0C0C0"), radius=[15, 15, 15, 15])
            date_layout.add_widget(
                MDLabel(text=day, theme_text_color="Custom", text_color=get_color_from_hex("#000000"), halign="center"))
            date_layout.add_widget(
                MDLabel(text=month, theme_text_color="Custom", text_color=get_color_from_hex("#000000"),
                        halign="center"))
            date_layout.add_widget(
                MDLabel(text=year, theme_text_color="Custom", text_color=get_color_from_hex("#000000"),
                        halign="center"))

            # button_layout = MDBoxLayout(orientation='vertical', size_hint=(None, None), size=("60dp", "60dp"),
            #                             padding=(0, 0, 5, 10))
            # button_layout.add_widget(
            #     MDIconButton(icon="chevron-right", theme_text_color="Custom", text_color=get_color_from_hex("#000000"),
            #                  pos_hint={"center_y": 0.5},
            #                  on_release=lambda x, service_type=service_type, book_date=str(book_date),
            #                                    book_time=book_time: self.view_booking_details(service_type, book_date,
            #                                                                                   book_time)))

            right_layout.add_widget(date_layout)
            #right_layout.add_widget(button_layout)

            booking_card.add_widget(left_layout)
            booking_card.add_widget(right_layout)
            self.bookings_layout.add_widget(booking_card)

    def view_booking_details(self, service_type, book_date, book_time):
        self.manager.load_screen("details")
        details_screen = self.manager.get_screen('details')
        details_screen.set_details(service_type, book_date, book_time)
        self.manager.current = 'details'

    def go_back(self):
        self.root.current = 'booking_details'


class Profile_screen(Screen):
    scroll_view = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Profile_screen, self).__init__(**kwargs)

    def on_kv_post(self, base_widget):
        self.server = Server()
        print("IDs dictionary:", self.ids)  # Debugging line

        try:
            # Load user information from JSON file
            with open('user_data.json', 'r') as file:
                self.user_info = json.load(file)

            # Update username and phone if their IDs are present
            if 'username' in self.ids:
                self.ids.username.text = self.user_info.get('username', '')
            else:
                print("Username ID not found")
            if 'phone' in self.ids:
                self.ids.phone.text = str(self.user_info.get('phone', ''))
            else:
                print("Phone ID not found")

            # Schedule a check for server connection
            Clock.schedule_once(self.check_server_connection, 1)
        except FileNotFoundError:
            print("user_data.json file not found.")
        except Exception as e:
            print("An error occurred:", str(e))

    def check_server_connection(self, dt):
        if self.server.is_connected():
            print("Connected to server")
            self.fetch_data_from_server()
        else:
            print("Not connected to server, retrying...")
            Clock.schedule_once(self.check_server_connection, 1)

    def fetch_data_from_server(self):
        try:
            details = app_tables.oxi_users.get(oxi_id=self.user_info.get('id'))

            if details:
                oxi_profile = details['oxi_profile']

                if oxi_profile:
                    current_dir = os.getcwd()
                    image_path = os.path.join(current_dir, 'profile_image.png')
                    with open(image_path, 'wb') as img_file:
                        img_file.write(oxi_profile.get_bytes())

                    if 'profile_image' in self.ids:
                        self.ids.profile_image.source = image_path
                        self.ids.profile_image.reload()
                    else:
                        print("Profile image ID not found")
        except KeyError as e:
            print(f"KeyError occurred while fetching data from server: {e}")
        except AttributeError as e:
            print(f"AttributeError occurred while fetching data from server: {e}")
        except Exception as e:
            print(f"An error occurred while fetching data from server: {e}")

    def go_back(self):
        self.manager.current = 'client_services'

    def notifications(self):
        self.manager.load_screen("menu_notification")
        self.manager.push_replacement("menu_notification")

    def profile(self):
        self.manager.load_screen("menu_profile")
        self.manager.push_replacement("menu_profile")

    def Bookings(self):
        self.manager.load_screen("menu_bookings")
        self.manager.push_replacement("menu_bookings")

    def Reports(self):
        self.manager.load_screen("menu_reports")
        self.manager.push_replacement("menu_reports")

    def Support(self):
        self.manager.load_screen("menu_support")
        self.manager.push_replacement("menu_support")

    def Log_out(self):
        self.manager.push_replacement("login", "right")
        try:
            with open('user_data.json', 'r') as file:
                user_info = json.load(file)
            user_info.update({
                'username': "",
                'email': "",
                'phone': "",
                'pincode': "",
                'password': ""
            })
            with open("user_data.json", "w") as json_file:
                json.dump(user_info, json_file)

            logged_in_data = {'logged_in': False}
            with open("logged_in_data.json", "w") as json_file:
                json.dump(logged_in_data, json_file)
        except FileNotFoundError:
            print("user_data.json file not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
class NavigationDrawerScreen(MDScreen):
    pass

class CustomImageTile(MDSmartTile):

    def on_release(self, *args):
        print("next screen")
        pass


class ClickableTextFieldRound(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()

    def on_focus(self):
        pass


class HeroItem(MDHeroFrom):
    text = StringProperty()
    text2 = StringProperty()
    tag = StringProperty()
    manager = ObjectProperty()
    id = ObjectProperty()
    details = DictProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.ids.tile.ids.image.ripple_duration_in_fast = 0.05

    def on_transform_in(self, instance_hero_widget, duration):
        print('in')
        Animation(
            radius=[0, 0, 0, 0],
            box_radius=[0, 0, 0, 0],
            duration=duration,
        ).start(instance_hero_widget)

    def on_transform_out(self, instance_hero_widget, duration):
        print('out')
        Animation(
            radius=[10, 10, 10, 10],
            box_radius=[0, 0, 10, 10],
            duration=duration,
        ).start(instance_hero_widget)

    def on_release(self):
        def switch_screen(*args):
            self.manager.current_heroes = [self.tag]
            self.manager.load_screen("servicer_details")
            screen = self.manager.get_screen("servicer_details")
            screen.ids.hero_to.tag = self.tag  # Access hero_to through ids
            # Extract the table identifier and ID from the tag
            table_identifier = self.tag[:2]

            # Check and fetch the description from the appropriate table
            if table_identifier == 'OC':
                discription_row = app_tables.oxiclinics.get(oxiclinics_id=self.tag)
                if discription_row:
                    discription = discription_row['oxiclinics_discription']
                    if discription == None:
                        discription = 'No description available'
                else:
                    discription = 'No description available'
            elif table_identifier == 'OW':
                discription_row = app_tables.oxiwheels.get(oxiwheels_id=self.tag)
                if discription_row:
                    discription = discription_row['oxiwheels_discrption']
                    if discription == None:
                        discription = 'No description available'
                else:
                    discription = 'No description available'
            elif table_identifier == 'OG':
                discription_row = app_tables.oxigyms.get(oxigyms_id=self.tag)
                if discription_row:
                    discription = discription_row['oxigyms_discrption']
                    if discription == None:
                        discription = 'No description available'
                else:
                    discription = 'No description available'

            print(discription)

            screen.ids.discrptions.text = discription
            self.manager.push("servicer_details")

        Clock.schedule_once(switch_screen, 0.2)


class Client_services(MDScreen):
    def __init__(self, **kwargs):
        super(Client_services, self).__init__(**kwargs)

        self.server = Server()
        #self.change()

    def change(self):
        with open('user_data.json', 'r') as file:
            user_info = json.load(file)
        self.ids.username.text = f"{user_info['username']}"
        self.ids.email.text = f"{user_info['email']}"
        try:
            profile_texture = base64.b64decode(user_info['profile'])
        except:
            # Load the image
            image_path = 'images/profile.jpg'
            # image = Image.open(image_path)

            # Convert the image to a byte array
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            profile_texture=img_byte_arr
        profile_image_path = "profile_image.png"
        with open(profile_image_path, "wb") as profile_image_file:
            profile_image_file.write(profile_texture)
        self.ids.image.source = profile_image_path

    def on_pre_enter(self):

        #self.change()
        images = ['images/1.png', 'images/2.png', 'images/3.png', 'images/gym.png']
        for i in images:
            environment_img = CustomImageTile(
                source=i
            )
            self.ids.box3.add_widget(environment_img)

    def logout(self):
        self.manager.current_heroes = []
        self.ids.bottom_nav.switch_tab('home screen')
        self.manager.push_replacement("login", "right")
        with open('user_data.json', 'r') as file:
            user_info = json.load(file)
        user_info['username'] = ""
        user_info['email'] = ""
        user_info['phone'] = ""
        user_info['pincode'] = ""
        user_info['password'] = ""
        with open("user_data.json", "w") as json_file:
            json.dump(user_info, json_file)
        logged_in_data = {'logged_in': False}
        with open("logged_in_data.json", "w") as json_file:
            json.dump(logged_in_data, json_file)

    def home(self):
        self.ids.bottom_nav.switch_tab('home screen')

    def location_screen(self):
        self.manager.current_heroes = []
        self.manager.load_screen("client_location")
        self.manager.get_screen("client_location")
        self.manager.push_replacement("client_location")

    def book_now(self, organization_name, organization_address):
        print(organization_name, organization_address)
        organization_info = {'organization_name': organization_name, 'organization_address': organization_address}
        with open("organization_data.json", "w") as json_file:
            json.dump(organization_info, json_file)
        self.manager.push("hospital_booking")

    def switch_to_service_screen(self):
        self.ids.bottom_nav.switch_tab('service_screen')
    # def activity_report(self):
    #     #current_user_id="000000"
    #     current_user = app_tables.oxi_users.get()
    #     current_user_id = current_user['oxi_id']
    #     print(current_user_id)
    #     all_bookings = app_tables.oxi_book_slot.search()  # Fetch all bookings
    #     bookings = [booking for booking in all_bookings if booking['oxi_id'] == current_user_id]
    #     self.ids.activity.clear_widgets()  # Clear existing widgets first
    #     print(f"Bookings found: {bookings}")
    #
    #     if not bookings:
    #         print("No bookings found, displaying Activity UI")
    #         self.ids.activity.add_widget(Activity(manager=self.manager))
    #     else:
    #         print("Bookings found, displaying booking details")
    #         booking_details = BookingDetails(manager=self.manager)  # Pass the manager
    #         booking_details.display_bookings(bookings)
    #         self.ids.activity.add_widget(booking_details)

    def activity_report(self):
        current_user_id="000000"
        # Assuming your JSON file structure looks like {'user_id': 'some_user_id'}
        with open('user_data.json', 'r') as f:
            data = json.load(f)
            #current_user_id = data.get('id', None)

        if current_user_id is None:
            print("User ID not found in JSON file.")
            return

        print(f"Current user ID: {current_user_id}")

        all_bookings = app_tables.oxi_book_slot.search()  # Fetch all bookings
        bookings = [booking for booking in all_bookings if booking['oxi_id'] == current_user_id]

        self.ids.activity.clear_widgets()  # Clear existing widgets first
        print(f"Bookings found: {bookings}")

        if not bookings:
            print("No bookings found, displaying Activity UI")
            self.ids.activity.add_widget(Activity(manager=self.manager))
        else:
            print("Bookings found, displaying booking details")
            booking_details = BookingDetails(manager=self.manager)  # Pass the manager
            booking_details.display_bookings(bookings)
            self.ids.activity.add_widget(booking_details)