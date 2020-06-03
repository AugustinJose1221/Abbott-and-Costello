#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 13:45:40 2020

@author: augustinjose
"""


import socket
import os
import signal
import threading
import hashlib
import fcntl
import struct
from Crypto import Random
import Crypto.Cipher.AES as AES
from Crypto.PublicKey import RSA


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', ifname[:15])
    )[20:24])


def RemovePadding(s):
    return s.replace(b'`',b'')


def Padding(s):
    return s + ((16 - len(s) % 16) * '`')


def ConnectionSetup():
    while True:
        if check is True:
            client, address = server.accept()
            print("\n[!] One client is trying to connect...")
            # get client public key and the hash of it
            clientPH = client.recv(2048)
            split = clientPH.split(b":")
            tmpClientPublic = split[0]
            clientPublicHash = split[1]
            print("\n[!] Anonymous client's public key\n")
            tmpClientPublic = tmpClientPublic.replace(b"\r\n", b'')
            clientPublicHash = clientPublicHash.replace(b"\r\n", b'')
            tmpHashObject = hashlib.md5(tmpClientPublic)
            tmpHash = tmpHashObject.hexdigest()

            if tmpHash == clientPublicHash.decode("utf-8") :
                # sending public key,encrypted eight byte ,hash of eight byte and server public key hash
                print("\n[!] Anonymous client's public key and public key hash matched\n")
                clientPublic = RSA.importKey(tmpClientPublic)
                fSend = eightByte + b":" + bytes(session, "utf-8") + b":" + bytes(my_hash_public, "utf-8")
                fSend = clientPublic.encrypt(fSend, None)
                client.send(fSend[0] + b"\:" + public)

                clientPH = client.recv(2048)
                if clientPH != b"":
                    print(clientPH)
                    clientPH = RSA.importKey(private).decrypt(clientPH)
                    print("\n[!] Matching session key\n")
                    if clientPH == eightByte:
                        # creating 128 bits key with 16 bytes
                        print("\n[!] Creating AES key\n")
                        key_128 = eightByte + eightByte[::-1]
                        AESKey = AES.new(key_128, AES.MODE_CBC,IV=key_128)
                        clientMsg = AESKey.encrypt(Padding(FLAG_READY))
                        client.send(clientMsg)
                        print("\n[!] Waiting for client's name\n")
                        # client name
                        clientMsg = client.recv(2048)
                        CONNECTION_LIST.append((clientMsg, client))
                        print("\n"+clientMsg.decode("utf-8")+" IS CONNECTED")
                        threading_client = threading.Thread(target=broadcast_usr,args=[clientMsg,client,AESKey])
                        threading_client.start()
                        threading_message = threading.Thread(target=send_message,args=[client,AESKey])
                        threading_message.start()
                    else:
                        print("\nSession key from client does not match")
            else:
                print("\nPublic key and public hash doesn't match")
                client.close()


def send_message(socketClient,AESk):
    while True:
        msg = input("\n[>] ENTER YOUR MESSAGE : ")
        en = AESk.encrypt(Padding(msg))
        socketClient.send(en)
        if msg == FLAG_QUIT:
            os.kill(os.getpid(), signal.SIGKILL)
        else:
            print("\n[!] Your encrypted message \n ", en)


def broadcast_usr(uname, socketClient,AESk):
    while True:
        try:
            data = socketClient.recv(1024)
            en = data
            if data:
                data = RemovePadding(AESk.decrypt(data))
                if data == FLAG_QUIT:
                    print("\n"+uname+" left the conversation")
                else:
                    b_usr(socketClient, uname, data)
                    print("\n[!] ", uname, " SAID : ", data)
                    print("\n[!] Client's encrypted message\n ",  en)
        except Exception as x:
            print(x.message)
            break


def b_usr(cs_sock, sen_name, msg):
    for client in CONNECTION_LIST:
        if client[1] != cs_sock:
            client[1].send(sen_name)
            client[1].send(msg)


if __name__ == "__main__":
    # objects
    host = ""
    port = 0
    server = ""
    AESKey = ""
    CONNECTION_LIST = []
    FLAG_READY = "Ready"
    FLAG_QUIT = "quit"
    YES = "1"
    NO = "2"

    # 10.1.236.227
    # public key and private key
    random = Random.new().read
    RSAkey = RSA.generate(1024, random)
    public = RSAkey.publickey().exportKey()
    private = RSAkey.exportKey()

    tmpPub = hashlib.md5(public)
    my_hash_public = tmpPub.hexdigest()

    eightByte = os.urandom(8)
    sess = hashlib.md5(eightByte)
    session = sess.hexdigest()

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
    print("[1] Auto connect by with broadcast IP & PORT\n[2] Manually enter IP & PORT\n")
    ask = input("[>] ")
    if ask == YES:
        host = get_ip_address('wlp2s0')
        port = 8080
    elif ask == NO:
        host = input("Host : ")
        port = int(input("Port : "))
    else:
        print("[!] Invalid selection")
        os.kill(os.getpid(), signal.SIGKILL)

    print("\n[!] Server IP "+host+" & PORT "+str(port))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)
    print("\n[!] Server Connection Successful")
    check = True
    # accept clients
    threading_accept = threading.Thread(target=ConnectionSetup)
    threading_accept.start()





