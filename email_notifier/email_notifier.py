"""
Email Notifier Module for Payment Reminder App
Handles sending notification emails to customers about payment status
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('email_notifier')

class EmailNotifier:
    def __init__(self, smtp_server=None, sender_email=None, app_password=None):
        """
        Initialize the EmailNotifier with SMTP server details
        
        Args:
            smtp_server (str, optional): SMTP server address (default is Gmail)
            sender_email (str, optional): Sender's email address
            app_password (str, optional): App password for sender's account
        """
        # Use provided values or try to get from environment variables
        self.smtp_server = smtp_server or os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = 587  # Standard port for TLS
        self.sender_email = sender_email or os.environ.get('SENDER_EMAIL', '')
        self.app_password = app_password or os.environ.get('EMAIL_APP_PASSWORD', '')
        self.company_name = os.environ.get('COMPANY_NAME', 'Our Company')
        
        # Check if credentials are set
        self.is_configured = bool(self.sender_email and self.app_password)
        
        if not self.is_configured:
            logger.warning("Email notifier not configured. Emails will not be sent.")
    
    def send_email(self, to_email, subject, body_text, body_html=None):
        """
        Send an email via SMTP
        
        Args:
            to_email (str): Recipient's email address
            subject (str): Email subject
            body_text (str): Plain text email body
            body_html (str, optional): HTML email body
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # Check if email notifier is configured
        if not self.is_configured:
            logger.warning("Email notifier not configured. Email not sent.")
            return False
        
        # Validate recipient email
        if not to_email or '@' not in to_email:
            logger.error(f"Invalid recipient email: {to_email}")
            return False
        
        try:
            # Create a multipart message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.company_name} <{self.sender_email}>"
            message["To"] = to_email
            
            # Add plain text part
            part1 = MIMEText(body_text, "plain")
            message.attach(part1)
            
            # Add HTML part if provided
            if body_html:
                part2 = MIMEText(body_html, "html")
                message.attach(part2)
            
            # Create secure SSL context
            context = ssl.create_default_context()
            
            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()  # Can be omitted
                server.starttls(context=context)
                server.ehlo()  # Can be omitted
                server.login(self.sender_email, self.app_password)
                server.sendmail(self.sender_email, to_email, message.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_payment_reminder(self, customer_name, amount, due_date, city=None):
        """
        Send a payment reminder email
        
        Args:
            customer_name (str): Customer's name
            amount (float): Amount due
            due_date (date): Payment due date
            city (str, optional): City name for reference
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # Format due date
        if hasattr(due_date, 'strftime'):
            due_date_str = due_date.strftime('%Y-%m-%d')
        else:
            due_date_str = str(due_date)
        
        # Format amount
        amount_str = f"${amount:.2f}"
        
        # Create subject
        subject = f"Payment Reminder - {amount_str} due on {due_date_str}"
        
        # Create plain text body
        body_text = f"""
Dear {customer_name},

This is a friendly reminder that a payment of {amount_str} is due on {due_date_str}.

Please ensure timely payment to avoid any inconvenience.

If you have already made the payment, please disregard this message.

Best regards,
{self.company_name}
"""
        
        # Create HTML body
        body_html = f"""
<html>
<head></head>
<body>
  <p>Dear {customer_name},</p>
  
  <p>This is a friendly reminder that a payment of <strong>{amount_str}</strong> is due on <strong>{due_date_str}</strong>.</p>
  
  <p>Please ensure timely payment to avoid any inconvenience.</p>
  
  <p>If you have already made the payment, please disregard this message.</p>
  
  <p>Best regards,<br>
  {self.company_name}</p>
</body>
</html>
"""
        
        # Send the email
        return self.send_email(to_email=None, subject=subject, body_text=body_text, body_html=body_html)
    
    def send_payment_confirmation(self, to_email, customer_name, amount_paid, payment_date=None):
        """
        Send a payment confirmation email
        
        Args:
            to_email (str): Recipient's email address
            customer_name (str): Customer's name
            amount_paid (float): Amount paid
            payment_date (date, optional): Date of payment
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # Format payment date
        if payment_date is None:
            payment_date = datetime.now().date()
            
        if hasattr(payment_date, 'strftime'):
            payment_date_str = payment_date.strftime('%Y-%m-%d')
        else:
            payment_date_str = str(payment_date)
        
        # Format amount
        amount_str = f"${amount_paid:.2f}"
        
        # Create subject
        subject = f"Payment Confirmation - {amount_str} received"
        
        # Create plain text body
        body_text = f"""
Dear {customer_name},

We have received your payment of {amount_str} on {payment_date_str}.

Thank you for your prompt payment.

Best regards,
{self.company_name}
"""
        
        # Create HTML body
        body_html = f"""
<html>
<head></head>
<body>
  <p>Dear {customer_name},</p>
  
  <p>We have received your payment of <strong>{amount_str}</strong> on <strong>{payment_date_str}</strong>.</p>
  
  <p>Thank you for your prompt payment.</p>
  
  <p>Best regards,<br>
  {self.company_name}</p>
</body>
</html>
"""
        
        # Send the email
        return self.send_email(to_email=to_email, subject=subject, body_text=body_text, body_html=body_html)
    
    def configure_smtp(self, smtp_server, sender_email, app_password):
        """
        Configure SMTP settings
        
        Args:
            smtp_server (str): SMTP server address
            sender_email (str): Sender's email address
            app_password (str): App password for sender's account
            
        Returns:
            bool: True if configuration successful
        """
        self.smtp_server = smtp_server
        self.sender_email = sender_email
        self.app_password = app_password
        
        # Update configuration status
        self.is_configured = bool(self.sender_email and self.app_password)
        
        return self.is_configured
    
    def test_connection(self):
        """
        Test SMTP server connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not self.is_configured:
            logger.warning("Email notifier not configured. Cannot test connection.")
            return False
            
        try:
            # Create secure SSL context
            context = ssl.create_default_context()
            
            # Test connection
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self.sender_email, self.app_password)
            
            logger.info("SMTP connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"SMTP connection test failed: {str(e)}")
            return False

# For testing
if __name__ == "__main__":
    # Create a test instance
    email_notifier = EmailNotifier()
    
    # If credentials are available in environment variables, test sending an email
    if email_notifier.is_configured:
        # Test connection
        connection_ok = email_notifier.test_connection()
        print(f"Connection test result: {connection_ok}")
        
        if connection_ok:
            # Test sending an email (replace with a valid test email)
            test_email = input("Enter a test email address: ")
            if test_email and '@' in test_email:
                result = email_notifier.send_payment_reminder(
                    to_email=test_email,
                    customer_name="Test Customer",
                    amount=100.50,
                    due_date=datetime.now().date()
                )
                print(f"Email sending result: {result}")
    else:
        print("Email notifier not configured. Set environment variables:")
        print("- SMTP_SERVER (default: smtp.gmail.com)")
        print("- SENDER_EMAIL")
        print("- EMAIL_APP_PASSWORD")
        print("- COMPANY_NAME (optional)")