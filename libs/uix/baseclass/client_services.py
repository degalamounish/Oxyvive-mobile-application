import json
from kivymd.uix.screen import MDScreen


class NavigationDrawerScreen(MDScreen):
    pass


class Client_services(MDScreen):
    def __init__(self, **kwargs):
        super(Client_services, self).__init__(**kwargs)

    def on_pre_enter(self):
        self.change()

    def change(self):
        with open('user_data.json', 'r') as file:
            user_info = json.load(file)
        self.ids.username.text = user_info['username']
        self.ids.email.text = user_info['email']

    def logout(self):
        self.manager.push_replacement("login", "right")
        self.ids.nav_drawer.set_state("close")
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
        self.ids.nav_drawer.set_state("close")

    def location_screen(self):
        self.manager.push("location")

    def book_now(self, organization_name, organization_address):
        print(organization_name, organization_address)
        organization_info = {'organization_name': organization_name, 'organization_address': organization_address}
        with open("organization_data.json", "w") as json_file:
            json.dump(organization_info, json_file)
        self.manager.push("hospital_booking")
