import smtplib
import ssl
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.conf import settings


class CustomSMTPEmailBackend(SMTPEmailBackend):
    """
    Custom SMTP email backend that handles SSL certificate verification issues
    """
    
    def open(self):
        """
        Open an SMTP connection with custom SSL context
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False
            
        # Create custom SSL context that doesn't verify certificates
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        try:
            if self.use_ssl:
                self.connection = smtplib.SMTP_SSL(
                    self.host, 
                    self.port, 
                    timeout=self.timeout,
                    context=context
                )
            else:
                self.connection = smtplib.SMTP(
                    self.host, 
                    self.port, 
                    timeout=self.timeout
                )
                if self.use_tls:
                    self.connection.starttls(context=context)
                    
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
            
        except Exception as e:
            if not self.fail_silently:
                raise e
            return False
