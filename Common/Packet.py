from datetime import datetime
import time
import os
import sys
import copy
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hmac
from cryptography.hazmat.primitives import hashes
from Crypto.Cipher import AES

#subject to change...

class TextPayload:
    """A class to determine the format of text messages for the purpose of server features..."""
    @staticmethod
    def Generate(username, content):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{timestamp},{username},{content}"
    
    @staticmethod
    def reorient_string(input_string):
        parts = input_string.split(",", 2)  # Split the string by comma

        # Extracting individual parts
        timestamp = parts[0]
        username = parts[1]
        content = parts[2]

        # Reorienting the string
        reoriented_string = f"[{timestamp}] [{username}] : {content}"

        return reoriented_string

    #Per object...
    @classmethod
    def from_string(cls, message_str):
        try:
            timestamp, username, content = message_str.split(',', 2)
            return cls(timestamp, username, content)
        except ValueError:
            return None

    #Defining string casting...
    def __str__(self):
        return f"{self.timestamp},{self.username},{self.content}"
    
   


class LitProtocolPacket:
    """
    A class to represent a Lit Protocol Packet which includes a packet header
    and payload, with functionality to calculate the total size of the packet
    and to serialize/deserialize the packet data. The packet length is calculated
    internally and not set in the constructor.
    """
    def __init__(self, message_type, options_flags, init, iv, payload, timestamp=None, hmac = None):
        self.message_type = message_type                        # Message type...
        self.options_flags = options_flags                      # Options flags...
        self.init = init                                        # Initialization field...
        self.iv = iv                                            # Encryption Interrupt Vector...
        self.payload = payload                                  # Message Payload...
        #self.secret_key = secret_key
        self.hmac = hmac                                    # HMAC hash value...
        self.timestamp = timestamp if timestamp is not None else self.generate_timestamp()  # Decode timestamp if provided, else decode from packet data...
        self.packet_length = self.calculate_packet_length()     # Generate length after object is constructed...

    def calculate_packet_length(self):
        """
        Calculates the overall length of the packet (Header + Payload).
        """
        #Header size = sum of the sizes of all fixed-length fields...
        header_size = 2 + 2 + 4 + 8 + 8 + 16 + 32
        #Packet length includes the size of the header and the payload...
        return header_size + len(self.payload)

    def generate_timestamp(self):
        """
        Calculates the current time and date, encodes it as a 64-bit UNIX timestamp...
        """
        dispatch_time = datetime.now()                           #Time message is sent as Python datetime object...
        unix_time = int(time.mktime(dispatch_time.timetuple()))  #Time message is sent as UNIX timestamp...

        #Bit-banging into an 8-byte wide string...
        bit_string = bytes([
            (unix_time >> 56) & 0xFF,
            (unix_time >> 48) & 0xFF,
            (unix_time >> 40) & 0xFF,
            (unix_time >> 32) & 0xFF,
            (unix_time >> 24) & 0xFF,
            (unix_time >> 16) & 0xFF,
            (unix_time >> 8) & 0xFF,
            unix_time & 0xFF,
        ])
        
        return bit_string

    def generate_hmac(self, secret_key):
        """
        Generate the HMAC of a particular message payload...
        """
        h = hmac.HMAC(secret_key, hashes.SHA256(), backend=default_backend())
        h.update(self.payload)
        return h.finalize()

    @staticmethod
    def encodePacket(packet):
        """
        Serializes the packet object into bytes for TCP transmission, including recalculating packet length.
        See documentation regarding packet structure...
        """
        packet.packet_length = packet.calculate_packet_length()  #Recalculate to ensure accuracy of packet length...
        return (
            packet.message_type +
            packet.options_flags +
            packet.packet_length.to_bytes(4, 'big') +
            packet.timestamp + 
            packet.init +
            packet.iv +
            packet.hmac +
            packet.payload
        )

    @staticmethod
    def decodePacket(packet_data):
        """
        Deserializes the bytes into a packet object for TCP reception. See documentation regarding packet structure...
        """
        message_type = packet_data[:2]
        options_flags = packet_data[2:4]
        packet_length = int.from_bytes(packet_data[4:8], 'big')
        timestamp = packet_data[8:16]
        init = packet_data[16:24]
        iv = packet_data[24:40]
        hmac = packet_data[40:72]
        payload = packet_data[72:]

        return LitProtocolPacket(
            message_type=message_type,
            options_flags=options_flags,
            timestamp=timestamp,
            init=init,
            iv=iv,
            hmac=hmac,
            payload=payload
        )

    @staticmethod
    def generateEncryptedTextMessage(shared_secret, message):
        #Encrypting the message...
        cipher = AES.new(shared_secret, AES.MODE_CFB)
        encrypted_message = cipher.encrypt(message)
        iv = cipher.iv

        #Values
        message_type = b'\x00\x00'                         #0x00 = TEXT MESSAGE, 0x01 = IMAGE, 0x02 = GENERIC FILE (subject to change)...
        message_options_flags = b'\x00\x01'                #0x00 = NO ENCRYPTION, 0x01 = ENCRYPTION...
        init = b'\x00\x00\x00\x00\x00\x00\x00\x04'         #Keep track of key-excyhange sequence...
        message_iv = iv                                    #Initialization Vector...
        message_payload = encrypted_message                #Payload (currently as TextPayload)
        message_hmac = os.urandom(32)                      #Dummy HMAC, for when we implement encryption...
        
        #Creating the LitProtocolPacket object...
        message_packet = LitProtocolPacket(
            message_type=message_type,
            options_flags=message_options_flags,
            init=init,
            iv=message_iv,                                
            hmac=message_hmac,                            
            payload=message_payload                       #Serializing the payload to a byte string for TCP transmission...
        )
        return message_packet    

    @staticmethod
    def generateTextMessage(message):
        
        #Sample values
        message_type = b'\x00\x00'                         #0x00 = TEXT MESSAGE, 0x01 = IMAGE, 0x02 = GENERIC FILE (subject to change)...
        message_options_flags = b'\x00\x00'                #0x00 = NO ENCRYPTION, 0x01 = ENCRYPTION...
        init = b'\x00\x00\x00\x00\x00\x00\x00\x00'         #0x...04 indicates key exchange process is finished...
        message_iv = os.urandom(16)                        #Dummy IV, for when we implement encryption...
        message_payload = message                          #Payload (currently as TextPayload)
        message_hmac = os.urandom(32)                      #Dummy HMAC, for when we implement encryption...
        
        #Creating the LitProtocolPacket object...
        message_packet = LitProtocolPacket(
            message_type=message_type,
            options_flags=message_options_flags,
            init=init,
            iv=message_iv,                                
            hmac=message_hmac,                            
            payload=message_payload                       #Serializing the payload to a byte string for TCP transmission...
        )
        return message_packet        

    def decryptPayload(self, shared_secret):
        iv = self.iv
        d_cipher = AES.new(shared_secret, AES.MODE_CFB, iv=iv)
        decrypted_payload = d_cipher.decrypt(self.payload).decode('utf-8', 'replace')
        print(f"INSIDE DECRYPT FUNC: {decrypted_payload}")

        # Create a copy of the object and modify the payload attribute
        new_instance = copy.deepcopy(self)
        new_instance.payload = decrypted_payload
        return new_instance

    def __repr__(self):
        return (f"LitProtocolPacket(message_type={self.message_type}, options_flags={self.options_flags}, "
                f"packet_length={self.packet_length}, timestamp={self.timestamp}, init={self.init}, "
                f"iv={self.iv}, hmac={self.hmac}, payload={self.payload[:10]}...)")