#!/usr/bin/env bash
#
# Copyright (c) 2019 m-ll. All Rights Reserved.
#
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.
#
# 2b13c8312f53d4b9202b6c8c0f0e790d10044f9a00d8bab3edf3cd287457c979
# 29c355784a3921aa290371da87bce9c1617b8584ca6ac6fb17fb37ba4a07d191
#

usage()
{
    echo "Usage: $0 [-h] [-d {none|hash|name|all}] -i /input/pathfile -r /reference/path -s /store/path"
    echo '  -h: help me'
    echo '  -d: display found files'
    echo '  -i: input pathfile'
    echo '  -r: reference path (the path where the images should be)'
    echo '  -s: store path (the path where the not found images will be copied)'
    exit 2
}

# The file with all hashes
INPUT_PATHFILE=
# The reference path
REFERENCE_PATH=
# The store path
STORE_PATH=
# Display found results
FOUND_RESULTS='name'

# Process all the parameters
while getopts ":hd:i:r:s:" option; do
	case "${option}" in
		i) INPUT_PATHFILE=${OPTARG} ;;
		r) REFERENCE_PATH=${OPTARG} ;;
		s) STORE_PATH=${OPTARG} ;;
		d) FOUND_RESULTS=${OPTARG} ;;
		h|*) usage ;;
	esac
done
shift $((OPTIND-1))

# Check all the mandatory parameters

if [[ -z "$INPUT_PATHFILE" || ! -f "$INPUT_PATHFILE" ]]; then
    echo "input pathfile is empty or doesn't exist: $INPUT_PATHFILE"
    usage
fi
if [[ -z "$REFERENCE_PATH" || ! -d "$REFERENCE_PATH" ]]; then
    echo "reference path is empty or doesn't exist: $REFERENCE_PATH"
    usage
fi
if [[ -n "$STORE_PATH" && ! -d "$STORE_PATH" ]]; then
    echo "store path doesn't exist: $STORE_PATH"
    usage
fi
if [[ x"$FOUND_RESULTS" != x'none' && x"$FOUND_RESULTS" != x'hash' && x"$FOUND_RESULTS" != x'name' && x"$FOUND_RESULTS" != x'all' ]]; then
    echo 'display found files value is wrong: '$FOUND_RESULTS
    usage
fi

#---

output_by_hash=
output_by_name=

# Check the file if its hash corresponds to a hash inside input file which contains all hashes (generated by ./create-create.sh)
check_file_hash() 
{
	file="$1"
	
	hash=`sha256sum "$file" | awk '{ print $1 }'`
	result=`grep $hash "$INPUT_PATHFILE"`

	if [[ x"$result" == x ]]; then
		output_by_hash=
		return 0
	fi
	                               # remove the hash            # remove the first spaces
	output_by_hash=`echo "$result" | sed -e 's/^[a-zA-Z0-9]*//' | sed -e 's/^[[:space:]]*//'`
	return 1
}

# Try to find files with the "same" name inside ~/Images
check_file_name()
{
	pathfile="$1"
	
	filename=${pathfile##*/}
	name=${filename%.*}
	
	result=`find "$REFERENCE_PATH" -iname "*$name*"`
	if [[ x"$result" == x ]]; then
		output_by_name=
		return 0
	fi
	
	output_by_name="$result"
	return 1
}

# https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux#20983251
green=`tput setaf 2`
yellow=`tput setaf 3`
grey=`tput setaf 8`
reset=`tput sgr0`
clear=`tput ed`

# Go through every files inside the current directory
find "$(pwd)" -type f -print0 | sort -z | while IFS= read -r -d '' file; do
	filename=`basename "$file"`
	# remove file from What's App
	if [[ "$file" =~ [wW][aA] ]]; then
		continue
	fi

	echo -ne "${grey}current: $file\r${reset}"

	check_file_hash "$file"
	found=$?
	if [[ $found -ne 0 ]]; then
		if [[ $FOUND_RESULTS == 'hash' || $FOUND_RESULTS == 'all' ]]; then
			# hash may appear multiple times inside input hash file, so display all the corresponding files
			printf "%s\n" "$output_by_hash" | while IFS= read -r line; do
				echo "${clear}${green}FOUND BY HASH: $file -> $line${reset}"
			done
		fi
		continue
	fi
	
	check_file_name "$file"
	found=$?
	if [[ $found -ne 0 ]]; then
		if [[ $FOUND_RESULTS == 'name' || $FOUND_RESULTS == 'all' ]]; then
			# The name may appear multiple times, so display all the corresponding files
			printf "%s\n" "$output_by_name" | while IFS= read -r line; do
				echo "${clear}${yellow}FOUND BY NAME (check it!): $file -> $line${reset}"
			done
		fi
		continue
	fi
	
	if [[ -z "$STORE_PATH" ]]; then
		echo "${clear}NOT FOUND : $file"
	else
		suffix="${file#$(pwd)/}"	# Remove the start path to get the suffix
		suffix="${suffix#/}"		# Remove the first '/' if any
		to="$STORE_PATH/$suffix"
		echo "${clear}NOT FOUND : $file ($suffix) -> $to"
		mkdir -p "$(dirname "$to")" && cp "$file" "$to"
	fi
done

echo "${clear}"
