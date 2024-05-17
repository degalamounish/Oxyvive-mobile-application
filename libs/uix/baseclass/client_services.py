import json

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivymd.uix.hero import MDHeroFrom
from kivymd.uix.imagelist import MDSmartTile
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen


class NavigationDrawerScreen(MDScreen):
    pass


class CustomImageTile(MDSmartTile):

    def on_release(self, *args):
        print("next screen")
        pass


class ClickableTextFieldRound(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()


class HeroItem(MDHeroFrom):
    text = StringProperty()
    tag = StringProperty()
    manager = ObjectProperty()
    id = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.tile.ids.image.ripple_duration_in_fast = 0.05

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
        print('release')

        def switch_screen(*args):
            print(args)
            self.manager.current_heroes = [self.tag]
            print(self.manager)
            # screen = self.manager.get_screen('menu_notification')
            self.manager.hero_to.tag = self.tag
            self.manager.current = " screen B"
            print(self.tag)

        Clock.schedule_once(switch_screen, 0.2)


class Client_services(MDScreen):
    def __init__(self, **kwargs):
        super(Client_services, self).__init__(**kwargs)

    def on_pre_enter(self):

        self.on_b1()
        self.on_b2()
        self.on_b3()
        for i in range(5):
            environment_img = CustomImageTile(
                source="images/gym.png"
            )
            self.ids.box3.add_widget(environment_img)

    def on_b1(self):
        print('on_b1')
        for i in range(12):
            hero_item = HeroItem(
                text="images/gym.png", tag=f"Dr.OxiClinic {i}", manager=self.ids.screen_manager
            )
            if not i % 2:
                hero_item.ids.tile.md_bg_color = "lightgrey"
            self.ids.box.add_widget(hero_item)

    def on_b2(self):
        print('on_b2')
        for i in range(12):
            hero_item = HeroItem(
                text="images/gym.png", tag=f"Dr.OxiWheel {i}", manager=self.ids.screen_manager
            )
            if not i % 2:
                hero_item.ids.tile.md_bg_color = "lightgrey"
            self.ids.box1.add_widget(hero_item)

    def on_b3(self):
        print('on_b3')
        for i in range(12):
            hero_item = HeroItem(
                text="images/gym.png", tag=f"Dr.OxiGym {i}", manager=self.ids.screen_manager
            )
            if not i % 2:
                hero_item.ids.tile.md_bg_color = "lightgrey"
            self.ids.box2.add_widget(hero_item)

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
