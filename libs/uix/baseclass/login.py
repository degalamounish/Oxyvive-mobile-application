import base64
import json
import bcrypt
import random
import smtplib
from email.message import EmailMessage

from io import BytesIO
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivymd.uix.screen import MDScreen
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from twilio.rest import Client
from anvil.tables import app_tables

from server import Server

class Login(MDScreen):
    def __init__(self, **kwargs):
        super(Login, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)
        self.server = Server()

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def google_sign_in(self):
        # Implement Google sign-in logic here
        print("Clicked on Google Sign-in. Implement Google sign-in logic.")

    def on_back_button(self):
        self.manager.push_replacement("main_sc", "right")

    def verify_login(self):
        if self.ids.login_with_otp.active:
            self.send_otp()
            self.ids.login_email.text = ''
        else:
            self.login_page()

    def login_page(self, instance=None, *args):
        user_type = None
        password_value = False
        password_value2 = False
        user_input = self.ids.login_email.text.strip()
        entered_password = self.ids.login_password.text.strip()

        if not user_input and not entered_password:
            self.ids.login_email.error = True
            self.show_popup("Please enter email/phone and password")
            return

        if not user_input:
            self.ids.login_email.error = True
            self.show_popup("Please enter email/phone")
            return

        if not entered_password and not self.ids.login_with_otp.active:
            self.ids.login_password.error = True
            self.show_popup("Please enter password")
            return

        user_anvil = None
        user_sqlite = None
        try:
            if self.server.is_connected():
                # Fetch user from Anvil's database
                if "@" in user_input:
                    user_anvil = app_tables.oxi_users.get(oxi_email=user_input)
                else:
                    try:
                        user_input = int(user_input)
                        user_anvil = app_tables.oxi_users.get(oxi_phone=user_input)
                    except ValueError:
                        self.show_popup("Invalid phone number format")
                        return
            else:
                # Fetch user from SQLite database
                cursor = self.server.get_database_connection().cursor()
                cursor.execute('''
                                SELECT * FROM users
                                WHERE email = ? OR phone = ?
                                ''', (user_input, user_input))
                user_sqlite = cursor.fetchone()
        finally:
            # Close the connection
            if self.server.get_database_connection() and self.server.is_connected():
                self.server.get_database_connection().close()

        if user_anvil or user_sqlite:
            if user_anvil is not None:
                password_value = bcrypt.checkpw(entered_password.encode('utf-8'),
                                                user_anvil['oxi_password'].encode('utf-8'))
                user_type = user_anvil['oxi_usertype']
            if user_sqlite is not None:
                password_value2 = bcrypt.checkpw(entered_password.encode('utf-8'),
                                                 user_sqlite[3].encode('utf-8'))
            print('Password : ', password_value)
            print('Password : ', password_value2)
            if user_type == 'client':
                if password_value or password_value2:
                    self.show_popup(
                        "Login successful!",
                        on_ok=lambda: self.manager.push('client_services')
                    )
                    if user_anvil:
                        username = str(user_anvil["oxi_username"])
                        email = str(user_anvil["oxi_email"])
                        password = str(user_anvil["oxi_password"])
                        phone = str(user_anvil["oxi_phone"])
                        pincode = str(user_anvil["oxi_pincode"])
                        id = str(user_anvil['oxi_id'])
                        try:
                            profile_data = user_anvil['oxi_profile'].get_bytes()
                            profile_data = base64.b64encode(profile_data).decode('utf-8')
                        except (KeyError, AttributeError):
                            profile_data = ''

                    if user_sqlite:
                        username = user_sqlite[1]
                        email = user_sqlite[2]
                        password = user_sqlite[3]
                        phone = user_sqlite[4]
                        pincode = user_sqlite[0]
                        print(f"hi {username}")
                    logged_in = True
                    self.manager.load_screen("menu_profile")
                    logged_in_data = {'logged_in': logged_in}
                    user_info = {'username': username, 'email': email, 'phone': phone, 'pincode': pincode,
                                 'password': password, 'profile': profile_data,'id':id }
                    with open("logged_in_data.json", "w") as json_file:
                        json.dump(logged_in_data, json_file)
                    with open("user_data.json", "w") as json_file:
                        json.dump(user_info, json_file)
                    self.manager.load_screen("client_services")
                    screen = self.manager.get_screen("client_services")
                    screen.ids.username.text = user_info['username']
                    screen.ids.email.text = user_info['email']
                    profile_texture = base64.b64decode(profile_data)
                    profile_image_path = "profile_image.png"

                    with open(profile_image_path, "wb") as profile_image_file:
                        profile_image_file.write(profile_texture)

                    screen.ids.image.source = profile_image_path
            elif user_type == 'service provider':
                if password_value:
                    self.show_popup(
                        "Login successful!",
                        on_ok=self.open_servicer_dashboard
                    )
                    if user_anvil:
                        username = str(user_anvil["oxi_username"])
                        email = str(user_anvil["oxi_email"])
                        phone = str(user_anvil["oxi_phone"])
                        pincode = str(user_anvil["oxi_pincode"])
                        address = str(user_anvil['oxi_address'])
                        try:
                            profile_data = user_anvil['oxi_profile'].get_bytes()
                            profile_data = base64.b64encode(profile_data).decode('utf-8')
                        except (KeyError, AttributeError):
                            profile_data = ''
                        id = user_anvil["oxi_id"]
                    user_info = {'username': username, 'email': email, 'phone': phone, 'pincode': pincode,
                                 'profile': profile_data, 'id': id, 'address': address}
                    with open("user_data.json", "w") as json_file:
                        json.dump(user_info, json_file)
                    self.manager.load_screen("servicer_dashdoard")
                    screen = self.manager.get_screen("servicer_dashboard")
                    screen.ids.srv_username.text = user_info['username']
                    screen.ids.srv_email.text = user_info['email']
                    profile_texture = base64.b64decode(profile_data)
                    profile_image_path = "profile_image.png"

                    with open(profile_image_path, "wb") as profile_image_file:
                        profile_image_file.write(profile_texture)

                    screen.ids.profile_image.source = profile_image_path
        else:
            self.ids.login_email.error = True
            self.show_popup("Invalid email or password")
            self.ids.login_password.error = True

        self.ids.login_email.text = ''
        self.ids.login_password.text = ''

    user_input = StringProperty('')
    otp_value = StringProperty('')
    otp_screen_visible = BooleanProperty(False)
    client = Client("AC4fb872448415e76a64bcee4a212bd2b5", "ba7d4fb7562708df6cbf468a192dc743")
    n = random.randint(100000, 999999)

    def send_otp(self):
        user_input = self.ids.login_email.text
        if user_input:
            self.n = random.randint(100000, 999999)
            if "@" in user_input:
                self.send_email_otp(user_input)
            else:
                self.send_sms_otp(user_input)
        else:
            self.show_popup("Please enter a phone number or email ID")

    def send_email_otp(self, email):
        try:
            from_mail = "yathishgowda509@gmail.com"
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_mail, "dwtf ixkg fhom fmua")

            msg = EmailMessage()
            msg['Subject'] = "OTP Verification"
            msg['From'] = from_mail
            msg['To'] = email
            msg.set_content(f"Your OTP is: {self.n}")
            server.send_message(msg)
            server.quit()
            self.show_popup(
                f"OTP sent via Email {email}",
                on_ok=lambda: self.show_otp_screen(email, self.n)
            )
        except Exception as e:
            self.show_popup("Failed to send email, try again!")

    def send_sms_otp(self, user_input):
        try:
            self.client.messages.create(
                to=user_input,
                from_="+14175242099",
                body=f"Your OTP is: {self.n}"
            )
            self.show_popup(
                f"OTP sent via SMS {user_input}",
                on_ok=lambda: self.show_otp_screen(user_input, self.n)
            )
        except Exception as e:
            self.show_popup("Failed to send SMS, try again!")

    def show_popup(self, message, on_ok=None):
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        message_label = Label(
            font_size=25,
            text=message,
            text_size=(0.8 * Window.width, None),
            halign='center',
            valign='middle',
            color=(0, 0, 0, 1)  # RGB Black
        )
        message_label.bind(size=message_label.setter('text_size'))

        ok_button = Button(
            text="OK",
            font_size=dp(18),
            size_hint=(None, None),
            size=(dp(100), dp(40)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(1, 0, 0, 1),  # Blue color
            color=(1, 1, 1, 1),  # White text color
            on_release=lambda x: (popup.dismiss(), on_ok() if on_ok else None)
        )

        popup_content.add_widget(message_label)
        popup_content.add_widget(ok_button)

        popup = Popup(
            title='Info',
            title_color='black',
            content=popup_content,
            size_hint=(0.8, 0.3),
            background='white',
        )
        popup.open()

    def open_client_services(self):
        self.manager.current = 'client_services'

    def open_servicer_dashboard(self):
        self.manager.current = 'servicer_dashboard'

    def show_otp_screen(self, user_input, otp_value):
        self.manager.load_screen('otp')
        otp_screen = self.manager.get_screen('otp')
        otp_screen.user_input = user_input
        otp_screen.otp_value = str(otp_value)
        self.manager.current = 'otp'

    def edit_user_input(self):
        self.manager.current = 'login'

    def get_otp_call(self):
        user_input = self.ids.user_input.text
        if user_input:
            self.n = random.randint(100000, 999999)
            self.send_voice_otp(user_input)
        else:
            self.show_popup("Please enter a phone number or email ID")

    def resend_otp(self):
        user_input = self.ids.user_input.text
        if user_input:
            if "@" in user_input:
                self.send_email_otp(user_input)
            else:
                self.send_sms_otp(user_input)
            self.show_popup(f"OTP resent successfully {user_input}")
        else:
            self.show_popup("Please enter a phone number or email ID")

    def check_otp(self):
        entered_otp = self.ids.otp_input.text.strip()
        if entered_otp == self.otp_value:
            self.show_popup("OTP verified successfully")
        else:
            self.show_popup("Invalid OTP. Please try again.")

    def send_voice_otp(self, user_input):
        self.client.calls.create(
            twiml=f'<Response><Say>Your OTP is {self.otp_value}</Say></Response>',
            to=user_input,
            from_="+14175242099"
        )
