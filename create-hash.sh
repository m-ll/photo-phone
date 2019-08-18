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
    echo "Usage: $0 [-h] -i /input/path -o /output/pathfile"
    echo '  -h: help me'
    echo '  -i: input path'
    echo '  -o: output pathfile'
    exit 2
}

# The path to compute hash
INPUT_PATH=
# The output path file
OUTPUT_PATHFILE=

# Process all the parameters
while getopts ":hi:o:" option; do
    case "${option}" in
        i) INPUT_PATH=${OPTARG} ;;
        o) OUTPUT_PATHFILE=${OPTARG} ;;
        h|*) usage ;;
    esac
done
shift $((OPTIND-1))

# Check all the mandatory parameters

if [[ -z $INPUT_PATH ]]; then
    echo 'input path is empty !'
    usage
fi
if [[ -z $OUTPUT_PATHFILE ]]; then
    echo 'output path is empty !'
    usage
fi

# Display all parameters containing a path and check its existence

echo 'input path: '$INPUT_PATH
if [[ ! -d "$INPUT_PATH" ]]; then
    echo 'The input path does not exist !'
    exit 5
fi

echo 'output path: '$OUTPUT_PATHFILE

#---

find "$INPUT_PATH" -type f -exec sha256sum "{}" \; > "$OUTPUT_PATHFILE"


