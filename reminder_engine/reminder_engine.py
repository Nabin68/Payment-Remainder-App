"""
Reminder Engine Module for Payment Reminder App
Identifies due and overdue payments from Excel files
"""
import logging
from datetime import datetime, timedelta
import pandas as pd
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('reminder_engine')

class ReminderEngine:
    def __init__(self, excel_manager):
        """
        Initialize the ReminderEngine with an instance of ExcelManager
        
        Args:
            excel_manager: An instance of ExcelManager class
        """
        self.excel_manager = excel_manager
        self.today = datetime.now().date()
    
    def get_due_payments(self, file_paths_and_cities):
        """
        Check all files and identify due or overdue payments
        
        Args:
            file_paths_and_cities (list): List of tuples (file_path, city_name)
            
        Returns:
            list: List of dictionaries containing due payment information
        """
        due_payments = []
        
        for file_path, city_name in file_paths_and_cities:
            # Skip files that don't exist
            if not os.path.exists(file_path):
                logger.warning(f"File does not exist: {file_path}")
                continue
                
            try:
                # Get all payment entries from this file
                entries = self.excel_manager.get_payment_entries(file_path, city_name)
                
                # Filter for due or overdue payments
                for entry in entries:
                    # Skip if payment is already fully paid
                    if entry.get('Status', '').lower() == 'paid':
                        continue
                    
                    # Get due date
                    due_date = entry.get('Due Date')
                    
                    # Skip if due date is missing or invalid
                    if not due_date:
                        continue
                    
                    # Convert string dates if needed
                    if isinstance(due_date, str):
                        try:
                            due_date = pd.to_datetime(due_date).date()
                        except Exception as e:
                            logger.warning(f"Failed to parse due date '{due_date}': {str(e)}")
                            continue
                    
                    # Convert Timestamp to date if needed
                    if hasattr(due_date, 'date'):
                        due_date = due_date.date()
                    
                    # Check if payment is due or overdue
                    if due_date <= self.today:
                        # Calculate days overdue
                        days_overdue = (self.today - due_date).days
                        entry['days_overdue'] = days_overdue
                        
                        # Add priority based on days overdue
                        if days_overdue > 30:
                            entry['priority'] = 'High'
                        elif days_overdue > 7:
                            entry['priority'] = 'Medium'
                        else:
                            entry['priority'] = 'Low'
                        
                        due_payments.append(entry)
            
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
        
        # Sort due payments by priority (days overdue)
        due_payments.sort(key=lambda x: x.get('days_overdue', 0), reverse=True)
        
        logger.info(f"Found {len(due_payments)} due/overdue payments across all files")
        return due_payments
    
    def get_upcoming_payments(self, file_paths_and_cities, days_ahead=7):
        """
        Check all files and identify upcoming payments within specified days
        
        Args:
            file_paths_and_cities (list): List of tuples (file_path, city_name)
            days_ahead (int): Number of days ahead to check
            
        Returns:
            list: List of dictionaries containing upcoming payment information
        """
        upcoming_payments = []
        future_date = self.today + timedelta(days=days_ahead)
        
        for file_path, city_name in file_paths_and_cities:
            # Skip files that don't exist
            if not os.path.exists(file_path):
                continue
                
            try:
                # Get all payment entries from this file
                entries = self.excel_manager.get_payment_entries(file_path, city_name)
                
                # Filter for upcoming payments
                for entry in entries:
                    # Skip if payment is already fully paid
                    if entry.get('Status', '').lower() == 'paid':
                        continue
                    
                    # Get due date
                    due_date = entry.get('Due Date')
                    
                    # Skip if due date is missing or invalid
                    if not due_date:
                        continue
                    
                    # Convert string dates if needed
                    if isinstance(due_date, str):
                        try:
                            due_date = pd.to_datetime(due_date).date()
                        except:
                            continue
                    
                    # Convert Timestamp to date if needed
                    if hasattr(due_date, 'date'):
                        due_date = due_date.date()
                    
                    # Check if payment is upcoming (not due yet, but will be soon)
                    if self.today < due_date <= future_date:
                        # Calculate days until due
                        days_until_due = (due_date - self.today).days
                        entry['days_until_due'] = days_until_due
                        upcoming_payments.append(entry)
            
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
        
        # Sort upcoming payments by due date (ascending)
        upcoming_payments.sort(key=lambda x: x.get('Due Date'))
        
        logger.info(f"Found {len(upcoming_payments)} upcoming payments within {days_ahead} days")
        return upcoming_payments
    
    def get_payment_summary(self, file_paths_and_cities):
        """
        Generate a summary of payment status across all files
        
        Args:
            file_paths_and_cities (list): List of tuples (file_path, city_name)
            
        Returns:
            dict: Summary statistics
        """
        summary = {
            'total_payments': 0,
            'paid_payments': 0,
            'partial_payments': 0,
            'unpaid_payments': 0,
            'overdue_payments': 0,
            'due_today': 0,
            'upcoming_payments': 0,
            'total_amount_due': 0
        }
        
        for file_path, city_name in file_paths_and_cities:
            if not os.path.exists(file_path):
                continue
                
            try:
                entries = self.excel_manager.get_payment_entries(file_path, city_name)
                
                for entry in entries:
                    summary['total_payments'] += 1
                    
                    status = entry.get('Status', '').lower()
                    if status == 'paid':
                        summary['paid_payments'] += 1
                    elif status == 'partial':
                        summary['partial_payments'] += 1
                        summary['total_amount_due'] += float(entry.get('Amount', 0))
                    else:  # Unpaid
                        summary['unpaid_payments'] += 1
                        summary['total_amount_due'] += float(entry.get('Amount', 0))
                    
                    due_date = entry.get('Due Date')
                    
                    # Skip if due date is missing or invalid
                    if not due_date:
                        continue
                    
                    # Convert to date object if needed
                    if isinstance(due_date, str):
                        try:
                            due_date = pd.to_datetime(due_date).date()
                        except:
                            continue
                    
                    if hasattr(due_date, 'date'):
                        due_date = due_date.date()
                    
                    # Check date status
                    if due_date < self.today and status != 'paid':
                        summary['overdue_payments'] += 1
                    elif due_date == self.today and status != 'paid':
                        summary['due_today'] += 1
                    elif due_date > self.today and status != 'paid':
                        summary['upcoming_payments'] += 1
            
            except Exception as e:
                logger.error(f"Error generating summary for file {file_path}: {str(e)}")
        
        return summary

