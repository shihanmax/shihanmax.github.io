---
title: Example protected page
password: s00pers3cr3t
date: 2021-03-03 20:30:03
categories: NLP
tags:  ["Machine Learning", "SVM"]
syntaxHighlighter: yes
Mathjax: true
---

## 零、前言

支持向量机（Support vector machine, SVM）是一种用于二分类的线性分类器，区别于感知机，SVM使用中定义在特征空间上的间隔最大化分类器。支持向量机可以处理线性分类，引入核技巧后，支持向量机则成为一个非线性分类器。当输入空间为欧氏空间或离散集合、特征空间为希尔伯特空间时，核函数表示将输入从输入空间映射到特征空间的到的向量之间的内积。此时等价于在高维特征空间中学习一个线性分类器。

优化方面，支持向量机的学习目标是间隔最大化，本质上一个凸二次规划问题，也等价于正则化的合叶损失函数（Hinge loss）最小化问题。

下文以线性分类器开始，引入间隔最大化的目标函数，接着介绍硬间隔SVM和加入松弛因子的软间隔SVM，然后讨论用于求解带不等式约束优化问题的KKT条件、SVM目标函数的原始问题（Prime form）向对偶形式（Dual form）的转换，在此基础上，讨论在SVM中引入核技巧的方式，最后，对序列最小化算法（SMO）进行简单的介绍。

# This content is served encrypted

You can use *markdown* as always.