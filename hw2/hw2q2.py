import xxhash
import subprocess
import os
import sys
import random

def get_words(filename):
    return open(filename, "rb").read().decode("utf8", "ignore").strip().split()

class HashXX32(object):
    def __init__(self, seed):
        self.h = xxhash.xxh32(seed=seed)

    def hash(self, o):
        self.h.reset()
        self.h.update(o)
        return self.h.intdigest() % sys.maxsize

class CountingBloomFilter(object):
    def __init__(self, size, num_hash, seeds):
        '''
        Initialize a Counting Bloom filter.

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
        Insert an object into the Counting Bloom filter.
        The object will be hashed with `self._num_hash` distinct hash functions.

        Inputs:
            - obj: a bytes-like object.
        
        Returns:
            - num_collision (int): number of collisions during this insertion operation.
        '''
        num_collision = 0
        # raise NotImplementedError()
        hash_results = [hasher.hash(obj) % self._size for hasher in self._hashers]
        if all(self._bits[i] > 0 for i in hash_results):
            num_collision = 1
        else:
            for i in hash_results:
                self._bits[i] += 1

        return num_collision

    def remove(self, obj):
        '''
        Removes an object from the Counting Bloom filter.
        The object will be hashed with `self._num_hash` distinct hash functions.

        Important: All the counters should remain non-negative. If you notice a 
                   a counter would become negative, then don't subtract from it.

        Inputs:
            - obj: a bytes-like object.
        '''
        # raise NotImplementedError()
        hash_results = [hasher.hash(obj) % self._size for hasher in self._hashers]
        for i in hash_results:
            if self._bits[i] > 0:
                self._bits[i] -= 1

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
        return all(self._bits[i] > 0 for i in hash_results)

    def get_num_set_buckets(self) -> int:
        '''Return the number of set buckets in the Bloom filter.'''
        return sum([1 for x in self._bits if x > 0])

    def get_bit_vector(self):
        return ''.join([str(val) for val in self._bits])
    
    # calculate the False Positive after removal
    def get_fp(self, words, remaining_members):
        fp = 0
        for word in words:
            if word not in remaining_members and self.__contains__(word):
                fp += 1
        return fp

def cbf_insertion(cbf, members):
    """ Inserts each member provided into the Counting Bloom Filter """
    num_collision = 0
    for word in members:
        num_collision += cbf.insert(word)

def cbf_removal(cbf, words):
    """ Try to remove all the words from words """
    for word in words:
        cbf.remove(word)

if __name__ == "__main__":
    all_words = [str(i) for i in range(10000)]

    # Grab the command line arguments
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    num_hash =int(sys.argv[3])
    bf_size = int(sys.argv[4])
    
    # Create CBF, and insert your members into it
    cbf = CountingBloomFilter(size=bf_size, num_hash=num_hash, seeds=range(num_hash))
    members = all_words[start:end]
    
    cbf_insertion(cbf, members)
    print(cbf.get_bit_vector())

    # Remove elements from CBF (Notice how it is only elements that were inserted)
    random.seed(a=888)
    num_elements_to_remove = int((end-start) * 0.5)

    removed_words = random.sample(members, k=num_elements_to_remove)
    remaining_members = [word for word in members if word not in removed_words]

    cbf_removal(cbf, removed_words)
    print(cbf.get_bit_vector())

    #################################################################
    #   Hint for Written Question 2:
    #   Notice how we are using a simple input dataset ('members' list)
    #   where each input item is unique, and then we remove some of
    #   them randomly. That makes it easier to compute FP and FNs 
    #   for the Counting Bloom Filter.
    #
    #   You can assume all the objects in the 'removed_words' list
    #   have been completely removed, and the variable 
    #   'remaining_members' are the elements that are still in the 
    #   filter which will help you to calculate FPs/FNs.
    #################################################################

    # This is where you should analyze for FP/FNs after the removal of random elements
    # print(f"False Positive: {cbf.get_fp(all_words, remaining_members)}")