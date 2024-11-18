import signal
import sys
import multiprocessing
import os
from time import perf_counter_ns as pcn
from itertools import product, islice
from hashlib import sha1

class Cracker():
    passwords = {}
    found_passwords = multiprocessing.Manager().list()
    num_processes = 0
    hashlist = []
    time_created = 0

    # Constructor
    def __init__(self):
        self.passwords = self._init_pwds()
        self.num_processes = os.cpu_count()
        self.time_created = pcn()
        self.hashlist = list(self.passwords.values())
        signal.signal(signal.SIGINT, self.signal_handler)


    # Custom signal handling to terminate multiprocesses elegantly and return currently found passwords
    def signal_handler(self, signal, frame):
        print("Ctrl+C pressed. Terminating execution...")
        exit_time = pcn() - self.time_created

        print(f"Time elapsed = {exit_time / pow(10,9)}s")
        print(self.found_passwords)
        sys.exit(0)

    # Function taking in a product() iterator that is split by designated chunk size and served as requested
    def split_iter(self, product_iter, chunksize):
        while True:
            chunk = list(islice(product_iter, chunksize))
            if not chunk: break
            yield iter(chunk)

    # Initalize the password dict
    def _init_pwds(self):
        pwd_file = open("passwords.txt", "r")
        with pwd_file:
            p = pwd_file.readlines()
            for line in p:
                p[p.index(line)] = line.replace("\n", "")
        pwd_file.close()
        pd = {}
        for pwd in p:
            index, hash = pwd.split(" ")
            pd[index] = hash
        return pd
    
    # Get a SHA-1 hash from a str
    def _hash(self, word):
        return sha1(word.encode('utf-8')).hexdigest()
    
    # Function to create a number hash and compare to hash list
    # Takes in tuple of the permutated numbers
    def _numbers_rule(self, number):
        if not self.hashlist: return
        pw = ''.join(map(str, number))
        print(f'\rtesting {pw}...', end='')
        pw_hash = self._hash(pw)
        if pw_hash in self.hashlist:
            self.hashlist.remove(pw_hash)
            self.found_passwords.append(f'{pw_hash}:{pw}')
    
    # Function to create a word hash and compare to hash list
    def _words_rule(self, word):
        if not self.hashlist: return
        print(f"\rtesting {word}...", end='')
        pw_hash = self._hash(word)
        if pw_hash in self.hashlist:
            self.hashlist.remove(pw_hash)
            self.found_passwords.append(f'{pw_hash}:{word}')
        return
    # Overload
    def _words_rule_tuple(self, perm: tuple):
        if not self.hashlist: return
        print(f"\rtesting {perm[0] + perm[1]}...", end='')
        pw_hash = self._hash(perm[0] + perm[1])
        if pw_hash in self.hashlist:
            self.hashlist.remove(pw_hash)
            self.found_passwords.append(f'{pw_hash}:{perm[0]+perm[1]}')
        return

    # Function to create a word + numbers hash for all number combos up to 5 digits and compare to hashlist
    def _word_numbers_rule(self, word):
        if not self.hashlist: return
        for n in range(1,6,1):
            num_perms = product(range(10), repeat=n)
            for perm in num_perms:
                nums = ''.join(map(str,perm))
                pw = word + nums
                print(f'\rtesting {pw}...', end='')
                pw_hash = self._hash(pw)
                if pw_hash in self.hashlist:
                    self.hashlist.remove(pw_hash)
                    self.found_passwords.append(f'{pw_hash}:{pw}')
        return
    # Overload(?) to limit to four digits/word for two word combinations
    def _words_numbers_rule(self, word):
        if not self.hashlist: return
        for n in range(1,3,1):
            num_perms = product(range(10), repeat=n)
            for perm in num_perms:
                nums = ''.join(map(str,perm))
                pw = word + nums
                print(f'\rtesting {pw}...', end='')
                pw_hash = self._hash(pw)
                if pw_hash in self.hashlist:
                    self.hashlist.remove(pw_hash)
                    self.found_passwords.append(f'{pw_hash}:{pw}')
        return

    # Executes cracking algorithm
    def crack(self):
        # Multi-threaded number rule, digit passwords up to length 10 - USE THIS
        # SUCCESS
        print("Numbers rule:")
        ts = pcn()
        for n in range(10,0,-1):
            if n < 5:
                for perm in product(range(10),repeat=n):
                    self._numbers_rule(perm)
            else:
                with multiprocessing.Pool(self.num_processes) as pool:
                    for chunk in self.split_iter(product(range(10), repeat=n), chunksize=90000000):
                        pool.map(self._numbers_rule, chunk, chunksize=999999)
                    pool.close()
                    pool.join()
        te = pcn()
        # Reports time for execution
        time = (te - ts) / pow(10,9)
        print(f"Time to complete rule: {time} s")

        
        # Single-threaded word rule, 1 word passwords - USE THIS
        # SUCCESS
        print("One word rule:")
        ts = pcn()
        with open('dictionary.txt', 'r', encoding='utf-8-sig') as df:
            for line in df:
                line = line.rstrip()
                self._words_rule(line)
        te = pcn()
        # Reports time for execution
        time = (te - ts) / pow(10,9)
        print(f"Time to complete rule: {time} s")


        # Multithreaded word rule, 2 word passwords - USE THIS
        # SUCCESS
        print("2 word rule:")
        ts = pcn()
        with open('dictionary_two_words.txt', 'r', encoding='utf-8-sig') as df:
            with multiprocessing.Pool(self.num_processes) as pool:
                pool.map(self._words_rule, df.read().splitlines())
                pool.close()
                pool.join()
        te = pcn()
        # Reports time for execution
        time = (te - ts) / pow(10,9)
        print(f"Time to complete rule: {time} s")


        # Multi-threaded word + numbers rule, 1 word passwords - USE THIS
        # SUCCESS
        print("1 word + numbers rule:")
        ts = pcn()
        with open('dictionary.txt', 'r', encoding='utf-8-sig') as df:
            with multiprocessing.Pool(self.num_processes) as pool:
                pool.map(self._word_numbers_rule, df.read().splitlines())
                pool.close()
                pool.join()
        te = pcn()
        # Reports time for execution
        time = (te - ts) / pow(10,9)
        print(f"Time to complete rule: {time} s")


        # Multi-threaded word + numbers rule, 2 word passwords
        # SUCCESS
        print("2 words + numbers rule:")
        ts = pcn()
        with open('dictionary_two_words.txt', 'r', encoding='utf-8-sig') as df:
            with multiprocessing.Pool(self.num_processes) as pool:
                for chunk in self.split_iter(df.read().splitlines(), chunksize=15000000):
                    pool.map(self._words_numbers_rule, chunk)
                pool.close()
                pool.join()
        te = pcn()
        # Reports time for execution
        time = (te - ts) / pow(10,9)
        print(f"Time to complete rule: {time} s")


        # Multithreaded word rule, 3 word passwords - USE THIS
        # SUCCESS
        print("3 word rule:")
        ts = pcn()
        with open('dictionary_two_words.txt', 'r', encoding='utf-8-sig') as dtf:
            with open('dictionary.txt', 'r', encoding='utf-8-sig') as df:
                with multiprocessing.Pool(self.num_processes) as pool:
                    count = 1
                    for chunk in self.split_iter(product(df.read().splitlines(), dtf.read().splitlines()), chunksize=32000000):
                        print(f"Chunk no. {count}\n")
                        pool.map(self._words_rule_tuple, chunk, chunksize=999999)
                        count += 1
                    pool.close()
                    pool.join()
        te = pcn()
        # Reports time for execution
        time = (te - ts) / pow(10,9)
        print(f"Time to complete rule: {time} s")


        # Reports time for execution
        time = (pcn() - self.time_created) / pow(10,9)
        print("\nCrack complete.")
        print(f'Found passwords: {len(self.found_passwords)}')
        print(f"Time to complete cracking: {time} s")
        
        return self.found_passwords

    

if __name__ == "__main__":
    cracker = Cracker()
    found = cracker.crack()

    print(found)
