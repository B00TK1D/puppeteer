#!/usr/bin/python3

import requests
import sys

HOST = sys.argv[1]

r = requests.get('http://' + HOST + '/flag.txt')