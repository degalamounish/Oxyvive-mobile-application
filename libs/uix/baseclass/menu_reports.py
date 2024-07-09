import json
import os
import anvil
from anvil.tables import app_tables
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from kivymd.app import MDApp
from kivy.lang import Builder
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from anvil.tables import app_tables
import anvil.server

class Report(MDScreen):
    def __init__(self, **kwargs):
        super(Report, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_keyboard)
        # self.invoice_app = InvoiceApp()

    def on_keyboard(self, instance, key, scancode, codepoint, modifier):
        if key == 27:  # Keycode for the back button on Android
            self.reports_back()
            return True
        return False

    def go_back(self):
        self.manager.current = 'client_services'

    def on_enter(self):
        self.fetch_data_from_anvil()
# class InvoiceApp():
#     def build(self):
#         self.title = 'Invoice Generator'
#         self.root = Builder.load_file('menu_reports.kv')
#         self.fetch_data_from_anvil()

    def fetch_data_from_anvil(self):
        try:
            anvil.server.connect("server_YIC6OAWPGEQYBFQPKYFQURNH-EHPN322OL4WF5PEF")
            # Fetch data from Anvil
            with open('user_data.json', 'r') as file:
                user_info = json.load(file)
            d = app_tables.oxi_reports.get(oxi_id=user_info.get('id'))
            print(d)

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
            d = app_tables.oxi_reports.get(oxi_email='yathishgowda@gmail.com')
            price = float(d['oxi_price'])  # Assuming price is fetched from database
            quantity = 1  # Example quantity, adjust as per your data model

            subtotal = price * quantity
            cgst = subtotal * 0.08
            sgst = subtotal * 0.08
            grand_total = subtotal + cgst + sgst

            # Create PDF document
            c = canvas.Canvas("invoice.pdf", pagesize=letter)
            width, height = letter

            # Draw company name and image
            c.drawImage('images/shot.png', 50, height - 150, width=100, height=100)
            c.setFont("Helvetica-Bold", 24)
            c.drawString(170, height - 80, "Oxivive")
            c.setFont("Helvetica", 18)
            c.drawString(170, height - 100, "Anti-aging shot therapy")

            # Draw patient information
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, height - 200, "Patient Name:")
            c.setFont("Helvetica", 18)
            c.drawString(200, height - 200, patient_name)

            # Draw doctor information
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, height - 235, "Doctor Name:")
            c.setFont("Helvetica", 18)
            c.drawString(200, height - 235, doctor_name)

            # Draw service type information
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, height - 270, "Service Type:")
            c.setFont("Helvetica", 18)
            c.drawString(200, height - 270, service_type)

            # Draw session information
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, height - 305, "Session:")
            c.setFont("Helvetica", 18)
            c.drawString(200, height - 305, session)

            # Draw payable to information
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, height - 340, "Payable to:")
            c.setFont("Helvetica", 18)
            c.drawString(200, height - 340, payable_to)

            # Draw bank details information
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, height - 375, "Bank Details:")
            c.setFont("Helvetica", 18)
            c.drawString(200, height - 375, bank_details)

            table_headers = ["Service Type", "Price", "Total"]
            col_widths = [280, 80, 80]
            row_height = 30
            x_start = 50
            y_start = height - 430

            c.setFillColorRGB(1, 0, 0)  # Set header text color to black
            c.setStrokeColorRGB(0, 0, 0)  # Set header border color to black
            c.setFont("Helvetica-Bold", 12)

            for i, header in enumerate(table_headers):
                c.rect(x_start + sum(col_widths[:i]), y_start, col_widths[i], row_height, fill=1)
                c.drawString(x_start + sum(col_widths[:i]) + 10, y_start + 10, header)

            # Fetch data from database and add rows dynamically
            data = [
                [self.ids.service_type.text, "${:.2f}".format(price), "${:.2f}".format(subtotal)],
            ]

            # Draw table data
            c.setFillColorRGB(0, 0, 0)  # Black color for text
            for row_index, row_data in enumerate(data):
                for col_index, cell_value in enumerate(row_data):
                    c.rect(x_start + sum(col_widths[:col_index]), y_start - (row_index + 1) * row_height,
                           col_widths[col_index], row_height, fill=0)
                    c.drawString(x_start + sum(col_widths[:col_index]) + 10,
                                 y_start - (row_index + 1) * row_height + 10,
                                 cell_value)

            # Draw subtotal, taxes, and grand total
            c.setFont("Helvetica-Bold", 18)
            c.drawString(200, y_start - (len(data) + 1) * row_height - 20, "Sub Total:")
            c.drawString(350, y_start - (len(data) + 1) * row_height - 20, "${:.2f}".format(subtotal))
            c.drawString(200, y_start - (len(data) + 2) * row_height - 20, "CGST (8%):")
            c.drawString(350, y_start - (len(data) + 2) * row_height - 20, "${:.2f}".format(cgst))
            c.drawString(200, y_start - (len(data) + 3) * row_height - 20, "SGST (8%):")
            c.drawString(350, y_start - (len(data) + 3) * row_height - 20, "${:.2f}".format(sgst))
            c.setFont("Helvetica-Bold", 18)
            c.drawString(200, y_start - (len(data) + 4) * row_height - 20, "Grand Total:")
            c.drawString(350, y_start - (len(data) + 4) * row_height - 20, "${:.2f}".format(grand_total))

            c.save()

            # Print the PDF name and path
            pdf_name = "invoice.pdf"
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

