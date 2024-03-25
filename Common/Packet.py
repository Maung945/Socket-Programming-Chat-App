from datetime import datetime

class TextPayload:
    """A class to determine the format of text messages for the purpose of server features..."""
    def __init__(self, timestamp, username, content):
        self.timestamp = timestamp
        self.username = username
        self.content = content

    #Generates a text payload object based on the current time...
    @staticmethod
    def Generate(username, content):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return TextPayload(timestamp, username, content)

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

    #Defining list casting...
    def to_csv(self):
        return [self.timestamp, self.username, self.content]
    
class LitProtocolPacket:
    """
    A class to represent a Lit Protocol Packet which includes a packet header
    and payload, with functionality to calculate the total size of the packet
    and to serialize/deserialize the packet data. The packet length is calculated
    internally and not set in the constructor.
    """
    
    def __init__(self, message_type, options_flags, timestamp, message_id, iv, hash_value, payload):
        self.message_type = message_type
        self.options_flags = options_flags
        self.timestamp = timestamp
        self.message_id = message_id
        self.iv = iv
        self.hash_value = hash_value
        self.payload = payload
        #Calculate packet length internally as the sum of all header fields and payload
        self.packet_length = self.calculate_packet_length()

    def calculate_packet_length(self):
        #Header size = sum of the sizes of all fixed-length fields
        header_size = 2 + 2 + 4 + 8 + 8 + 16 + 32
        #Packet length includes the size of the header and the payload
        return header_size + len(self.payload)

    @staticmethod
    def encode(packet):
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
            packet.message_id +
            packet.iv +
            packet.hash_value +
            packet.payload
        )

    @staticmethod
    def decode(packet_data):
        """
        Deserializes the bytes into a packet object for TCP reception. See documentation regarding packet structure...
        """
        message_type = packet_data[:2]
        options_flags = packet_data[2:4]
        packet_length = int.from_bytes(packet_data[4:8], 'big')
        timestamp = packet_data[8:16]
        message_id = packet_data[16:24]
        iv = packet_data[24:40]
        hash_value = packet_data[40:72]
        payload = packet_data[72:]

        return LitProtocolPacket(
            message_type=message_type,
            options_flags=options_flags,
            timestamp=timestamp,
            message_id=message_id,
            iv=iv,
            hash_value=hash_value,
            payload=payload
        )

    def __repr__(self):
        return (f"LitProtocolPacket(message_type={self.message_type}, options_flags={self.options_flags}, "
                f"packet_length={self.packet_length}, timestamp={self.timestamp}, message_id={self.message_id}, "
                f"iv={self.iv}, hash_value={self.hash_value}, payload={self.payload[:10]}...)")
