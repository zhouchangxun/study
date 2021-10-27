from typing import List


def debugHelper(func):  # 装饰器
    cnt = 0
    indent = '│ '  # 根据自己的喜好来选择缩进方式

    def wrapper(*args, **kwargs):
        nonlocal cnt
        # 按照自己的需求来打印 begin
        print(indent * cnt, end="")
        print(args)
        # 按照自己的需求来打印 end
        cnt += 1
        res = func(*args, **kwargs)  # 被修饰函数
        cnt -= 1
        # 按照自己的需求来打印 begin
        print(indent * cnt, end="")
        print(args, ':', res)
        # 按照自己的需求来打印 end
        return res

    return wrapper


class Solution:

    def subsets(self, nums) -> List[List[int]]:
        result = []
        path = []

        @debugHelper
        def helper(path, pos):
            # if (终止条件) {
            #     存放结果;
            #     return;
            # }

            if True:  # 过滤符合要求的子集-- 根据题目要求变化。（全遍历时path都符合要求）
                result.append(path[:]) # 保存结果
                pass  # 是否继续向下分叉？ -- 根据题目要求变化。(全遍历时得到一个子集后不return，继续向下分叉遍历, 若当前path满足条件后，再向下分叉不可能满足，就return终止，相当于剪枝子树)

            # for (选择：本层集合中元素（树中孩子节点的数量就是剩余集合的大小）) {
            #     处理节点;
            #     backtracking(路径，选择列表); // 递归
            #     回溯，撤销处理结果
            # }
            # 开始下一层选择
            for idx in range(pos, len(nums)):
                path.append(nums[idx]) # 选择并处理
                helper(path, idx + 1) # 向下递归分叉
                path.pop()  # 撤销并向右选择

        helper(path, 0)

        return result


print(Solution().subsets([1, 2, 3]))
