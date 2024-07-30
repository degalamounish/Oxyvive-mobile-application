import os

from kivy.utils import platform
from kivymd.uix.list import OneLineListItem, TwoLineIconListItem
from kivymd.uix.screen import MDScreen
from libs.uix.baseclass.client_location import ItemConfirm as ic

# Set JAVA_HOME environment variable
os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-22'

# Debugging: Print JAVA_HOME to verify it's set correctly
print(f"JAVA_HOME is set to: {os.environ.get('JAVA_HOME')}")

# Import jnius and Android classes if on Android platform
if platform == 'android':
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    ContentResolver = autoclass('android.content.ContentResolver')
    Uri = autoclass('android.net.Uri')
    Cursor = autoclass('android.database.Cursor')
    ContactsContract = autoclass('android.provider.ContactsContract')
    ActivityCompat = autoclass('androidx.core.app.ActivityCompat')
    Permission = autoclass('android.Manifest$permission')


from kivymd.uix.list import TwoLineAvatarListItem, IconLeftWidget
from kivymd.uix.dialog import MDDialog

class Item(TwoLineAvatarListItem):
    def __init__(self, text, source=None, manager=None, callback=None, **kwargs):
        super().__init__(text=text, **kwargs)
        self.source = source
        self.manager = manager
        self.callback = callback

    def update_myself_button(self):
        if self.callback:
            self.callback(self.text)

class ItemConfirm(TwoLineAvatarListItem):
    def __init__(self, manager=None, **kwargs):
        super().__init__( **kwargs)
        self.manager = manager

    def contact_screen(self):
        ic.contact_screen(self)


class ChooseContact(MDScreen):
    all_contacts = []
    dialog_contacts = []  # List to keep track of contacts currently in the dialog

    def on_back_button(self):
        self.manager.push_replacement("client_location")  # Replace 'previous_screen' with the actual screen name

    def add_new_contact(self):
        self.manager.push_replacement("add_contacts")

    def on_enter(self):
        if platform == 'android':
            self.check_permissions_and_fetch_contacts()

    def check_permissions_and_fetch_contacts(self):
        if platform == 'android':
            context = PythonActivity.mActivity.getApplicationContext()
            if ActivityCompat.checkSelfPermission(context, Permission.READ_CONTACTS) != autoclass(
                    'android.content.pm.PackageManager').PERMISSION_GRANTED:
                ActivityCompat.requestPermissions(PythonActivity.mActivity, [Permission.READ_CONTACTS], 1)
            else:
                self.fetch_contacts()

    def on_request_permissions_result(self, request_code, permissions, grant_results):
        if request_code == 1:
            if grant_results[0] == autoclass('android.content.pm.PackageManager').PERMISSION_GRANTED:
                self.fetch_contacts()
            else:
                print("Permission denied")

    def fetch_contacts(self):
        if platform == 'android':
            try:
                context = PythonActivity.mActivity.getApplicationContext()
                resolver = context.getContentResolver()
                uri = ContactsContract.Contacts.CONTENT_URI
                cursor = resolver.query(uri, None, None, None, None)
                if cursor is not None:
                    contacts_list = self.ids.contacts_list
                    contacts_list.clear_widgets()
                    while cursor.moveToNext():
                        name = cursor.getString(cursor.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME))
                        item = OneLineListItem(text=name)
                        contacts_list.add_widget(item)
                    cursor.close()
                else:
                    print("Cursor is None, failed to query contacts.")
            except Exception as e:
                print(f"Failed to fetch contacts: {e}")

    def add_contact(self, contact):
        contact_display = f"{contact['first_name']} {contact['last_name']}: {contact['phone_number']}"
        contact_item = TwoLineIconListItem()

        # Set the icon for the contact item
        icon = IconLeftWidget(icon="account")
        contact_item.add_widget(icon)

        # Set the primary and secondary text
        contact_item.text = f"{contact['first_name']} {contact['last_name']}"
        contact_item.secondary_text = contact['phone_number']

        # Add the contact item to the list
        self.ids.contacts_list.add_widget(contact_item)

        # Optionally, keep track of all contacts
        self.all_contacts.append(contact)

    def filter_contacts(self, search_text):
        # Clear the current list
        self.ids.contacts_list.clear_widgets()

        # Filter contacts
        filtered_contacts = [contact for contact in self.all_contacts
                             if (search_text.lower() in f"{contact['first_name']} {contact['last_name']}".lower() or
                                 search_text in contact['phone_number'])]

        # Add filtered contacts to the list
        for contact in filtered_contacts:
            contact_display = f"{contact['first_name']} {contact['last_name']}: {contact['phone_number']}"
            contact_item = TwoLineIconListItem()

            # Set the icon for the contact item
            icon = IconLeftWidget(icon="account")
            contact_item.add_widget(icon)

            # Set the primary and secondary text
            contact_item.text = f"{contact['first_name']} {contact['last_name']}"
            contact_item.secondary_text = contact['phone_number']
            contact_item.bind(on_release=lambda x, c=contact: self.on_contact_click(c))
            self.ids.contacts_list.add_widget(contact_item)

    def create_on_release(self, contact):
        def on_release(instance):
            self.on_contact_click(contact)

        return on_release

    def on_contact_click(self, contact):
        # Load the client_location screen
        self.manager.load_screen("client_location")
        screen = self.manager.get_screen("client_location")

        # Initialize dialog_contacts list if not present
        if not hasattr(self, 'dialog_contacts'):
            self.dialog_contacts = []

        # Add contact to the list if not already present
        if contact not in self.dialog_contacts:
            self.dialog_contacts.append(contact)

        # Ensure the dialog is initialized
        if not hasattr(screen, 'dialog'):
            screen.dialog = MDDialog(
                title="Someone else taking this appointment?",
                type="confirmation",
                items=[
                    Item(text="Myself", source="images/profile.jpg", manager=self.manager),
                    ItemConfirm(text="Choose another contact", manager=self.manager),
                ] +[self.create_item(contact) for contact in self.dialog_contacts]
            )
            screen.dialog.open()
        else:
            # Update the dialog items to include the contact details
            screen.dialog.items =  [
                Item(text="Myself", source="images/profile.jpg", manager=self.manager),
                ItemConfirm(text="Choose another contact", manager=self.manager),
            ] + [self.create_item(contact) for contact in self.dialog_contacts]
            # Recreate and open the dialog to reflect the updated items
            screen.dialog = MDDialog(
                title="Someone else taking this appointment?",
                type="confirmation",
                items=screen.dialog.items,
            )

        screen.ids.choose.text = f"{contact['first_name']} {contact['last_name']}      "
        self.manager.push_replacement("client_location")

    def create_item(self, contact):
        contact_item = TwoLineIconListItem()

        # Set the icon for the contact item
        icon = IconLeftWidget(icon="account")
        contact_item.add_widget(icon)

        # Set the primary and secondary text
        contact_item.text = f"{contact['first_name']} {contact['last_name']}"
        contact_item.secondary_text = contact['phone_number']
        contact_item.bind(on_release=lambda x, c=contact: self.on_contact_click(c))

        return contact_item




