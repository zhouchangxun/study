# Definition for a binary tree node.
class TreeNode:
    def __init__(self, x, left=None, right=None):
        self.val = x
        self.left = left
        self.right = right


class Solution:
    @staticmethod
    def construct_tree1(pre_order, mid_order):
        # 忽略参数合法性判断
        if len(pre_order) == 0:
            return None
        # 前序遍历的第一个结点一定是根结点
        root_data = pre_order[0]
        # 得到根节点在mid_order的下标
        i = mid_order.index(root_data)
        # 递归构造左子树和右子树
        left = Solution.construct_tree1(pre_order[1: 1 + i], mid_order[:i])
        right = Solution.construct_tree1(pre_order[1 + i:], mid_order[i + 1:])
        # 返回树
        return TreeNode(root_data, left, right)

    @staticmethod
    def construct_tree2(mid_order, post_order):
        # 忽略参数合法性判断
        if len(post_order) == 0:
            return None
        # 前序遍历的第一个结点一定是根结点
        root_data = post_order.pop()
        # 得到根节点在mid_order的下标
        i = mid_order.index(root_data)
        # 递归构造左子树和右子树
        left = Solution.construct_tree2(mid_order[:i], post_order[:i])
        right = Solution.construct_tree2(mid_order[i+1:], post_order[i:])
        # 返回树
        return TreeNode(root_data, left, right)

    @staticmethod
    def buildTree(preorder, inorder, postorder):
        print('input:pre:{}, mid:{}, post:{}'.format(preorder, inorder, postorder))
        if preorder and inorder:
            return Solution.construct_tree1(preorder, inorder)
        if postorder and inorder:
            return Solution.construct_tree2(inorder, postorder)

    def preorderTraversal(self, root):
        """#https://leetcode-cn.com/problems/binary-tree-preorder-traversal/solution/er-cha-shu-de-qian-xu-bian-li-by-leetcode/
        :type root: TreeNode
        :rtype: List[int]
        """
        if root is None:
            return []
        
        stack, output = [root, ], []
        
        while stack:
            root = stack.pop()
            if root is not None:
                output.append(root.val)
                if root.right is not None:
                    stack.append(root.right)
                if root.left is not None:
                    stack.append(root.left)
        
        return output

    def postorderTraversal(self, root):
        """#https://leetcode-cn.com/problems/binary-tree-postorder-traversal/solution/er-cha-shu-de-hou-xu-bian-li-by-leetcode/
        :type root: TreeNode
        :rtype: List[int]
        """
        if root is None:
            return []

        stack, output = [root, ], []
        # simulate a stack: root->right->left
        while stack:
            root = stack.pop()
            output.append(root.val)
            if root.left is not None:
                stack.append(root.left)
            if root.right is not None:
                stack.append(root.right)
        # output reversely: left, right, root
        return output[::-1]


def traversal(node, order, result):
    """traversal the tree with different order(NLR,LNR,LRN)"""
    def visitor(node):
        if node is not None:
            result.append(node.val)

    if node is None:
        return

    op = {
            'N': lambda: visitor(node),
            'L': lambda: traversal(node.left, order, result),
            'R': lambda: traversal(node.right, order, result),
    }
    for x in order:
        op[x]()
    return result

def levelOrder(root):
    """
    普通二叉树层次遍历，并输出
    :type root: TreeNode
    :rtype: List[List[int]]
    """
    res, level = [], [root]
    while root and level:
        current_res = []
        nextLevel = []
        for node in level:
            if node is None:
                current_res.append('-')
                continue
            current_res.append(node.val)
            if not node.left and not node.right:
                continue
            if node.left:
                nextLevel.append(node.left)
            else:
                nextLevel.append(None)

            if node.right:
                nextLevel.append(node.right)

        res.append(current_res)
        level = nextLevel
    return res

pre = 'EBCD'
mid = 'BDCE'
post = 'DCBE'

import sys;
if(len(sys.argv) > 1):
    pre, mid, post = sys.argv[1].split(',')
print('input:pre:[{}], mid:[{}], post:[{}]'.format(pre, mid, post))

solution = Solution()
root = solution.buildTree(list(pre), list(mid), list(post))

for level in levelOrder(root):
    print(level)
print('pre:', traversal(root, 'NLR', []) )
print('mid:', traversal(root, 'LNR', []) )
print('post:', traversal(root, 'LRN', []) )
