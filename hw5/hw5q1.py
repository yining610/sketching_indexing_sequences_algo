import sys

def get_test_case(fn) -> str:
    f = open(fn, 'r')
    test_case = ''
    for line in f:
        test_case += line.rstrip()
    return test_case

class BitVector:
    ''' 
    BitVector Class.
    We will use BitVector as our Rank/Select/Access (RSA) interface in this homework.
    BitVector is not really implemented using succint data structures. In practice, you 
    could replace BitVector with an efficient Python RSA library.
    Example:
        bv = BitVector([0,0,1,1,0,1,1,0,1,1,0])
        # Look at the example outputs to understand
        # how rank and select works
        print('access(6)=1', bv.access(6))
        print('rank_1(3)=1', bv.rank(1, 3))
        print('rank_0(3)=1', bv.rank(0, 3))
        print('select_1(2)=5', bv.select(1, 2))
        print('select_0(2)=4', bv.select(0, 2))
    '''
    def __init__(self, bv: list) -> None:
        for b in bv:
            assert b in [0, 1]
        self.bv = bv

    def rank(self, a: int, i: int) -> int:
        if a not in [0, 1]:
            raise(ValueError, "Invalid rank query: base must in [0, 1]")
        if i >= len(self.bv):
            return self.bv.count(a)
        return self.bv[:i].count(a)

    def select(self, a: int, j: int) -> int:
        if a not in [0, 1]:
            raise(ValueError, "Invalid select query: base must in [0, 1]")
        if j < 0:
            raise(ValueError, "Invalid select query: j must >= 0")
        for i, _ in enumerate(self.bv):
            if self.bv[:i].count(a) > j:
                return i - 1
        return len(self.bv) - 1

    def access(self, i: int) -> int:
        return self.bv[i]

    def __len__(self) -> int:
        return len(self.bv)

    def __repr__(self) -> str:
        return ''.join([str(b) for b in self.bv])

class WaveletTreeNode:
    '''
    WaveletTree node Abstract Class. 
    IMPORTANT (READ THIS!): Before you start to code, make sure you understand the 
                            meaning/purpose of each attribute described below. In addition, 
                            make sure you understand which attributes need to be set for 
                            internal versus leaf nodes. 
    
    Public members:
        - parent: a WaveletTreeNode object for a non-root node; None for the root node
        - code: the path from root to this node

    Private members:
        - alphabet: the alphabet set of `sequence`. Each element is unique
        - sequence: the corresponding sequence of this node
    '''
    def __init__(self, code: str, parent) -> None:
        self.parent = parent
        self.code = code

    def is_leaf(self) -> bool:
        # NOTE: ideally we would raise NotImplementedError because the subclass should implement
        #       this, but we don't want to confuse you with what needs to be implemented.
        raise Exception('is_leaf should be implemented in subclass')
    
class WaveletTreeLeafNode(WaveletTreeNode):
    '''
    WaveletTree leaf node Class.
    Public members:
        - leaf_label: a character in the alphabet
    '''
    def __init__(self, code: str, parent, leaf_label: str) -> None:
        '''
        Set `leaf_label` for a leaf node.
        '''
        super().__init__(code, parent)

        # Public attributes
        self.leaf_label = leaf_label

    def is_leaf(self) -> bool:
        return True
    
    def __repr__(self) -> str:
        ''' Define the output of `print(WaveletTreeNode)`. '''
        return f'Leaf({self.leaf_label})'

class WaveletTreeInternalNode(WaveletTreeNode):
    '''
    WaveletTree internal node Class.
    Public members:
        - bitvector: a BitVector object
        - left: a WaveletTreeNode pointed leftward from this node (with edge label '0')
        - right: a WaveletTreeNode pointed rightward from this node (with edge label '1')
    '''
    def __init__(self, code : str, parent : WaveletTreeNode, bv : BitVector, alphabet: list, sequence: str) -> None:
        '''
        Set `alphabet` and `sequence` for a non-leaf node.
        '''
        super().__init__(code, parent)

        # Public attributes
        self.bitvector = bv
        self.left = None
        self.right = None
        
        # Private attributes
        # 
        # NOTE: `_sequence` and `_alphabet` should not be accessed outside 
        #        of class WaveletTreeInternalNode
        self._sequence = sequence
        self._alphabet = alphabet

    def is_leaf(self) -> bool:
        return False
    
    def child(self, b):
        assert(b in [0, 1])
        return self.left if b == 0 else self.right

    def __repr__(self) -> str:
        ''' Define the output of `print(WaveletTreeNode)`. '''
        out = f'BitVector: {self.bitvector}\nSequence: {self._sequence}\nAlphabet: {self._alphabet}'
        if self.left:
            out += f'\n  Left: {self.left}'
        if self.right:
            out += f'\n  Right: {self.right}'
        return out

