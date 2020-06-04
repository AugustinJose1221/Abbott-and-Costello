#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 12:52:25 2020

@author: augustinjose
"""


import sys
from PIL import Image
import cv2

def imageCapture():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    return frame

def OutputAscii():
    # pass the image as command line argument
    #image_path = "/home/augustinjose/Projects/Python/Abbott-and-Costello/src/Augustin.JPG"
    #img = Image.open(image_path)
    frame = imageCapture()
    img_cv2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img_cv2)
    # resize the image
    width, height = img.size
    aspect_ratio = height/width
    new_width = 120
    new_height = aspect_ratio * new_width * 0.55
    img = img.resize((new_width, int(new_height)))
    # new size of image
    # print(img.size)
    
    # convert image to greyscale format
    img = img.convert('L')
    
    pixels = img.getdata()
    
    # replace each pixel with a character from array
    chars = ["B","S","#","&","@","$","%","*","!",":","."]
    new_pixels = [chars[pixel//25] for pixel in pixels]
    new_pixels = ''.join(new_pixels)
    
    # split string of chars into multiple strings of length equal to new width and create a list
    new_pixels_count = len(new_pixels)
    ascii_image = [new_pixels[index:index + new_width] for index in range(0, new_pixels_count, new_width)]
    ascii_image = "\n".join(ascii_image)
    print(ascii_image)
    return(ascii_image)

while(True):
    OutputAscii()