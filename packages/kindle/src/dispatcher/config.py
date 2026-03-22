import os
from dotenv import load_dotenv
from dataclasses import dataclass

@dataclass(frozen=True)
class SmtpConfig:
    sender: str
    password: str
    destination: str

def load_smtp_config() -> SmtpConfig:
    load_dotenv()
    
    sender = os.getenv('SMTP_SENDER')
    password = os.getenv('SMTP_PASSWORD')
    destination = os.getenv('KINDLE_DESTINATION')
    
    if not sender or not password or not destination:
        raise EnvironmentError(
            "Incomplete environment state. Ensure SMTP_SENDER, "
            "SMTP_PASSWORD, and KINDLE_DESTINATION are strictly defined."
        )
        
    return SmtpConfig(
        sender=sender, 
        password=password, 
        destination=destination
    )
