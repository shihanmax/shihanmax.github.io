---
date: 2024-03-04 21:30:06
display_type: none
layout: post
mathjax: true
syntaxHighlighter: true
tags:
- Deep Learning
- LLM
- Transformer
title: 大模型中的两种位置编码方式&文本扩展方法
---

不同于RNN这种递归架构，transformer模型是一种完全的并行架构，可以看做将输入表示为一个全连接图，因此，transformer无法直接建模位置信息。为了处理序列中的位置信息，transformer引入了位置编码的概念。位置编码是一种编码方式，它将序列中的位置信息编码为向量，并将其与输入向量进行融合，本文简单总结常见的位置编码方法，文章的后半部分介绍近期在大模型应用中的几种用于长度扩展的位置插值方法。

## 位置编码

### 随机初始化训练

在BERT模型中，位置编码被初始化为随机向量。训练过程中位置编码会随着模型的训练而更新，从而逐渐适应不同位置的语义信息。一般需要预设一个模型支持的最大序列长度$L$，随机初始化一个$L*H$的embedding矩阵$\mathrm{E}$，使用token的位置$i$来索引对应的位置编码，并与token embedding进行逐位相加。

### Sinusoidal位置编码

$$
PE_{pos, 2i} = \sin(\frac{pos}{10000^{2i/d}})
$$

$$
PE_{pos, 2i+1} = \cos(\frac{pos}{10000^{2i/d}})
$$

其中$pos$表示位置，$d$表示embedding的维度，$i$表示embedding的第$i$个分量。

训练式和sinusoidal编码都属于绝对位置编码。

## 插值方法