import sys
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid, formatdate
from src.dispatcher.config import load_smtp_config

def verify_smtp_loopback() -> None:
    config = load_smtp_config()
    
    message = EmailMessage()
    message['Subject'] = "Automated System Diagnostic: SMTP Loopback Test"
    message['From'] = config.sender
    # Transmit the payload to the sender to verify outbound network routing
    message['To'] = config.sender
    message['Message-ID'] = make_msgid(domain=config.host)
    message['Date'] = formatdate(localtime=True)
    message.set_content("If this packet is received, the SMTP dispatch module is operating nominally.")

    sys.stdout.write(f"Initiating loopback transmission to {config.sender} via {config.host}:{config.port}...\n")
    
    try:
        with smtplib.SMTP(config.host, config.port) as server:
            server.set_debuglevel(1)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(config.sender, config.password)
            server.send_message(message)
            sys.stdout.write("\nLoopback transmission executed. Check your inbox.\n")
    except smtplib.SMTPException as error_state:
        sys.exit(f"\nCritical failure in loopback transmission:\n{error_state}")

if __name__ == "__main__":
    verify_smtp_loopback()
