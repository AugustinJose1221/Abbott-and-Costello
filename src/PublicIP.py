#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 12:47:12 2020

@author: augustinjose
"""


from requests import get
def publicIP():
    ip = get('https://api.ipify.org').text
    return ip