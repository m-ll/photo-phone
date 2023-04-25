#!/usr/bin/env python3
#
# Copyright (c) 2023 m-ll. All Rights Reserved.
#
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.
#
# 2b13c8312f53d4b9202b6c8c0f0e790d10044f9a00d8bab3edf3cd287457c979
# 29c355784a3921aa290371da87bce9c1617b8584ca6ac6fb17fb37ba4a07d191
#

import argparse
import getpass
from pathlib import Path
import platform
import subprocess

from colorama import init, Fore, Back, Style
init( autoreset=True )

os = platform.system().lower()

#--- Windows (doesn't work... can't access the content in cli...)

# if os == 'windows':
#     parser = argparse.ArgumentParser( description='"Add Network LOCATION" on this PC.' )
#     args = parser.parse_args()

#     print( Fore.GREEN + 'In explorer:' )
#     print( Fore.GREEN + '- right-click on "This PC"' )
#     print( Fore.GREEN + '- "Add Network LOCATION" ' + Fore.RED + '(and NOT "connect network drive")' )

#--- WSL

if os == 'linux':
    parser = argparse.ArgumentParser( description='Map ftp to drive.' )
    parser.add_argument( '-i', '--ip', help='The ftp ip', required=True )
    parser.add_argument( '-p', '--port', type=int, help='The port', required=True )
    parser.add_argument( '-u', '--user', help='The user', required=True )
    args = parser.parse_args()

    password = getpass.getpass()

    parameters = [
        f'{args.user}:{password}@{args.ip}:{args.port}',
        f'/mnt/phone',
    ]

    cmd = ['curlftpfs'] + parameters
    # print( cmd )
    result = subprocess.run( cmd )

