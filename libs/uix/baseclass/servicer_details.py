from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.screen import MDScreen


class ServicerDetails(MDScreen):
    tag = StringProperty()
    heroes_to = ObjectProperty()
    hero_to = ObjectProperty()

    def __init__(self, **kwargs):
        super(ServicerDetails, self).__init__(**kwargs)
