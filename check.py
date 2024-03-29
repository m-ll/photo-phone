#!/usr/bin/env python
#
# Copyright (c) 2018-23 m-ll. All Rights Reserved.
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
parser.add_argument( '-f', '--from-path', nargs='+', help='From this folder inside input' )
parser.add_argument( '-a', '--input-hash-file', type=FilePath, help='Input pathfile containing all hashes', required=True )
parser.add_argument( '-r', '--reference-path', type=DirectoryPath, help='Reference folder which represents the NAS', required=True )
parser.add_argument( '-d', '--display-result', type=eDisplayResult, choices=list( eDisplayResult ), default=eDisplayResult.kName, help='Display found files' )
parser.add_argument( '-s', '--store-path', type=DirectoryPath, help='Intermediate folder to store files which are not already on the NAS' )
args = parser.parse_args()

def GetNotFoundHashLogFile():
    global args
    not_found_hash_pathfile = Path( args.input_hash_file ).parent / 'not-found.hash'
    return not_found_hash_pathfile

#---

def AddHashToNotFoundHashLogFile( iPathFile: Path, iHash: str ):
    with GetNotFoundHashLogFile().open( 'a' ) as f:
        f.write( f'{iHash}  {iPathFile}\n' )

def IsUnwantedHash( iHash: str ):
    unwanted_hashes_5Mo = [
        # Mic
        # - Doc
        'a95ce50b260dde66d6df9732d21b02272ad4f6b09acee30a34efdcc87c87b556', # 5Mo
        'aa6e0e5d658da792835cb7618aafc0d288d8dcf07434d95c55e2269d110ecc3e', # 5Mo
        'a346dcc9a38cec0d86bbbd6889cc319b9de37e051579f2a204db41fb1e266f06', # 5Mo
        'b1f06c55a807ad52a9db9e721b819f5c1a29d262d0fca190306b3b51261d6988', # 5Mo
        '43d632d79d9c610d7556a5b2ff07a294b2c69bf0a3a0ed4d67fd6bdeb79c785b', # 5Mo
        '7d37db4c6fb75822c4d2df1fd6d3825fd03e3f4e62e6ca153fa7e96a3d51030a', # 1Mo
        '7c4c0973248eecccf998110fdd8443f1b0b8bdefd267bf467e60e430cc5f7922', # 1Mo
        '240299ec03d08d568cdbd29ba0513ffe770aed0dd88486231c668fdfe24b12e8', # 1Mo
        '2ed10b9f5bdb27c2cf1c26e118254d91d8a290a01cf113944bc5991ab68486c6', # 1Mo
        '2aee8e2aa4fe519b1b2ae8b91ad8a0b7af427fec429214451cca84b99f53d561', # 1Mo

        # Maman
        # - Docteur
        'e0b1417f228371542f6d8e63b8ea201fd5531eb7a9cd0deee1b1bc7428a30eac',
        '29353bfbaa53973544f9cedaa1f3b4200b800a32b22d9c0f9b1928bf5945ed24',
        '1b6b10ada09f974deb8736affa41866ab3ea2e35128f29bf1d82a03fde583ad9',
        'ddeb0acbab19dc6420867342d3f14ffccfdc32cf5ce5e77eac97cc7ffaf2dea5',
        'f942f682a06d15c6347a0fee60f49e6a9a2e96e7b3b6eb32075ae4ade573b498',
        ]

    unwanted_hashes_1Mo = [
    ]

    return iHash in unwanted_hashes_5Mo + unwanted_hashes_1Mo

def CheckFileByHash( iPathFile, iHashes ):
    sha = hashlib.sha256()
    # The hash computation must be the same as in create-hash.py
    chunk_size = 1*1024*1024 # 1Mo
    # chunk_size = 5*1024*1024 # 5Mo

    # Read and update the hash by chunk (to not load all the file in memory)
    with iPathFile.open( "rb" ) as f:
        chunk = f.read( chunk_size )
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
        # Check if it is wanted to not have it in nas (not all images in phone should be on nas)
        if IsUnwantedHash( current_hash ):
            return current_hash, []
        # Otherwise, hash is really missing and should be added
        else:
            AddHashToNotFoundHashLogFile( iPathFile, current_hash )
            return '', []

    # The hash is already in the hash list, so try to get the corresponding file(s)
    # Note: a hash may appear multiple times in the hash list, some files need to be cleaned
    corresponding_pathfiles = []
    for found_hash_line in found_hash_lines:
        corresponding_pathfiles.append( found_hash_line.lstrip( "0123456789abcdef " ) )

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

# https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
def HumanSize( iSize ):
    for unit in ["o", "Ko", "Mo", "Go", "To", "Po", "Eo", "Zo"]:
        if abs(iSize) < 1000.0:
            return f"{iSize:3.1f}{unit}"
        iSize /= 1000.0

    return f"{iSize:.1f}Yo"

def CheckFile( iCommonSearchPath, iPathfile, iHashes, iReferencePath, iStorePath, iDisplayResult ):
    # remove file from What's App
    if iPathfile.name.lower().find( "wa" ) >= 0:
        print( Fore.YELLOW + f"don't take whatsapp: {iPathfile}" + Style.CLEAR )
        return
    # remove files in .thumbnails folder
    if iPathfile.match( '*/.thumbnails/*' ):
        print( Fore.YELLOW + f"don't take .thumbnails: {iPathfile}" + Style.CLEAR )
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
        print( Fore.RED + f"NOT FOUND: {iPathfile} [{HumanSize( iPathfile.stat().st_size )}]" + Style.CLEAR )
    else:
        suffix = iPathfile.relative_to( iCommonSearchPath )
        move_to_path = iStorePath / suffix
        print( Fore.RED + f"NOT FOUND: {iPathfile} ({suffix}) [{HumanSize( iPathfile.stat().st_size )}] -> {move_to_path}" + Style.CLEAR )

        move_to_path.parent.mkdir( parents=True, exist_ok=True )
        if move_to_path.exists():
            print( f'... But already exists in store path ... {move_to_path}' )
        else:
            shutil.copy( iPathfile, move_to_path )

#---
#---
#---

# Store all the hashes in memory to not read the file each time
hashes = []
with Path( args.input_hash_file ).open( "r" ) as f:
    hashes = [line.strip() for line in f]

# Empty the file with all not found hashes
with GetNotFoundHashLogFile().open( 'w' ) as f:
    pass

# Find the most relevant common path of all input paths
common_search_path = Path( os.path.commonpath( args.input_search_paths ) )

# Check every files inside all input paths
for search_path in args.input_search_paths:
    pathfiles = Path( search_path ).rglob( "*" )
    pathfiles_sorted_by_name = sorted( pathfiles, key=lambda s: str(s).casefold() )

    from_path = None
    if args.from_path is not None:
        from_path = Path( search_path ).joinpath( '/'.join( args.from_path ) )

    for current_pathfile in pathfiles_sorted_by_name:
        if current_pathfile.is_file():
            # print( current_pathfile, end='' )

            # For all files which are before 'from_path', skip them
            if from_path and str(current_pathfile).casefold() < str(from_path).casefold():
                # print()
                continue

            # print( Fore.GREEN + '... processed' )
            CheckFile( common_search_path, current_pathfile, hashes, Path( args.reference_path ), args.store_path, args.display_result )

print()