# For testing
if __name__ == "__main__":
    # Import necessary modules for testing
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from excel_manager.excel_manager import ExcelManager
    
    # Create test data
    excel_manager = ExcelManager()
    
    # Create a test excel file with various payment scenarios
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    next_week = today + timedelta(days=7)
    
    test_df = pd.DataFrame({
        'Name': ['Overdue Person', 'Due Today Person', 'Future Person', 'Paid Person'],
        'Amount': [100, 200, 300, 400],
        'Due Date': [last_week, today, next_week, yesterday],
        'Email': ['overdue@example.com', 'today@example.com', 'future@example.com', 'paid@example.com'],
        'Status': ['Unpaid', 'Unpaid', 'Unpaid', 'Paid']
    })
    
    test_file = "test_reminder.xlsx"
    test_df.to_excel(test_file, index=False)
    
    try:
        # Create reminder engine
        reminder_engine = ReminderEngine(excel_manager)
        
        # Test finding due payments
        due_payments = reminder_engine.get_due_payments([(test_file, "TestCity")])
        print(f"Due or overdue payments: {len(due_payments)}")
        for payment in due_payments:
            print(f"- {payment['Name']}: ${payment['Amount']} due on {payment['Due Date']}, "
                  f"{payment['days_overdue']} days overdue, Priority: {payment['priority']}")
        
        # Test finding upcoming payments
        upcoming_payments = reminder_engine.get_upcoming_payments([(test_file, "TestCity")])
        print(f"\nUpcoming payments: {len(upcoming_payments)}")
        for payment in upcoming_payments:
            print(f"- {payment['Name']}: ${payment['Amount']} due in {payment['days_until_due']} days")
        
        # Test summary generation
        summary = reminder_engine.get_payment_summary([(test_file, "TestCity")])
        print(f"\nPayment summary:")
        for key, value in summary.items():
            print(f"- {key}: {value}")
    
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)