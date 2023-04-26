import xxhash
import sys

def get_words(filename):
    return open(filename, "rb").read().decode("utf8", "ignore").strip().split()

class HashXX32(object):
    """
    HashXX32 class: Used to draw hash functions
    """
    def __init__(self, seed):
        self.h = xxhash.xxh32(seed=seed)

    def hash(self, o):
        self.h.reset()
        self.h.update(o)
        return self.h.intdigest() % (2**32) 

class MinHash_KHash(object):
    """
    MinHash_KHash data structure.

    The sketch will use k hash functions, and keep track of the 
    minimum hash value produced by each of the hash functions.

    Important: The attributes are already defined for you. You may 
               lose points if you add any attributes/global variables. You
               can still add new methods if you would like. If you have 
               any questions/concerns, feel free to reach out. 
    """

    def __init__(self, num_hashers, start_seed):
        """
        Constructor - all attributes are already defined for you.

        Key Attributes:
            - self._hashers: The k hash functions you will use to hash each object
            - self._minhashes: The minimum hash values from each hash function
        """
        self._numhashers = num_hashers
        self._hashers = [HashXX32(start_seed+i) for i in range(self._numhashers)]
        self._hashrange = 2**32
        self._minhashes = [self._hashrange for i in range(self._numhashers)]

    def update_sketch(self, obj):
        """
        Hash the object with each of the k hash functions, and check 
        for all k hash values whether they are smaller than the minimum 
        hash value seen so far from that hash function. If so, replace 
        that value with the new minimum.
        """
        
        for i in range(self._numhashers):
            hash_val = self._hashers[i].hash(obj)
            if hash_val < self._minhashes[i]:
                self._minhashes[i] = hash_val
    
    def get_sketch(self):
        """
        Return the MinHash_KHash sketch - minimum hashes for each hash function
        """
        return self._minhashes
    
    def estimate_cardinality(self):
        """
        Find the arithmetic mean of the minimum hashes from each hash function,
        and then use that average to estimate the cardinality using the 
        expectation from class. Return the estimated cardinality.

        M_avg = hash_range/(N + 1)

        """
        M_avg = sum(self._minhashes)/len(self._minhashes)
        
        return self._hashrange / M_avg - 1
    
    def union(self, b_minhash):
        """
        Finds the union sketch of self and b_minhash.

        The union sketch will consist of a list of hashes equal to the number
        of hash functions. To fill in the union sketch, you just have to 
        iterate list of minimum hashes and store the smaller of the two 
        minimum hashes (from self and b_minhash) for that hash function.

        Hint: we create a union_sketch object with the same list of hash functions.
        You can set the union_sketch._minhashes attribute to a new sketch and return this object!

        Parameters: b_minhash - second MinHash object to compute intersection
        
        Hint: Using get_sketch() will give you the list of minhashes for a MinHash object

        """
        union_sketch = MinHash_KHash(self._numhashers, 0)
        union_sketch._hashers = self._hashers

        union_minhash = [] 

        union_sketch._minhashes = union_minhash

        for i in range(self._numhashers):
            union_sketch._minhashes.append(min(self.get_sketch()[i], b_minhash.get_sketch()[i]))

        return union_sketch
        

    def compute_intersection(self, b_minhash):
        """
        Computes and returns the cardinality of the intersection between the current sketch, 
        and the second sketch. It uses the exclusion-inclusion principle to estimate the intersection 
        cardinality:
        |A.intersect(B)| = |A| + |B| - |AUB|

        Parameters: b_minhash - second MinHash object to compute intersection
        
        Hint: Using estimate_cardinality() will allow
              you quickly get the values you need.
        """
        return self.estimate_cardinality() + b_minhash.estimate_cardinality() - self.union(b_minhash).estimate_cardinality()

    def compute_indirect_jaccard(self, b_minhash):
        """
        Computes and returns jaccard between the current sketch, and the
        second sketch. It uses the "indirect" method discussed in class which uses 
        the exclusion-inclusion principle to estimate the intersection 
        cardinality.

        |A.jaccard(B)| = |A.intersect(B)|/|AUB|

        |A.intersect(B)| = |A| + |B| - |AUB|

        Parameters: b_minhash - second MinHash object in the jaccard
        
        Hint: Using the get_sketch() and estimate_cardinality() will allow
              you quickly get the values you need.
        """
        return self.compute_intersection(b_minhash) / self.union(b_minhash).estimate_cardinality()
    
    def compute_containment(self, b_minhash):
        """
        Computes and returns the containment between current sketch
        and second sketch. Use the exclusion-inclusion principle to 
        estimate the intersection.

        |A.contain(B)| = |A.intersect(B)|/|A|

        |A.intersect(B)| = |A| + |B| - |AUB|

        Parameters: b_minhash - MinHash object that we want to 
                                find jaccard with.
        
        Hint: Using the get_sketch() and estimate_cardinality() will allow
              you quickly get the values you need.
        """
        return self.compute_intersection(b_minhash) / self.estimate_cardinality()

if __name__ == '__main__':
    # Grab the command-line arguments
    num_hash = int(sys.argv[1])
    fn_a = sys.argv[2]
    fn_b = sys.argv[3]

    # Construct the MinHash sketches
    mh_a = MinHash_KHash(num_hash, 0)
    mh_b = MinHash_KHash(num_hash, 0)
    data_a = get_words(fn_a)
    data_b = get_words(fn_b)

    for x in data_a:
        mh_a.update_sketch(x)
    for x in data_b:
        mh_b.update_sketch(x)
    
    est_card_a = mh_a.estimate_cardinality()
    est_card_b = mh_b.estimate_cardinality()
    est_card_union = mh_a.union(mh_b).estimate_cardinality()

    jaccard = mh_a.compute_indirect_jaccard(mh_b)
    a_contain_b = mh_a.compute_containment(mh_b)
    b_contain_a = mh_b.compute_containment(mh_a)

    print(f"|A|= {est_card_a:<10.3f}|B|= {est_card_b:<10.3f}|AUB|= {est_card_union:<10.3f}")
    print(f"A.jaccard(B)= {jaccard:<10.3f}A.contain(B)= {a_contain_b:<10.3f}B.contain(A)= {b_contain_a:<10.3f}")
    print(f"{mh_a.get_sketch()}")
    print(f"{mh_b.get_sketch()}")