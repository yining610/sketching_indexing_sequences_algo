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

class MinHash_BottomK(object):
    """
    MinHash_BottomK data structure.

    The sketch will keep track of the k smallest hash values from a single hash function.

    Important: The attributes are already defined for you. You may
               lose points if add any attributes/global variables. You
               can still add new methods if you would like. If you have
               any questions/concerns, feel free to reach out.
    """

    def __init__(self, k, seed):
        """
        Constructor - all attributes are already defined for you.

        Key Attributes:
            - self._minhashes: The k smallest hash values encountered while building the sketch
        """
        self._k = k
        self._hasher = HashXX32(seed)
        self._hashrange = 2**32
        
        self._minhashes = [self._hashrange for _ in range(self._k)]

    def update_sketch(self, obj):
        """
        Hash the object, and if the hash value is smaller than any hash value present
        in the bottom-k sketch, update the sketch to include the k smallest hash values.
        Note: you should assume that we don't input the same obj multiple times.
        (i.e. any identical hash values are a result of collisions, not duplicates)
        This is not a realistic assumption in practice, but simplifies the data structure 
        for the purposes of this HW.

        Hint: Though a heap would be the ideal data structure for this purpose,
        we can use just a python list. Try adding the hash value to self._minhashes,
        sorting the list, and keeping the smallest k values.
        """
        
        hash_val = self._hasher.hash(obj)
        if hash_val < self._minhashes[-1]:
            self._minhashes[-1] = hash_val
            self._minhashes.sort()
    
    def get_sketch(self):
        """
        Return the MinHash_BottomK sketch - k minimum hashes
        """
        return self._minhashes
    
    def estimate_cardinality(self):
        """
        We can use the sketch to find the KMV (kth minimum value). Using the expectation
        of the KMV, we can solve for the estimated cardinality in terms of KMV.

        E[KMV] = k * hash_range/(N + 1)
        
        """
        
        return self._k * self._hashrange / self.get_sketch()[-1] - 1
    
    def union(self, b_minhash):
        """
        Finds the union sketch of self and b_minhash.

        The union sketch will consist of a list of k hashes. To fill in 
        the union sketch, you just have to merge the list of k minimum hashes 
        from each sketch, and store the k smallest hash values.

        Hint: we create a union_sketch object with the same list of hash functions.
        You can set the union_sketch._minhashes attribute to a new sketch and return this object!

        Parameters: b_minhash - second MinHash object to compute union
        
        Hint: Using get_sketch() will give you the list of minhashes for a MinHash object

        """
        union_sketch = MinHash_BottomK(self._k, 0)
        union_sketch._hasher = self._hasher

        union_minhash = [] 

        union_sketch._minhashes = union_minhash

        # merge two lists of k minimum hashes
        union_minhash = self.get_sketch() + b_minhash.get_sketch()
        union_minhash.sort()
        union_minhash = union_minhash[:self._k]
        union_sketch._minhashes = union_minhash
        
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

if __name__ == "__main__":
    # Grab the command-line arguments
    k = int(sys.argv[1])
    fn_a = sys.argv[2]
    fn_b = sys.argv[3]

    # Construct the MinHash sketches
    mh_a = MinHash_BottomK(k, 0)
    mh_b = MinHash_BottomK(k, 0)
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