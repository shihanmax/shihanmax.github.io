---
title:  "Paper Reading Vol 1"
layout: post
date: 2022-05-14 12:17:16
tags:  ["Paper Reading"]
syntaxHighlighter: yes
mathjax: true
---
## [REBEL: Relation Extraction By End-to-end Language generation（Findings of EMNLP 21）](https://aclanthology.org/2021.findings-emnlp.204/)

### motivation

关系抽取的Pipeline方式有误差传递现象，或者抽取的关系类型有限，或者无法解决“多关系”、“一头多尾”、“多头一尾”等重叠的问题；
一些seq2seq模型虽然可以通过多次生成实体的方式解决上述重叠问题，但存在暴露偏差的问题。

### contribution

使用自回归预训练模型（BART）以端到端生成的方式做三元组抽取。可以抽取多达200多种关系；然暴露偏差的问题仍然存在，但可以通过引入注意力机制来考虑已经解码的token，另外，作者引入了triplet linearization（用来保持三元组的顺序）。

### method

REBEL输入包含实体（及隐含的关系）的句子，输出一系列三元组。三元组是以一系列token的形式来生成的。模型也引入了几个特殊的token：$\lt  triplet \gt, \lt subj \gt, \lt obj \gt$，其中$\lt  triplet \gt$表示三元组的开始；$\lt subj \gt$表示头实体的结束，同时表示尾实体的开始；$\lt obj\gt$表示尾实体的结束，同时表示关系的开始。（在遇到下一个$\lt triplet \gt$（如有）之前，所有的三元组共享同一个$\lt subj\gt$）。举一个简单的例子：

> 刘德华作曲并演唱了这首《天意》。

三元组抽取序列可以表示为：

```
<triplet> 刘 德 华 <subj> 天 意 <obj> 作 曲 者 <subj> 天 意 <obj> 演 唱 者
```

当然，这种生成方式需要按头实体（或尾实体）将所有的三元组排序，要不然模型在预测时可能东一榔头西一棒锤地不讲武德。

最后，作者在6个数据集上评估了他们的模型（CONLL04，NYT，DocRED，ADE，Re-TACRED，REBEL）。

### Qs：

- 解码时，如何保证结果的合理性？
- 模型的推理效率与传统的抽取模型相比如何？
- pipeline可能存在误差传递、多头多尾/多关系的情况，但联合抽取模型可以解决这些问题，本文为啥没有作对比呢？（比如TPLinker、CasRel等）
- 本文针对“抽取的关系类型有限”这一问题，但为何生成式模型可以解决这些问题呢？



## [Text Smoothing: Enhance Various Data Augmentation Methods on Text Classification Tasks (Findings of EMNLP 21)](https://arxiv.org/abs/2202.13840)

### motivation

在NLP领域，数据扩增主要有两种方式：直接修改输入token，或者从token的embedding入手，通过MLM的模块输出的在词表上的分布作为词的分布式的表征，这些替换方式面临一个问题，即替换后的token往往是一些高频词，这些词汇在一些任务上，对应的标签甚至是相反的。一些方法使用有监督的方式来做扩增，但对于样本较少的场景，这些方法的使用是受限的。

### contribution

作者借鉴数据扩方法mixup的思想（将两个不同的$x$/不同的$y$按照某种权重分配进行加权相加来得到新的样本），但是对同一个token，将通过MLM编码得到的分布与编码前的onehot分布进行加权融合。

### method

通过MLM来获得一个token（被mask掉）的表征后，与其原始onehot表征进行加权融合，作为新的表征（而标签保持不变），即：

$$t_i= \lambda \cdot t_i + (1=\lambda ) \cdot mathrm{MLM}(t_i)$$

其中$t_i$表示某一个词的onehot表征。
作者在多个数据集上，证明了这种简单的数据扩增方法的有效性。

### Qs：

- 修改一个样本时，如何决定哪些token要替换为这种mixup表征？
- 权重$\lambda$的影响是怎样的
