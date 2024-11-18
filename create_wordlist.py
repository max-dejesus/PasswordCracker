from itertools import product

# This file creates a new wordlist based on the original, 
# including all permutations of two words

dict_file = open("dictionary.txt" , "r", encoding='utf-8-sig')
of = open("dictionary_two_words.txt", 'w+', encoding="utf-8-sig")
with dict_file:
    d = dict_file.readlines()
    for line in d:
        d[d.index(line)] = line.replace("\n", "")
dict_file.close()

with of:
    perms = product(d, repeat=2)
    for perm in perms:
        words = ''.join(perm)
        of.write(words + '\n')
of.close()
