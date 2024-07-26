from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.list import IconLeftWidget
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.core.window import Window
from anvil.tables import app_tables

class DetailsScreen(MDScreen):
    service_type = StringProperty("")
    date = StringProperty("")
    time = StringProperty("")
    time_slot = StringProperty("")
    book_id = StringProperty("")
    service_id = StringProperty("")
    fees = 0
    address = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)  # Bind keyboard event

    def on_enter(self, *args):
        self.populate_details()

    def populate_details(self):
        self.fetch_service_details()  # Fetch details from the database
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
        top_card.add_widget(MDLabel(text=f"Time-Slot:     {self.time_slot}", font_style='Caption', halign='left'))
        top_card.add_widget(MDLabel(text=f"Treatment Charges:     ₹{self.fees}", font_style='Caption', halign='left'))
        #top_card.add_widget(MDLabel(text="Completed", font_style='Caption', halign='left'))
        details_box.add_widget(top_card)

        # Ride details card
        treatment_details_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height='250dp',
            padding=20,
            spacing=15,
            md_bg_color=get_color_from_hex("#FFFFFF"),
            radius=[15, 15, 15, 15],
            elevation=2
        )
        treatment_details_card.add_widget(MDLabel(text="Treatment DETAILS", font_style='H6', halign='left'))

        # From location
        from_layout = MDBoxLayout(orientation='horizontal', spacing=25, padding=[0, 5, 0, 20])
        from_icon = IconLeftWidget(icon="map-marker", theme_text_color="Custom", text_color=get_color_from_hex("#4CAF50"))
        from_label = MDLabel(text=self.address, font_style='Caption', halign='left')
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
        duration_layout.add_widget(MDLabel(text="2 hour", font_style='Caption', halign='right'))
        treatment_details_card.add_widget(duration_layout)

        # distance_layout = MDBoxLayout(orientation='horizontal')
        # distance_layout.add_widget(MDLabel(text="Booking Time", font_style='Caption', halign='left'))
        # #op_card.add_widget(MDLabel(text=f"Time-Slot:     {self.time}", font_style='Caption', halign='left'))
        # distance_layout.add_widget(MDLabel(text="10:37 am", font_style='Caption', halign='right'))
        # treatment_details_card.add_widget(distance_layout)

        distance_layout = MDBoxLayout(orientation='horizontal')
        distance_layout.add_widget(MDLabel(text="Booking Date and time", font_style='Caption', halign='left'))
        distance_layout.add_widget(MDLabel(text=f"{self.time}", font_style='Caption', halign='right'))
        treatment_details_card.add_widget(distance_layout)

        treatment_id_layout = MDBoxLayout(orientation='horizontal')
        treatment_id_layout.add_widget(MDLabel(text="Booking ID", font_style='Caption', halign='left'))
        treatment_id_layout.add_widget(MDLabel(text=f"{self.book_id}", font_style='Caption', halign='right'))
        treatment_details_card.add_widget(treatment_id_layout)

        details_box.add_widget(treatment_details_card)

        # Invoice card
        invoice_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height='200dp',
            padding=10,
            spacing=10,
            md_bg_color=get_color_from_hex("#FFFFFF"),
            radius=[15, 15, 15, 15],
            elevation=2
        )
        invoice_card.add_widget(MDLabel(text="INVOICE", font_style='H6', halign='left'))

        treatment_charge_layout = MDBoxLayout(orientation='horizontal')
        treatment_charge_layout.add_widget(MDLabel(text="Treatment Charges", font_style='Caption', halign='left'))
        treatment_charge_layout.add_widget(MDLabel(text=f"₹{(self.fees)}", font_style='Caption', halign='right'))
        invoice_card.add_widget(treatment_charge_layout)

        fees_layout = MDBoxLayout(orientation='horizontal')
        fees_layout.add_widget(MDLabel(text="Booking Fees & Convenience Charges (inclusive in treatment charges)", font_style='Caption', halign='left'))
        fees_layout.add_widget(MDLabel(text="₹19.27", font_style='Caption', halign='right'))
        invoice_card.add_widget(fees_layout)

        invoice_card.add_widget(LineSeparator(size_hint_y=None, height=1))

        total_fare_layout = MDBoxLayout(orientation='horizontal')
        total_fare_layout.add_widget(MDLabel(text="Total Fare", font_style='Subtitle1', halign='left'))
        #total_fare_layout.add_widget(MDLabel(text=f"₹{int(self.fees) + 19.27}", font_style='Subtitle1', halign='right'))
        total_fare_layout.add_widget(MDLabel(text=f"₹{int(self.fees)}", font_style='Subtitle1', halign='right'))
        invoice_card.add_widget(total_fare_layout)

        paid_layout = MDBoxLayout(orientation='horizontal')
        paid_layout.add_widget(MDLabel(text="Paid via QR Pay", font_style='Caption', halign='right'))
        invoice_card.add_widget(paid_layout)



        details_box.add_widget(invoice_card)

    def set_details(self, service_type, book_date, book_time, time_slot, service_id, book_id):
        print(f"Setting details: service_type={service_type}, book_date={book_date}, book_time={book_time}")  # Debugging line
        self.service_type = service_type if service_type is not None else "None"
        self.date = book_date if book_date is not None else "None"
        self.time = book_time if book_time is not None else "None"
        self.time_slot = time_slot if time_slot is not None else "None"
        self.service_id = service_id if service_id is not None else "None"
        self.book_id = book_id if book_id is not None else "None"
        self.populate_details()

    def go_back(self, *args):
        self.manager.push_replacement('client_services')

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.go_back()
            return True
        return False

    def fetch_service_details(self):
        try:
            result = None
            fees_column = ""
            address_column = ""

            if self.service_type == "OxiClinic":
                result = app_tables.oxiclinics.get(oxiclinics_id=self.service_id)
                fees_column = "oxiclinics_fees"
                address_column = "oxiclinics_address"
            elif self.service_type == "OxiWheel":
                result = app_tables.oxiwheels.get(oxiwheels_id=self.service_id)
                fees_column = "oxiwheels_fees"
                address_column = "oxiwheels_address"
            elif self.service_type == "OxiGym":
                result = app_tables.oxigyms.get(oxigyms_id=self.service_id)
                fees_column = "oxigyms_fees"
                address_column = "oxigyms_address"

            if result:
                self.fees = result[fees_column]
                self.address = result[address_column]
                self.service_details_fetched = True
            else:
                self.fees = 0
                self.address = "N/A"
        except Exception as e:
            print(f"Error fetching service details: {e}")
            self.fees = 0
            self.address = "N/A"


class LineSeparator(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.88, 0.88, 0.88, 1)  # Light grey color
            self.line = Line(points=[self.x, self.y, self.x + self.width, self.y], width=1.5)
        self.bind(size=self._update_line, pos=self._update_line)

    def _update_line(self, *args):
        self.line.points = [self.x, self.y, self.x + self.width, self.y]
