import re

import anvil
from anvil.tables import app_tables
from kivy import platform
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from twilio.rest import Client


# Your Twilio credentials
account_sid = "AC64ab0fed3c9135f8011fb5e50f969cbe"
auth_token = "2c450c5297067c3a88b338397d95beaf"
verify_sid = "VA8937ab1f8c09c4e3842e4b32f72c8dc7"
verified_number = "+919108340960"

# Initialize Twilio client
try:
    client = Client(account_sid, auth_token)
except Exception as e:
    print(f"Error: {e}")


class ForgotPassword(MDScreen):
    def __init__(self, **kwargs):
        super(ForgotPassword, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.on_back_button()
            return True
        return False

    def on_back_button(self):
        self.manager.push_replacement("login","right")

    def show_validation_dialog(self, message):
        # Create the dialog asynchronously
        Clock.schedule_once(lambda dt: self._create_dialog(message), 0)

    def _create_dialog(self, message):
        dialog = MDDialog(
            text=f"{message}",
            elevation=0,
        )
        dialog.open()

    def validate_password(self, password):
        # Check if the password is not empty
        if not password:
            return False, "Password cannot be empty"
        # Check if the password has at least 8 characters
        if len(password) < 6:
            return False, "Password must have at least 6 characters"
        # Check if the password contains both uppercase and lowercase letters
        if not any(c.isupper() for c in password) or not any(c.islower() for c in password):
            return False, "Password must contain uppercase, lowercase"
        # Check if the password contains at least one digit
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        # Check if the password contains at least one special character
        special_characters = r"[!@#$%^&*(),.?\":{}|<>]"
        if not re.search(special_characters, password):
            return False, "Password must contain a special character"
        # All checks passed; the password is valid
        return True, "Password is valid"

    def change_password(self):
        phone = float(self.ids.phone.text)
        new_password = self.ids.new_password.text
        is_valid_password, password_error_message = self.validate_password(new_password)
        self.ids.change_password.disabled = False
        anvil.server.connect("server_UY47LMUKBDUJMU4EA3RKLXCC-LP5NLIEYMCLMZ4NU")
        record = app_tables.users.get(phone=phone)
        if not is_valid_password:
            self.ids.new_password.error = True
            self.ids.new_password.helper_text = password_error_message

        else:
            if record:
                self.manager.push_replacement("login")
                record.update(password=new_password)
                print("changed")

    #
    def sent_otp(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.SEND_SMS, Permission.RECEIVE_SMS])

        phone = self.ids.phone.text

        if not (phone and len(phone) == 10):
            self.handle_invalid_phone()
        else:
            phone_number = f"+91{phone}"
            try:
                # Send OTP via Twilio
                verification = client.verify.v2.services(verify_sid).verifications.create(
                    to=phone_number, channel="sms"
                )
                self.update_ui_on_otp_sent(phone_number)
            except Exception as e:
                self.handle_otp_sending_error(e)

    def handle_invalid_phone(self):
        self.ids.phone.error = True
        self.ids.phone.helper_text = "Invalid Phone number (10 digits required)"

    def update_ui_on_otp_sent(self, phone_number):
        print(f"OTP sent to {phone_number}")
        self.ids.sent_otp.text = "Sent"
        self.ids.sent_otp.color = (0, 1, 0, 1)
        self.ids.otp.disabled = False
        self.ids.verify_otp.disabled = False

    def handle_otp_sending_error(self, e):
        self.show_validation_dialog(f"{e}")

    #
    def verify_otp(self):
        phone_number = f"+91{self.ids.phone.text}"
        user_entered_otp = self.ids.otp.text
        try:
            # Verify OTP via Twilio
            verification_check = client.verify.v2.services(verify_sid) \
                .verification_checks \
                .create(to=phone_number, code=user_entered_otp)
            if verification_check.status == 'approved':
                self.update_ui_on_otp_verified()
            else:
                self.handle_invalid_otp()
        except Exception as e:
            self.handle_otp_verification_error(e)

    def update_ui_on_otp_verified(self):
        print("OTP verified")
        self.ids.verify_otp.text = "Verified"
        self.ids.verify_otp.color = (0, 1, 0, 1)
        self.ids.new_password.disabled = False
        self.change_password()

    def handle_invalid_otp(self):
        self.show_validation_dialog("Invalid OTP")

    def handle_otp_verification_error(self, e):
        self.show_validation_dialog("Error Occurred")
        print(e)
