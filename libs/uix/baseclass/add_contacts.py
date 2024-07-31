import json
import os

from anvil.tables import app_tables
from kivymd.uix.button import MDFlatButton
from kivymd.uix.screen import MDScreen


class AddContact(MDScreen):
    def phone_input_filter(self, string, from_undo):
        allowed_chars = '+0123456789'
        filtered_string = ''.join([ch for ch in string if ch in allowed_chars])
        if len(filtered_string) > 13:
            return filtered_string[:13]
        return filtered_string
    def go_back(self):
        self.manager.push_replacement("client_dashboard") # Switch to Choose Contact screen

    def __init__(self, **kwargs):
        super(AddContact, self).__init__(**kwargs)
        # Initialize the contact list
        self.contact_list = []

    def add_to_contact_list(self, contact):
        # Add the contact to the list
        self.contact_list.append(contact)

    def add_contact(self):
        # Fetch data from text fields
        first_name = self.ids.first_name.text
        last_name = self.ids.last_name.text
        phone_number = self.ids.phone_number.text

        # Perform validation if needed
        if not first_name or not phone_number:
            # Display an error message or alert the user
            print("Please fill in all fields.")
            return

        # Create a new contact
        new_contact = {
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number
        }
        print(new_contact)

        try:
            # Add the new contact to the contact list
            self.add_to_contact_list(new_contact)

            script_dir = os.path.dirname(os.path.abspath(__file__))
            json_user_file_path = os.path.join(script_dir, "user_data.json")
            with open(json_user_file_path, 'r') as file:
                user_info = json.load(file)

            row_to_update = app_tables.oxi_book_slot.get(oxi_id=user_info.get('id'))

            if row_to_update is not None:
                # Update the fields
                row_to_update['oxi_another_person_name'] = self.ids.first_name.text + " " + self.ids.last_name.text
                row_to_update['oxi_another_person_number'] = int(self.ids.phone_number.text[3:])

            # Load the Client_dashboard screen
            self.manager.current = "client_dashboard"
            screen = self.manager.get_screen("client_dashboard")

            # Update the screen with the new contact
            screen.add_contact(new_contact)

            # Example: Clear the text fields after saving the contact
            self.ids.first_name.text = ""
            self.ids.last_name.text = ""
            self.ids.phone_number.text = "+91"

            # Notify the user that the contact has been added successfully
            # You could use a dialog or a toast notification here
            print("Contact added successfully.")
        except Exception as e:
            print(f"Error: {e}")
            self.show_popup("Error: unable to update to database")

    def show_popup(self, message):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton

        def on_ok(instance):
            dialog.dismiss()
            self.manager.current = "client_location"

        dialog = MDDialog(
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=on_ok
                )
            ]
        )
        dialog.open()