---
title:  "Paper Reading Vol 1"
layout: post
date: 2022-05-11 15:23:16
tags:  ["Paper Reading"]
syntaxHighlighter: yes
mathjax: true
---

20220511-0513

## REBEL: Relation Extraction By End-to-end Language generation（EMNLP 21）

### motivation
关系抽取的Pipeline方式有误差传递现象，或者抽取的关系类型有限，或者无法解决“多关系”、“一头多尾”、“多头一尾”等重叠的问题；
一些seq2seq模型虽然可以通过多次生成实体的方式解决上述重叠问题，但存在暴露偏差的问题。

### contribution
使用自回归预训练模型（BART）以端到端生成的方式做三元组抽取。可以抽取多达200多种关系；然暴露偏差的问题仍然存在，但可以通过引入注意力机制来考虑已经解码的token，另外，作者引入了triplet linearization（用来保持三元组的顺序）。

### method
REBEL输入包含实体（及隐含的关系）的句子，输出一系列三元组。三元组是以一系列token的形式来生成的。模型也引入了几个特殊的token：$<triplet>, <subj>, <obj>$，其中$<triplet>$表示三元组的开始；$<subj>$表示头实体的结束，同时表示尾实体的开始；$<obj>$表示尾实体的结束，同时表示关系的开始。（在遇到下一个$<triplet>$（如有）之前，所有的三元组共享同一个$<subj>$）。举一个简单的例子：

> 刘德华作曲并演唱了这首《天意》。

三元组抽取序列可以表示为：

```
<triplet> 刘 德 华 <subj> 天 意 <obj> 作 曲 者 <subj> 天 意 <obj> 演 唱 者
```

当然，这种生成方式需要按头实体（或尾实体）将所有的三元组排序，要不然模型在预测时可能东一榔头西一棒锤的不讲武德。

最后，作者在6个数据集上评估了他们的模型（CONLL04，NYT，DocRED，ADE，Re-TACRED，REBEL）。