# Abbott-and-Costello
Post-Apocalyptic Communication System

This is a client-server communication system with messages encrypted with RSA-SHA1. Like normal encrypted systems, it uses a public key to enable a handshake between the two users. The messages are first converted to base-64. This encrypted message is again encyrpted using the user's private key. For further security, it is hashed with a hash function.
