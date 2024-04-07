# Lit Protocol Parket (LITP) Encoding/Decoding Guide

This document explains the how to encode and decode a `LitProtocolPacket` class and associated methods for processing by a client/server.

## Overview

The Lit Protocol Packet is designed to represent a packet in the Lit Protocol, consisting of a header and payload. It provides functionality to calculate packet length, serialize/deserialize packet data, generate HMAC, and more. First you instantiate a LITP packet using it's constructor, you then encode it into bytes. Then, when recieving the packet via TCP, you can decode it into a LITP packet object, and can retrieve data from the member variables of the object.

## Usage Example

```python
sample_secret_key = secrets.token_bytes(32)
sample_iv = os.urandom(16)
sample_payload = "SAMPLE"

SamplePacket = LitProtocolPacket(b'\x01', b'\x01', b'\x01', sample_iv, sample_secret_key, sample_payload.encode())
print("ORIGINAL:\n" + str(SamplePacket))
EncodedSamplePacket = LitProtocolPacket.encode(SamplePacket)
print("ENCODED:\n" + str(EncodedSamplePacket))
DecodedSamplePacket = LitProtocolPacket.decode(EncodedSamplePacket)
print("DECODED:\n" + str(SamplePacket))
