---
title:  "Decoder-only模型的参数与计算量分析"
layout: post
date: 2024-03-22 23:37:56
tags:  ["Deep Learning", "LLM"]
syntaxHighlighter: yes
mathjax: true
---

目前主流大语言模型都采用transformer decoder作为基础架构，本文简单总结：大模型参数计算方法、训练及推理状态的显存占用分析，以及训练状态下所需计算量、计算时间分析。

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

计算MLP层的参数（以GPT-3为例）：

- 上投影$W_1$、偏置：$h\times 4h, 1\times 4h$
- 下投影$W_2$、偏置：$4h \times h, 1\times h$

MLP层参数共$8h^2 + 5h$；

在self attention和MLP后均有一个LayerNorm层，每个LN层均包含两个可训练参数，因此LN层共有参数$4h$；

Embedding层包含参数：$\mid V \mid h$；


综上，一层transformer decoder layer共包含参数：$12h^2 + 13h$，一个包含$l$层decoder layer的生成模型，共包含参数$l(12h^2 + 13h) + \mid V \mid h$。

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

- 计算$Q, K, V$： 三次$x^{b\times L \times h} \cdot W_Q^{h \times h}$，运算量为$3 * 2bLh^2=6bLh^2$；
- 计算$QK^{T}$：$Q^{b\times n_{head} \times L \times h_{head}} \cdot K^{b\times n_{head} \times  h_{head} \times L}$，运算量为$2bn_{head} h_{head} L^2=2bL^2h$ ($n_{head} h_{head}=h$)；
- 计算$score \* V$：$S^{b\times n_{head} \times L \times L} \cdot V^{b \times n_{head} \times h_{head} \times L}$，运算量为$2bn_{head}h_{head}L^2=2bL^2h$；
- 结果线性映射：$O^{b \times L \times h} \cdot W_O^{h \times h}$，运算量为$2bLh^2$；

MLP层计算量：

MLP层的计算可以表示为：$x=f(x_{out}W_1)W_2 + x_{out}$

- 计算$x_{mid} = x_{out}W_1$：$x_{out}^{b\times L \times h} \cdot W_1^{h \times 4h}$，运算量为$8bLh^2$；
- 计算$x_{mid}W_2$：$x_{mid}^{b\times L \times 4h} \cdot W_2^{4h \times h}$，运算量为$8bLh^2$；

综上，一层transformer decoder进行一次前向计算的计算量：$24bLh^2 + 4bL^2 h$。

在前向传播中，输出token总数为$bL$，模型总参数量为$12h^2 + 13h$，可以计算出，每个token，每个参数需要的浮点数计算次数为 $\frac{24bLh^2 + 4bL^2 h}{bL \cdot (12h^2 + 13h)}=\frac{24h + 4L}{12h + 13} \approx 2$，即，前向传播一次，每token、每个参数需要进行2次浮点数运算（flops），反向传播所需计算量是前向传播的2倍$^1$，因此，前向+反向传播，每token、每个参数需要进行6次浮点数运算（flops）。

以GPT3-175B为例，其参数为$174600M$，训练数据为$300B$，则训练所需总运算量为：$6 \* 174600 \* 10^6 \* 300 \* 10^9 \approx 3.143 \times 10^{23} flops$。


## 训练时间估算

在实际训练中，为了节省中间激活的显存占用，通常会在反向传播时进行一次重计算，因此会引入一次额外的前向传播，此时，一次完整的前向-反向传播，每token每参数共需要进行8次浮点数运算，训练时间估计可以参考如下公式：

$$T = \frac{8 \times N_{tokens} \times N_{parameters}}{GPU数 \times GPU峰值flops \times GPU平均利用率}$$

以GPT3-175B为例，需要的训练时间为$\frac{8 \* 300 \* 10^9 \* 174600 \* 10^6}{1024 \* 312 \*10^{12} \* 0.45} \approx 2921340s \approx 34 days$


<img src="https://imgbed4s.oss-cn-beijing.aliyuncs.com/%E6%88%AA%E5%B1%8F2024-03-23%2013.59.28.png" alt="gpt3-train" width="70%" >

<center>Calculations of GPT3</center>


## 参考

1. [浅谈后向传递的计算量大约是前向传递的两倍](https://zhuanlan.zhihu.com/p/675517271)
2. [分析transformer模型的参数量、计算量、中间激活、KV cache](https://zhuanlan.zhihu.com/p/624740065)
3. [Language Models are Few-Shot Learners](https://arxiv.org/pdf/2005.14165.pdf)
4. [Attention is all you need](https://arxiv.org/pdf/1706.03762.pdf)