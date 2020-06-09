# Definition for a binary tree node.
class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None


class Solution:
    """提供如下函数：
       1.构造树：根据 前序中序， 中序后序， 前序后序
       2.递归遍历：前序，中序，后序
       3.非递归遍历：前序，中序，后序, 层序
    """
    def constructFromPreMid(self, pre_order, mid_order):
        # 结束条件：子树为空
        if not pre_order: return None
        # 前序遍历的第一个结点是根结点
        root = TreeNode(pre_order[0])
        # 得到根节点在mid_order的下标
        i = mid_order.index(root.val)
        # 递归构造左子树和右子树
        root.left = self.constructFromPreMid(pre_order[1: 1 + i], mid_order[:i])
        root.right = self.constructFromPreMid(pre_order[1 + i:], mid_order[i + 1:])
        return root

    def constructFromMidPost(self, mid_order, post_order):
        # 结束条件：子树为空
        if not post_order: return None
        # 后序序遍历的最后一个结点是根结点
        root = TreeNode(post_order[-1])
        # 得到根节点在mid_order的下标
        i = mid_order.index(root.val)
        # 递归构造左子树和右子树
        root.left = self.constructFromMidPost(mid_order[:i], post_order[:i])
        root.right = self.constructFromMidPost(mid_order[i+1:], post_order[i:-1])
        return root

    def constructFromPrePost(self, pre, post):
        """功能：找出任意一个满足条件的树.
        因为结果不唯一，此函数优先构造左子树存在的情况。
        #https://leetcode-cn.com/problems/construct-binary-tree-from-preorder-and-postorder-traversal/solution/gen-ju-qian-xu-he-hou-xu-bian-li-gou-zao-er-cha-sh/
        """
        if not pre: return None
        root = TreeNode(pre[0])
        if len(pre) == 1: return root
        # length of left sub tree.（如果左子树为空，那这就是右子树的长度，这里我们只查找左子树非空的树）
        L = post.index(pre[1]) + 1
        root.left = self.constructFromPrePost(pre[1:L+1], post[:L])
        root.right = self.constructFromPrePost(pre[L+1:], post[L:-1])
        return root

    def buildTree(self, preorder, inorder, postorder):
        print('input:pre:{}, mid:{}, post:{}'.format(preorder, inorder, postorder))
        if preorder and inorder:
            return self.constructFromPreMid(preorder, inorder)
        if postorder and inorder:
            return self.constructFromMidPost(inorder, postorder)
        if preorder and postorder:
            return self.constructFromPrePost(preorder, postorder)

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

    def inorderTraversal(self, root):
        """
        :type root: TreeNode
        :rtype: List[int]
        https://leetcode-cn.com/problems/binary-tree-inorder-traversal/solution/er-cha-shu-de-zhong-xu-bian-li-by-alpaca-8/
        """
        res = []
        stack = []
        cur = root
        while stack or cur:
            # 模拟递归调用中序遍历子树时的压栈过程
            while cur:
                stack.append(cur)
                cur = cur.left
            # 此处相当于开始执行递归函数的最内层函数
            top = stack.pop()
            # 打印中节点的值(左节点为空)
            res.append(top.val)
            # 开始中序遍历右子树，设置入参
            cur = top.right
        return res

    def traversal(self, root, order):
        """traversal the tree with different order(*LR,L*R,LR*)"""
        result = []

        def visitor(node):
            if node is not None:
                result.append(node.val)

        def _traversal(node):
            if node is None:
                return
            op = {
                    '*': lambda: visitor(node),
                    'L': lambda: _traversal(node.left),
                    'R': lambda: _traversal(node.right),
            }
            for x in order:
                op[x]()

        _traversal(root)
        return result

    def levelOrder(self, root):
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

# test
""" usage: 
    python tree_traval.py 'EBCD,BDCE,'
    python tree_traval.py ',BDCE,DCBE'
    python tree_traval.py 'EBCD,,DCBE' 
"""
import sys;
if(len(sys.argv) > 1):
    pre, mid, post = sys.argv[1].split(',')
else:
    # default example value
    pre, mid, post = 'EBCD', 'BDCE', ''
print('input:pre:[{}], mid:[{}], post:[{}]'.format(pre, mid, post))

solution = Solution()
root = solution.buildTree(list(pre), list(mid), list(post))

print('make tree:')
for level in solution.levelOrder(root):
    print(level)

print('reverse method:')
print('pre:', solution.traversal(root, '*LR'))
print('mid:', solution.traversal(root, 'L*R'))
print('post:', solution.traversal(root, 'LR*'))

print('non-reverse method:')
print(solution.preorderTraversal(root))
print(solution.inorderTraversal(root))
print(solution.postorderTraversal(root))
