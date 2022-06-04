---
title:  "Paper Reading: 6月"
layout: post
date: 2022-06-04
tags:  ["Paper Reading"]
syntaxHighlighter: yes
mathjax: true
---

[导航：汇总页](/2022/05/14/paper-reading/)

## W1

### [An Empirical Study of Memorization in NLP](https://arxiv.org/pdf/2203.12171.pdf)

#### Motivation

Feldman$^1$提出了长尾理论（long-tail theory）来解释深度学习模型中的“记忆行为”（memorization behavior），NLP领域缺少对其的实验验证。长尾理论认为，在模型训练过程中，训练集中存在的非典型的长尾样本，如果这些样本在测试集中出现过，那么记忆住这些样本对于提升模型的泛化能力就会有帮助。

#### Contribution

本文在三种NLP任务上，通过实验验证了长尾理论的存在性，实验表明，最易被模型记忆的那些样本（top-ranked instances）并非典型的，去掉他们会导致模型在测试集上的效果下降明显。另外，作者提出了一种归因方式，来解释样本为什么会被模型记忆。实验结果证明，那些top-memorized 样本包含的特征往往和类别标签是负相关的。

作者在本文尝试回答3个问题：

1. 在NLP任务中，被模型记忆的样本是否是非典型的样本（atypical instances）
2. 如果模型记住了这些样本，会导致其在测试集上的泛化能力提升吗？
3. 我们是否可以解释，为什么样本会被模型记忆（比如是否可以量化地计算出每个token被记忆的程度）

#### method

作者在情感分类、NLI和文本分类三个任务上进行实验。

首先，对于训练集的某个样本$z=(x,y)$，对其的记忆可以理解为，去掉这个样本后，模型对其的预测结果的变化情况。在$^2$中，作者对一个样本的记忆定义为，去掉这个样本（或减小其在训练集中的权重），对测试集loss的影响。作者参考$^2$的实现，定义了对样本的记忆分数。

在记忆归因方面（即如何更好地认识记忆现象，比如为什么被模型记忆了，哪些部分容易被模型记忆之类的），作者不是仅仅在样本级别分析模型为什么被记住了，在NLP场景下，作者希望从每一个token的角度来分析。作者参考$^3$，定义了基于提督的归隐方法。

### refs

1. [Does learning require memorization? a short tale about a long tail](https://arxiv.org/abs/1906.05271)
2. [Understanding black-box predictions via influence function`s](https://arxiv.org/abs/1703.04730)
3. [Axiomatic attribution for deep networks](http://proceedings.mlr.press/v70/sundararajan17a/sundararajan17a.pdf)
