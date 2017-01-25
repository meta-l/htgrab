#!/usr/bin/python2

# Grabs http banners from nmap (use gnmap file), stash in files, grep files for logins
# Author Ian Simons, 17/01/17
# Licence: WTFPL - wtfpl.net
# Version 0.1 - Loops the curl command. Woop-di-fucking-do.
# Version 0.2 - The barely working one. Shoddy as shit, honest.
# Version 0.3 - Error reporting, tidied console/file output. Still shoddy, but kinda functional
# Version 0.4 - Now works for all ports, can set SSL with -s switch. Doesn't suck as much.

# TO DO: Guess could set search pattern (currently 'login') for greater flex
# Not sure it would add much. Would like to keep sys.argv as clean as preferably

import subprocess
import re
import sys
import socket
import argparse
import time
from os.path import isfile

__version__ = "0.4"

clear = "\x1b[0m"
red = "\x1b[1;31m"
green = "\x1b[1;32m"
cyan = "\x1b[1;36m"
yellow = "\x1b[1;33m"



# Oblig banner
def banner():
    print"""\x1b[1;32m
@@@  @@@  @@@@@@@   @@@@@@@@  @@@@@@@    @@@@@@   @@@@@@@   
@@@  @@@  @@@@@@@  @@@@@@@@@  @@@@@@@@  @@@@@@@@  @@@@@@@@  
@@!  @@@    @@!    !@@        @@!  @@@  @@!  @@@  @@!  @@@  
!@!  @!@    !@!    !@!        !@!  @!@  !@!  @!@  !@   @!@  
@!@!@!@!    @!!    !@! @!@!@  @!@!!@!   @!@!@!@!  @!@!@!@   
!!!@!!!!    !!!    !!! !!@!!  !!@!@!    !!!@!!!!  !!!@!!!!  
!!:  !!!    !!:    :!!   !!:  !!: :!!   !!:  !!!  !!:  !!!  
:!:  !:!    :!:    :!:   !::  :!:  !:!  :!:  !:!  :!:  !:!  
::   :::     ::     ::: ::::  ::   :::  ::   :::   :: ::::  
 :   : :     :      :: :: :    :   : :   :   : :  :: : ::   
-----+++++----- Grab dem httpeas -----+++++----- Ver: %s

\x1b[0m""" % __version__



# Set the command up for subprocess. Curl timeout currently set to 4000ms
def setcmd(ssl, ip_address):
    global cmd
    if not ssl:
        cmd = ["curl", "-m", "4", ip_address]
        return cmd
    if ssl:
        ip_address = "https://" + ip_address
        cmd = ["curl", "-m", "4", "-k", ip_address]
        return cmd



# Runs a check to ensure an actual IP address is being passed
def validate_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        print ("%s{!} Stripped line \"%s\" submitted to function. \"%s\" is not an IP address.%s" % (red,ip,ip,clear))
        return False



def main():
    banner()

# Set time var to tack onto output file
    timestring = time.strftime("%H%M%S_%d-%m-%Y")

# Set output file name
    outfile = "HTGrab_" + timestring + ".txt"

    parser = argparse.ArgumentParser(description=green + "Grab HTTP/S and checks for login pages" + clear)
    parser.add_argument("-p", help="Port to query, 80 or 443 only atm", required=True)
    parser.add_argument("-f", help="Gnmap file", required=True)
    parser.add_argument("-v", help="Some verbosity", action="store_true")
    parser.add_argument("-vv", help="MAXIMUM SPID... verbosity", action="store_true")
    parser.add_argument("-q", help="Quench errors. Recommend -v if used.", action="store_true")
    parser.add_argument("-s", help="Perform insecure SSL connection", action="store_true")
    args = parser.parse_args()

    infile = open(args.f,"r")

# Open gnmap input file and loop, trigger curl to grab HTTP
    for line in infile:
        if re.search(args.p,line):
            ip = line.split(' ')[1]

            if validate_ip(ip):
                setcmd(args.s,ip)
            else:
                continue
            try:
                proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                stdout_data, stderr_data = proc.communicate()

# Tell you which IP is current target. At least shows that something is happening
                if args.v:
                    print("%s{+}Running: %s%s " % (cyan,cmd,clear))

# Max Verbosity, will show curl progress per IP
                if args.vv:
                    print("%s{+}Running: %s%s " % (cyan,cmd,clear))
                    print stderr_data

# Simple check if 'login' exists in HTML, stash IP.
                if "login" in stdout_data:
                    targetfile = open(outfile,"a")
                    targetfile.write(ip)
                    targetfile.write("\n")

# Quench the ol' errors.
                if not args.q:
                    if proc.returncode != 0:
                        raise RuntimeError("%r failed, stderr:\n%r" % (cmd, stderr_data))

            except Exception as e:
                print ("%s{!} Process error: %s%s" % (red,e,clear))
                continue

    if isfile(outfile):
        print ("%s\n{+} Complete. Check %s%s%s for details.%s" % (green,yellow,outfile,green,clear))
    else:
        print ("%s\n{+} Complete. No login pages found.%s" % (green,clear))

if __name__=="__main__":
    main()
