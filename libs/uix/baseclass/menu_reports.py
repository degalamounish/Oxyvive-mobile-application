import json
import os
from platform import platform

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from fpdf import FPDF
import anvil.server
from anvil.tables import app_tables

from libs.uix import root

if platform == 'android':
    from android.permissions import (
        request_permissions, check_permission, Permission
    )
from kivy.factory import Factory

class Main(MDScreen):
    def on_enter(self):
        self.check_data_availability()

    def check_data_availability(self):
        try:
            with open('user_data.json', 'r') as file:
                user_info = json.load(file)
            bookings= app_tables.oxi_book_slot.get(oxi_id=user_info.get('id'))
            if not bookings:
                self.clear_widgets()
                details = Reports(manager=self.manager)
                self.add_widget(details)
            else:
                self.clear_widgets()
                print('checking if condition')
                details = Report(manager=self.manager)
                details.fetch_data_from_anvil()# Pass the manager
                self.add_widget(details)

        except Exception as e:
            print(f"Error checking data availability: {e}")

class Reports(Screen):
    def go_back(self):
        self.manager.current = 'client_services'  # Assuming you have a main screen to go back to

    def show_add_report_dialog(self):
        # Implement the method to show a dialog to add new report
        pass


class Report(MDScreen):
    def __init__(self, **kwargs):
        super(Report, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)
        # Request necessary permissions on Android
        if platform() == 'android':
            self.request_android_permissions()

    def request_android_permissions(self):
        request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.go_back()
            return True
        return False

    def go_back(self):
        self.manager.current = 'client_services'

    def on_enter(self):
        self.fetch_data_from_anvil()

    def fetch_data_from_anvil(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct the path to the JSON file within the script's directory
            json_user_file_path = os.path.join(script_dir, "user_data.json")
            with open(json_user_file_path, 'r') as file:
                user_info = json.load(file)
            # Fetch all booking slots for the given oxi_id
            bookings_iterator = app_tables.oxi_book_slot.search(oxi_id=user_info.get('id'))

            # Convert the SearchIterator to a list
            bookings = list(bookings_iterator)
            print(bookings)

            if bookings:
                # Debug: print the structure of the bookings
                for booking in bookings:
                    # Find the booking with the latest booking date
                    latest_booking = dict(max(bookings, key=lambda booking: booking['oxi_book_date']))
                # Assigning fetched data to UI elements
                self.ids.booking_id.text = latest_booking['oxi_book_id'] if 'oxi_book_id' in latest_booking else ''
                self.ids.patient_name.text = latest_booking['oxi_username'] if 'oxi_username' in latest_booking else ''
                self.ids.doctor_name.text = latest_booking[
                    'oxi_doctor_name'] if 'oxi_doctor_name' in latest_booking else ''
                self.ids.address.text = latest_booking['oxi_address'] if 'oxi_address' in latest_booking else 'N/A'
                self.ids.service_type.text = latest_booking[
                    'oxi_service_type'] if 'oxi_service_type' in latest_booking else ''
                self.ids.session.text = str(latest_booking['oxi_session']) if 'oxi_session' in latest_booking else ''
                self.ids.price_label.text = f"${latest_booking['oxi_price']:.2f}" if 'oxi_price' in latest_booking else "$0.00"
                self.ids.subtotal.text = f"${latest_booking['oxi_price']:.2f}" if 'oxi_price' in latest_booking else "$0.00"

                # Calculate and assign tax values
                price = latest_booking['oxi_price']
                cgst_value = price * 0.08
                sgst_value = price * 0.08
                grand_total_value = price + cgst_value + sgst_value

                self.ids.cgst.text = f"${cgst_value:.2f}"
                self.ids.sgst.text = f"${sgst_value:.2f}"
                self.ids.grand_total.text = f"${grand_total_value:.2f}"

                self.ids.payable_to.text = latest_booking['oxi_payable_to']
                self.ids.bank_details.text = latest_booking['oxi_bank_details']
            else:
                # Handle case where no bookings are found
                print("No bookings found for this user.")

        except Exception as e:
            print(f"An error occurred: {e}")

    def save_pdf(self):
        try:
            # Fetch data from UI fields
            booking_id = self.ids.booking_id.text
            patient_name = self.ids.patient_name.text
            doctor_name = self.ids.doctor_name.text
            address = self.ids.address.text
            service_type = self.ids.service_type.text
            session = self.ids.session.text
            price = float(self.ids.price_label.text.strip('$'))
            subtotal = float(self.ids.subtotal.text.strip('$'))
            cgst = float(self.ids.cgst.text.strip('$'))
            sgst = float(self.ids.sgst.text.strip('$'))
            grand_total = float(self.ids.grand_total.text.strip('$'))

            # Initialize PDF object
            pdf = FPDF()
            pdf.add_page()

            # Header
            pdf.set_fill_color(204, 0, 0)
            pdf.rect(0, 0, 210, 40, 'F')
            if platform() == 'android':
                pdf.image('file:///storage/emulated/0/Download/shot.png', 10, 8, 33)  # Adjust path for Android
            else:
                pdf.image('images/shot.png', 10, 8, 33)  # Adjust path for other platforms
            pdf.set_font('Arial', 'B', 16)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(80)
            pdf.cell(30, 10, 'Oxivive', 0, 1, 'C')
            pdf.set_font('Arial', 'I', 12)
            pdf.cell(80)
            pdf.cell(30, 10, 'INVOICE', 0, 1, 'C')
            pdf.ln(20)

            # Reset text color to black for the body
            pdf.set_text_color(0, 0, 0)

            # Invoice details
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f'Invoice Number: {booking_id}', 0, 1, 'L')
            pdf.cell(0, 10, 'Date: August 21, 2023', 0, 1, 'L')
            pdf.ln(10)

            # Billing information
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Billed To:', 0, 1, 'L')  # Start of Billing information
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(0, 10, f"{patient_name}\n{address}", 0, 'L')

            # Doctor information (alignment)
            pdf.set_x(10)  # Set x position to align doctor info on the right side
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Doctor:', 0, 1, 'L')  # Start of Doctor information
            pdf.set_font('Arial', '', 12)
            pdf.set_x(10)  # Reset x position to align subsequent lines
            pdf.multi_cell(0, 10, f"{doctor_name}\n{address}", 0, 'L')
            pdf.ln(10)

            # Table header
            pdf.set_fill_color(204, 0, 0)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(80, 10, 'DETAILS', 1, 0, 'C', 1)
            pdf.cell(30, 10, 'SESSION', 1, 0, 'C', 1)
            pdf.cell(30, 10, 'PRICE', 1, 0, 'C', 1)
            pdf.cell(50, 10, 'AMOUNT', 1, 1, 'C', 1)

            # Table row
            pdf.set_fill_color(255, 204, 204)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 12)
            pdf.cell(80, 10, service_type, 1, 0, 'C', 1)
            pdf.cell(30, 10, str(session), 1, 0, 'C', 1)
            pdf.cell(30, 10, f'${price:.2f}', 1, 0, 'C', 1)
            pdf.cell(50, 10, f'${subtotal:.2f}', 1, 1, 'C', 1)

            # Totals
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, '', 0, 1)
            pdf.set_fill_color(255, 204, 204)
            pdf.set_text_color(0, 0, 0)  # Set text color to black for totals
            pdf.cell(160, 10, 'SUB TOTAL:', 0, 0, 'R')
            pdf.cell(30, 10, f'${subtotal:.2f}', 0, 1, 'R', 1)
            pdf.cell(160, 10, 'CGST 8%:', 0, 0, 'R')
            pdf.cell(30, 10, f'${cgst:.2f}', 0, 1, 'R', 1)
            pdf.cell(160, 10, 'SGST 8%:', 0, 0, 'R')
            pdf.cell(30, 10, f'${sgst:.2f}', 0, 1, 'R', 1)
            pdf.cell(160, 10, 'GRAND TOTAL:', 0, 0, 'R')
            pdf.cell(30, 10, f'${grand_total:.2f}', 0, 1, 'R', 1)

            pdf.cell(0, 10, '', 0, 1)

            # Footer
            footer_height = 30
            pdf.set_y(-footer_height - 0)  # Adjust the y-coordinate to position the footer correctly
            pdf.set_fill_color(255, 0, 0)
            pdf.rect(0, pdf.get_y(), 210, footer_height, 'F')

            # Calculate vertical position for the centered text within the footer
            footer_y = pdf.get_y() + (footer_height / 2) - 15.5  # Adjust 5 based on the text size

            pdf.set_y(footer_y)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', 'I', 12)
            pdf.cell(0, 10, 'Thank you for your business!', 0, 0, 'C')
            # Save PDF
            if platform() == 'android':
                pdf_path = '/storage/emulated/0/Download/invoice.pdf'  # Adjust path for Android
            else:
                desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
                if not os.path.exists(desktop_path):
                    os.makedirs(desktop_path)
                pdf_path = os.path.join(desktop_path, 'invoice.pdf')

            pdf.output(pdf_path)
            print(f"PDF saved successfully:\nPath: {pdf_path}")

        except Exception as e:
            print(f"Error saving PDF: {e}")