Payment Reminder App
A desktop application to manage, track, and remind company staff of upcoming and overdue payments from clients based on data in Excel files.
Overview
The Payment Reminder App is a Python-based desktop application designed to help businesses track client payments across different cities. The application reads payment information from Excel files, provides persistent reminders for due or overdue payments, and allows users to mark payments as paid or reschedule them for future dates. All changes are reflected directly in the Excel files for seamless record-keeping.
Show Image
Features

Local Excel File Management

Upload and manage Excel files organized by city
Files are stored locally in a structured folder system
New files can be uploaded anytime while using the app


Reminder Engine

Automatic checking for due or overdue payments on startup
Manual checking available through the UI
Non-dismissible notification popups for payments that need attention


Persistent Notifications

Each reminder shows client name, amount due, due date, and city
Two actionable options: Mark as Paid (full or partial) or Update with New Payment Date
Notifications must be addressed before they can be dismissed


Excel File Updates

When marking as paid, status is updated in the Excel file
When rescheduling, due date is updated and remarks can be added
All changes are saved back to the original Excel files


In-App Data Display

Searchable list of people, cities, due dates, and amounts
Filter by city, payment status, or search terms
Double-click entries to view detailed information


Email Notification to Customers (Optional)

Send automated emails for payment confirmations or rescheduling
Uses Gmail SMTP for sending messages



System Requirements

Python 3.6 or higher
Windows, macOS, or Linux operating system
Excel files with the following columns:

Name: Client name
Amount: Payment amount
Due Date: Date when payment is due
Email: Client email (optional)
Status: Payment status (will be updated by the app)
Remarks: Additional notes (optional)



Installation

Clone or download this repository
Install required dependencies:

bashpip install -r requirements.txt

Run the application:

bashpython main.py
Project Structure
payment-reminder-app/
│
├── main.py                  # Main controller
├── requirements.txt         # Required Python packages
│
├── file_manager/            # File upload, save, organize
│   └── file_manager.py
│
├── excel_manager/           # Read/write Excel logic
│   └── excel_manager.py
│
├── reminder_engine/         # Due date checker
│   └── reminder_engine.py
│
├── ui_handler/              # All UI (notifications, list view)
│   └── ui_handler.py
│
└── email_notifier/          # Gmail-based email sender (optional)
    └── email_notifier.py
Module Details
main.py
The central controller that coordinates all modules. It initializes the application, sets up error handling, checks for due payments on startup, and runs the main application loop.
file_manager.py
Handles file uploads, validation, and organization of Excel files locally.
Key functions:

save_excel_file(file_path, city_name) - Saves file in the data/<city>/ folder
list_all_files() - Returns paths of all saved Excel files for processing

excel_manager.py
Reads data from Excel files and updates rows after user actions.
Key functions:

get_payment_entries(file_path) - Returns list of payment records
update_payment(file_path, row_index, amount_paid, status, new_date=None) - Updates a row

reminder_engine.py
Checks which payments are due or overdue by date.
Key functions:

get_due_payments(file_paths) - Scans all files and returns records where due date <= today and status ≠ 'Paid'

ui_handler.py
Shows the user interface, including upload UI, payment list view, and reminder popups.
Key functions:

show_due_reminder(entry) - Display popup for due entry
update_list_view(entries) - Refresh visible list
mark_as_paid(entry, amount_paid, reminder_window) - Process payment
reschedule_payment(entry, new_date, remark, reminder_window) - Update due date

email_notifier.py (Optional)
Sends confirmation and update emails to customers.
Key functions:

send_email(to_email, subject, body) - Sends email via SMTP

Usage Guide
Adding New Payment Files

Click the "Browse" button to select an Excel file
Enter the city name for the file
Click "Upload" to save the file in the system

Viewing Payments

All payments will be displayed in the main list view
Use the search box to find specific entries
Filter by city or payment status using the dropdown menus
Click "Reset Filters" to show all entries

Managing Due Payments

Due payments will be automatically checked on startup
Click "Check Due Payments" to manually check for due payments
For each reminder, you can:

Mark as paid (full or partial amount)
Reschedule for a future date with optional remarks



Viewing Payment Details

Double-click any payment in the list to view detailed information

Configuration
Email Notifications
To enable email notifications, configure the settings in email_notifier.py:
python# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
APP_PASSWORD = "your_app_password"  # Gmail App Password, not your regular password
Troubleshooting

Excel Files Not Loading: Make sure files are in the correct format with the required columns
Email Not Sending: Check your Gmail credentials and enable less secure apps in your Google account settings
UI Elements Missing: Ensure all dependencies are installed with pip install -r requirements.txt

Dependencies

tkinter - GUI framework
pandas - Excel file handling
openpyxl - Excel reading/writing
tkcalendar - Date selection widget
pillow - Image handling for UI

License
This project is licensed under the MIT License - see the LICENSE file for details.
Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

Fork the project
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request
