import base64
import json
import os
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from twilio.rest import Client
import random
import smtplib
from email.message import EmailMessage
from kivy.core.window import Window
from anvil.tables import app_tables


class Otp(MDScreen):
    user_input = StringProperty('')
    otp_value = StringProperty('')
    client = Client("AC4fb872448415e76a64bcee4a212bd2b5", "ba7d4fb7562708df6cbf468a192dc743")

    def get_otp_call(self, user_input):
        if user_input:
            self.otp_value = str(random.randint(100000, 999999))
            self.send_voice_otp(user_input)
        else:
            self.show_popup("Please enter a phone number or email ID")

    def send_email_otp(self, email):
        try:
            from_mail = "oxivive@gmail.com"
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_mail, "bqrt soih plhy dnix")

            msg = EmailMessage()
            msg['Subject'] = "OTP Verification"
            msg['From'] = from_mail
            msg['To'] = email
            msg.set_content(f"Your OTP is: {self.otp_value}")
            server.send_message(msg)
            server.quit()
            self.show_popup(f"OTP is sent to {email}")
        except Exception as e:
            self.show_popup("Failed to send email. Please try again!")

    def send_sms_otp(self, user_input):
        try:
            self.client.messages.create(
                to=user_input,
                from_="+14175242099",
                body=f"Your OTP is: {self.otp_value}"
            )
            self.show_popup(f"OTP is sent to {user_input}")
        except Exception as e:
            self.show_popup("Failed to send SMS. Please try again!")

    def resend_otp(self, user_input):
        if user_input:
            if "@" in user_input:
                self.send_email_otp(user_input)
            else:
                self.send_sms_otp(user_input)
            self.show_popup(f"OTP is resent to {user_input}")
        else:
            self.show_popup("Please enter a phone number or email ID")

    def check_otp(self):
        entered_otp = self.ids.otp_input.text.strip()
        if entered_otp == self.otp_value:
            self.show_popup(
                "OTP verified successfully",
                on_ok=lambda: (self.save_user_data_after_otp(self.user_input), self.open_client_services())
            )
            self.ids.otp_input.text = ''  # Clear the OTP input field
        else:
            self.show_popup("Invalid OTP. Please try again.")

    def save_user_data_after_otp(self, user_input):
        user_anvil = None
        try:
            if "@" in user_input:
                user_anvil = app_tables.oxi_users.get(oxi_email=user_input)
            else:
                user_anvil = app_tables.oxi_users.get(oxi_phone=user_input)

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
                user_info = {
                    'username': username,
                    'email': email,
                    'phone': phone,
                    'pincode': pincode,
                    'profile': profile_data,
                    'id': id,
                    'address': address
                }

                script_dir = os.path.dirname(os.path.abspath(__file__))
                # Construct the path to the JSON file within the script's directory
                json_user_file_path = os.path.join(script_dir, "user_data.json")

                with open(json_user_file_path, "w") as json_file:
                    json.dump(user_info, json_file)
            else:
                self.show_popup("User not found in the database.")
        except Exception as e:
            self.show_popup("Error occurred while saving user data.")
            print(f"Exception: {e}")

    def send_voice_otp(self, user_input):
        try:
            self.client.calls.create(
                twiml=f'<Response><Say>Your OTP is {self.otp_value}</Say></Response>',
                to=user_input,
                from_="+14175242099"
            )
            self.show_popup(f"OTP is sent via call to: {user_input}")
        except Exception as e:
            self.show_popup("Failed to send voice OTP. Please try again!")

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
            background_color=(1, 0, 0, 1),  # Red color
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
            auto_dismiss=False  # Prevent dismissal without pressing OK
        )
        popup.open()

    def edit_user_input(self):
        self.manager.current = 'login'

    def open_client_services(self):
        self.manager.push('client_services')

    def show_otp_screen(self, user_contact):
        self.user_input = user_contact
        self.manager.current = 'otp'
