from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.screen import MDScreen


class ServicerDetails(MDScreen):

    def __init__(self, **kwargs):
        super(ServicerDetails, self).__init__(**kwargs)

    def on_back_button(self, hero):
        self.manager.current_heroes = [hero]
        self.manager.current = "servicer_details"
