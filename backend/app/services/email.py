# backend/app/services/email.py
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, select_autoescape, PackageLoader
from typing import List, Optional

from ..core.config import settings

class EmailService:
    """Service for handling email operations."""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAILS_FROM_EMAIL
        self.from_name = settings.EMAILS_FROM_NAME
        
        # Initialize Jinja2 environment for email templates
        self.env = Environment(
            loader=PackageLoader('app', 'templates/email'),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def _create_message(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> MIMEMultipart:
        """Create email message with proper headers and content."""
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = f"{self.from_name} <{self.from_email}>"
        message['To'] = to_email
        
        if cc:
            message['Cc'] = ', '.join(cc)
        if bcc:
            message['Bcc'] = ', '.join(bcc)

        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)
        
        return message

    def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        template_data: dict,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email using a template.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            template_name: Name of the template file
            template_data: Data to be passed to the template
            cc: List of CC recipients
            bcc: List of BCC recipients
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Get template and render content
            template = self.env.get_template(f"{template_name}.html")
            html_content = template.render(**template_data)
            
            # Create message
            message = self._create_message(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                cc=cc,
                bcc=bcc
            )
            
            # Create secure SSL/TLS context
            context = ssl.create_default_context()
            
            # Send email
            if settings.SMTP_TLS:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls(context=context)
                    if self.smtp_user and self.smtp_password:
                        server.login(self.smtp_user, self.smtp_password)
                    server.send_message(message)
            else:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                    if self.smtp_user and self.smtp_password:
                        server.login(self.smtp_user, self.smtp_password)
                    server.send_message(message)
            
            return True
            
        except Exception as e:
            # Log the error in production
            print(f"Failed to send email: {str(e)}")
            return False

    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email."""
        return self.send_email(
            to_email=to_email,
            subject="Password Reset Request",
            template_name="password_reset",
            template_data={
                "reset_url": f"{settings.SERVER_HOST}/reset-password?token={reset_token}",
                "valid_hours": settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
            }
        )

    def send_2fa_code(self, to_email: str, code: str) -> bool:
        """Send 2FA verification code."""
        return self.send_email(
            to_email=to_email,
            subject="Your Verification Code",
            template_name="2fa_code",
            template_data={
                "code": code,
                "valid_minutes": settings.TWO_FACTOR_CODE_TTL_SECONDS // 60
            }
        )

    def send_login_alert(self, to_email: str, ip_address: str, location: str) -> bool:
        """Send login alert for suspicious activity."""
        return self.send_email(
            to_email=to_email,
            subject="Security Alert: New Login Detected",
            template_name="login_alert",
            template_data={
                "ip_address": ip_address,
                "location": location,
                "timestamp": "now"  # You might want to pass actual timestamp
            }
        )

# Create a singleton instance
email_service = EmailService()
