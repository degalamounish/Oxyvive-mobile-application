from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty

from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar


class CardItem(MDCard):
    manager = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elevation = 3

    def schedule_screen(self):
        self.manager.push_replacement("slot_booking")


class SliverToolbar(MDTopAppBar):
    manager = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shadow_color = (0, 0, 0, 0)
        self.type_height = "medium"
        self.headline_text = "Available Services"
        self.left_action_items = [["arrow-left", lambda x: self.back_screen()]]

    def back_screen(self):
        self.manager.push_replacement('client_location')


class AvailableService(MDScreen):
    silver_tool_bar = SliverToolbar()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self, *args):
        self.populate_cards()
        self.silver_tool_bar.manager = self.manager

    def populate_cards(self):
        for _ in range(10):
            self.ids.content.add_widget(CardItem(manager=self.manager))
