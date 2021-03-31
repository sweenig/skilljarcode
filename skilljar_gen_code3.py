from __future__ import print_function # make this possible to run in python2, but you should be using python3

import sys, subprocess, pkg_resources

required = {'pysimplegui', 'requests', 'python-dateutil'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    print(f"Missing required libraries: {', '.join([str(s) for s in missing])}. Attempting to install...")
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)

import json, requests, random, string, datetime
from os import path,getcwd
from dateutil.relativedelta import relativedelta
from getpass import getpass
from pprint import pprint
import PySimpleGUI as sg

debug = True

### IMPORT CREDS ###
credsfile = "creds.json"

if path.exists(credsfile):
    with open(credsfile) as f: file = json.load(f)
    creds = (file["token"],"")
else:
    print(f"File not found: {credsfile}")
    quit()

baseURL = "https://api.skilljar.com:443/v1"

### Display UI to collect options ###
sg.theme('Material2')

layout = [
    [sg.Text("Company:"),sg.InputText(key="company")],
    [sg.Text("LMCA Code Count:"),sg.InputText(key="lmca_count",default_text="0")],
    [sg.Text("LMCP Code Count:"),sg.InputText(key="lmcp_count",default_text="0")],
    [sg.Text("How many months will the customer be given to start using this code?")],
    [sg.InputText(key="expires_at",default_text="3")],
    [sg.Submit(),sg.Cancel()]
]

window = sg.Window('Skilljar LMCA/LMCP Code Generator', layout)

event, values = window.read()
window.close()

### Process input data on SUBMIT ###
if event == "Submit":
    #if the input variables were not specified on the command line, prompt for them
    company=values["company"].replace(" ","_").replace("\n","").lower()
    lmca_count=int(values["lmca_count"])
    lmcp_count=int(values["lmcp_count"])
    expires_at=int(values["expires_at"])

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
    output = ""
    output += f"Here are the codes you requested:\n"
    if lmca_count > 0:
        output += f"{lmca_code} good for {lmca_count} LMCA.\n"
    if lmcp_count > 0:
        output += f"{lmcp_code} good for {lmcp_count} LMCP.\n"
    output +=f"""
The codes have an expiration date of {expires_at} months and must be used to register for the course before they expire. Once the codes are used to register, they'll have a year to complete the course.

Let us know if you need anything else!

Thanks,
The Training Team\n"""

    layout = [
        [sg.Multiline(output,size=(150,50))],
        [sg.Cancel("Done")]
    ]

    window = sg.Window('Skilljar LMCA/LMCP Code Generator', layout)

    event, values = window.read()
    window.close()
