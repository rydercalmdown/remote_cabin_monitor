from telnetlib import Telnet
import logging
import requests


class Communicator():
    """Communicator module for interacting with the swarm tile"""

    def __init__(self):
        self._set_defaults()

    def _set_defaults(self):
        """Set defaults for the system"""
        self.swarm_tile_host = '192.168.4.1'
        self.swarm_tile_telnet_port = 23
        self.telnet_timeout = 2

    def _calculate_checksum(self, command):
        """Calculate the checksum of a particular message"""
        # https://nmeachecksum.eqth.net/
        checksum = 0
        for c in list(command)[1:-1]:
            checksum = checksum ^ ord(c)
        return hex(checksum)[2:]
    
    def _clean_message(self, message):
        """Cleans the message string"""
        message = message.strip()
        message = message.replace('\n', ' ')
        message = message.replace('"', "'")
        return message

    def _build_command(self, message):
        """Build the command for sending data"""
        message = self._clean_message(message)
        initial = f'$TD "{message}"*'
        checksum = self._calculate_checksum(initial)
        return initial + str(checksum)

    def send_email(self, email_from, email_to, subject, message):
        """Send an email with the swarm network using the tile"""
        available_chars = 147
        used_chars = len(email_from) + len(email_to) + len(subject) + len(message)
        if used_chars > available_chars:
            logging.error('Message data too long; reduce characters')
            return
        parameters = {
            "user_from": email_from,
            "user_to": email_to,
            "user_subject": subject,
            "user_message": message,
        }
        url = f"http://{self.swarm_tile_host}/msgsend"
        response = requests.get(url, params=parameters, timeout=2)
        if response.status_code == 204:
            logging.info(f'Email Sent to {email_to}: {subject}')
            return True
        return False

    def send_message(self, msg_string):
        """Sends a message string to the tile"""
        command = self._build_command(msg_string)
        logging.info(f'Establishing connection to {self.swarm_tile_host}')
        with Telnet(self.swarm_tile_host, self.swarm_tile_telnet_port, self.telnet_timeout) as session:
            logging.info(f'Established connection to {self.swarm_tile_host}')
            session.write(command.encode("ascii"))
            logging.info(f'Wrote command to {self.swarm_tile_host}: {command}')
