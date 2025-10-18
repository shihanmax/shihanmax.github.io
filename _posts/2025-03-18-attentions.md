---
date: 2025-03-18 20:37:50
display_type: post
layout: post
mathjax: true
syntaxHighlighter: true
title: Attentions
tags: ["Deep Learning", "NLP", "attention"]
---

## 1. 背景与动机

Attention机制最早在machine translation中被提出，用于seq2seq的解码过程中与encoder作注意力计算。

在传统seq2seq模型中，输入通过encoder计算得到一个固定维度的中间向量（context vector），decoder接受中间向量后解码得到输出。这里存在一个关键问题：**固定维度的中间向量容量有限，无法完整保留长序列的所有信息**，导致信息瓶颈问题。针对这个现象，[Bahdanau et al., 2015](https://arxiv.org/pdf/1409.0473.pdf)提出了attention机制。

## 2. Seq2Seq中的Attention

以一般的seq2seq模型为例，定义如下：

**符号定义：**
- 输入序列：$\mathrm{x}=[x_1, x_2, ...,x_n]$
- 输出序列：$\mathrm{y}=[y_1, y_2,...,y_m]$
- Encoder RNN在第$i$时刻的隐状态：$\mathrm{h}_i=[\overrightarrow{h_i}^T;\overleftarrow{h_i}^T]^T, i=1,2,...,n$
- Decoder RNN在第$t$个时间步的隐状态：$\rm{s}_t=f(\rm{s}_{t-1},y_{t-1},\rm{c}_t)$

**Context vector计算：**

$$\rm{c}_t = \sum_{i=1}^{n} \alpha_{ti} \mathrm{h}_i$$

其中$\alpha_{ti}$是attention权重，表示在生成第$t$个输出时，对第$i$个输入位置的关注程度。

**Attention权重计算：**

$$\alpha_{ti} = \frac{\exp(e_{ti})}{\sum_{j=1}^{n}\exp(e_{tj})}$$

$$e_{ti} = a(\rm{s}_{t-1}, \mathrm{h}_i)$$

这里$a(\cdot)$是alignment函数（或称为scoring function），用于计算query和key之间的相关性。

## 3. 常见的Attention变体

### 3.1 按信息来源分类

- **Content-based Attention**: 基于内容计算attention权重，依赖于query和key的语义相关性
- **Location-based Attention**: 基于位置信息计算attention权重，主要用于图像等有空间结构的数据

### 3.2 经典Attention机制

#### 3.2.1 Bahdanau Attention (Additive Attention)

最早提出的attention机制，使用加性模型计算alignment score：

$$e_{ti} = \mathbf{v}^T \tanh(\mathbf{W}_1 \rm{s}_{t-1} + \mathbf{W}_2 \mathrm{h}_i)$$

其中$\mathbf{v}, \mathbf{W}_1, \mathbf{W}_2$是可学习参数。

**特点：**
- 使用单层前馈神经网络
- 参数量：$d_h \times d_s + d_h \times d_h + d_h$
- 计算复杂度：$O(n \times d_h)$

#### 3.2.2 Luong Attention (Multiplicative Attention)

[Luong et al., 2015](https://arxiv.org/pdf/1508.04025.pdf)提出了三种变体：

**(1) Dot Product:**

$$e_{ti} = \rm{s}_{t}^T \mathrm{h}_i$$

- **前提条件**: $\rm{s}_t$和$\mathrm{h}_i$维度必须相同
- **优点**: 计算最简单，无参数
- **缺点**: 无法学习query和key之间的变换关系

**(2) General (Bilinear):**

$$e_{ti} = \rm{s}_{t}^T \mathbf{W} \mathrm{h}_i$$

- **参数量**: $d_s \times d_h$
- **优点**: 可以学习query和key之间的映射关系
- **适用**: query和key维度可以不同

**(3) Concat (Additive):**

$$e_{ti} = \mathbf{v}^T \tanh(\mathbf{W}[\rm{s}_{t}; \mathrm{h}_i])$$

- 与Bahdanau类似，但使用拼接而非分别变换
- 参数量：$(d_s + d_h) \times d_h + d_h$

#### 3.2.3 Scaled Dot-Product Attention

[Vaswani et al., 2017](https://arxiv.org/pdf/1706.03762.pdf)在Transformer中提出，是目前最广泛使用的attention机制：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

**关键创新：**

1. **显式的Q, K, V表示**：
   - $Q = XW_Q$ (query matrix)
   - $K = XW_K$ (key matrix)  
   - $V = XW_V$ (value matrix)

2. **Scaling factor** $\frac{1}{\sqrt{d_k}}$：
   - **目的**: 防止点积结果过大导致softmax梯度消失
   - **原理**: 当$d_k$较大时，$q \cdot k$的方差为$d_k$，缩放后方差恢复为1
   - **效果**: 使softmax输入保持在合理范围，避免进入饱和区

**计算流程：**

假设输入序列长度为$n$，embedding维度为$d$：

1. 线性变换：$Q, K, V \in \mathbb{R}^{n \times d_k}$（通常$d_k = d_v = d/h$，$h$为head数量）
2. 计算相似度：$QK^T \in \mathbb{R}^{n \times n}$
3. 缩放：除以$\sqrt{d_k}$
4. Softmax归一化：得到attention权重矩阵
5. 加权求和：与$V$相乘得到输出

**复杂度分析：**
- 时间复杂度：$O(n^2 d_k)$
- 空间复杂度：$O(n^2)$（需存储attention矩阵）

## 4. Self-Attention vs Cross-Attention

### 4.1 Self-Attention（自注意力）

$Q, K, V$来自**同一个序列**：

$$Q = K = V = X$$

**作用**：捕获序列内部元素之间的依赖关系

**应用场景**：
- Transformer Encoder
- BERT等预训练模型
- GPT的causal self-attention

**示例**：在句子"The animal didn't cross the street because it was too tired"中，self-attention可以让模型学习到"it"指向"animal"。

### 4.2 Cross-Attention（交叉注意力）

$Q$来自一个序列，$K, V$来自**另一个序列**：

$$Q = X_{\text{target}}, \quad K = V = X_{\text{source}}$$

**作用**：建模两个序列之间的交互关系

**应用场景**：
- Transformer Decoder（连接encoder和decoder）
- 机器翻译
- 图像captioning（文本attend to图像特征）
- Vision-Language模型（CLIP, BLIP等）

## 5. Multi-Head Attention

**核心思想**：并行运行多个attention head，每个head关注不同的表示子空间。

**公式定义**：

$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, ..., \text{head}_h)W^O$$

$$\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$$

**参数设置**：
- Head数量：$h$（通常为8或16）
- 每个head的维度：$d_k = d_v = d_{\text{model}}/h$
- 投影矩阵：$W_i^Q, W_i^K, W_i^V \in \mathbb{R}^{d_{\text{model}} \times d_k}$
- 输出投影：$W^O \in \mathbb{R}^{hd_v \times d_{\text{model}}}$

**优势**：
1. **多样性**: 不同head可以关注不同类型的依赖关系（如语法、语义、位置等）
2. **表达能力**: 增强模型的表示能力而不增加总计算量
3. **鲁棒性**: 多个head提供冗余，提高稳定性

**计算复杂度**：
与单个scaled dot-product attention相同：$O(n^2 d)$

## 6. Causal/Masked Attention

**应用场景**：自回归语言模型（GPT系列）

**核心机制**：在计算attention时，对未来位置进行mask，确保位置$i$只能attend到位置$\leq i$的token。

**实现方式**：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T + M}{\sqrt{d_k}}\right)V$$

