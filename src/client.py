#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 13:45:16 2020

@author: augustinjose
"""


import socket
import os
import threading
import hashlib
from Crypto import Random
import Crypto.Cipher.AES as AES
from Crypto.PublicKey import RSA
import signal


def RemovePadding(s):
    return s.replace(b'`',b'')


def Padding(s):
    return s + ((16 - len(s) % 16) * '`')


def ReceiveMessage():
    while True:
        emsg = server.recv(1024)
        msg = RemovePadding(AESKey.decrypt(emsg))
        if msg == FLAG_QUIT:
            print("\n[!] Server down! Over")
            os.kill(os.getpid(), signal.SIGKILL)
        else:
            print("\nAbbot> ", msg.decode("utf-8"))


def SendMessage():
    while True:
        msg = input("")
        msg = " "+msg
        en = AESKey.encrypt(Padding(msg))
        server.send(en)
        if msg == FLAG_QUIT:
            print("If I'm not back in 5 mins, just wait longer\n\n\n\n")
            os.kill(os.getpid(), signal.SIGKILL)
        else:
            continue


if __name__ == "__main__":
    #objects
    server = ""
    AESKey = ""
    FLAG_READY = "Ready"
    FLAG_QUIT = "quit"
    # 10.1.236.227
    # public key and private key
    random = Random.new().read
    RSAkey = RSA.generate(1024, random)
    public = RSAkey.publickey().exportKey()
    private = RSAkey.exportKey()

    tmpPub = hashlib.md5(public)
    my_hash_public = tmpPub.hexdigest()

    #print(public)
    #print("\n",private)

    host = input("Host : ")
    port = int(input("Port : "))
#    host = "127.0.0.1"
#    port = 5599

    with open('private.txt', 'wb'):
        pass
    with open('public.txt', 'wb'):
        pass

    try:
        file = open('private.txt', 'wb')
        file.write(private)
        file.close()
    
        file = open('public.txt', 'wb')
        file.write(public)
        file.close()
    except BaseException:
        print("Key storing in failed")

    check = False

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((host, port))
        check = True
    except BaseException:
        print("\n[!] Check Server Address or Port")

    if check is True:
        print("\n[!] Connection Successful")
        server.send(public + b":" + bytes(my_hash_public, "utf-8"))
        # receive server public key,hash of public,eight byte and hash of eight byte
        fGet = server.recv(4072)
        split = fGet.split(b"\:")
        toDecrypt = split[0]
        serverPublic = split[1]
        decrypted = RSA.importKey(private).decrypt(toDecrypt.replace(b"\r\n", b''))
        splittedDecrypt = decrypted.split(b":")
        eightByte = splittedDecrypt[0]
        hashOfEight = splittedDecrypt[1]
        hashOfSPublic = splittedDecrypt[2]

        # hashing for checking
        sess = hashlib.md5(eightByte)
        session = sess.hexdigest()

        hashObj = hashlib.md5(serverPublic)
        server_public_hash = hashObj.hexdigest()
        if server_public_hash == hashOfSPublic.decode("utf-8") and session == hashOfEight.decode("utf-8"):
            # encrypt back the eight byte key with the server public key and send it
            serverPublic = RSA.importKey(serverPublic).encrypt(eightByte, None)
            server.send(serverPublic[0])
            # creating 128 bits key with 16 bytes
            key_128 = eightByte + eightByte[::-1]
            AESKey = AES.new(key_128, AES.MODE_CBC,IV=key_128)
            # receiving ready
            serverMsg = server.recv(2048)
            serverMsg = RemovePadding(AESKey.decrypt(serverMsg))
            if serverMsg.decode("utf-8") == FLAG_READY:
                print("\n[!] Server is ready to communicate\n")
                serverMsg = input("\n[>] ENTER YOUR NAME : ")
                server.send(bytes(serverMsg, "utf-8"))
                threading_rec = threading.Thread(target=ReceiveMessage)
                threading_rec.start()
                threading_send = threading.Thread(target=SendMessage)
                threading_send.start()
        else:
            print("\nServer (Public key && Public key hash) || (Session key && Hash of Session key) doesn't match")
