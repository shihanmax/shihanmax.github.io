---
title:  "Decoder-only模型的参数与计算量分析"
layout: post
date: 2024-03-22 23:37:56
tags:  ["Deep Learning", "LLM"]
syntaxHighlighter: yes
mathjax: true
---

目前主流大语言模型都采用transformer decoder作为基础架构，本文简单总结：大模型参数计算方法、训练及推理状态的现存占用分析，以及训练状态下所需计算量、计算时间分析。

<img src="https://imgbed4s.oss-cn-beijing.aliyuncs.com/attention_research_1.webp"  width="50%" alt="transformer_arch">

<center>transformer</center>


## 参数量计算

一般而言，在整体结构上，大模型一般由Embedding + 若干层transformer layer组成，每层transformer decoder主要由self attention层和MLP层构成。

计算self attention层的参数：

- $W_Q$、偏置：$h\times h, 1\times h$
- $W_K$、偏置：$h\times h, 1\times h$
- $W_V$、偏置：$h\times h, 1\times h$
- $W_o$、偏置：$h\times h, 1\times h$

self attention层参数共：$4h^2 + 4h$；

计算MLP层的参数（以llama2为例）：

- 上投影$W_1$、偏置：$h\times 4h, 1\times 4h$
- gating $W_2$、偏置：$h\times 4h, 1\times 4h$
- 下投影$W_3$、偏置：$4\times h, 1\times h$

MLP层参数共$12h^2 + 9h$；

在self attention和MLP后均有一个LayerNorm层，每个LN层均包含两个可训练参数，因此LN层共有参数$4h$；

Embedding层包含参数：$\mid V \mid h$；


综上，一层transformer decoder layer共包含参数：$16h^2 + 17h$，一个包含$l$层decoder layer的生成模型，共包含参数$l(16h^2 + 17h) + \mid V \mid h$。

以Qwen-1.8B为例：

Qwen-1.8B：$l=24, h=2048, \mid V\mid = 151851$，按上述公式计算得，参数量约为：1922439168，约等于1.92B。


## 显存占用

### 推理

推理时，仅参数占用显存，每个fp16精度的参数占用2个byte，因此一个7B的模型，大概需要占用7*2GB显存。

### 训练

以fp16方式训练时，训练过程中需要保存的数据有：

- 模型参数：fp16
- 参数梯度：fp16
- 优化器状态：fp32的一阶、二阶动量、fp32的模型参数、fp32的参数梯度

一个fp16的数据占用2个byte、fp32占用4个byte，因此，对于参数量为$\Phi$的模型来说，共需要$(2+2+4 \* 4) \Phi = 20 \Phi$的空间，例，一个7B的模型，大约需要$20 \* 7 \* 10^9 / 1024^3 \approx 130 GB$显存空间。


## 训练计算量估计

前置：对于矩阵$A \in \mathbb{R}^{m\times p}$，$B \in \mathbb{R}^{p\times n}$，$A$、$B$相乘的计算量：$m\*n\*p\*2$，其中，$m\*n$表示结果矩阵包含$m\*n$个元素，$p \* 2$表示每个元素需要经过$p$次加法和$p$次乘法计算得到。


self attention计算量：

- 计算$Q, K, V$： 三次$x^{b\times L \times h} \cdot W_Q^{h \times h}$：运算量为$3 * 2bLh^2=6bLh^2$
- 计算$QK^{T}$：$Q^{b\times n_{head} \times L \times h_{head}} \cdot K^{b\times n_{head} \times  h_{head} \times L}$：运算量为$2bn_{head} h_{head} L^2=2bL^2h$ ($n_{head} h_{head}=h$)
- 计算$score \* V$：$S^{b\times n_{head} \times L \times L} \cdot V^{b \times n_{head} \times h_{head} \times L}$：运算量为$2bn_{head}h_{head}L^2=2bL^2h$
- 结果线性映射：$O^{b \times L \times h} \cdot W_O^{h \times h}$：运算量为$2bLh^2$

MLP层计算量：





