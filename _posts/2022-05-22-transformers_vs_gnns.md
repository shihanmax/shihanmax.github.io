---
title:  "Transformers and GNN"
layout: post
date: 2022-05-22 12:46:05
tags:  ["Deep Learning", "GNN"]
syntaxHighlighter: yes
mathjax: true
---

在推荐系统、社交网络等场景中，图神经网络（Graph Neural Networks）的应用比较广泛，近年来一些GNN的变种如GCN（Graph convolutional Network）、GraphSAGE (Graph SAmple and aggreGatE)、GAT (Graph Attention Network)、GRN（Graph Recurrent Network）等在深度学习领域内逐渐引起关注，有一些模型在NLP领域也取得了不错的成绩。

卷积神经网络（CNN）或递归神经网络（RNN）可以处理规整的输入（eg., grid-like structure$^{1}$），比如对于图像，可以看做一个张量，其中任意一个元素周围总是具有相同的结构，这样我们便可以使用一个卷积核对所有位置的元素进行投影和聚合；又比如可以将文本视为一个一维的token序列，使用RNN依序对每一个token进行处理（同时考虑上文的信息）。图神经网络的一个优势在于，其可以处理非结构化的数据，比如，在一个图中的两个节点，其一度、二度、..，邻居节点的数量不相同，但GNN可以对这种结构进行特征抽取。

Transformer结构是2017年提出的一种基于自注意力的特征抽取器，目前在NLP领域应用非常广泛，基于其搭建的预训练模型也曾出不穷。

这篇文章关注图神经网络中的图自注意力网络（GAT）和Transformer在结构上的相似性。记得在前司做相关的项目时，有位大佬（此处@生哥）就曾说“BERT（当然指的是transformer了）就是GAT在全连接情况下的特例”。最近有空来梳理一下这两种结构后，不仅可以发现二者结构上的相似性，更能从“离散节点的信息融合”这个角度重新认识这两种特征抽取器。

## GAT

我们先看一下GAT的实现。GAT的基本单元是Graph Attention Layer (GAT)，我们暂且称其为图注意力层，该层接收图上的一组节点的特征$\mathrm{h}=\\{\vec{h}_1, \vec{h}\_2 ,...,\vec{h}\_N \\}, \vec{h}\_i \in \mathbb{R}^F$，其中$N$是节点个数，$F$是节点特征向量维度。经过注意力层运算后，输出每个节点对应的新的特征：$\mathrm{h}'=\{\vec{h'}_1, \vec{h'}\_2 ,...,\vec{h'}\_N\}$。GAT是迭代式的，每一次迭代时，根据当前节点$i$自身的特征及其周围邻居节点的特征，通过一系列变换计算得到该节点的此轮迭代后的特征，在对其他节点的信息进行聚合时，为了考虑到不同节点的影响，GAT引入了Attention机制，具体地，对于节点$i$和节点$j$，它们之间的注意力系数可以计算为：

$$e_{ij}=a (\textrm{W} \vec{h_i} , \textrm{W} \vec{h_j})$$

其中，$\textrm{W} \in \mathbb{R}^{F' \times F}$是可训练的参数矩阵，$a(\cdot)$表示一种注意力机制：$a: \mathbb{R}^{F'} \times \mathbb{R}^{F'} \rightarrow \mathbb{R}$，这里作者引入了masked attention，即认为，计算注意力系数时，仅考虑节点的一阶邻居，通过这种方式保留图的结构信息。计算出节点$i$和所有邻居节点的注意力系数$e_{ij}$之后，进行一次归一化：

$$\alpha_{ij} = \textrm{softmax}_j(e_{ij})$$

在GAT中，作者使用一个投影层来实现$a(\cdot)$，具体地，

$$e_{ij}= \textrm{LeakyReLU}( \vec{\textrm{a}}[ \textrm{W}\vec{h}_i \Vert \textrm{W} \vec{h}_j ])$$

其中，$\Vert$表示向量拼接。


$$$$
## Transformer


Refs:

[1. GAT: GRAPH ATTENTION NETWORKS](https://openreview.net/pdf?id=rJXMpikCZ)
[2. ]()
[3. ]()
[4. ]()
[5. ]()
