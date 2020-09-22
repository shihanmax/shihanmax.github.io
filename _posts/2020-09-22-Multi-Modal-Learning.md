---
title:  "多模态学习"
layout: post
date: 2020-09-22 22:35:01
categories: NLP
tags:  Multi-modal learning
syntaxHighlighter: yes
Mathjax: true
---

多模态学习是深度学习领域中一个比较热门的方向，本文记录一下这个方向的相关论文，方便参考。

## 1. one model to learn them all

本文提出了一个多模态模型，将8个任务融合在一个模型中，具体包含：

- Parsing
- Speech recognization
- ImageNet classification
- Image caption
- Translation

模型在各个任务上都取得了不错的效果，部分超过了一些新模型（虽然还没有达到sota水平）。

作者认为，本文有两个主要贡献（对多模态网络至关重要的两点）：

1. 信息通过各个模态相关的小型网络转换到一个通用的中间形态，再由该中间形态通过不同的模态网络转化为输出
   - 中间表示层的尺度是可变的
   - 同一领域下，不同任务共享模态网络
2. 各种任务对各个子计算模块的重要性依赖程度不同（如，attention机制在翻译任务中的重要程度高于其在image caption任务中的影响）

### 模型结构

模型的整体结构分为三部分：

1. encoder
2. I/O Mixer
3. AR decoder

在encoder和decoder中，主要包含以下计算组件（computational blocks）：

1. conv

   局部特征捕获，使用depthwise separable conv

2. attention layer

   关注重要的特征

3. 稀疏门限模块集成（Sparsely-gated mixture-of-experts）

   在保证计算复杂度的前提下，增大模型容量，由一系列前馈网络和可训练的门限网络构成，负责从各个输入中选择稀疏的组合

为了适应各个任务的形态，本文提出了一些任务相关的子网络（模态网络，Modality-nets），主要包括：

1. 语言模态网络
2. 图像模态网络
3. 类别模态网络（Categorical modality net）
4. 语音模态网络

### 实验部分

实验部分，本文回答了三个问题：

1. 本文提出的MultiModel在8个子任务上，离sota还有多远？

   看论文结果，应该还是有一段距离，作者表示由于没有仔细调参，当前多模态模型的结果还无法超越经过细致调参的传统模型。

2. 同时训练8个子任务，与分别训练有什么差别？

   在训练多模态模型的同时 ，作者在同等条件下同时训练了独立的模型，实验结果表明多模态联合训练时的结果与独立训练各个任务相似，在个别任务上甚至有一些提升，训练数据越少的任务，提升通常会越明显。

3. 不同的计算组件（computational blocks）在子任务上的影响如何？

   这些组件的存在，至少不会带来子任务性能的下降。

多模态网络设计的要点在于，任务间能够共享的参数尽量要在模态间共享，这有助于不同模态之间表示空间的统一，同时也能降低task-specific的参数量，控制模型的尺寸。

Refs.

[Depthwise separable conv](http://arxiv.org/abs/1610.02357)

[Outrageously large neural networks: The sparsely-gated mixture-of-experts layer](https://arxiv.org/abs/1701.06538)

[One model to learn them all](https://arxiv.org/pdf/1706.05137.pdf)



