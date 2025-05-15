import os
import sys
import tkinter as tk
from tkinter import messagebox

# Import all modules
from file_manager.file_manager import FileManager
from excel_manager.excel_manager import ExcelManager
from reminder_engine.reminder_engine import ReminderEngine
from ui_handler.ui_handler import UIHandler
from email_notifier.email_notifier import EmailNotifier


class PaymentReminderApp:
    def __init__(self):
        """Initialize the Payment Reminder App"""
        # Create the main tkinter window
        self.root = tk.Tk()
        
        # Set app icon and styling
        self.setup_app_appearance()
        
        # Initialize module instances
        self.initialize_modules()
        
        # Setup error handling
        self.setup_error_handling()
        
    def setup_app_appearance(self):
        """Setup app icon, title and styling"""
        self.root.title("Payment Reminder App")
        
        # Set window icon if available
        try:
            # You can add your own icon file here
            # self.root.iconbitmap("path/to/icon.ico")
            pass
        except:
            pass
            
        # Set window size and position
        width = 950
        height = 650
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def initialize_modules(self):
        """Initialize all application modules"""
        try:
            # Create data directory if it doesn't exist
            self.create_data_directory()
            
            # Initialize file manager
            self.file_manager = FileManager()
            
            # Initialize excel manager
            self.excel_manager = ExcelManager()
            
            # Initialize reminder engine
            self.reminder_engine = ReminderEngine(self.excel_manager)

            #self.reminder_engine = ReminderEngine()
            
            # Initialize email notifier (optional, can be None)
            try:
                self.email_notifier = EmailNotifier()
                email_enabled = True
            except Exception as e:
                print(f"Email notification disabled: {str(e)}")
                self.email_notifier = None
                email_enabled = False
                
            # Initialize UI handler last (must be after all other modules)
            self.ui_handler = UIHandler(
                self.root,
                self.file_manager,
                self.excel_manager,
                self.reminder_engine,
                self.email_notifier
            )
            
            # Show startup message
            self.show_startup_message(email_enabled)
            
            # Check for due payments on startup
            self.check_due_payments_on_startup()
            
        except Exception as e:
            messagebox.showerror("Initialization Error", 
                              f"Failed to initialize application: {str(e)}")
            self.root.destroy()
            sys.exit(1)
            
    def create_data_directory(self):
        """Create data directory structure if it doesn't exist"""
        # Create main data directory
        os.makedirs("data", exist_ok=True)
        
    def setup_error_handling(self):
        """Setup global error handling"""
        # Redirect uncaught exceptions to messagebox
        sys.excepthook = self.handle_exception
        
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions"""
        # Log the exception
        import traceback
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"Uncaught exception: {error_msg}")
        
        # Show error message to user
        messagebox.showerror("Application Error", 
                          f"An unexpected error occurred:\n{str(exc_value)}")
                          
    def show_startup_message(self, email_enabled):
        """Show startup welcome message with application status"""
        message = "Payment Reminder Application started successfully!\n\n"
        
        # Get number of files/cities already loaded
        try:
            files = self.file_manager.list_all_files()
            cities = set(city for _, city in files)
            
            message += f"Found {len(files)} payment file(s) for {len(cities)} city/cities.\n"
            
            # Check if email notifications are enabled
            if email_enabled:
                message += "Email notifications are enabled."
            else:
                message += "Email notifications are disabled. Check email_notifier configuration."
                
            messagebox.showinfo("Welcome", message)
        except Exception as e:
            print(f"Error displaying startup message: {str(e)}")
            
    def check_due_payments_on_startup(self):
        """Check for due payments when application starts"""
        try:
            # Get all files
            files = self.file_manager.list_all_files()
            
            if not files:
                # No files to check
                return
                
            # Get due payments
            due_payments = self.reminder_engine.get_due_payments(files)
            
            if due_payments:
                # Add city information to each payment
                for payment in due_payments:
                    city = os.path.basename(os.path.dirname(payment['file_path']))
                    payment['city'] = city
                
                # Ask user if they want to see reminders now
                response = messagebox.askyesno(
                    "Due Payments Found",
                    f"Found {len(due_payments)} due or overdue payment(s).\nWould you like to see them now?"
                )
                
                if response:
                    # Set pending reminders in UI handler
                    self.ui_handler.pending_reminders = due_payments
                    
                    # Show first reminder
                    self.ui_handler.show_next_reminder()
        except Exception as e:
            print(f"Error checking due payments: {str(e)}")
    
    def run(self):
        """Run the application main loop"""
        # Start the UI main loop
        self.ui_handler.start()


if __name__ == "__main__":
    app = PaymentReminderApp()
    app.run()