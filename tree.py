#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# test tree as below:
'''
           1
         /   \
        /     \
       /       \
      /         \
     2           3
    / \         / \
   /   \       /   \
   4    5     6     N
  / \  / \   / \
 7  N N   N 8   9
/ \        / \  / \   
N  N      N   N N N
'''

from collections import namedtuple
from io import StringIO

#define the node structure
Node = namedtuple('Node', ['data', 'left', 'right'])
#initialize the tree
tree = Node(1,
            Node(2,
                 Node(4,
                      Node(7, None, None),
                      None),
                 Node(5, None, None)),
            Node(3,
                 Node(6,
                      Node(8, None, None),
                      Node(9, None, None)),
                 None))
#read and write str in memory
output = StringIO()


#read the node and write the node's value
#if node is None, substitute with 'N '
def visitor(node):
    if node is not None:
        output.write('%i ' % node.data)
    else:
        output.write('N ')


#traversal the tree with different order
def traversal(node, order):
    if node is None:
        visitor(node)
    else:
        op = {
                'N': lambda: visitor(node),
                'L': lambda: traversal(node.left, order),
                'R': lambda: traversal(node.right, order),
        }
        for x in order:
            op[x]()


#traversal the tree level by level
def traversal_level_by_level(node):
    if node is not None:
        current_level = [node]
        while current_level:
            next_level = list()
            for n in current_level:
                if type(n) is str:
                    output.write('N ')
                else:
                    output.write('%i ' % n.data)
                    if n.left is not None:
                        next_level.append(n.left)
                    else:
                        next_level.append('N')
                    if n.right is not None:
                        next_level.append(n.right)
                    else:
                        next_level.append('N ')

            output.write('\n')
            current_level = next_level


if __name__ == '__main__':
    for order in ['NLR', 'LNR', 'LRN']:
        output.write('== {} == traversal:\n'.format(order))
        traversal(tree, order)
        output.write('\n')

    output.write('traversal by level:'+'\n')
    traversal_level_by_level(tree)

    print(output.getvalue())
