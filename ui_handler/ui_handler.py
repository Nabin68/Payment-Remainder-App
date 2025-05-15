import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import datetime
try:
    from tkcalendar import DateEntry
except ImportError:
    # Show a warning only once if tkcalendar isn't installed
    class DateEntry(ttk.Entry):
        def __init__(self, master=None, **kw):
            super().__init__(master, **kw)
            self.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
            messagebox.showwarning("Missing Dependency", 
                                "tkcalendar module is not installed. Please install it using pip: pip install tkcalendar")
        
        def get_date(self):
            try:
                date_str = self.get()
                return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                return datetime.date.today()


class UIHandler:
    def __init__(self, root, file_manager, excel_manager, reminder_engine, email_notifier=None):
        """Initialize the UI Handler with references to other modules"""
        self.root = root
        self.file_manager = file_manager
        self.excel_manager = excel_manager
        self.reminder_engine = reminder_engine
        self.email_notifier = email_notifier
        
        self.pending_reminders = []
        self.reminder_windows = []
        
        # Set window title and size
        self.root.title("Payment Reminder App")
        self.root.geometry("900x600")
        
        # Create main frames
        self.setup_frames()
        
        # Create UI elements
        self.setup_upload_section()
        self.setup_filter_section()
        self.setup_list_view()
        self.setup_status_bar()
        
    def setup_frames(self):
        """Create the main frames for the UI layout"""
        # Top frame for file upload
        self.upload_frame = ttk.Frame(self.root, padding=10)
        self.upload_frame.pack(fill=tk.X)
        
        # Filter frame
        self.filter_frame = ttk.Frame(self.root, padding=10)
        self.filter_frame.pack(fill=tk.X)
        
        # Main frame for payment list
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status bar at the bottom
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
    
    def setup_upload_section(self):
        """Create the file upload section"""
        ttk.Label(self.upload_frame, text="Upload Excel File:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        # File path display
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(self.upload_frame, textvariable=self.file_path_var, width=50)
        self.file_path_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Browse button
        self.browse_button = ttk.Button(self.upload_frame, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)
        
        # City input
        ttk.Label(self.upload_frame, text="City:").grid(row=0, column=3, padx=5, pady=5)
        self.city_var = tk.StringVar()
        self.city_entry = ttk.Entry(self.upload_frame, textvariable=self.city_var, width=15)
        self.city_entry.grid(row=0, column=4, padx=5, pady=5)
        
        # Upload button
        self.upload_button = ttk.Button(self.upload_frame, text="Upload", command=self.upload_file)
        self.upload_button.grid(row=0, column=5, padx=5, pady=5)
        
    def setup_filter_section(self):
        """Create the filter section for searching and filtering payments"""
        # Search box
        ttk.Label(self.filter_frame, text="Search:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.filter_frame, textvariable=self.search_var, width=25)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.apply_filters)
        
        # City filter
        ttk.Label(self.filter_frame, text="City:").grid(row=0, column=2, padx=5, pady=5)
        self.city_filter_var = tk.StringVar()
        self.city_filter_combo = ttk.Combobox(self.filter_frame, textvariable=self.city_filter_var, width=15)
        self.city_filter_combo.grid(row=0, column=3, padx=5, pady=5)
        self.city_filter_combo.bind("<<ComboboxSelected>>", self.apply_filters)
        
        # Status filter
        ttk.Label(self.filter_frame, text="Status:").grid(row=0, column=4, padx=5, pady=5)
        self.status_filter_var = tk.StringVar()
        self.status_filter_combo = ttk.Combobox(self.filter_frame, textvariable=self.status_filter_var, 
                                               values=["All", "Paid", "Unpaid"], width=10)
        self.status_filter_combo.current(0)
        self.status_filter_combo.grid(row=0, column=5, padx=5, pady=5)
        self.status_filter_combo.bind("<<ComboboxSelected>>", self.apply_filters)
        
        # Reset filters button
        self.reset_button = ttk.Button(self.filter_frame, text="Reset Filters", command=self.reset_filters)
        self.reset_button.grid(row=0, column=6, padx=5, pady=5)
        
        # Check payments button
        self.check_button = ttk.Button(self.filter_frame, text="Check Due Payments", command=self.check_due_payments)
        self.check_button.grid(row=0, column=7, padx=5, pady=5)
        
    def setup_list_view(self):
        """Create the payment list view with treeview"""
        # Create treeview with scrollbar
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Define columns for the treeview
        columns = ("name", "amount", "due_date", "status", "city", "email")
        self.payment_tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", 
                                        yscrollcommand=self.tree_scroll.set)
        
        # Configure the scrollbar
        self.tree_scroll.config(command=self.payment_tree.yview)
        
        # Define column headings
        self.payment_tree.heading("name", text="Name")
        self.payment_tree.heading("amount", text="Amount")
        self.payment_tree.heading("due_date", text="Due Date")
        self.payment_tree.heading("status", text="Status")
        self.payment_tree.heading("city", text="City")
        self.payment_tree.heading("email", text="Email")
        
        # Configure column widths
        self.payment_tree.column("name", width=150)
        self.payment_tree.column("amount", width=100)
        self.payment_tree.column("due_date", width=100)
        self.payment_tree.column("status", width=80)
        self.payment_tree.column("city", width=100)
        self.payment_tree.column("email", width=200)
        
        self.payment_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click event to open payment details
        self.payment_tree.bind("<Double-1>", self.show_payment_details)
        
    def setup_status_bar(self):
        """Create status bar at the bottom of the window"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var, 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)
        
    def browse_file(self):
        """Open file dialog to select Excel file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")],
            title="Select Excel Payment File"
        )
        if file_path:
            self.file_path_var.set(file_path)
            # Try to auto-extract city from filename
            filename = os.path.basename(file_path)
            city_name = os.path.splitext(filename)[0]
            self.city_var.set(city_name)
            
    def upload_file(self):
        """Handle the file upload process"""
        file_path = self.file_path_var.get()
        city = self.city_var.get()
        
        if not file_path or not city:
            messagebox.showerror("Error", "Please select a file and enter a city name.")
            return
            
        try:
            saved_path = self.file_manager.save_excel_file(file_path, city)
            self.status_var.set(f"File for {city} uploaded successfully!")
            self.file_path_var.set("")
            self.city_var.set("")
            
            # Update the city filter combo with all available cities
            self.update_city_filter_combo()
            
            # Refresh the payment list
            self.update_list_view()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload file: {str(e)}")
            
    def update_city_filter_combo(self):
        """Update the city filter combobox with all available cities"""
        try:
            cities = [os.path.basename(os.path.dirname(file)) for file in self.file_manager.list_all_files()]
            cities = list(set(cities))  # Remove duplicates
            cities.insert(0, "All")
            self.city_filter_combo['values'] = cities
            self.city_filter_combo.current(0)
        except Exception as e:
            print(f"Error updating city filter: {str(e)}")
            
    def apply_filters(self, event=None):
        """Apply search and filters to the payment list"""
        self.update_list_view()
        
    def reset_filters(self):
        """Reset all filters to default"""
        self.search_var.set("")
        self.city_filter_var.set("All")
        self.status_filter_var.set("All")
        self.update_list_view()
        
    def update_list_view(self):
        """Update the payment list based on the current filters"""
        # Clear current list
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
            
        try:
            # Get all files
            file_paths = self.file_manager.list_all_files()
            
            all_entries = []
            
            # Get entries from each file
            for file_path in file_paths:
                city = os.path.basename(os.path.dirname(file_path))
                entries = self.excel_manager.get_payment_entries(file_path)
                
                # Add city information to each entry
                for entry in entries:
                    entry['city'] = city
                    entry['file_path'] = file_path
                    entry['row_index'] = entries.index(entry)
                    
                all_entries.extend(entries)
                
            # Apply filters
            filtered_entries = self.filter_entries(all_entries)
            
            # Add filtered entries to treeview
            for entry in filtered_entries:
                self.payment_tree.insert("", tk.END, values=(
                    entry.get('Name', ''),
                    entry.get('Amount', ''),
                    entry.get('Due Date', ''),
                    entry.get('Status', 'Unpaid'),
                    entry.get('city', ''),
                    entry.get('Email', '')
                ))
                
            # Update status with count
            self.status_var.set(f"Showing {len(filtered_entries)} payment entries")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update list: {str(e)}")
            
    def filter_entries(self, entries):
        """Filter entries based on current filter settings"""
        filtered = []
        
        search_term = self.search_var.get().lower()
        city_filter = self.city_filter_var.get()
        status_filter = self.status_filter_var.get()
        
        for entry in entries:
            # Apply search term filter
            if search_term and not any(search_term in str(value).lower() for value in entry.values() if isinstance(value, (str, int, float))):
                continue
                
            # Apply city filter
            if city_filter != "All" and entry.get('city') != city_filter:
                continue
                
            # Apply status filter
            if status_filter != "All":
                if status_filter == "Paid" and entry.get('Status', '') != "Paid":
                    continue
                if status_filter == "Unpaid" and entry.get('Status', '') == "Paid":
                    continue
                    
            filtered.append(entry)
            
        return filtered
        
    def check_due_payments(self):
        """Manually check for due payments and show reminders"""
        file_paths = self.file_manager.list_all_files()
        due_payments = self.reminder_engine.get_due_payments(file_paths)
        
        if not due_payments:
            messagebox.showinfo("Reminders", "No due or overdue payments found.")
            return
            
        # Add city information
        for payment in due_payments:
            city = os.path.basename(os.path.dirname(payment['file_path']))
            payment['city'] = city
            
        # Store pending reminders
        self.pending_reminders = due_payments
        
        # Show first reminder
        if self.pending_reminders:
            self.show_next_reminder()
        
    def show_next_reminder(self):
        """Show the next payment reminder from the queue"""
        if not self.pending_reminders:
            return
            
        entry = self.pending_reminders.pop(0)
        self.show_due_reminder(entry)
        
    def show_due_reminder(self, entry):
        """Display a non-dismissible popup for due payment"""
        # Create a new top-level window
        reminder_window = tk.Toplevel(self.root)
        reminder_window.title("Payment Reminder")
        reminder_window.geometry("400x350")
        reminder_window.attributes("-topmost", True)
        
        # Prevent window from being closed with the X button
        reminder_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Store the window and related info
        self.reminder_windows.append({
            'window': reminder_window,
            'entry': entry
        })
        
        # Payment info frame
        info_frame = ttk.Frame(reminder_window, padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add payment information
        ttk.Label(info_frame, text="PAYMENT REMINDER", font=("Arial", 14, "bold")).pack(anchor=tk.W)
        ttk.Separator(info_frame).pack(fill=tk.X, pady=5)
        
        # Create info grid
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X, pady=5)
        
        # Row 1: Name
        ttk.Label(info_grid, text="Name:", width=12).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_grid, text=entry.get('Name', 'N/A'), font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Row 2: Amount
        ttk.Label(info_grid, text="Amount Due:", width=12).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_grid, text=str(entry.get('Amount', 'N/A')), font=("Arial", 10, "bold")).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Row 3: Due Date
        ttk.Label(info_grid, text="Due Date:", width=12).grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_grid, text=str(entry.get('Due Date', 'N/A')), font=("Arial", 10, "bold")).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Row 4: City
        ttk.Label(info_grid, text="City:", width=12).grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_grid, text=entry.get('city', 'N/A')).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        ttk.Separator(reminder_window).pack(fill=tk.X, padx=10)
        
        # Options frame
        options_frame = ttk.Frame(reminder_window, padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Option 1: Mark as Paid
        ttk.Label(options_frame, text="Option 1:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        ttk.Label(options_frame, text="Mark this payment as paid").pack(anchor=tk.W)
        
        # Payment amount frame
        payment_frame = ttk.Frame(options_frame)
        payment_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(payment_frame, text="Amount Paid:").grid(row=0, column=0, padx=5)
        paid_amount_var = tk.StringVar()
        paid_amount_var.set(str(entry.get('Amount', '0')))
        paid_amount_entry = ttk.Entry(payment_frame, textvariable=paid_amount_var, width=10)
        paid_amount_entry.grid(row=0, column=1, padx=5)
        
        mark_paid_button = ttk.Button(options_frame, text="Mark as Paid",
                                    command=lambda: self.mark_as_paid(entry, paid_amount_var.get(), reminder_window))
        mark_paid_button.pack(fill=tk.X, pady=5)
        
        ttk.Separator(reminder_window).pack(fill=tk.X, padx=10, pady=5)
        
        # Option 2: Reschedule Payment
        reschedule_frame = ttk.Frame(reminder_window, padding=10)
        reschedule_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(reschedule_frame, text="Option 2:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        ttk.Label(reschedule_frame, text="Reschedule payment for a new date").pack(anchor=tk.W)
        
        # Date selection frame
        date_frame = ttk.Frame(reschedule_frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_frame, text="New Due Date:").grid(row=0, column=0, padx=5)
        
        # Use DateEntry for date selection
        new_date_var = tk.StringVar()
        date_picker = DateEntry(date_frame, width=12, background='darkblue',
                              foreground='white', borderwidth=2)
        date_picker.grid(row=0, column=1, padx=5)
        
        # Remark entry
        ttk.Label(date_frame, text="Remark:").grid(row=1, column=0, padx=5, pady=5)
        remark_var = tk.StringVar()
        remark_entry = ttk.Entry(date_frame, textvariable=remark_var, width=25)
        remark_entry.grid(row=1, column=1, padx=5, pady=5, columnspan=2)
        
        reschedule_button = ttk.Button(reschedule_frame, text="Reschedule Payment",
                                     command=lambda: self.reschedule_payment(
                                         entry, 
                                         date_picker.get_date(), 
                                         remark_var.get(), 
                                         reminder_window
                                     ))
        reschedule_button.pack(fill=tk.X, pady=5)
        
    def mark_as_paid(self, entry, amount_paid, reminder_window):
        """Mark a payment as paid and update the Excel file"""
        try:
            # Convert amount to float
            try:
                amount_paid = float(amount_paid)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount.")
                return
                
            # Update Excel file
            self.excel_manager.update_payment(
                entry['file_path'],
                entry['row_index'],
                amount_paid,
                "Paid"
            )
            
            # Send email notification if email is present and email notifier is enabled
            if self.email_notifier and entry.get('Email'):
                try:
                    subject = "Payment Confirmation"
                    body = f"Dear {entry.get('Name')},\n\n"
                    body += f"This is to confirm that we have received your payment of {amount_paid}.\n"
                    body += "Thank you for your prompt payment.\n\n"
                    body += "Best regards,\nPayment Reminder App"
                    
                    self.email_notifier.send_email(entry.get('Email'), subject, body)
                except Exception as e:
                    print(f"Error sending email: {str(e)}")
                    
            # Close the reminder window
            self.close_reminder_window(reminder_window)
            
            # Update the payment list
            self.update_list_view()
            
            # Show the next reminder if any
            self.show_next_reminder()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to mark payment as paid: {str(e)}")
            
    def reschedule_payment(self, entry, new_date, remark, reminder_window):
        """Reschedule a payment for a new date"""
        try:
            # Format the new date
            formatted_date = new_date.strftime("%Y-%m-%d")
            
            # Update Excel file
            self.excel_manager.update_payment(
                entry['file_path'],
                entry['row_index'],
                entry.get('Amount'),
                "Rescheduled",
                new_date,
                remark if remark else None
            )
            
            # Send email notification if email is present and email notifier is enabled
            if self.email_notifier and entry.get('Email'):
                try:
                    subject = "Payment Rescheduled"
                    body = f"Dear {entry.get('Name')},\n\n"
                    body += f"Your payment of {entry.get('Amount')} has been rescheduled to {formatted_date}.\n"
                    if remark:
                        body += f"Note: {remark}\n\n"
                    body += "Thank you for your cooperation.\n\n"
                    body += "Best regards,\nPayment Reminder App"
                    
                    self.email_notifier.send_email(entry.get('Email'), subject, body)
                except Exception as e:
                    print(f"Error sending email: {str(e)}")
                    
            # Close the reminder window
            self.close_reminder_window(reminder_window)
            
            # Update the payment list
            self.update_list_view()
            
            # Show the next reminder if any
            self.show_next_reminder()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reschedule payment: {str(e)}")
            
    def close_reminder_window(self, window):
        """Close a reminder window and remove it from the list"""
        # Find the window in the list and remove it
        self.reminder_windows = [w for w in self.reminder_windows if w['window'] != window]
        
        # Destroy the window
        window.destroy()
        
    def show_payment_details(self, event):
        """Show details for a payment when double-clicked"""
        # Get selected item
        selection = self.payment_tree.selection()
        if not selection:
            return
            
        # Get selected payment values
        item = self.payment_tree.item(selection[0])
        values = item['values']
        
        if not values:
            return
            
        # Create detail window
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Payment Details")
        detail_window.geometry("400x300")
        
        # Add payment details
        detail_frame = ttk.Frame(detail_window, padding=10)
        detail_frame.pack(fill=tk.BOTH, expand=True)
        
        # Headers
        ttk.Label(detail_frame, text="Payment Details", font=("Arial", 14, "bold")).pack(anchor=tk.W)
        ttk.Separator(detail_frame).pack(fill=tk.X, pady=5)
        
        # Details grid
        details_grid = ttk.Frame(detail_frame)
        details_grid.pack(fill=tk.X, pady=5)
        
        # Add each field
        row = 0
        fields = ["Name", "Amount", "Due Date", "Status", "City", "Email"]
        for i, field in enumerate(fields):
            ttk.Label(details_grid, text=f"{field}:", width=12).grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Label(details_grid, text=str(values[i])).grid(row=row, column=1, sticky=tk.W, pady=2)
            row += 1
            
        # Close button
        ttk.Button(detail_frame, text="Close", command=detail_window.destroy).pack(pady=10)
        
    def start(self):
        """Start the UI main loop"""
        self.root.mainloop()