---
title:  "Paper Reading Vol 1"
layout: post
date: 2022-05-22 10:12:45
category: paper
tags:  ["Paper Reading"]
syntaxHighlighter: yes
mathjax: true
---

## [Is Graph Structure Necessary for Multi-hop Question Answering?（EMNLP 20）](https://aclanthology.org/2020.emnlp-main.583.pdf)

来自EMNLP 20的一篇短文，讨论了在多跳事实问答中使用图结构的必要性。结论是，在强大的预训练语言模型的加持下，图结构必要性不强。

> Background: The key to solving the multi-hop question is to find the corresponding entity in the original text through the query.

### Motivation

因为多跳事实问答中，需要考虑很多个对话轮次中的信息，因此有许多文章在这个场景中引入了图结构来对多个段落中的实体的关系进行建模。并且有文章认为，图结构对这种问题的解决是至关重要的。

### Contribution

作者在本文中讨论了这个问题：“多跳问答中，图结构本身究竟贡献有多大？”

### Method

作者为了回答上述问题，设计了一系列实验，对于传统模型来说，将paragraph中的实体关系以图的方式组织起来，然后将其输入GNN中，最终获得各个实体之间的表征，作者尝试将GNN模块完全去掉，即直接使用预训练语言模型对输入paragraph进行建模，对比两种方式的结果差异。从结果中发现，如果仅仅将PTM作为特征抽取器，那么GNN在整个模型中的作用是显著的，但是如果以finetune的方式引入PTM，则GNN的优势并不明显。


## [Unified Structure Generation for Universal Information Extraction](https://aclanthology.org/2022.acl-long.395.pdf)

### Motivation

目前的信息抽取任务包括实体识别、关系抽取、事件抽取、情绪识别等，下游任务之间的联系不强，需要分别进行数据构造和模型训练。

### Contribution

本文提出了一种统一的text-to-structure生成网络，将以上信息抽取任务的形式使用schema-based prompt进行融合，构造了一种统一的生成式的信息抽取框架。在四种任务共13个数据集上验证了该方法的有效性。


### Method

作者认为，信息抽取的任务包含两个原子操作：片段抽取和片段之间的“关系”抽取，前者称为spotting（如实体、触发词、论元等的抽取），后者称为Associating（如实体之间的关系、触发词和论元之间的关系等）。

作者首先设计了一种结构化抽取语言（SEL），将不同的信息抽取任务统一为：

```
(
    (Spot Name: Info Span
        (Asso Name: Info Span)
        (Asso Name: Info Span)
    )
)
```

然后提出结构模式指示器（SSI），即一个基于模式的prompt机制，用于控制属于中哪些信息需要抽取。
