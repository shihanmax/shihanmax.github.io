---
title:  "Non-parametric masked language modeling"
layout: post
date: 2023-01-03 22:22:18
tags:  ["Deep Learning", "Language Model"]
syntaxHighlighter: yes
mathjax: true
---

这篇文章简单记录一下最近读的Meta的一篇的有关非参掩码语言模型的论文。这篇文章主要讨论的是类似BERT中的掩码语言模型，仅涉及encoder，不涉及decoder。

首先讨论一下BERT，BERT采用了基于token的掩码语言模型，具体地，随机地掩盖掉原句中的一些词汇，然后让模型去预测出它们，希望通过预训练过程，使模型学习到上下文的理解能力。模型的参数调整本质上也是通过“词预测”这个任务来实现的，词预测任务的目标是最大化对应token出现的概率，对于任意一个$\mathrm{[MASK]}$，经过encoder后得到的表征，通过一个映射将hidden向量映射到词表空间，在此空间上，通过$\mathrm{softmax}$计算出所有词出现的概率，并最终选择概率最大的那个作为最终的预测结果。

概率最大化是符合直觉的，但这种方式也存在一些“问题”，比如，当词库规模很大时，$\mathrm{softmax}$操作的计算还是比较耗时的；另外，对于一些罕见词，由于其在预训练过程中出现的频次较低，那么实际上在整个预训练过程中，其对应的embedding参数其实被调整的幅度相对来说并不是太大（也即，这些词的embedding并没有被充分地学习）。在这个前提下，模型对这些词汇的理解和预测能力其实是不足的。

基于上述分析，论文[Nonparametric Masked Language Modeling](https://arxiv.org/pdf/2212.01349.pdf)提出了一种新的掩码语言模型——非参数掩码语言模型（NPM），首次将常规语言模型中的$\mathrm{softmax}$替换为在reference corpus中的每一个短语上的非参数概率分布，并通过batch内近似采样、构造对比学习的方式来进行预训练。实验表明这种方式相比传统的（甚至规模更大的）参数语言模型，在零样本学习任务上都有显著的提升，在低频词汇场景下提升会更明显。

NPM模型包含一个encoder和一个参考语料集（包含若干段文本）。对于包含[MASK]的一段文本（token序列），encoder将其每一个token转化为固定长度的编码向量，参考语料集转化为一个短语集合，每个短语也通过encoder获得了其对应的表征，NPM则可以根据一种相似度计算方式，从短语集合中检索出与当前[MASK]最相近的短语，然后将其作为预测结果。




## 参考
1. [Nonparametric Masked Language Modeling](https://arxiv.org/pdf/2212.01349.pdf)