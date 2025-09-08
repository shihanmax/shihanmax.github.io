---
date: 2025-01-01 16:34:29
display_type: note
layout: post
mathjax: true
syntaxHighlighter: true
tags:
title: Algorithm Notes
---


# 1. 数组

[912 排序](https://leetcode.cn/problems/sort-an-array/)

快排实现

```python
class Solution:
    def sortArray(self, nums: List[int]) -> List[int]:
        self.q_sort(nums, 0, len(nums)-1)
        return nums
    
    def q_sort(self, arr, l, r):
        p = self.partition(arr, l, r)
        
        if p > l:
            self.q_sort(arr, l, p-1)
        if p < r:
            self.q_sort(arr,  p+1, r)
        

    def partition(self, arr, l, r):
        p = r
        
        while l < r:
            while  l < r and arr[l] <= arr[p]:
                l += 1
            while l<r and arr[r] >= arr[p]:
                r -=1
            
            if arr[l] != arr[r]:
                arr[l], arr[r] = arr[r], arr[l]
        
        arr[r], arr[p] = arr[p], arr[r]
        
        return r
```

[704 二分查找](https://leetcode.cn/problems/binary-search/description/)：
左右闭合，查中点，循环条件l<=r

```python
class Solution:
    def search(self, nums: List[int], target: int) -> int:
        l = 0
        r = len(nums) - 1

        while l <= r:
            mid = l + (r - l) // 2

            if nums[mid] < target:
                l = mid + 1
            elif nums[mid] > target:
                r = mid - 1
            else:
                return mid
        return -1
```

[27 移除元素](https://leetcode.cn/problems/remove-element/description/)
快慢指针，快指针先找到第一个不等于 val 的值，将其值与慢指针交换（复制到慢指针上），随后快慢指针各走1；循环条件：fast < len(nums)

```python
class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        slow, fast = 0, 0

        while fast < len(nums):
            while fast < len(nums) and nums[fast] == val:
                fast += 1

            # now nums[fast] != nums[slow]
            if fast < len(nums):
                nums[slow], nums[fast] = nums[fast], nums[slow]

                slow += 1
                fast += 1
        
        return slow
```

[977 有序数组的平方](https://leetcode.cn/problems/squares-of-a-sorted-array/description/)

双指针向内收缩从大到小收集结果到res（新数组）

```python
class Solution:
    def sortedSquares(self, nums: List[int]) -> List[int]:
        l = 0
        r = len(nums) - 1

        res = []

        while l <= r:
            if abs(nums[l]) > abs(nums[r]):
                res.append(nums[l] * nums[l])
                l += 1
            else:
                res.append(nums[r] * nums[r])
                r -= 1
        
        return res[::-1]
```

[209 长度最小的子数组](https://leetcode.cn/problems/minimum-size-subarray-sum/)
（数组中 和>=target的长度最小的连续子数组的\*\*长度\*\*）：快慢双指针，快指针每次走1，随后，在窗口满足要求前提下，移动慢指针，更新最小长度；

```python
class Solution:
    def minSubArrayLen(self, target: int, nums: List[int]) -> int:
        min_len = len(nums) + 1

        l, r = 0, 0
        
        curr_sum = 0

        while r < len(nums):
            curr_sum += nums[r]
            r += 1

            while curr_sum >= target and l < r:
                min_len = min(min_len, r - l)
                curr_sum -= nums[l]
                l += 1

        if min_len == len(nums) + 1:
            return 0

        return min_len
```

[59 螺旋矩阵](https://leetcode.cn/problems/spiral-matrix-ii/description/)

要求将1～n^2这些数字，顺时针/逆时针螺旋填入一个n\*n矩阵中

定义top、right、bottom、left四个变量，分别表示当前处理完成后，目前的边界，循环（left<= right && top <=bottom）{四个循环，依次：左右、上下、右左、下上；每次循环结束后，调整边界（比如第一个左右完成后，调整top += 1）}

```python
class Solution:
    def generateMatrix(self, n: int) -> List[List[int]]:
        left, right, top, bottom = 0, n - 1, 0, n - 1

        res = [[0] * n for _ in range(n)]

        num = 1
        while left <= right and top <= bottom:
            for i in range(left, right + 1):
                res[top][i] = num
                num += 1
            top += 1

            for i in range(top, bottom + 1):
                res[i][right] = num
                num += 1
            right -= 1

            for i in range(right, left - 1, -1):
                res[bottom][i] = num
                num += 1
            
            bottom -= 1

            for i in range(bottom, top - 1, -1):
                res[i][left] = num
                num += 1
            
            left += 1
        
        return res
```

# 2. 链表

[203 移除链表元素](https://leetcode.cn/problems/remove-linked-list-elements/description/)

在node前加一个dummy（curr），循环条件：curr && curr.next不为空，判断curr.next.val，如果等于val，则curr.next = curr.next.next；否则，curr = curr.next
```python
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def removeElements(self, head: Optional[ListNode], val: int) -> Optional[ListNode]:
        dummy = ListNode(None)
        dummy.next = head

        curr = dummy

        while curr and curr.next:
            if curr.next.val == val:
                curr.next = curr.next.next
            else:
                curr = curr.next
        
        return dummy.next
```

[707 设计链表](https://leetcode.cn/problems/design-linked-list/)：链表常见操作，无他

[206 翻转链表](https://leetcode.cn/problems/reverse-linked-list/description/)

next_ = curr.next ; curr.next=pre ; pre=curr; curr = next_;

```python
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if not head or not head.next:
            return head
        
        new_head = self.reverseList(head.next)
        head.next.next = head
        head.next = None
    
        return new_head
```


[24 两两交换链表中的节点](https://leetcode.cn/problems/swap-nodes-in-pairs/description/)

递归版比较好写，画图即可调转前两个，递归处理后面的；

```python
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def swapPairs(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if not head or not head.next:
            return head

        new_head = head.next
        head.next = self.swapPairs(head.next.next)
        
        new_head.next = head
        
    
        return new_head
```

[19 删除链表的倒数第n个节点](https://leetcode.cn/problems/remove-nth-node-from-end-of-list/description/)：设置dummy，fast移动n+1步；slow/fast同时移动直至fast为None，然后slow.next = slow.next.next即可

```python
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        dummy = ListNode(None)

        dummy.next = head

        def get_len(node):
            if not node:
                return 0

            len_ = 0

            while node:
                len_ += 1
                node = node.next
            
            return len_

        curr = dummy

        len_ = get_len(head)

        for i in range(1, len_ - n + 1):
            curr = curr.next

        curr.next = curr.next.next

        return dummy.next
```

[面试题02.07 链表相交](https://leetcode-cn.com/problems/intersection-of-two-linked-lists-lcci/)：分别取两个指针，指向A和B的头节点，当指针不相同时，分别移动两者，如果有一个为空，则将其置换为另一个链表的头，继续遍历，结束后，指针1的位置即是相交位置（如果没有相交，指针1为None）

```python
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def getIntersectionNode(self, headA: ListNode, headB: ListNode) -> ListNode:

        h1, h2 = headA, headB

        while h1 != h2:
            h1 = h1.next if h1 else headB
            h2 = h2.next if h2 else headA

        return h1
```

[142 环形链表II](https://leetcode-cn.com/problems/linked-list-cycle-ii/)：快慢指针法，slow每次走一，fast每次走2，如果slow == fast，将其中一个放到head，再次循环各走1，直至相遇，相遇点即是入环点；
```python
class Solution:
    def detectCycle(self, head: Optional[ListNode]) -> Optional[ListNode]:
        
        slow = fast = head

        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next

            if fast == slow:
                while head != slow:
                    head = head.next
                    slow = slow.next
                return head

        return None
```
# 3. 哈希表

[242 有效的字母异位词](https://leetcode.cn/problems/valid-anagram/submissions/637444743/)：遍历第一个串，记录char的次数，遍历第二个串，减去char的次数，最后看value是否都为0
```python
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        m = {}

        for c in s:
            m[c] = m.get(c, 0) + 1
        
        for c in t:
            m[c] = m.get(c, 0) - 1
        
        for v in m.values():
            if v != 0:
                return False
        
        return True
```

1002 查找共用字符：维护一个全局freq、遍历每个word，将word中每个char的最少出现次数更新在freq中，最终即可得到结果；

349 两个数组的交集：无他

202 快乐数：可以用set，但是当输入过大时，可能会溢出无法存储，可以使用“快慢指针”的思想，fast每次变换两次，slow变换一次，当最终二者相等时，如果为1，则为快乐数；(注意定义slow、fast时直接tran即可)

1 两数之和：略

454 两数相加II：四个数组，要求计算从四个数组分别抽取一个数，四个数相加为0的情况：分为两组，用dict统计1、2数组中的和的出现次数（复杂度n\*\*2），然后再二层遍历3、4数组

383 赎金信：hash统计两个字符串中的字母出现次数。略

15 三数之和：先排序，一层遍历取数字a，接下来，a右方取b和c，采用双指针法判断（注意a的去重、以及在a+b+c==0时b和c的下标去重）

18 四数之和：原理与三数之和相同，两层遍历取到两组数字i in range(n)和j in range(i, n)，然后在j和n-1之间采用双指针查找；注意i、j两层均有去重逻辑；且在collect结果之前，对left和right也有去重逻辑

# 4. 字符串

344 反转字符串：双指针首尾互换

541 反转字符串II：基于双指针，实现子函数；for i in range(0, len(s), 2k)来实现2k个一组进行翻转（翻转前k个）

151 翻转字符串里的单词：（split 翻转即可）略

kama55 右旋字符串：整体翻转，然后在依次翻转两个子串

28 实现strStr：子串查找算法，KMP算法，暂时放弃

459 重复的子字符串：KMP算法 / 或者调用find：(s[1:] + s[:-1]).find(s) == -1

# 5. 双指针

27 344 151 206 19 142 15 18 均已出现

# 6. 栈与队列

232 用栈实现队列：用两个栈 s_in、s_out；入队：压入s_in;出队：如果s_out非空，则直接弹出，如果s_out为空，则将全部元素由s_in移动到s_out，之后从s_out弹出一个；；重点注意peek：先执行队列pop，获得元素后，将元素在压入s_out中（入队进s1，出队从s2出（s2为空时，先从s1移入s2；不空时直接弹出，peek时，执行一次pop获得内容，然后压入s2）

225 用队列实现栈：用两个队列，q1和q2，q1用于存储数据，pop、top、empty都根据q1来判断；push操作，将元素压入q2，然后再将q1所有元素压入q2，再替换q1、q2即可

20 有效的括号：遍历串，遇到左括号入栈，遇到右括号判断栈是否为空，不空判断栈顶元素是否与当前匹配；重要：结束时判断栈是否为空（应为空）

1047 删除字符串中的所有相邻重复项:略

150 逆波兰表达式求值：遇到数字压栈、遇到操作符出栈两次，运算后压栈；返回栈顶元素即可

239 滑动窗口最大值：使用：单调队列；需要自己实现单调队列

# 7. 二叉树

递归遍历：略

迭代遍历：

- 前序遍历：使用栈，加入root，栈不为空时，顺序：结果加入node.val，压栈node.right, 压栈node.left（因为是栈，先进后出，这样遍历便可以得到中-左-右的顺序）

- 中序遍历：

- 后序：（前序遍历调换left和right顺序）使用栈，稍微改动前序遍历代码，先加入left节点，再加入righr节点，然后再将结果翻转即可

102 二叉树的层序遍历：使用队列；将root节点加入队列，当队列不空时循环以下：依次弹出len(队列)个元素（左侧弹出pop0，即为当前层的节点；对于每一个节点，加入结果集中后，分别将left和right子节点加入队列；结果为双层列表；

以下题目均可以通过层序遍历解决：

[107.二叉树的层次遍历II](https://leetcode.cn/problems/binary-tree-level-order-traversal-ii/)

[199.二叉树的右视图](https://leetcode.cn/problems/binary-tree-right-side-view/)

[637.二叉树的层平均值](https://leetcode.cn/problems/average-of-levels-in-binary-tree/)

[429.N叉树的层序遍历](https://leetcode.cn/problems/n-ary-tree-level-order-traversal/)

[515.在每个树行中找最大值](https://leetcode.cn/problems/find-largest-value-in-each-tree-row/)

[116.填充每个节点的下一个右侧节点指针](https://leetcode.cn/problems/populating-next-right-pointers-in-each-node/)

[117.填充每个节点的下一个右侧节点指针II](https://leetcode.cn/problems/populating-next-right-pointers-in-each-node-ii/)（此题适合用递归做，待迁移）
左孩子指向右孩子
右孩子指向父节点的next的左孩子（如果有）

[104.二叉树的最大深度](https://leetcode.cn/problems/maximum-depth-of-binary-tree/)
此题递归

226 翻转二叉树：先交换，再递归处理左、右
递归 简单

101 对称二叉树：（简单）转化为比较两棵树是否对称；两棵树对称的条件：root值相同 && r1.left 与r2.right对称 && r1.right与r2.left对称
简单

111 二叉树的最小深度：根节点到最近叶子结点的最短路径上的节点数量：

迭代：层序遍历，每层记录层数，如果node左右孩子都为空，则return结果；

递归：如果左右孩子都不为空，则返回二者较小者+1；如果有一个不为空，则返回该孩子的最小值+1；如果都为空，返回0

222 完全二叉树的节点个树：递归即可

110 平衡二叉树：
知识点：
- 节点的深度：指从根节点到该节点的最长简单路径边的条数；
- 节点的高度：指从该节点到叶子节点的最长简单路径边的条数。

此题：先定义一个计算树高度的函数，并切通过该函数判断，是否是平衡二叉树（左右子树高度差<1且左右子树均是平衡二叉树）

257 二叉树所有路径：递归或者回溯
递归好写

404 左叶子之和：建全局变量，递归调用左右子树，更新变量条件，左子树不为空，且左子树无子节点（left、right）；


112 路径总合（判断根节点到叶子结点是否存在一条路径，使得路径上节点和为target）：用递归
```python
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:
    def hasPathSum(self, root, _sum):
        if not root:
            return False
        
        if not root.left and not root.right:
            return _sum == root.val

        val_for_child = _sum - root.val

        return self.hasPathSum(root.left, val_for_child) or self.hasPathSum(root.right, val_for_child)
```
654 最大二叉树（通过数组中最大数作为root.val，其左边构造左子树，右边构造右子树）

找到最大值，分隔左右分别构建你即可。

*二叉树未完成*

# 8. 回溯

总览：

回溯类问题分为 组合/子集类（组合问题和子集问题等价） 和 排列类；

根据元素是否有重复、是否可以复选，分为三类：无重复不可复选、无重复可复选、有重复不可复选 三类；

共6类模板，参考[https://labuladong.online/algo/essential-technique/permutation-combination-subset-all-in-one/#%E6%9C%80%E5%90%8E%E6%80%BB%E7%BB%93](https://labuladong.online/algo/essential-technique/permutation-combination-subset-all-in-one/#%E6%9C%80%E5%90%8E%E6%80%BB%E7%BB%93)：

77 组合（返回[1, n]中所有可能的k个数字的组合）

组合问题，无重复 不可复选；

216 组合总和III（找出所有相加之和为 n 的 k 个数的组合。组合中只允许含有 1 - 9 的正整数，并且每种组合中不存在重复的数字。）：回溯

组合问题，无重复，不可复选；

17 电话号码的字母组合：回溯（回溯两个要素：路径+选择）

39 组合总和（给定一个无重复元素的数组 candidates 和一个目标数 target ，找出 candidates 中所有可以使数字和为 target的组合。candidates 中的数字可以无限制重复被选取。）

如果数字可以被无限制重复选取，则在回溯下一层时，保持start不变（而不是+1）

131 分割回文串（将s分割为一些子串，使得每个子串都是回文串）

```python
def is_palindrome(s):

   i = 0

   j = len(s) - 1

   while i <= j:

       if s[i] != s[j]:

           return False

       i += 1

       j -= 1

   return True



def main(s):

   if not s:

       return []

   result = []

   def backtrack(path, choice):
       print(f"path:{path}; choice:{choice}")
       if not choice:  # 已经没有选择了
           result.append(path[:])
           return

       for i in range(1, len(choice) + 1):  # 注意这里是+1

           if is_palindrome(choice[:i]):

               backtrack(path + [choice[:i]], choice[i:])

   backtrack([], s)

   return result

print(main("aab"))
```

93 复原IP地址

```python
def is_valid_sub(s):

   value = int(s)

   if not 0 <= value <= 255:

       return False

   if value != 0 and s.startswith("0"):

       return False

   return True

def main(s):

   if not s:

       return []

   result = []

   def backtrack(path, choice):

       if len(path) == 4 and not choice:

           result.append(path[:])

           return

       for i in range(1, len(choice) + 1):

           sub = choice[:i]

           if is_valid_sub(sub):

               backtrack(path + [sub], choice[i:])

   backtrack([], s)

   return result

print(main("101023"))
```

78 子集（给定一组不含重复元素的整数数组nums，返回该数组的所有可能的子集（幂集），解集不重复）子集/组合问题，使用start标记开始位置。

90 子集II（给定一个可能包含重复元素的整数数组 nums，返回该数组所有可能的子集（幂集））

子集/组合类问题，回溯时应该带参数start，标识起始位置，如果有重复元素，应该排序后跳过相同元素。

491 递增子序列（给定一个整型数组, 你的任务是找到所有该数组的递增子序列，递增子序列的长度至少是2。）



```python
# a little bit dirty

def main(nums):

   result = []

   mem = set()

   def backtrack(start, path):

       print(start, path)

       if len(path) > 1 and str(path) not in mem:

           result.append(path[:])

           mem.add(str(path))

       for i in range(start, len(nums)):

           if not path or nums[i] >= path[-1]:  # 满足递增条件

               backtrack(i + 1, path + [nums[i]])

   backtrack(0, [])

   return result

print(main([4, 6, 7, 7]))
```

46 全排列：(nums不包含重复数字，求全排列) 常规思路，从0开始遍历，使用used记录使用过的元素；

47 全排列：(nums包含重复数字，求全排列) 包含重复数字时，先sort，然后在回溯前判断重复数字，跳过，并且通过 ! used[i-1]来保证相同元素的顺序不发生变化；

51 N皇后m(n 皇后问题 研究的是如何将 n 个皇后放置在 n×n 的棋盘上，并且使皇后彼此之间不能相互攻击。给你一个整数 n ，返回所有不同的 n 皇后问题 的解决方案。每一种解法包含一个不同的 n 皇后问题 的棋子放置方案，该方案中 'Q' 和 '.' 分别代表了皇后和空位。）

# 9. 贪心

455 分发饼干（一堆孩子，一堆饼干，问这堆饼干最多可以满足多少个孩子的胃口），将胃口和饼干从小到大排序，判断饼干是否能够满足最小的胃口，如果不可以，就增大饼干，如果可以，就满足之，并往后移动饼干和胃口；

376 摆动序列 DP方法不理解

53 最大子序列和

贪心解法: 维护一个最大子序列和sum_，遍历每一个位置，计算当前位置数字和sum_的和是否大于结果；如果当前sum_已经小于等于0，则将sum_置为0

DP：dp[i]：截至i位置（包含）的最大子序列和；状态转移：dp[i] = max(nums[i], dp[i-1] + nums[i])

122 买卖股票的最佳时机 II（给定一个数组，它的第  i 个元素是一支给定股票第 i 天的价格。设计一个算法来计算你所能获取的最大利润。你可以尽可能地完成更多的交易（多次买卖一支股票）。）

解法：将利润分解为当前与前一天的价差：  
  
```python
def main(arr):

   res = 0

   for i in range(1, len(arr)):

       res += max(0, arr[i] - arr[i-1])

   return res

print(main([7,1,5,3,6,4]))
```

55 跳跃游戏（给一个数组，数组中某个位置表示当前位置往右跳的最大步数，判断是否可以从起点跳到终点）