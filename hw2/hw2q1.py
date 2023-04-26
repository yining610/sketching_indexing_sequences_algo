import xxhash
import subprocess
import os
import sys


def get_words(filename):
    return open(filename, "rb").read().decode("utf8", "ignore").strip().split()

class HashXX32(object):
    def __init__(self, seed):
        self.h = xxhash.xxh32(seed=seed)

    def hash(self, o):
        self.h.reset()
        self.h.update(o)
        return self.h.intdigest() % sys.maxsize

class BloomFilter(object):
    def __init__(self, size, num_hash, seeds):
        '''
        Initialize a Bloom filter.

        Inputs:
            - size: number of slots in the Bloom filter (n)
            - num_hash: number of hash functions (k)
            - seeds: seeds to initialize hash functions

        Raises:
            - ValueError if the number of seeds differ with num_hash
        '''
        self._size = size
        self._num_hash = num_hash
        self._hashers = [HashXX32(seed) for seed in seeds]
        # raise NotImplementedError()
        if num_hash != len(self._hashers):
            raise ValueError('Number of hash functions should equal number of seeds.')
        self._bits = [0] * self._size

    def insert(self, obj) -> int:
        '''
        Insert an object into the Bloom filter.
        The object will be hashed with `self._num_hash` distinct hash functions.

        Inputs:
            - obj: a bytes-like object.
        
        Returns:
            - num_collision (int): number of collisions during this insertion operation.
        '''
        num_collision = 0
        for hasher in self._hashers:
            index = hasher.hash(obj) % self._size
            if self._bits[index]:
                num_collision += 1
            self._bits[index] = True
        return num_collision


    def __contains__(self, obj) -> bool:
        '''
        Check if an object is in the Bloom filter.

        Inputs:
            - obj: a bytes-like object.
        
        Returns:
            True if `obj` is in the filter; otherwise False.
        '''
        # raise NotImplementedError()
        hash_results = [hasher.hash(obj) % self._size for hasher in self._hashers]
        return all(self._bits[i] == 1 for i in hash_results)

    def get_num_set_buckets(self) -> int:
        '''Return the number of set buckets in the Bloom filter.'''
        return sum(self._bits)

    def get_bit_vector(self):
        return ''.join([str(b*1) for b in self._bits])
    
    def compute_fp_fn(self, words, members):
        # words: words to be queried
        # members: members inserted in the bloom filter
        fp = 0
        fn = 0
        for word in words:
            # FP: word not in members but in bf
            if word not in members and self.__contains__(word):
                fp += 1
            # FN: word in members but not in bf
            elif word in members and not self.__contains__(word):
                fn += 1
        return fp, fn


def bf_insertion(bf, members):
    num_collision = 0
    for word in members:
        num_collision += bf.insert(word)
    print(num_collision)


if __name__ == '__main__':
    words = [str(i) for i in range(10000)]

    # Grab the command line arguments
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    num_hash = int(sys.argv[3])
    bf_size = int(sys.argv[4])

    # Create Bloom Filter, and insert the set of words
    bf = BloomFilter(size=bf_size, num_hash=num_hash, seeds=range(num_hash))
    members = words[start:end]
    
    bf_insertion(bf, members)
    print(bf.get_bit_vector())
    # print(bf.get_num_set_buckets())

    fp, fn = bf.compute_fp_fn(words, members)
    print(f"False Positive: {fp}, False Negative: {fn}")



