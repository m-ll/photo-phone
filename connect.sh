#!/usr/bin/env bash
#
# Copyright (c) 2020 m-ll. All Rights Reserved.
#
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.
#
# 2b13c8312f53d4b9202b6c8c0f0e790d10044f9a00d8bab3edf3cd287457c979
# 29c355784a3921aa290371da87bce9c1617b8584ca6ac6fb17fb37ba4a07d191
#

usage()
{
    echo "Usage: $0 [-h] user ftp:port"
    echo '  -h: help me'
    exit 2
}

if [[ $# -ne 2 ]]; then
    usage
fi

USER=$1
FTP=$2
read -sp 'Password: ' PASSWORD
echo

if [[ -z "$FTP" ]]; then
    echo "ftp address is empty !"
    usage
fi
if [[ -z "$USER" ]]; then
    echo "user is empty !"
    usage
fi
if [[ -z "$PASSWORD" ]]; then
    echo "password is empty !"
    exit 10
fi

curlftpfs $USER:$PASSWORD@$FTP /mnt/phone/
if [[ $? -ne 0 ]]; then
    echo "curlftpfs can't mount"
    exit 20
fi
