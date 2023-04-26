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

class HashSetWithProbing(object):
    def __init__(self, size, seed):
        """
        Description of attributes:
            hasher - hash function you will use to insert elements
                     into the table
            size - number of buckets in the hash table
            table - the actual hash table
            n - number of distinct items in the hash table
            probing_steps - total number of probing steps taken while
                            inserting elements into the table. Each time
                            you have to increment the index according to the quadratic rule
                            is considered a probing step, and only increment this attribute
                            when you actually insert the element. Notably, you should count 
                            probing steps even when the index according to the quadratic function
                            is invalid! Lastly, if you are trying to insert a duplicate item do not 
                            include any steps it took to get to that duplicate
                            entry.
        """
        self.hasher = HashXX32(seed)
        self.size = size
        self.m = 2 ** (self.size - 1).bit_length()
        # raise NotImplementedError()
        self.table = [None] * size
        self.n = 0
        self.probing_steps = 0
           
    def insert(self, obj):
        '''
        Insert the object into the hash set. If the initial bucket
        already has an element, use quadratic probing to find the next 
        available bucket. 
        
        For example, if your hash function points you to bucket n and 
        it is full, use the quadratic probing function:
        (n + 1/2i + 1/2i^2) mod m, where m is the size of the table rounded
        up to the nearest power of two (precomputed and stored in self.m).
        If the probing function yields invalid index, ignore the value and
        continue probing until a valid index is found (i.e. 0 <= index < table size).
        Continue probing until you find an empty slot.

        Return True if you could insert the element or it already exists
        in the table, and return False if you cannot
        '''
        initial_index = self.hasher.hash(obj) % self.size
        i = 0

        insertion = False if not self.__contains__(obj) else True

        # begin inserting iff obj is not in the table and the table has empty slot
        # otherwise insertaion would be failed
        while (not insertion) & (None in self.table):
            new_index = round((initial_index + 1/2*i + 1/2*(i**2)) % self.m)
            # invalid index or the bucket has been occupied
            if (new_index >= self.size) or (self.table[new_index] is not None):
                i += 1
            else:
                self.table[new_index] = obj
                self.n += 1
                insertion = True
        
        self.probing_steps += i
        return insertion

        # raise NotImplementedError()
    
    def __contains__(self, obj):
        '''
        Return True if the object has been added 
        and False if it has not been.
        '''
        return obj in self.table
        # raise NotImplementedError()
    
    def avg_probing_steps(self):
        '''
        Returns the average number of steps needed to insert an 
        element into the table
        '''
        # total number of probing steps / number of distinct items
        return self.probing_steps / self.n
        # raise NotImplementedError()
        
class HashSetWithChaining(object):
    def __init__(self, size, seed):
        """
        Description of attributes:
            hasher - hash function you will use to insert elements
                     into the table
            size - number of buckets in the hash table
            table - the actual hash table 
        """
        self.hasher = HashXX32(seed)
        self.size = size
        # raise NotImplementedError()
        self.table = table = [[] for i in range(size)]
    
    def insert(self, obj):
        '''
        Insert the object into the hash set.
        '''
        index = self.hasher.hash(obj) % self.size
        if not self.__contains__(obj):
            self.table[index].append(obj)
        # raise NotImplementedError()
            
    def __contains__(self, obj):
        '''
        Return True if the object has been added 
        and False if it has not been.
        '''
        return any(obj in bucket for bucket in self.table)
        # raise NotImplementedError()

    def max_num_in_bucket(self):
        '''
        Return the maximum number of items in a given hash bucket
        for the hash set.
        '''
        return max(len(bucket) for bucket in self.table)
        # raise NotImplementedError()

if __name__ == "__main__":
    for fn in sys.argv[1:]:
        words = get_words(fn)

        # Vary the size of your hash table
        for iter_num, size in enumerate([100, 150, 200, 500]):
            assert len(set(words)) <= size, \
                "Can't put more items into a HashSetWithProbing than there are buckets"

            hashsets_ch = [HashSetWithChaining(size=size, seed=seed) for seed in range(10)] # 10 different hash-sets
            hashsets_pr = [HashSetWithProbing(size=size, seed=seed) for seed in range(10)] 

            # Insert all the words, and verify their insertion
            for word in words:
                for pos in range(len(hashsets_ch)):
                    hashsets_ch[pos].insert(word)
                    hashsets_pr[pos].insert(word)
            for word in words:
                assert word in hashsets_ch[0], "word %s is missing in chaining hashset" % word
                assert word in hashsets_pr[0], "word %s is missing in probing hashset" % word

            ## Print the maximum number of items in a given hash bucket for each hash set
            ## as a list of integers, along with the average maximum count, and the word
            ## that occurs the most in the input text
            result_ch = [x.max_num_in_bucket() for x in hashsets_ch]
            result_pr = [round(x.avg_probing_steps(), 1) for x in hashsets_pr]

            avg_maxcount = sum(result_ch) / len(result_pr)
            avg_probingsteps = round(sum(result_pr)/len(result_pr), 1)

            print(f"chaining: {fn}, {size}, {result_ch}, {avg_maxcount}")
            print(f"probing:  {fn}, {size}, {result_pr}, {avg_probingsteps}")