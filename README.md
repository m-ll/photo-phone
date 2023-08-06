# photo-phone

Check and list photos to be copied from phone to PC

# Initialization

- `git clone <repo>`
- `cd <repo>`
- `py -m venv .venv` *(.venv is the directory name)*
- `.\.venv\Scripts\activate` *(on windows)*
- *...we are now in the virtual environment, so all pip commands will apply to the .venv...*
- `py -m pip install -r requirements.txt`

*[common venv commands help](https://gist.github.com/m-ll/f2d92237b9b1aa47c0b8c79d880b8e56)*

# Usage

### Common

- `./create-hash.py -i /mnt/f/Photo -o /mnt/f/photo.5Mo.hash`
- `./connect.py -i 192.168.1.xx -p 2221 -u Mike`
- `./check.py -i /mnt/phone/.../DCIM -a /mnt/f/photo.5Mo.hash -r /mnt/f/Photo -s /mnt/f/ARANGER`

### Recompute all hash of reference files

```
(.venv) .>./create-hash.py -h

usage: create-hash.py [-h] -i INPUT_PATHS [INPUT_PATHS ...] -o OUTPUT_FILE

Create all hash for image/video files.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_PATHS [INPUT_PATHS ...], --input-paths INPUT_PATHS [INPUT_PATHS ...]
                        Source folders to search files
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        The output file with all hashes
```

### Connect to the ftp server on the phone

```
(.venv) .>./connect.py -h

usage: connect.py [-h] -i IP -p PORT -u USER

Map ftp to drive.

optional arguments:
  -h, --help            show this help message and exit
  -i IP, --ip IP        The ftp ip
  -p PORT, --port PORT  The port
  -u USER, --user USER  The user
```

### Check and download all missing files

```
(.venv) .>./check.py -h

usage: check.py [-h] -i INPUT_SEARCH_PATHS [INPUT_SEARCH_PATHS ...] [-f FROM_PATH [FROM_PATH ...]] -a INPUT_HASH_FILE -r REFERENCE_PATH [-d {none,hash,name,all}] [-s STORE_PATH]

Check missing images/videos in NAS.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_SEARCH_PATHS [INPUT_SEARCH_PATHS ...], --input-search-paths INPUT_SEARCH_PATHS [INPUT_SEARCH_PATHS ...]
                        Source folders to search files which are not in NAS
  -f FROM_PATH [FROM_PATH ...], --from-path FROM_PATH [FROM_PATH ...]
                        From this folder inside input
  -a INPUT_HASH_FILE, --input-hash-file INPUT_HASH_FILE
                        Input pathfile containing all hashes
  -r REFERENCE_PATH, --reference-path REFERENCE_PATH
                        Reference folder which represents the NAS
  -d {none,hash,name,all}, --display-result {none,hash,name,all}
                        Display found files
  -s STORE_PATH, --store-path STORE_PATH
                        Intermediate folder to store files which are not already on the NAS
```
