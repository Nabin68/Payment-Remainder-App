"""
Excel Manager Module for Payment Reminder App
Handles reading from and writing to Excel files, ensuring data integrity
"""
import pandas as pd
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('excel_manager')

class ExcelManager:
    def __init__(self):
        """Initialize the ExcelManager with expected column definitions"""
        # Define expected columns
        self.required_columns = ['Name', 'Amount', 'Due Date']
        self.optional_columns = ['Email', 'Status', 'Remarks', 'Payment Date']
        self.all_columns = self.required_columns + self.optional_columns
    
    def get_payment_entries(self, file_path, city_name=None):
        """
        Read payment entries from an Excel file
        
        Args:
            file_path (str): Path to the Excel file
            city_name (str, optional): Name of the city, added to each entry if provided
            
        Returns:
            list: List of dictionaries containing payment information
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Check if required columns exist
            missing_columns = [col for col in self.required_columns if col not in df.columns]
            if missing_columns:
                error_msg = f"Missing required columns in Excel file: {missing_columns}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Add optional columns if they don't exist
            for col in self.optional_columns:
                if col not in df.columns:
                    df[col] = ""
            
            # Convert DataFrame to list of dictionaries
            entries = df.to_dict('records')
            
            # Add file path and city name to each entry
            for entry in entries:
                entry['file_path'] = file_path
                entry['row_index'] = entries.index(entry)  # Add row index for future updates
                if city_name:
                    entry['city'] = city_name
                
                # Ensure dates are proper datetime objects
                if isinstance(entry['Due Date'], str):
                    try:
                        entry['Due Date'] = pd.to_datetime(entry['Due Date']).date()
                    except:
                        logger.warning(f"Could not convert Due Date '{entry['Due Date']}' to datetime")
                elif hasattr(entry['Due Date'], 'date'):
                    entry['Due Date'] = entry['Due Date'].date()
                
                # Ensure status is set
                if not entry['Status'] or pd.isna(entry['Status']):
                    entry['Status'] = 'Unpaid'
            
            logger.info(f"Successfully read {len(entries)} entries from {file_path}")
            return entries
            
        except Exception as e:
            logger.error(f"Error reading Excel file {file_path}: {str(e)}")
            raise
    
    def update_payment(self, file_path, row_index, amount_paid=None, status=None, new_date=None, remarks=None):
        """
        Update payment details in an Excel file
        
        Args:
            file_path (str): Path to the Excel file
            row_index (int): Index of the row to update
            amount_paid (float, optional): Amount paid (updates Status to 'Partial' if less than total)
            status (str, optional): New payment status ('Paid', 'Partial', 'Unpaid')
            new_date (datetime, optional): New due date
            remarks (str, optional): Remarks or notes to add
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Ensure row index is valid
            if row_index < 0 or row_index >= len(df):
                error_msg = f"Invalid row index: {row_index}, file has {len(df)} rows"
                logger.error(error_msg)
                raise IndexError(error_msg)
            
            # Update amount and status if specified
            if amount_paid is not None:
                total_amount = df.at[row_index, 'Amount']
                
                # Check if this is a full or partial payment
                if amount_paid >= total_amount:
                    df.at[row_index, 'Status'] = 'Paid'
                    df.at[row_index, 'Amount'] = 0  # Fully paid, set remaining to 0
                else:
                    df.at[row_index, 'Status'] = 'Partial'
                    df.at[row_index, 'Amount'] = total_amount - amount_paid  # Update remaining amount
                
                # Record payment date
                df.at[row_index, 'Payment Date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Override status if explicitly specified
            if status:
                df.at[row_index, 'Status'] = status
            
            # Update due date if specified
            if new_date:
                df.at[row_index, 'Due Date'] = new_date
            
            # Update remarks if specified
            if remarks:
                # Append to existing remarks if any
                existing_remarks = df.at[row_index, 'Remarks']
                if existing_remarks and not pd.isna(existing_remarks):
                    new_remarks = f"{existing_remarks}; {remarks}"
                else:
                    new_remarks = remarks
                df.at[row_index, 'Remarks'] = new_remarks
            
            # Save changes back to Excel file
            df.to_excel(file_path, index=False)
            logger.info(f"Successfully updated row {row_index} in {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Excel file {file_path}: {str(e)}")
            return False
    
    def append_log(self, file_path, row_index, log_message):
        """
        Append a log/remark to a specific row
        
        Args:
            file_path (str): Path to the Excel file
            row_index (int): Index of the row to update
            log_message (str): Message to append to remarks
            
        Returns:
            bool: True if update successful, False otherwise
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        log_entry = f"[{timestamp}] {log_message}"
        return self.update_payment(file_path, row_index, remarks=log_entry)
    
    def create_template_file(self, output_path):
        """
        Create a template Excel file with the required columns
        
        Args:
            output_path (str): Path where the template file will be saved
            
        Returns:
            bool: True if file created successfully, False otherwise
        """
        try:
            # Create an empty DataFrame with the required columns
            df = pd.DataFrame(columns=self.all_columns)
            
            # Add a sample row to demonstrate the expected format
            sample_row = {
                'Name': 'John Doe',
                'Amount': 1000.00,
                'Due Date': datetime.now().strftime('%Y-%m-%d'),
                'Email': 'john.doe@example.com',
                'Status': 'Unpaid',
                'Remarks': 'Initial invoice',
                'Payment Date': ''
            }
            df = pd.concat([df, pd.DataFrame([sample_row])], ignore_index=True)
            
            # Save to Excel
            df.to_excel(output_path, index=False)
            logger.info(f"Created template file at {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating template file: {str(e)}")
            return False

# For testing
if __name__ == "__main__":
    # Create a test instance
    excel_manager = ExcelManager()
    
    # Create a test excel file
    test_df = pd.DataFrame({
        'Name': ['John Doe', 'Jane Smith'],
        'Amount': [100, 200],
        'Due Date': ['2023-06-01', '2023-06-15'],
        'Email': ['john@example.com', 'jane@example.com'],
        'Status': ['Unpaid', 'Unpaid']
    })
    
    test_file = "test_payment_excel.xlsx"
    test_df.to_excel(test_file, index=False)
    
    try:
        # Read entries
        entries = excel_manager.get_payment_entries(test_file, "TestCity")
        print(f"Read entries: {entries}")
        
        # Update a payment
        updated = excel_manager.update_payment(
            test_file, 
            0,  # First row
            amount_paid=50,  # Partial payment
            remarks="First installment"
        )
        print(f"Update successful: {updated}")
        
        # Read updated entries
        updated_entries = excel_manager.get_payment_entries(test_file)
        print(f"Updated entries: {updated_entries}")
        
        # Create a template file
        template_created = excel_manager.create_template_file("payment_template.xlsx")
        print(f"Template created: {template_created}")
        
    finally:
        # Clean up
        import os
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists("payment_template.xlsx"):
            os.remove("payment_template.xlsx")