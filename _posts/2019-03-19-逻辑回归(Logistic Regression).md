---
title:  "机器学习算法之逻辑回归(Logistic Regression)"
layout: post
date:   2019-03-19 00:00:00
categories: 机器学习
tags:  ["Machine Leaning"]
syntaxHighlighter: yes
mathjax: true
---

### A. 模型推导

现有样本集合$\{X,y\}$，$X$为特征$\{x_1,x_2,...,x_n\}$，$y$为实数，线性回归中，$X$与$y$之间存在映射关系$y=h_\theta(x)$，其中，

$$h_\theta(x)=\sum \theta_ ix_i$$

在逻辑回归中，$y$属于集合$\{0,1\}$，$1$表示属于某类别，而$0$表示不属于该类别。

期望得到模型$M$，使得$M(x)\in[0,1]$，这样能够较为方便地衡量$x$属于该类别的概率。

<!--more-->

$sigmoid$函数可以满足这个需求：

$$sigmoid(x)=\cfrac{1}{1+e^{-x}}$$

逻辑回归的$h_\theta(x)$可以写成：

$$h_ \theta (x)=\cfrac{1}{1+e^ {- \theta x}}$$

对正样本:

$$P({y=1 \mid x, \theta})=h_ \theta(x)$$

对负样本:

$$P({y=0 \mid x, \theta})=1-h_ \theta(x)$$

将二者合并，有:

$$P({y \mid \theta})={h_ \theta(x)}^y{1-h_ \theta(x)}^{1-y}$$

为方便求解，采用最大化似然函数求解参数$\theta$，对$m$个样本，似然函数$L(\theta)$为：

$$L(\theta)=\prod P(y \mid \theta)=\prod {h_ \theta(x)}^y{1-h_ \theta(x)}^{1-y}$$

对似然函数取对数并取负，可得损失函数$J(\theta)$：

$$J(\theta)=-lnL(\theta)=-\sum {yh_ \theta(x)}+{(1-y)(1-h_ \theta(x))}$$

将$J(\theta)$对$\theta$求导，可得

$$\cfrac{\partial{}}{\partial{\theta}}J(\theta)=x^T(h_\theta (x)-y)$$

使用梯度下降法迭代求解：

$$\theta = \theta - \alpha x^T(h_\theta(x)-y)$$

其中$\alpha$为学习率。

### B. 正则化

为避免过拟合问题，可对模型施加$L1$或$L2$正则化项，$Loss$的定义：

$Loss_{L1}=\beta \mid\mid\theta\mid\mid_1$

$Loss_{L2}=\cfrac{1}{2}\beta \mid\mid\theta\mid\mid_2^2$

其中，$\beta$为正则化超参数。

训练时，将$Loss_{L1/2}$与$J(\theta)$相加，并执行梯度下降。

### C. 多分类

逻辑回归应用于$n$类多分类时，可以针对每一个类别分别训练$n$个逻辑回归模型$\{h_{\theta1},h_{\theta2},...h_{\theta n}\}$，在模型$h _{\theta i}$中，将属于类别$i$的数据视为正类，其余类别设为负类（1 vs others），预测时对样本$i$，计算所有模型的分数，取分数最大的模型的正样本类别作为该样本$i$的类别。

### D. 优缺点

#### 优点

- 形式简单，模型可解释性强（从权重可以看到各个特征的影响）
- 效果较好，尤其是在特征选取适当的情况下，工程上经常作为baseline模型
- 训练速度快，计算量仅与特征量和数据量有关，占用资源小

#### 缺点

- 应对数据不均衡情况的能力不强
- 不能解决非线性的问题，因为LR的决策面是线性的
- 数据特征缺失或特征空间很大时效果不好
- 包含高度线性相关特征时，不适合使用逻辑回归，会影响特征的解释性





