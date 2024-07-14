import json
import os
import anvil
from anvil.tables import app_tables
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from fpdf import FPDF
import anvil.server

class Report(MDScreen):
    def __init__(self, **kwargs):
        super(Report, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)

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
            with open('user_data.json', 'r') as file:
                user_info = json.load(file)
            d = app_tables.oxi_reports.get(oxi_id=user_info.get('id'))

            if d is not None:
                # Populate UI fields with fetched data
                self.ids.patient_name.text = d['oxi_patient_name']
                self.ids.doctor_name.text = d['oxi_doctor_name']
                self.ids.service_type.text = d['oxi_service_type']
                self.ids.session.text = str(d['oxi_session'])
                self.ids.payable_to.text = str(d['oxi_payable_to'])
                self.ids.bank_details.text = d['oxi_bank_details']

                # Update company logo and description
                self.ids.company_logo.source = 'Oxyvive-mobile-application/images/shot.png'
                self.ids.company_description.text = 'Anti-aging shot therapy'
            else:
                print("No data found from Anvil.")

        except Exception as e:
            print(f"Error fetching data from Anvil: {e}")

    def save_pdf(self):
        try:
            # Fetch data from UI fields
            patient_name = self.ids.patient_name.text
            doctor_name = self.ids.doctor_name.text
            service_type = self.ids.service_type.text
            session = self.ids.session.text
            payable_to = self.ids.payable_to.text
            bank_details = self.ids.bank_details.text
            with open('user_data.json', 'r') as file:
                user_info = json.load(file)
            d = app_tables.oxi_reports.get(oxi_id=user_info.get('id'))
            price = float(d['oxi_price'])  # Assuming price is fetched from database
            quantity = 1  # Example quantity, adjust as per your data model

            subtotal = price * quantity
            cgst = subtotal * 0.08
            sgst = subtotal * 0.08
            grand_total = subtotal + cgst + sgst

            # Create PDF document
            pdf = FPDF()
            pdf.add_page()

            # Add company logo and name
            pdf.image('images/shot.png', x=10, y=8, w=33)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 20, '', 0, 1)  # Add some space below the logo
            pdf.cell(0, 10, 'Oxivive - Anti-aging shot therapy', 0, 1, 'C')

            # Add patient information
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, '', 0, 1)  # Add some space
            pdf.cell(50, 10, 'Patient Name:', 0, 0)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, patient_name, 0, 1)

            pdf.set_font('Arial', 'B', 12)
            pdf.cell(50, 10, 'Doctor Name:', 0, 0)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, doctor_name, 0, 1)

            pdf.set_font('Arial', 'B', 12)
            pdf.cell(50, 10, 'Service Type:', 0, 0)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, service_type, 0, 1)

            pdf.set_font('Arial', 'B', 12)
            pdf.cell(50, 10, 'Session:', 0, 0)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, session, 0, 1)

            pdf.set_font('Arial', 'B', 12)
            pdf.cell(50, 10, 'Payable to:', 0, 0)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, payable_to, 0, 1)

            pdf.set_font('Arial', 'B', 12)
            pdf.cell(50, 10, 'Bank Details:', 0, 0)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, bank_details, 0, 1)

            # Add table with service details
            pdf.cell(0, 10, '', 0, 1)  # Add empty line
            pdf.set_fill_color(200, 220, 255)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(95, 10, 'Service Type', 1, 0, 'C', 1)
            pdf.cell(30, 10, 'Price', 1, 0, 'C', 1)
            pdf.cell(30, 10, 'Total', 1, 1, 'C', 1)

            pdf.set_font('Arial', '', 12)
            pdf.cell(95, 10, service_type, 1)
            pdf.cell(30, 10, f'${price:.2f}', 1)
            pdf.cell(30, 10, f'${subtotal:.2f}', 1, 1)

            # Add totals
            pdf.cell(0, 10, '', 0, 1)  # Add empty line
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(95, 10, 'Sub Total:', 0)
            pdf.cell(30, 10, f'${subtotal:.2f}', 0, 1, 'R')

            pdf.cell(95, 10, 'CGST (8%):', 0)
            pdf.cell(30, 10, f'${cgst:.2f}', 0, 1, 'R')

            pdf.cell(95, 10, 'SGST (8%):', 0)
            pdf.cell(30, 10, f'${sgst:.2f}', 0, 1, 'R')

            pdf.cell(95, 10, 'Grand Total:', 0)
            pdf.cell(30, 10, f'${grand_total:.2f}', 0, 1, 'R')

            # Save PDF
            pdf_name = "invoice.pdf"
            pdf.output(pdf_name)

            # Print the PDF name and path
            pdf_path = os.path.abspath(pdf_name)  # Get absolute path to the PDF
            print(f"PDF saved successfully:\nName: {pdf_name}\nPath: {pdf_path}")

        except Exception as e:
            print(f"Error saving PDF: {e}")

    def clear_fields(self):
        # Clear all input fields
        self.ids.patient_name.text = ''
        self.ids.doctor_name.text = ''
        self.ids.service_type.text = ''
        self.ids.session.text = ''
        self.ids.payable_to.text = ''
        self.ids.bank_details.text = ''

        # Reset labels to default
        self.ids.subtotal_label.text = "$0.00"
        self.ids.cgst_label.text = "$0.00"
        self.ids.sgst_label.text = "$0.00"
        self.ids.grand_total_label.text = "$0.00"

# Note: Ensure you have the necessary UI elements with the correct IDs in your KV file.