class WaveletTree:
    ''' 
    A WaveletTree Class supporting Rank/Select/Access (RSA) queries.
    Required public members:
        - seq: the input string
            e.g. 'mississippi'
        - codebook: a dict where keys are alphabets and values are codewords (str)
            e.g. {'$': '00', 'i': '01', 'm': '10', 'p': '110', 's': '111'}
    
    Required private members (should not be accessed outside of WaveletTree Class):
        - _root: the root WaveletTreeNode object
    Example showing how we can use a WaveletTree object:
        s = 'mississippi'
        wt = WaveletTree(s)
        print(wt)
        print('access:')
        for i, _ in enumerate(s):
            print(wt.access(i), wt.get_code(wt.access(i)))
        print('Rank:')
        print('rank_i(6)=2', wt.rank('i', 6))
        print('Select:')
        print('select_s(3)=6', wt.select('s', 3))
        print('select_p(0)=8', wt.select('p', 0))
    '''
    def __init__(self, seq) -> None:
        self.seq = seq
        self.codebook = {}
        
        # Create a list of characters in string
        alphabet = sorted(list(set(self.seq)))

        # Calls recursive method to build the tree (see hint in _add_node)
        self._root = self._add_node(code='', parent=None, alphabet=alphabet, sequence=self.seq)

    def _partition_alphabet(self, alphabet: list) -> tuple:
        """ 
        Takes in a list of alphabet characters, and returns two lists: a list of 
        characters in the left sub-tree, and a list of characters in the right sub-tree
        NOTE: As mentioned in the write-up, this means you will split using alphabetical
              order. So if the alphabet list has n characters, the first floor(n/2)
              characters (e.g n = 5, floor(5/2) = 2) go to left sub-tree, and  the rest
              to the right sub-tree.
        HINT: You will want to use this method in your _add_node method when you 
              are creating an internal node.
        """
        left_alphabet = alphabet[:len(alphabet)//2]
        right_alphabet = alphabet[len(alphabet)//2:]

        return left_alphabet, right_alphabet

    def _add_node(self, code: str, parent: WaveletTreeNode, alphabet: list, sequence: str=None) -> WaveletTreeNode:
        """
        Recursively add nodes to a WaveletTree.
        For your reference, the lines below show you which attributes you will need for different
        types of nodes, and how to instantiate them:
            - Internal Node: node = WaveletTreeInternalNode(code=code, parent=parent, bv=bv, alphabet=alphabet, sequence=sequence)
            - Leaf Node: node = WaveletTreeLeafNode(code=code, parent=parent, leaf_label=alphabet[0])
        """

        left_alphabet, right_alphabet = self._partition_alphabet(alphabet)

        if len(alphabet) > 1:
            """
            If section: checks if the node we are about to create is an internal node (non-leaf node)
                - An internal node has a bitvector summarizing the sequence at that node. Think 
                  about how would you create that bitvector by hand? 
                - Once you create this internal node, you can recursively call the _add_node() to add
                  the left and right sub-tree. 
                - Remember you have to return the node you created.
            """

            bv = BitVector([1 if char in right_alphabet else 0 for char in sequence])
            node = WaveletTreeInternalNode(code=code, parent=parent, bv=bv, alphabet=alphabet, sequence=sequence)

            # partition sequence
            left_sequence = ''.join([char for char in sequence if char in left_alphabet])
            right_sequence = ''.join([char for char in sequence if char in right_alphabet])
            
            node.left = self._add_node(code=code+'0', parent=node, alphabet=left_alphabet, sequence=left_sequence)
            node.right = self._add_node(code=code+'1', parent=node, alphabet=right_alphabet, sequence=right_sequence)

            return node
            
        elif len(alphabet) == 1:
            """
            Else If section: checks if the node we are about to create is a leaf node
                - At this point, we know the code for your character which we can use
                  to update our self.codebook attribute.
                - We can create and return the leaf node. 
            """
            node = WaveletTreeLeafNode(code=code, parent=parent, leaf_label=alphabet[0])
            self.codebook[alphabet[0]] = code

            return node

    def __repr__(self) -> str:
        return self._root.__repr__()

    def get_code(self, a: str) -> list:
        ''' Return the code (in int) for alphabet `a` in a WaveletTree. '''
        return [int(i) for i in self.codebook[a]]

    def access(self, i: int) -> str:
        ''' access(i) '''
        
        node = self._root
        while not isinstance(node, WaveletTreeLeafNode):
            B = node.bitvector
            b = B.access(i)
            if b == 1:
                node = node.right
            else:
                node = node.left
            i = B.rank(b, i)
        
        return node.leaf_label

    def rank(self, a: str, i: int) -> int:
        ''' rank_a(i) '''
        node = self._root
        k = 0
        while not isinstance(node, WaveletTreeLeafNode):
            B = node.bitvector
            b = self.codebook[a][k]
            if b == '1':
                node = node.right
            else: 
                node = node.left
            i = B.rank(int(b), i)
            k += 1
        
        return i

    def select(self, a: str, j: int) -> int:
        ''' select_a(j) '''
        
        # find the leaf node of a
        leaf_node = self._root
        k = 0
        while not isinstance(leaf_node, WaveletTreeLeafNode):
            if self.codebook[a][k] == '1':
                leaf_node = leaf_node.right
            else:
                leaf_node = leaf_node.left
            k += 1

        k = len(self.codebook[a]) - 1
        node = leaf_node
        while node.parent is not None:
            node = node.parent
            B = node.bitvector
            b = self.codebook[a][k]
            j = B.select(int(b), j)
            k -= 1

        return j


class ReverseBwt:
    ''' Class for the reversal of a BWT.
    Usage: 
        rbwt = ReverseBwt('ipssm$pissii')
        rbwt.print_t() # 'mississippi'
    '''
    def __init__(self, bwt: str) -> str:
        self._bwt_wt = WaveletTree(bwt)
        front = ''.join(sorted(bwt))
        self._front_wt = WaveletTree(front)
        self._skip_array = self.build_skip_array(front)
        self._t = self.reverse()
        
    def reverse(self) -> str:
        ''' Reverse a BWT sequence and return it. The BWT to reverse is stored in self._bwt_wt.
        Some examples:
            r_bwt = 'abba$aa'       # 'abaaba'
            r_bwt = 'ccagtc$'       # 'tcgcac'
            r_bwt = 'bc$baaab'      # 'ababcab'    
            r_bwt = 'tca$ag'        # 'caagt'
            r_bwt = 'ipssm$pissii'  # 'mississippi'
        '''
        next_char = self._bwt_wt.seq[0]
        original_seq = next_char
        next_row = 0
        while next_char != '$':
            rank = self._bwt_wt.rank(next_char, next_row)
            skip = self._skip_array[next_char]
            next_row = rank + skip
            next_char = self._bwt_wt.access(next_row)
            original_seq += next_char

        # remove the last character and then reverse the string
        return original_seq[:-1][::-1]
    
    def build_skip_array(self, seq: str) -> dict:
        ''' 
        Build the skip array for a string `seq`. As the name implies, it will 
        tell you how many rows in the Burrows-Wheeler matrix to skip to reach
        the first row with a certain character. 
        Here is an example:
            - seq = "abcabcabcd"
            - skip_array = {'a': 0, 'b': 3, 'c': 6, 'd': 9} (Python Dictionary)
        '''
        skip_array = {}
        # sort the characters in seq
        sorted_seq = ''.join(sorted(seq))
        # iterate through the sorted sequence
        for i, char in enumerate(sorted_seq):
            # if the character is not in the skip array, add it
            if char not in skip_array:
                skip_array[char] = i
        return skip_array

    def print_t(self) -> str:
        return self._t

if __name__ == '__main__':
    seq = get_test_case(sys.argv[1])
    print('#### Input')
    print(seq)
    print()
    wt_a = WaveletTree(seq)
    print('#### WaveletTree')
    print(wt_a)
    print(wt_a.codebook)
    print()
    print('#### ReverseBWT')
    print(ReverseBwt(seq).print_t())