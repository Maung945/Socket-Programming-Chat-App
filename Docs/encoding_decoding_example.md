# Lit Protocol Packet (LITP) Encoding/Decoding Guide

This document details the process of encoding and decoding packets using the `LitProtocolPacket` class, specifically designed for secure and efficient data transmission in the Lit Protocol. The protocol supports various message types, including text, images, and generic files, with options for encryption.

## Overview

The `LitProtocolPacket` class represents a packet within the Lit Protocol, featuring a structured format that includes a header, payload, and optional security features like encryption and HMAC for integrity verification. This guide covers the instantiation of a `LitProtocolPacket` object, its encoding to bytes for transmission, and decoding back into an object upon receipt.

## Constructor Parameters

To create a `LitProtocolPacket` object, the following parameters are required:

- **message_type**: Specifies the type of message being sent. Examples include `0x00` for text messages, `0x01` for images, and `0x02` for generic files. This allows the protocol to handle different data types appropriately.
  
- **options_flags**: Indicates any special handling or features for the packet, such as encryption. For example, `0x00` denotes no encryption, while `0x01` indicates that the packet is encrypted.
  
- **message_id**: A unique identifier for the packet, typically generated randomly. This can be used for tracking, reordering, or deduplication of messages.
  
- **iv**: The Initialization Vector (IV) used for encryption. This parameter is necessary for decryption and should be randomly generated to ensure security.
  
- **hmac**: A Hash-based Message Authentication Code (HMAC) used for verifying the integrity and authenticity of the packet. This ensures that the packet has not been tampered with during transit.
  
- **payload**: The actual data being transmitted. This could be a text message, image data, or any binary data, depending on the `message_type`. The payload should be serialized to a byte string for TCP transmission.

## Usage Example

The following example demonstrates how to create a `LitProtocolPacket` object with a text message payload, showcasing the process from instantiation to encoding and decoding, this example also demonstrates how one would parse the packet header in order to determine the appropriate operations to perform on the payload:

```python
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from Common.Packet import LitProtocolPacket

#Sample values for creating a LitProtocolPacket object
message_type = b'\x00\x00'       #TEXT MESSAGE...
options_flags = b'\x00\x00'      #NO ENCRYPTION...
message_id = os.urandom(8)       #Dummy ID, not decided on what information will be here...
iv = os.urandom(16)              #Dummy IV for future encryption implementation...
payload = "sample payload"       #Retrieve message payload from UI...
hmac = os.urandom(32)            #Dummy HMAC for future encryption implementation...

#Create the LitProtocolPacket object...
message_packet = LitProtocolPacket(
    message_type=message_type,
    options_flags=options_flags,
    message_id=message_id,
    iv=iv,
    hmac=hmac,
    payload=payload.encode()  #Serialize the payload to a byte string...
)


encoded_packet = LitProtocolPacket.encodePacket(message_packet) #Encoding (serializing) packet...
decoded_packet = LitProtocolPacket.decodePacket(encoded_packet) #Decoding (deserializing) pacet...

print("ORIGINAL:", message_packet)
print("ENCODED:", encoded_packet)
print("DECODED:", decoded_packet)

#Retriving message (payload) from packet and determining message type...
if(decoded_packet.message_type == b'\x00\x00'):
    print("Payload from Packet (text message): " + decoded_packet.payload.decode())
elif(decoded_packet.message_type == b'\x00\x01'):
    print("Payload from Packet (image)...") 
    #Logic for decoding images not implemented yet...
else:
    print("Payload from Packet (other kind of file)...") 
    #Add logic for other files as needed...