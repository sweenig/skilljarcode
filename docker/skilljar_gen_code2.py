from __future__ import print_function # make this possible to run in python2, but you should be using python3

import sys, subprocess, pkg_resources

required = {'requests', 'python-dateutil'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    print(f"Missing required libraries: {', '.join([str(s) for s in missing])}. Attempting to install...")
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)

from os import path
import __main__ as main
import json

debug = False

credsfile = "creds.json"

if path.exists(credsfile):
    with open(credsfile) as f: creds = json.load(f)
    #creds = list(creds.values())[0]
    #print(f"Setting creds: {creds}")
    token                    = creds['token']
else:
    print(f"File not found: {credsfile}")
    print("""Create a config file called creds.json in this directory that looks like this:
{
  "token": "adelarthrosomatous"
}""")
    quit()

import requests, random, string, datetime, sys
from dateutil.relativedelta import relativedelta
from getpass import getpass
from pprint import pprint

baseURL = "https://api.skilljar.com:443/v1"

try:
    #if the input variables were not specified on the command line, prompt for them
    creds = (token,"")
    company=input("Company: ")
    lmca_count=input("How many LMCA codes/uses: [0] ")
    if lmca_count == "":
        lmca_count=0
    else:
        lmca_count=int(lmca_count)
    lmcp_count=input("How many LMCP codes/uses: [0] ")
    if lmcp_count == "":
        lmcp_count=0
    else:
        lmcp_count=int(lmcp_count)
    expires_at=input("How many months will the customer be given to start using this code? [3] ")
    if expires_at == "":
        expires_at=3
    else:
        expires_at=int(expires_at)
except KeyboardInterrupt:
    print("\n")
    sys.exit(0)


#if they want some LMCA codes, let's build the stuff
if lmca_count > 0:
    #first create the promo-code-pool
    data = {
        "name": company + " LMCA",
        "active": True,
        "starts_at": datetime.datetime.now().isoformat(),
        "discount_type": "PERCENT_OFF",
        "percent_off": 100,
        "single_use_per_user": True,
        "expires_at": (datetime.datetime.now() + relativedelta(months=+expires_at)).isoformat()
    }
    pool = requests.post(baseURL + "/promo-code-pools", auth=creds, data=data).json()
    if debug:
        print("Here's the pool result")
        pprint(pool)
        print("="*80)
    poolid = pool["id"]

    # then add offers to the pool
    data = {"id":"2y7pg5fp4mrd5"}
    offer = requests.post(baseURL + "/promo-code-pools/" + poolid + "/offers", auth=creds, data=data).json()
    if debug: pprint(offer)

    #then create the promo-code itself
    salt = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
    lmca_code = company + "_" + salt
    data = {
        "code": lmca_code,
        "max_uses": lmca_count,
        "active": True,
        "promo_code_pool_id": poolid
    }
    promocode = requests.post(baseURL + "/promo-codes", auth=creds, data=data).json()
    if debug: pprint(promocode)
    if debug: print("done.")

if lmcp_count > 0:
    if debug: print("Setting up LMCP code pool...")
    data = {
        "name": company + " LMCP",
        "active": True,
        "starts_at": datetime.datetime.now().isoformat(),
        "discount_type": "PERCENT_OFF",
        "percent_off": 100,
        "single_use_per_user": True,
        "expires_at": (datetime.datetime.now() + relativedelta(months=+expires_at)).isoformat()
    }
    pool = requests.post(baseURL + "/promo-code-pools", auth=creds, data=data).json()
    poolid = pool["id"]
    if debug:
        print("Here's the pool result")
        pprint(pool)
        print("="*80)

    # then add offers to the pool
    data = {"id":"2ay3hs3fr6h3s"}
    offer = requests.post(baseURL + "/promo-code-pools/" + poolid + "/offers", auth=creds, data=data).json()
    if debug: pprint(offer)

    #then create the promo-code itself
    salt = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
    lmcp_code = company + "_" + salt
    data = {
        "code": lmcp_code,
        "max_uses": lmcp_count,
        "active": True,
        "promo_code_pool_id": poolid
    }
    promocode = requests.post(baseURL + "/promo-codes", auth=creds, data=data).json()
    if debug: pprint(promocode)
    if debug: print("done.")
if debug: print("=" * 80)

print(f"Here are the codes you requested:")
if lmca_count > 0:
    print(f"{lmca_code} good for {lmca_count} LMCA.")
if lmcp_count > 0:
    print(f"{lmcp_code} good for {lmcp_count} LMCP.")
print(f"""
The codes have an expiration date of {expires_at} months and must be used to register for the course before they expire. Once the codes are used to register, they'll have a year to complete the course.

Let us know if you need anything else!

Thanks,
The Training Team""")
if debug: print("="*80)
