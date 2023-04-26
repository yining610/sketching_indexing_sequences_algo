import sys
import math

def get_string(filename):
    return ''.join(open(filename, "rb").read().decode("utf8", "ignore").split())

'''
Below are a series of functions to compute the Burrows-Wheeler Transform
along with functions to compute compression metrics related to strings.

Do not change any function names or inputs. You may add extra helper 
functions if needed.
'''

def compute_BWM(sequence):
    '''
    Compute the Burrows-Wheeler Matrix for a given sequence

    Input:
    sequence: an input string to compute the BWM from. You
              should use the default lexicographical sorting convention
              in python, i.e. sorted(), to sort strings. 

    Output:
    bwm: a list of strings, each a cyclic permutation of the 
         original string, in lexicographically sorted order. 
    '''

    # find all permutations of input sequence
    permutations = []
    for i in range(len(sequence)):
        permutations.append(sequence[i:] + sequence[:i])

    # sort permutations
    return sorted(permutations)


def BWT_from_BWM(bwm):
    '''
    Compute the BWT given a Burrows-Wheeler matrix

    Input:
    bwm: a list of lexicographically sorted cyclic permutations
         of a string

    Output:
    bwt: string, the Burrows-Wheeler transform
    '''

    # get last column of bwm
    return ''.join([row[-1] for row in bwm])

def run_length_encode(sequence):
    '''
    Compute the run length encoding for a given sequence

    Input:
    sequence: an input string

    Output:
    rle: a list of tuples, each of the form (char, frequency).
         i.e. string 'AABBBCBBA' would return 
         [('A', 2), ('B', 3), ('C', 1), ('B', 2), ('A', 1)]
    '''
    
    rle = []
    prev = sequence[0]
    count = 1
    for c in sequence[1:]:
        if c == prev:
            count += 1
        else:
            rle.append((prev, count))
            prev = c
            count = 1
    rle.append((prev, count))
    return rle


def compression_ratio(sequence, rle):
    '''
    Compute the compression ratio, given the run length encoding
    (Hint: you should count run characters and any frequency values > 1
    as one unit each. i.e. the RLE of string 'AABCCCAAAA' would have a length of 7)
    We compute the rle_length below for you.

    Input:
    sequence: an input string
    rle: the run length encoding of sequence, as defined in run_length_encoding()

    Output:
    compression_ratio: (length of uncompressed string) / (length of compressed string)
    '''
    # [('A', 2), ('B', 1), ('C', 3), ('A', 4)]
    rle_length = len(''.join([c + str(f) if f > 1 else c for c, f in rle]))
    
    return len(sequence) / rle_length

def entropy(sequence):
    '''
    Compute the Shannon entropy of an input string.
    You should use log base 2.

    Input:
    sequence: an input string

    Output:
    S: Shannon entropy of the string
    '''
    
    # count frequency of each character
    freq = {}
    for c in sequence:
        if c in freq:
            freq[c] += 1
        else:
            freq[c] = 1
    
    # compute entropy
    S = 0
    for c in freq:
        p = freq[c] / len(sequence)
        S += p * math.log2(p)

    return -S
    
if __name__ == '__main__':
    # string = get_string(sys.argv[1])
    string = "tagtcccgtagtcggttct$"


    # Compute the BWT via the BWM
    bwm = compute_BWM(string)
    bwt = BWT_from_BWM(bwm)

    rle = run_length_encode(bwt)
    print(f"rle: {len(run_length_encode(string))}")
    ratio = compression_ratio(string, rle)

    ent = entropy(string)

    # Print out BWT and metrics
    print("Input string:\t", string)
    print("BWT:\t", bwt)
    print("Run length encoding:\t", ''.join([c + str(f) if f > 1 else c for c, f in rle]))
    print('Compression ratio:\t %.3f'%ratio)
    print("Shannon entropy:\t %.3f"%ent)
