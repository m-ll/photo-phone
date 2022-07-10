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
Style.CLEAR = "\033[K" #This the code to clear the line from the cursor

#---

class eDisplayResult( Enum ):
    kNone = 'none'
    kHash = 'hash'
    kName = 'name'
    kAll = 'all'

    def __str__( self ):
        return self.value

def FilePath( iPath ):
    if Path( iPath ).is_file():
        return iPath
    else:
        raise argparse.ArgumentTypeError( f"readable_dir: {iPath} is not a valid path" )

def DirectoryPath( iPath ):
    if Path( iPath ).is_dir():
        return iPath
    else:
        raise argparse.ArgumentTypeError( f"readable_dir: {iPath} is not a valid path" )

parser = argparse.ArgumentParser( description='Check missing images/videos in NAS.' )
parser.add_argument( '-i', '--input-search-paths', nargs='+', type=DirectoryPath, help='Source folders to search files which are not in NAS', required=True )
parser.add_argument( '-a', '--input-hash-file', type=FilePath, help='Input pathfile containing all hashes', required=True )
parser.add_argument( '-r', '--reference-path', type=DirectoryPath, help='Reference folder which represents the NAS', required=True )
parser.add_argument( '-d', '--display-result', type=eDisplayResult, choices=list( eDisplayResult ), default=eDisplayResult.kName, help='Display found files' )
parser.add_argument( '-s', '--store-path', type=DirectoryPath, help='Intermediate folder to store files which are not already on the NAS' )
args = parser.parse_args()

#---

def CheckFileByHash( iPathFile, iHashes ):
    sha = hashlib.sha256()
    chunk_size = 1024*1024 # 1Mo

    # Read and update the hash by chunk (to not load all the file in memory)
    with iPathFile.open( "rb" ) as f:
        while True:
            chunk = f.read( chunk_size )
            if not chunk:
                break
            sha.update(chunk)

    # Get the hash
    current_hash = sha.hexdigest()

    # Try to find the hash inside input hash list
    found_hash_lines = []
    for hash_line in iHashes:
        if current_hash in hash_line:
            found_hash_lines.append( hash_line )

    # If the hash is not inside the hash list
    if not found_hash_lines:
        return '', []

    # The hash is already in the hash list, so try to get the corresponding file(s)
    # Note: a hash may appear multiple times in the hash list, some files need to be cleaned
    corresponding_pathfiles = []
    for found_hash_line in found_hash_lines:
        corresponding_pathfiles.append( found_hash_line.strip( "0123456789abcdef " ) )

    # Return the hash and the corresponding file(s)
    return current_hash, corresponding_pathfiles

def CheckFileByName( iPathFile, iReferencePath ):
    # Get the name without the extension of the file to use it like a pattern
    filestem = iPathFile.stem

    # Try to find a file in the reference path which contains the name of the current file
    # Note: use 'find' instead of rglob to be sure that's case-INsensitve (with '-iname')
    process = subprocess.run( [ "find", iReferencePath, "-iname", f"*{filestem}*" ], capture_output=True )
    # print( process )
    # if there are no matching files
    if process.returncode != 0:
        return []

    # Otherwise, get all the files as a list
    return process.stdout.splitlines() # stdout is a binary string

def CheckFile( iCommonSearchPath, iPathfile, iHashes, iReferencePath, iStorePath, iDisplayResult ):
    # remove file from What's App
    if iPathfile.name.lower().find( "wa" ) >= 0:
        return

    print( Style.DIM + f"Current file: {iPathfile}" + Style.CLEAR, end='\r' )

    hash, pathfiles = CheckFileByHash( iPathfile, iHashes )
    if hash:
        if iDisplayResult in [ eDisplayResult.kAll, eDisplayResult.kHash ]:
            for pathfile in pathfiles:
                print( Fore.GREEN + f"FOUND BY HASH: {iPathfile} -> {pathfile}" + Style.CLEAR )
        return

    pathfiles = CheckFileByName( iPathfile, iReferencePath )
    if pathfiles:
        if iDisplayResult in [ eDisplayResult.kAll, eDisplayResult.kName ]:
            for pathfile in pathfiles:
                print( Fore.YELLOW + f"FOUND BY NAME (check it!): {iPathfile} -> {pathfile}" + Style.CLEAR )
        return

    if iStorePath is None:
        print( Fore.RED + f"NOT FOUND: {iPathfile}" + Style.CLEAR )
    else:
        suffix = iPathfile.relative_to( iCommonSearchPath )
        move_to_path = iStorePath / suffix
        print( Fore.RED + f"NOT FOUND: {iPathfile} ({suffix}) -> {move_to_path}" + Style.CLEAR )

        move_to_path.parent.mkdir( parents=True, exist_ok=True )
        shutil.copy( iPathfile, move_to_path )

#---
#---
#---

# Store all the hashes in memory to not read the file each time
hashes = []
with Path( args.input_hash_file ).open( "r" ) as f:
    hashes = [line.strip() for line in f]

# Find the most relevant common path of all input paths
common_search_path = Path( os.path.commonpath( args.input_search_paths ) )

# Check every files inside all input paths
for search_path in args.input_search_paths:
    for current_pathfile in Path( search_path ).rglob( "*" ):
        if current_pathfile.is_file():
            CheckFile( common_search_path, current_pathfile, hashes, Path( args.reference_path ), args.store_path, args.display_result )

print()
