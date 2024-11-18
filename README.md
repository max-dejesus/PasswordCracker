# Cracking SHA-1 Password Cracker

This repo implements a variety of algorithms to process and crack a list of passwords encoded with SHA-1. It is written in Pythons
using hashlib, itertools and multiprocessing to paralellize tasks.

Passwords can either be containing only digits (up to ten), only words (one to three words), and a combination of words and number (one to two words, up to five digits). ALl are lowercase and digits 0-9 with no special characters.

## Disclaimer

I ran this with the WSL layer in Windows on a Debian distrubution of Linux. Issues may occur when running on Windows.