其中mask矩阵$M$：

$$M_{ij} = \begin{cases}
0 & \text{if } i \geq j \\
-\infty & \text{if } i < j
\end{cases}$$

**Attention矩阵可视化**：
```
      k1  k2  k3  k4
q1 [  ✓   ✗   ✗   ✗  ]  (只能看到k1)
q2 [  ✓   ✓   ✗   ✗  ]  (只能看到k1, k2)
q3 [  ✓   ✓   ✓   ✗  ]  (只能看到k1, k2, k3)
q4 [  ✓   ✓   ✓   ✓  ]  (可以看到全部)
```

## 7. Attention机制的现代应用

### 7.1 Natural Language Processing

- **BERT**: Bidirectional self-attention用于预训练
- **GPT系列**: Causal self-attention用于文本生成
- **T5**: Encoder-decoder架构，同时使用self和cross-attention
- **LLaMA/Llama 2/3**: 使用Grouped-Query Attention（GQA）减少KV cache

### 7.2 Computer Vision

- **Vision Transformer (ViT)**: 将图像分割成patches，使用self-attention
  - 输入：$16\times16$或$32\times32$的image patches
  - Position embedding：添加位置信息
  - 全局感受野：每层都能看到全图
  
- **DETR (Detection Transformer)**: 
  - Object detection的端到端方案
  - Object queries通过cross-attention从图像特征中提取目标
  - 消除了NMS等hand-crafted组件

