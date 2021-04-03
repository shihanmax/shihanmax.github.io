---
title:  "CRF,HMM,MEMM的区别和联系"
layout: post
date:   2018-12-22 00:00:00
categories: Machine Learning
tags:  ["PGM"]
syntaxHighlighter: yes
Mathjax: true
---

## 生成式模型和判别式模型

已知输入$x$和标签$y$：
- 判别式模型估计条件概率分布$p(y\mid x)$，常见的算法有：LR，SVM，神经网络，KNN，CRF，LDA，线性回归
- 生成式模型估计联合概率$p(x,y)$，常见的的有Naive Bayes，HMM

## CRF、HMM、MEMM的对比
CRF、HMM、MEMM（最大熵隐马模型）是序列标注任务中常用的三种模型，他们各有优缺点，以下从不同的角度对比这三者。

<!--more-->

# Finding multiple core-periphery pairs in networks

### 1.模型种类
- HMM：对转移概率和状态概率进行建模，是生成式模型
- CRF：在有限样本下建立判别函数（预测函数），是判别式模型
- MEMM：是一种基于状态分类的有限状态模型，是判别式模型

### 2.拓扑结构
HMM和MEMM是一种有向图，CRF是无向图

### 3.全局最优 or 局部最优

全局最优与否要看我们构造出的loss function是否是convex，如是，则存在全局最优解。

- HMM对转移概率和状态概率直接建模，是一种全局最优模型
- MEMM是对转移概率和状态概率建立联合概率，统计是使用条件概率，由于其只在局部做归一化，容易陷入局部最优
- CRF是全局范围内统计归一化概率，可以得到全局最优解，解决了MEMM中标注偏置的问题

### 4.比较
- 与HMM比较，CRF不需要严格的独立性假设条件，可以容纳任意范围内的上下文信息，特征设计灵活
- 与MEMM比较，由于CRF计算全局最优输出节点的条件概率，克服了MEMM模型标记偏置的缺点

## 其他
### HMM和RNN的比较
HMM和RNN结构相似，都是通过hidden state来刻画序列建的依赖关系，但二者有较大不同，体现在：
- HMM本质上是一个概率模型，而RNN不是，RNN没有马尔科夫性假设，可以考虑很长的历史信息
- 隐状态的表示不同：HMM是one hot表示，而RNN则是distributed representation，其表示能力较HMM强很多，在面对高维时，表示效率更高（类似于one hot 和 word2vec）
- 隐状态的转移方式：HMM是线性的，而RNN则是高度非线性
- 深度不同：RNN的堆叠可以使得其表达能力指数提高




[1. 概率图模型笔记](https://www.zhihu.com/question/53458773/answer/330396666)（详细）
[2. CRF，HMM和MEHMM区别](https://blog.csdn.net/xingchenhy/article/details/72847543)
