"""
File Manager Module for Payment Reminder App
Handles Excel file upload, storage, and organization
"""
import os
import shutil
from datetime import datetime
import logging
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('file_manager')

class FileManager:
    def __init__(self, base_folder="payment_data"):
        """Initialize the FileManager with a base folder for data storage"""
        self.base_folder = base_folder
        self._ensure_base_folder_exists()
    
    def _ensure_base_folder_exists(self):
        """Create the base folder structure if it doesn't exist"""
        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)
            logger.info(f"Created base folder: {self.base_folder}")
    
    def _ensure_city_folder_exists(self, city_name):
        """Create a folder for a specific city if it doesn't exist"""
        city_folder = os.path.join(self.base_folder, city_name)
        if not os.path.exists(city_folder):
            os.makedirs(city_folder)
            logger.info(f"Created city folder: {city_folder}")
        return city_folder
    
    def save_excel_file(self, source_file_path, city_name):
        """
        Save an Excel file to the appropriate city folder
        
        Args:
            source_file_path (str): Path to the Excel file to be saved
            city_name (str): Name of the city (used as folder name)
            
        Returns:
            str: Path where the file was saved
        """
        # Validate input
        if not os.path.exists(source_file_path):
            error_msg = f"Source file does not exist: {source_file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Check file extension
        _, file_extension = os.path.splitext(source_file_path)
        if file_extension.lower() not in ['.xls', '.xlsx']:
            error_msg = f"Invalid file type. Expected Excel file, got {file_extension}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Create city folder if it doesn't exist
        city_folder = self._ensure_city_folder_exists(city_name)
        
        # Generate target filename with timestamp to avoid overwrites
        filename = os.path.basename(source_file_path)
        base_name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_filename = f"{base_name}_{timestamp}{ext}"
        target_path = os.path.join(city_folder, target_filename)
        
        # Copy the file
        try:
            shutil.copy2(source_file_path, target_path)
            logger.info(f"File saved successfully: {target_path}")
            return target_path
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
    
    def list_all_files(self):
        """
        List all Excel files in all city folders
        
        Returns:
            list: List of tuples (file_path, city_name)
        """
        result = []
        
        # If base folder doesn't exist, return empty list
        if not os.path.exists(self.base_folder):
            return result
            
        # Iterate through all city folders
        for city_name in os.listdir(self.base_folder):
            city_path = os.path.join(self.base_folder, city_name)
            
            # Skip if not a directory
            if not os.path.isdir(city_path):
                continue
                
            # Find all Excel files in the city folder
            for filename in os.listdir(city_path):
                if filename.endswith(('.xlsx', '.xls')):
                    file_path = os.path.join(city_path, filename)
                    result.append((file_path, city_name))
        
        logger.info(f"Found {len(result)} Excel files across all city folders")
        return result
    
    def get_city_files(self, city_name):
        """
        Get all Excel files for a specific city
        
        Args:
            city_name (str): Name of the city
            
        Returns:
            list: List of file paths
        """
        city_folder = os.path.join(self.base_folder, city_name)
        result = []
        
        if not os.path.exists(city_folder):
            logger.warning(f"City folder does not exist: {city_folder}")
            return result
            
        for filename in os.listdir(city_folder):
            if filename.endswith(('.xlsx', '.xls')):
                file_path = os.path.join(city_folder, filename)
                result.append(file_path)
        
        return result
    
    def get_latest_file_by_city(self, city_name):
        """
        Get the most recently added Excel file for a specific city
        
        Args:
            city_name (str): Name of the city
            
        Returns:
            str or None: Path to the latest file, or None if no files exist
        """
        files = self.get_city_files(city_name)
        
        if not files:
            return None
            
        # Sort by modification time, newest first
        latest_file = max(files, key=os.path.getmtime)
        return latest_file
    
    def list_all_cities(self):
        """
        List all city folders
        
        Returns:
            list: List of city names
        """
        result = []
        
        if not os.path.exists(self.base_folder):
            return result
            
        for item in os.listdir(self.base_folder):
            item_path = os.path.join(self.base_folder, item)
            if os.path.isdir(item_path):
                result.append(item)
                
        return result

# For testing
if __name__ == "__main__":
    # Create a test instance
    file_manager = FileManager("test_payment_data")
    
    # Test creating a dummy Excel file
    
    
    # Create a test excel file
    test_df = pd.DataFrame({
        'Name': ['John Doe', 'Jane Smith'],
        'Amount': [100, 200],
        'Due Date': ['2023-06-01', '2023-06-15'],
        'Email': ['john@example.com', 'jane@example.com'],
        'Status': ['Unpaid', 'Unpaid']
    })
    
    test_file = "test_payment.xlsx"
    test_df.to_excel(test_file, index=False)
    
    # Save the test file
    try:
        saved_path = file_manager.save_excel_file(test_file, "TestCity")
        print(f"File saved to: {saved_path}")
        
        # List all files
        all_files = file_manager.list_all_files()
        print(f"All files: {all_files}")
        
        # List all cities
        all_cities = file_manager.list_all_cities()
        print(f"All cities: {all_cities}")
        
        # Get latest file for city
        latest_file = file_manager.get_latest_file_by_city("TestCity")
        print(f"Latest file for TestCity: {latest_file}")
        
    finally:
        # Clean up
        import os
        if os.path.exists(test_file):
            os.remove(test_file)