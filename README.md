# Socket Programming Chat App

## Overview
This project is an encrypted messaging application implemented in Python, utilizing a server-client architecture. It allows users to securely communicate over a network. The application encrypts messages before transmission, ensuring confidentiality.

## Authors
- Daniel Appel
- Tony Alhusori
- Myo Aung
- Sungeun Kim
- Noah King

## Features
- Secure messaging: Messages are encrypted before transmission to ensure confidentiality.
- Server-client architecture: Facilitates communication between multiple users over a network.
- Easy-to-use interface: Simple commands for connecting to the server and sending/receiving messages.
- Cross-platform compatibility: Works on various operating systems supporting Python.

## Description and Report
  [a link](https://github.com/user-attachments/files/16043443/CS-3800.Final.Report-.Socket.Programming.Secured.Chat.App.pdf)
## Installation
1. Clone the repository to your local machine.
   ```
   git clone https://github.com/Maung945/socket-programming-chat-app.git
   ```
2. Navigate to the project directory.
   ```
   cd socket-programming-chat-app
   ```
3. Install the required dependencies.
   ```
   pip install pycryptodome emoji 
   ```

## Usage
1. Start the server:
   ```
   python server.py
   ```
2. Connect clients to the server:
   ```
   python client.py
   ```
3. Follow the prompts to enter your username and start sending/receiving messages.

## Encryption
To achieve secure end-to-end encrypted conversation, the implementation of a hybrid cryptosystem is needed. A hybrid cryptosystem has two essential components: a key encapsulation mechanism(asymmetric cryptography) and a data encapsulation scheme(symmetric cryptography). Generally, symmetric encryption costs less computing resources for large amounts of data compare to asymmetric encryption. However, since both parties need to use the same key for symmetric encryption, asymmetric cryptography is needed to securely share the one key.

## License
TBD
