import sys

def get_words(filename):
    return open(filename, "rb").read().decode("utf8", "ignore").strip().split()

class BitVector:
    ''' 
    Bit Vector Class:

    We will implement a BitVector object that supports rank, and
    select operations. It will simply be stored as a Python list of 
    1s and 0s. See the examples below to understand what each 
    operation should return.

    Example:
        bv = BitVector([0,0,1,1,0,1,1,0,1,1,0])

        # Access query
        access(6)=1 

        # Rank query
        rank_1(3)=1 
        rank_0(3)=2

        # Select query
        select_1(2)=5 
        select_0(2)=4
    '''
    def __init__(self, bv: list) -> None:
        for b in bv:
            assert b in [0, 1]
        self.bv = bv

    def rank(self, query_int: int, i: int) -> int:
        """ 
        Compute the rank of integer query_int (0 or 1) at position i 

        If the i is greater than or equal to length of bitvector, then
        just return the total number of the integer query_int in the bitvector. 
        Otherwise, compute the rank of query_int at position i.
        """
        if query_int not in [0, 1]:
            raise(ValueError, "Invalid rank query: base must in [0, 1]")
        
        if i >= len(self.bv):
            return len([b for b in self.bv if b == query_int])
        else:
            return len([b for b in self.bv[:i] if b == query_int])


    def select(self, query_int: int, j: int) -> int:
        """ 
        Computes the select for the integer query_int with a rank of j
        """
        if query_int not in [0, 1]:
            raise(ValueError, "Invalid select query: base must in [0, 1]")
        if j < 0:
            raise(ValueError, "Invalid select query: j must >= 0")
        
        # Get the list of indices where the query_int occurs
        indices = [i for i, x in enumerate(self.bv) if x == query_int]
        if j > len(indices):
            raise(ValueError, "Invalid select query: j is too large")
        
        # Return the largest index
        return indices[j]

    def access(self, i: int) -> int:
        return self.bv[i]

    def __len__(self) -> int:
        return len(self.bv)

    def __repr__(self) -> str:
        return ''.join([str(b) for b in self.bv])

if __name__ == '__main__':

    # Grab the words in the input file, and length paramter
    words = get_words(sys.argv[1])
    l = int(sys.argv[2])
    
    # Convert the word list into a list of 1s and 0s. Each
    # 1 means the word in that corresponding position has 
    # a length greater than or equal to l
    input_list = [1 if len(word) >= l else 0 for word in words]
    assert len(input_list) >= 500, "file is too short for these example commands"

    # Build the bitvector, and perform some operations on it
    bv = BitVector(input_list)

    print(f"rank_0(50) = {bv.rank(0, 50)}")
    print(f"rank_1(100) = {bv.rank(1, 100)}")

    print(f"select_0(150) = {bv.select(0, 150)}")
    print(f"select_1(250) = {bv.select(1, 250)}")