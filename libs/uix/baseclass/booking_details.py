from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import IconLeftWidget, OneLineIconListItem
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen


class DetailsScreen(MDScreen):
    service_type = StringProperty("")
    date = StringProperty("")
    time = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)  # Bind keyboard event

    def on_enter(self, *args):
        self.populate_details()

    def populate_details(self):
        details_box = self.ids.details_box
        details_box.clear_widgets()

        # Top card with ride summary
        top_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height='120dp',
            padding=10,
            spacing=5,
            md_bg_color=get_color_from_hex("#FFFFFF"),
            radius=[15, 15, 15, 15],
            elevation=2
        )
        top_card.add_widget(MDLabel(text=self.service_type, font_style='H6', halign='left'))
        top_card.add_widget(MDLabel(text=f"Date:     {self.date}", font_style='Caption', halign='left'))
        top_card.add_widget(MDLabel(text=f"Time-Slot:     {self.time}", font_style='Caption', halign='left'))
        top_card.add_widget(MDLabel(text="₹4000", font_style='Caption', halign='left'))
        top_card.add_widget(MDLabel(text="Completed", font_style='Caption', halign='left'))
        details_box.add_widget(top_card)

        # Ride details card
        treatment_details_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height='260dp',
            padding=20,
            spacing=15,
            md_bg_color=get_color_from_hex("#FFFFFF"),
            radius=[15, 15, 15, 15],
            elevation=2
        )
        treatment_details_card.add_widget(MDLabel(text="Treatment DETAILS", font_style='H6', halign='left'))

        # From location
        from_layout = MDBoxLayout(orientation='horizontal', spacing=25)
        from_icon = IconLeftWidget(icon="map-marker", theme_text_color="Custom", text_color=get_color_from_hex("#4CAF50"))
        from_label = MDLabel(text="Kodigehalli Gate\nSahakar Nagar, Byatarayanapura, Bengaluru...", font_style='Caption', halign='left')
        from_layout.add_widget(from_icon)
        from_layout.add_widget(from_label)
        treatment_details_card.add_widget(from_layout)

        # To location
        to_layout = MDBoxLayout(orientation='horizontal', spacing=25)
        to_icon = IconLeftWidget(icon="map-marker", theme_text_color="Custom", text_color=get_color_from_hex("#F44336"))
        to_label = MDLabel(text="Sri Parijatha Enterprises Sri Parijatha\n4th Cross Corner, Maruthi Nagar, Yelahanka...", font_style='Caption', halign='left')
        to_layout.add_widget(to_icon)
        to_layout.add_widget(to_label)
        treatment_details_card.add_widget(to_layout)

        treatment_details_card.add_widget(LineSeparator(size_hint_y=None, height=1))

        duration_layout = MDBoxLayout(orientation='horizontal')
        duration_layout.add_widget(MDLabel(text="Duration", font_style='Caption', halign='left'))
        duration_layout.add_widget(MDLabel(text="1 hour", font_style='Caption', halign='right'))
        treatment_details_card.add_widget(duration_layout)

        distance_layout = MDBoxLayout(orientation='horizontal')
        distance_layout.add_widget(MDLabel(text="Booking Time", font_style='Caption', halign='left'))
        distance_layout.add_widget(MDLabel(text="10:37 am", font_style='Caption', halign='right'))
        treatment_details_card.add_widget(distance_layout)

        distance_layout = MDBoxLayout(orientation='horizontal')
        distance_layout.add_widget(MDLabel(text="Booking Date", font_style='Caption', halign='left'))
        distance_layout.add_widget(MDLabel(text="20-March-2021", font_style='Caption', halign='right'))
        treatment_details_card.add_widget(distance_layout)

        treatment_id_layout = MDBoxLayout(orientation='horizontal')
        treatment_id_layout.add_widget(MDLabel(text="Booking ID", font_style='Caption', halign='left'))
        treatment_id_layout.add_widget(MDLabel(text="RD17181999166816697", font_style='Caption', halign='right'))
        treatment_details_card.add_widget(treatment_id_layout)

        details_box.add_widget(treatment_details_card)

        # Invoice card
        invoice_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height='180dp',
            padding=10,
            spacing=10,
            md_bg_color=get_color_from_hex("#FFFFFF"),
            radius=[15, 15, 15, 15],
            elevation=2
        )
        invoice_card.add_widget(MDLabel(text="INVOICE", font_style='H6', halign='left'))

        total_fare_layout = MDBoxLayout(orientation='horizontal')
        total_fare_layout.add_widget(MDLabel(text="Total Fare", font_style='Subtitle1', halign='left'))
        total_fare_layout.add_widget(MDLabel(text="₹4000", font_style='Subtitle1', halign='right'))
        invoice_card.add_widget(total_fare_layout)

        paid_layout = MDBoxLayout(orientation='horizontal')
        paid_layout.add_widget(MDLabel(text="Paid via QR Pay", font_style='Caption', halign='right'))
        invoice_card.add_widget(paid_layout)

        invoice_card.add_widget(LineSeparator(size_hint_y=None, height=1))

        treatment_charge_layout = MDBoxLayout(orientation='horizontal')
        treatment_charge_layout.add_widget(MDLabel(text="Treatment Charge", font_style='Caption', halign='left'))
        treatment_charge_layout.add_widget(MDLabel(text="₹4019.27", font_style='Caption', halign='right'))
        invoice_card.add_widget(treatment_charge_layout)

        fees_layout = MDBoxLayout(orientation='horizontal')
        fees_layout.add_widget(MDLabel(text="Booking Fees & Convenience Charges", font_style='Caption', halign='left'))
        fees_layout.add_widget(MDLabel(text="₹19.27", font_style='Caption', halign='right'))
        invoice_card.add_widget(fees_layout)

        details_box.add_widget(invoice_card)

    date = StringProperty()

    def set_details(self, service_type, book_date, book_time):
        self.service_type = service_type
        self.date = str(book_date)
        self.time = book_time
        self.populate_details()

    def go_back(self, *args):
        self.manager.push_replacement('client_services')

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.go_back()
            return True
        return False

class LineSeparator(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.88, 0.88, 0.88, 1)  # Light grey color
            self.line = Line(points=[self.x, self.y, self.x + self.width, self.y], width=1.5)
        self.bind(size=self._update_line, pos=self._update_line)

    def _update_line(self, *args):
        self.line.points = [self.x, self.y, self.x + self.width, self.y]