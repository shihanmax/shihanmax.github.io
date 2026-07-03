---
date: 2025-10-25 09:43:00
display_type: post
layout: post
mathjax: true
syntaxHighlighter: true
tags: 
    - 统计学习方法
title: 五、决策树（Decision Tree）
collection: 统计学习方法
---

[合集：统计学习方法笔记](/tags#统计学习方法)

---

## 决策树基础概念

### 1.1 决策树结构
- **节点**: 有向边连接的结构单元
- **内部节点**: 表示特征或属性
- **叶子节点**: 表示类别或结果

### 1.2 决策规则
- DT可以认为是一组if-then规则集合
- 从根节点到叶子节点的每条路径对应一条决策规则
- 规则由一系列条件组成，最终指向一个类别

### 1.3 训练过程
1. 从根节点开始，对样本进行递归划分
2. 直至分配到叶子节点（类别）上
3. 目标：构造一个与训练集矛盾值较小的决策树

### 1.4 最优决策树问题
- 存在最优决策树是NP完全问题
- 当前算法为启发式算法
- 测试集稀疏性限制了优化空间

---

## 特征选择

### 2.1 信息论基础

#### 熵 (Entropy)
对于离散随机变量X，其熵定义为：
$$
H(X) = -\sum_{i=1}^{n} p_i \log_2 p_i
$$

#### 条件熵 (Conditional Entropy)
在已知X的情况下，Y的条件熵：
$$
H(Y|X) = \sum_{i=1}^{n} p(x_i) H(Y|X=x_i)
$$

### 2.2 信息增益 (Information Gain)

#### 定义
信息增益表示得知特征X的信息后，类Y的信息不确定性减少的程度：
$$
g(D, A) = H(D) - H(D|A)
$$

#### 计算步骤
1. **计算数据集D的经验熵**：
   $$
   H(D) = -\sum_{k=1}^{K} \frac{|C_k|}{|D|} \log_2 \frac{|C_k|}{|D|}
   $$

2. **计算特征A的经验条件熵**：
   $$
   H(D|A) = \sum_{i=1}^{n} \frac{|D_i|}{|D|} H(D_i)
   $$

3. **计算信息增益**：
   $$
   g(D, A) = H(D) - H(D|A)
   $$

### 2.3 信息增益比

为解决信息增益偏向多值特征的问题，引入信息增益比：
$$
g_R(D, A) = \frac{g(D, A)}{H_A(D)}
$$

其中：
$$
H_A(D) = -\sum_{i=1}^{n} \frac{|D_i|}{|D|} \log_2 \frac{|D_i|}{|D|}
$$

---

## ID3算法

### 3.1 算法思想
ID3算法使用信息增益作为特征选择的标准，其核心思想是使用极大似然估计进行概率模型的选择。

### 3.2 算法步骤
1. **初始化**：从根节点开始，包含所有训练样本
2. **特征选择**：计算所有特征的信息增益，选择信息增益最大的特征
3. **节点划分**：根据选定特征的取值创建分支
4. **递归构建**：对每个分支递归执行上述过程
5. **停止条件**：
   - 所有样本属于同一类别
   - 没有剩余特征可选
   - 信息增益小于阈值ε

### 3.3 算法流程图
```python
def ID3(D, A, ε):
    # 如果所有样本属于同一类别
    if all samples in D have same class:
        return leaf_node(class_label)
    
    # 如果信息增益小于阈值
    if max_info_gain < ε:
        return leaf_node(most_common_class)
    
    # 选择信息增益最大的特征
    best_feature = argmax(g(D, A))
    
    # 创建决策节点
    node = DecisionNode(best_feature)
    
    # 为每个特征值创建分支
    for value in feature_values[best_feature]:
        subset = D[D[best_feature] == value]
        child = ID3(subset, A - {best_feature}, ε)
        node.add_child(value, child)
    
    return node
```

---

## C4.5算法

### 4.1 算法改进
C4.5算法是对ID3算法的改进，主要改进点：
1. 使用信息增益比代替信息增益
2. 处理连续值特征
3. 处理缺失值
4. 引入剪枝技术

### 4.2 信息增益比计算
$$
g_R(D, A) = \frac{g(D, A)}{H_A(D)}
$$

### 4.3 连续值处理
对于连续值特征A：
1. 将A的所有取值排序
2. 取相邻值的中点作为候选分割点
3. 计算每个分割点的信息增益比
4. 选择信息增益比最大的分割点

---

## CART算法

### 5.1 算法概述
CART (Classification and Regression Tree) 是一种既能用于分类又能用于回归的决策树算法。

### 5.2 分类树 - 基尼指数

#### 基尼指数定义
对于样本集合D，其基尼指数为：
$$
Gini(D) = 1 - \sum_{k=1}^{K} \left(\frac{|C_k|}{|D|}\right)^2
$$

#### 特征选择的基尼指数
对于特征A，其基尼指数为：
$$
Gini(D, A) = \sum_{i=1}^{m} \frac{|D_i|}{|D|} Gini(D_i)
$$

### 5.3 回归树 - 最小二乘法

#### 回归树模型
将输入空间划分为M个单元$R_1, R_2, ..., R_M$，每个单元对应一个固定输出值$c_m$：
$$
f(x) = \sum_{m=1}^{M} c_m I(x \in R_m)
$$

#### 最优划分
寻找最优划分变量j和切分点s：
$$
\min_{j,s} \left[ \min_{c_1} \sum_{x_i \in R_1(j,s)} (y_i - c_1)^2 + \min_{c_2} \sum_{x_i \in R_2(j,s)} (y_i - c_2)^2 \right]
$$

#### 最优输出值
每个单元$R_m$上的最优输出值为该单元内所有样本输出的均值：
$$
c_m = \frac{1}{|R_m|} \sum_{x_i \in R_m} y_i
$$

---

## 决策树剪枝

### 6.1 剪枝目的
- 避免过拟合
- 提高泛化能力
- 简化模型结构

### 6.2 损失函数定义
对于决策树T，其损失函数定义为：
$$
C_\alpha(T) = \sum_{t=1}^{|T|} N_t H_t(T) + \alpha |T|
$$

其中：
- $H_t(T) = -\sum_{k=1}^{K_t} \frac{N_{tk}}{N_t} \log \frac{N_{tk}}{N_t}$ 是节点t的经验熵
- $|T|$ 是树的叶子节点数
- $\alpha$ 是正则化参数，控制模型复杂度

### 6.3 剪枝算法步骤
1. **计算每个节点的经验熵**
2. **递归剪枝**：从叶节点开始向上回溯
3. **损失函数比较**：如果剪枝后损失函数降低，则进行剪枝
4. **交叉验证**：使用验证集选择最优子树

### 6.4 CART剪枝算法
```python
def prune_tree(T, alpha):
    # 计算子树的损失函数
    def loss_function(subtree):
        return calculate_loss(subtree) + alpha * count_leaves(subtree)
    
    # 从底向上遍历所有内部节点
    for node in post_order_traversal(T):
        # 计算剪枝前后的损失函数
        loss_before = loss_function(node.subtree)
        loss_after = loss_function(node.as_leaf())
        
        # 如果剪枝后损失更小，则进行剪枝
        if loss_after < loss_before:
            node.convert_to_leaf()
    
    return T
```

---

## 总结与比较

### 7.1 算法比较

| 算法 | 特征选择标准 | 处理连续值 | 处理缺失值 | 剪枝方法 |
|------|--------------|------------|------------|----------|
| ID3 | 信息增益 | 否 | 否 | 无 |
| C4.5 |  信息增益比 | 是 | 是 | 后剪枝 |
| CART | 基尼指数(分类) / 最小二乘(回归) | 是 | 是 | 后剪枝 |

### 7.2 优缺点分析

#### 决策树优点
- 易于理解和解释
- 可以处理数值型和类别型特征
- 不需要数据标准化
- 可以处理多输出问题
- 使用白盒模型，易于解释

#### 决策树缺点
- 容易过拟合
- 可能不稳定（数据微小变化可能导致树结构大幅变化）
- 学习最优决策树是NP完全问题
- 某些概念难以学习（如XOR问题）
- 如果某些类别占主导，可能产生有偏树

### 7.3 实际应用建议
1. **特征工程**：选择合适的特征，避免过多无用特征
2. **参数调优**：通过交叉验证选择最优的树深度、最小样本分割数等参数
3. **集成方法**：使用随机森林、梯度提升树等集成方法提高性能
4. **剪枝策略**：合理使用预剪枝和后剪枝避免过拟合

---

> 注：本文使用Qwen转换自本人的[统计学习方法笔记](https://imgbed4s.oss-cn-beijing.aliyuncs.com/images/2025-10-25_决策树.png)。


## 参考文献
1. 《统计学习方法》- 李航
2. 《机器学习》- 周志华
3. Breiman, L., Friedman, J., Stone, C. J., & Olshen, R. A.(1984). Classification and regression trees. CRC press.
4. Quinlan, J. R. (1986). Induction of decision trees. Machine learning, 1(1), 81-106.
