from ctypes import sizeof
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

class MultiChoicePerfectionistHashSet(object):
    """
    This hashset is defined by the multiple hash functions (num_hashers) used 
    when it comes to insert an element into the table.
    """
    def __init__(self, size, seed, num_hashers = 2):
        """
        Description of attributes:
            hashers - list of hash functions, sorted by priority of hash index 
                      (use first function, then second, etc.)
            size - number of buckets in the hash table
            table - the actual hash table
        """
        self.hashers = [HashXX32(seed * (idx + 1)) for idx in range(num_hashers)] # IMPORTANT: Don't change this instantiation
        self.size = size
        # raise NotImplementedError()
        self.table = [None] * self.size
    
    def insert(self, obj):
        """
        Use the set of hash functions to determine where to insert 
        the element. 
        
        If multiple hash functions point to empty buckets, use the 
        bucket pointed to by the hash function with a lower index position
        in the hashers attribute (i.e. prioritize hashers[0] over hashers[1:], etc.)
        If only one bucket is empty, insert the item into that bucket. 
        If all the hash functions point to occupied buckets, the insertion has failed.
        """
        for hasher in self.hashers:
            index = hasher.hash(obj) % self.size
            bucket_value = self.table[index]
            if (bucket_value == None) or (bucket_value == obj):
                self.table[index] = obj
                return True
        return False

        # raise NotImplementedError()
            
    def __contains__(self, obj):
        '''
        Return True if the item is in the set and False otherwise.
        '''
        return obj in self.table
        # raise NotImplementedError()

class OneChoicePerfectionistHashSet(object):
    """
    This hashset will use one hash function to determine 
    where to insert an element.
    """
    def __init__(self, size, seed):
        """
        Description of attributes:
            hasher - hash function you will use for inserting elements 
            size - number of buckets in the hash table
            table - the actual hash table
        """
        self.hasher = HashXX32(seed)
        self.size = size
        # raise NotImplementedError()
        self.table = [None]*self.size

    def insert(self, obj):
        '''
        If the bucket is empty, set the bucket to be obj 
        and return True, representing success.
        Otherwise, return True if there is no collision 
        and False if there is not, representing failure.
        '''
        index = self.hasher.hash(obj) % self.size
        if self.table[index] == obj:
            return True
        elif self.table[index] is None:
            self.table[index] = obj
            return True
        else:
            return False

        # raise NotImplementedError()

    def __contains__(self, obj):
        '''
        Return True if the item is in the set and False otherwise.
        '''
        return obj in self.table
        # raise NotImplementedError()


def make_perfectionist_hashset(items, tablesize, seed, type, num_hashers = 2):
    assert len(set(items)) <= tablesize, \
        "Can't put more items into a table than there are buckets"
    iter_num = 1
    while True:
        if type == 1:
            hs = OneChoicePerfectionistHashSet(tablesize, seed=iter_num + seed)
        else:
            hs = MultiChoicePerfectionistHashSet(tablesize, seed=iter_num + seed, num_hashers=num_hashers)
        # Insert all items, and exit the loop in case of success
        if all(hs.insert(item) for item in items):
            return hs, iter_num
        iter_num += 1

if __name__ == "__main__":
    for fn in sys.argv[1:]:
        stringset = get_words(fn)
        set_size = len(stringset)
        multihasher_n = list(range(2, 6))
        for table_size in (10000, 5000, 2000):
            nt1 = []; nt_multi = {n : [] for n in multihasher_n}
            for i in range(25000):
                perfect_hs, num_trials1 = make_perfectionist_hashset(stringset, table_size, i * 1000, 1)
                nt1.append(num_trials1)
                for n in multihasher_n:
                    multichoice_hs, num_trials = make_perfectionist_hashset(stringset, table_size, i * 1000, 2, num_hashers=n)
                    nt_multi[n].append(num_trials)

            print(f"One-Choice: num_words = {set_size}, size = {table_size}, avg_trials = {sum(nt1) / len(nt1)}")
            for n in multihasher_n:
                print(f"Multi-Choice (n = {n}): num_words = {set_size}, size = {table_size}, avg_trials = {sum(nt_multi[n]) / len(nt_multi[n])}")