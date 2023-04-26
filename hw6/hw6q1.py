import sys
import math

def get_edge_list(filename):
    return [tuple(row.split(', ')) for row in open(filename, "rb").read().decode("utf8", "ignore").splitlines()]
def get_node_order(filename):
    return open(filename, "rb").read().decode("utf8", "ignore").splitlines()


'''
Below is a class to verify the wheeler properties for a given node ordering over a graph

Do not change any function names or inputs. You may add extra helper 
functions if needed.
'''

class WheelerChecker:
    def __init__(self, edges):
        '''
        A wheeler property checker class. Input is the list of edges,
        each a tuple of form (source_node, dest_node, edge_label)
        '''
        self.edges = edges

    def is_wheeler(self, node_order):
        '''
        Check if a given node_order satisfies the Wheeler graph properties
        for the underlying graph structure.

        node_order is defined as a list of node labels, provided in a given order.
        Thus, the number of nodes is len(node_order), and node_order represents the 
        set of node labels (i.e. no duplicates)
        '''
        return self.zero_degree_property(node_order) and self.consecutivity_case1(node_order) and self.consecutivity_case2(node_order)
    def zero_degree_property(self, node_order):
        '''
        Check the first property, namely:
        0 in-degree nodes must come before others

        Start by identifying the zero in-degree nodes from the list of edges
        Then check the ordering of the zero in-degree nodes in the given node_order
        '''
        
        # find the zero in-degree nodes: node with no incoming edges
        src_nodes = set([edge[0] for edge in self.edges])
        dst_nodes = set([edge[1] for edge in self.edges])
        zero_indegree_nodes = list(src_nodes - dst_nodes)

        # find the index of the zero in-degree nodes in the given node_order
        zero_indegree_nodes_index = node_order.index(zero_indegree_nodes[0])
        if zero_indegree_nodes_index != 0:
            return False
        else:
            return True

    def consecutivity_case1(self, node_order):
        '''
        Check the second property, namely:
        For all pairs of edges labeled e = (u, v) and e' = (u', v'), we have:
        a ≺ a′⟹ v < v′
        
        Verify this property holds for all the edges, given the ordering in node_order.
        You may assume that comparator operators return the correct lexicographic ordering
        '''

        for src, dest, a in self.edges:
            v = node_order.index(dest)
            for src_, dest_, a_ in self.edges:
                v_ = node_order.index(dest_)
                if a < a_ and v >= v_:
                    return False
        return True

    def consecutivity_case2(self, node_order):
        '''
        Check the second property, namely:
        For all pairs of edges labeled e = (u, v) and e' = (u', v'), we have:
        (a = a′) ∧ (u < u′) ⟹ v ≤ v′
        
        Verify this property holds for all the edges, given the ordering in node_order.
        You may assume that comparator operators return the correct lexicographic ordering
        '''
        for src, dest, a in self.edges:
            v = node_order.index(dest)
            u = node_order.index(src)
            for src_, dest_, a_ in self.edges:
                v_ = node_order.index(dest_)
                u_ = node_order.index(src_)
                if a == a_ and u < u_ and v > v_:
                    return False
        return True

    def visualize_graph(self, output):
        with open(output, 'w') as out:
            out.write('digraph G {\nrankdir=LR;\nnode [shape = circle];\n')
            for u, v, label in edges:
                out.write('%s -> %s [label = "%s"];\n'%(u, v, label))

if __name__ == '__main__':
    edges = get_edge_list(sys.argv[1])
    node_order = get_node_order(sys.argv[2])
    wheeler = WheelerChecker(edges)

    print('This graph is %sa Wheeler graph.' %('not ' if not wheeler.is_wheeler(node_order) else ''))