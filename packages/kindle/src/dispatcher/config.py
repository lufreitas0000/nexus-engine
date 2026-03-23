import os
from dotenv import load_dotenv
from dataclasses import dataclass

@dataclass(frozen=True)
class SmtpConfig:
    sender: str
    password: str
    destination: str
    host: str
    port: int

def load_smtp_config() -> SmtpConfig:
    load_dotenv()
    
    sender = os.getenv('SMTP_SENDER')
    password = os.getenv('SMTP_PASSWORD')
    destination = os.getenv('KINDLE_DESTINATION')
    host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    port_str = os.getenv('SMTP_PORT', '587')
    
    if not sender or not password or not destination:
        raise EnvironmentError(
            "Incomplete environment state. Ensure SMTP_SENDER, "
            "SMTP_PASSWORD, and KINDLE_DESTINATION are strictly defined."
        )
        
    try:
        port = int(port_str)
    except ValueError as type_error:
        raise EnvironmentError(
            f"Type conversion failure. SMTP_PORT must be an integer. Received: {port_str}"
        ) from type_error
        
    return SmtpConfig(
        sender=sender, 
        password=password, 
        destination=destination,
        host=host,
        port=port
    )
