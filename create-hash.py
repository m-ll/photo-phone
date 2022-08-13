#!/usr/bin/env python3
#
# Copyright (c) 2018-19 m-ll. All Rights Reserved.
#
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.
#
# 2b13c8312f53d4b9202b6c8c0f0e790d10044f9a00d8bab3edf3cd287457c979
# 29c355784a3921aa290371da87bce9c1617b8584ca6ac6fb17fb37ba4a07d191
#

import argparse
from enum import Enum
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys

from colorama import init, Fore, Back, Style
init( autoreset=True )

#---

def DirectoryPath( iPath ):
    if Path( iPath ).is_dir():
        return Path( iPath )
    else:
        raise argparse.ArgumentTypeError( f"readable_dir: {iPath} is not a valid path" )

parser = argparse.ArgumentParser( description='Create all hash for image/video files.' )
parser.add_argument( '-i', '--input-paths', nargs='+', type=DirectoryPath, help='Source folders to search files', required=True )
parser.add_argument( '-o', '--output-file', type=Path, help='The output file with all hashes', required=True )
args = parser.parse_args()

#---

def CreateHash( iPathFile ):
    sha = hashlib.sha256()
    # The hash computation must be the same as in check.py
    chunk_size = 5*1024*1024 # 5Mo

    # Create the hash with the first chunk (to reduce time for big videos)
    with iPathFile.open( "rb" ) as f:
        chunk = f.read( chunk_size )
        sha.update(chunk)

    # Get the hash
    current_hash = sha.hexdigest()

    return current_hash

#---
#---
#---

output_file = args.output_file.resolve()
print( Fore.GREEN + f'Output: {output_file}' )

with output_file.open( "w" ) as f:

    # Check every files inside all input paths
    for input_path in args.input_paths:
        input_path = input_path.resolve()
        print( Fore.GREEN + f'Input: {input_path}' )

        for current_pathfile in input_path.rglob( "*" ):
            if current_pathfile.is_file():
                hash = CreateHash( current_pathfile )
                print( f'{hash}  {current_pathfile.resolve()}', file=f )
