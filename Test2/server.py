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
    return s.replace('`','')


def Padding(s):
    return s + ((16 - len(s) % 16) * '`')


def ReceiveMessage():
    while True:
        emsg = server.recv(1024)
        msg = RemovePadding(AESKey.decrypt(emsg))
        if msg == FLAG_QUIT:
            print("\n[!] Server was shutdown by admin")
            os.kill(os.getpid(), signal.SIGKILL)
        else:
            print("\n[!] Server's encrypted message \n" + emsg)
            print("\n[!] SERVER SAID : ", msg)


def SendMessage():
    while True:
        msg = input("[>] YOUR MESSAGE : ")
        en = AESKey.encrypt(Padding(msg))
        server.send(str(en))
        if msg == FLAG_QUIT:
            os.kill(os.getpid(), signal.SIGKILL)
        else:
            print("\n[!] Your encrypted message \n" + en)


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
        server.bind((host, port))
        check = True
    except BaseException:
        print("\n[!] Check Server Address or Port")

    if check is True:
        print("\n[!] Connection Successful")
        server.send(public + b':' + bytes(my_hash_public, 'utf-8'))
        # receive server public key,hash of public,eight byte and hash of eight byte
        fGet = server.recv(4072)
        split = fGet.split(":")
        toDecrypt = split[0]
        serverPublic = split[1]
        print("\n[!] Server's public key\n")
        print(serverPublic)
        decrypted = RSA.importKey(private).decrypt(eval(toDecrypt.replace("\r\n", '')))
        splittedDecrypt = decrypted.split(":")
        eightByte = splittedDecrypt[0]
        hashOfEight = splittedDecrypt[1]
        hashOfSPublic = splittedDecrypt[2]
        print("\n[!] Client's Eight byte key in hash\n")
        print(hashOfEight)

        # hashing for checking
        sess = hashlib.md5(eightByte)
        session = sess.hexdigest()

        hashObj = hashlib.md5(serverPublic)
        server_public_hash = hashObj.hexdigest()
        print("\n[!] Matching server's public key & eight byte key\n")
        if server_public_hash == hashOfSPublic and session == hashOfEight:
            # encrypt back the eight byte key with the server public key and send it
            print("\n[!] Sending encrypted session key\n")
            serverPublic = RSA.importKey(serverPublic).encrypt(eightByte, None)
            server.send(str(serverPublic))
            # creating 128 bits key with 16 bytes
            print("\n[!] Creating AES key\n")
            key_128 = eightByte + eightByte[::-1]
            AESKey = AES.new(key_128, AES.MODE_CBC,IV=key_128)
            # receiving ready
            serverMsg = server.recv(2048)
            serverMsg = RemovePadding(AESKey.decrypt(serverMsg))
            if serverMsg == FLAG_READY:
                print("\n[!] Server is ready to communicate\n")
                serverMsg = input("\n[>] ENTER YOUR NAME : ")
                server.send(serverMsg)
                threading_rec = threading.Thread(target=ReceiveMessage)
                threading_rec.start()
                threading_send = threading.Thread(target=SendMessage)
                threading_send.start()
        else:
            print("\nServer (Public key && Public key hash) || (Session key && Hash of Session key) doesn't match")
