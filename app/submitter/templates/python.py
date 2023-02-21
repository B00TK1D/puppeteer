#!/usr/bin/python3

import requests
import sys

FLAG = sys.argv[1]

r = requests.get('http://scoreboard.com/submit?flag=' + FLAG)