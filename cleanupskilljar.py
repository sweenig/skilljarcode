#!/usr/bin/env python3
from __future__ import print_function # make this possible to run in python2, but you should be using python3

#parse the command line arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument(f"--token", required=True)
parser.add_argument(f"--lmcapool", required=True)
parser.add_argument(f"--lmcppool", required=True)
args = parser.parse_args()

import requests
baseURL = "https://api.skilljar.com:443/v1"
creds = (args.token,"")

print(requests.delete(baseURL + "/promo-code-pools/" + args.lmcapool, auth=creds))
print(requests.delete(baseURL + "/promo-code-pools/" + args.lmcppool, auth=creds))