- **Swin Transformer**: 
  - Shifted window attention降低复杂度到$O(n)$
  - 层级结构，适合密集预测任务

### 7.3 Multimodal

- **CLIP**: Vision-text对比学习，使用双编码器架构
- **BLIP**: 使用cross-attention融合图像和文本
- **Flamingo**: Few-shot learning，cross-attention连接vision和language

### 7.4 Audio/Speech

- **Whisper**: 语音识别，encoder-decoder transformer架构
- **AudioLM**: 音频生成
- **MusicGen**: 音乐生成，使用multi-stream modeling

## 8. 效率优化变体

标准attention的$O(n^2)$复杂度在长序列上成为瓶颈，催生了众多高效变体：

### 8.1 Linear Attention
- **Linformer**: 将$K, V$投影到低维：$O(n)$复杂度
- **Performer**: 使用随机特征近似softmax：$O(n)$复杂度

### 8.2 Sparse Attention
- **Sparse Transformer**: 固定稀疏模式
- **Longformer**: Sliding window + global attention
- **BigBird**: Random + window + global attention

### 8.3 FlashAttention
- **核心创新**: IO-aware算法，优化GPU内存访问
- **效果**: 2-4x加速，支持更长上下文
- **应用**: 广泛用于GPT-4、LLaMA等模型训练

### 8.4 Grouped-Query Attention (GQA)
- **动机**: 减少KV cache大小，降低推理成本
- **方法**: 多个query head共享同一组KV head
- **应用**: LLaMA 2, Mistral等模型

## 9. Attention权重可视化与可解释性

Attention权重提供了一定的可解释性：

- **词级别关系**: 可视化哪些词对当前词的预测最重要
- **句法结构**: 某些head学习到句法依赖关系
- **语义对应**: 翻译任务中source和target的对齐关系

**注意事项**：
- Attention权重≠因果关系
- Multi-head中不同head关注点不同
- 深层网络的attention解释性较弱

## 10. 实现要点

### 10.1 数值稳定性
- Softmax前进行scaling（$1/\sqrt{d_k}$）
- 使用log-space计算避免overflow

### 10.2 掩码机制
- Padding mask：处理变长序列
- Causal mask：自回归生成
- Attention mask：控制可见范围

### 10.3 位置编码
- Absolute: Sinusoidal或learnable
- Relative: T5-style相对位置编码
- Rotary (RoPE): 旋转位置编码，用于LLaMA等

## 参考文献

1. [Bahdanau et al., 2015] Neural Machine Translation by Jointly Learning to Align and Translate
2. [Luong et al., 2015] Effective Approaches to Attention-based Neural Machine Translation  
3. [Vaswani et al., 2017] Attention Is All You Need
4. [Dosovitskiy et al., 2020] An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale
5. [Dao et al., 2022] FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness