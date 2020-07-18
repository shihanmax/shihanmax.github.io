---
title:  "网络中的多C-P结构检测"
layout: post
date:   2018-12-13 00:00:00
categories: Algorithm
tags:  "CP"
syntaxHighlighter: yes
Mathjax: true
---


# Finding multiple core-periphery pairs in networks

## Abstract

在一个包含C-P结构的网络中，core节点之间紧密连接，periphery节点与core节点紧密相连，而periphery节点之间稀疏连接。目前单核识别已有实现方法，在实际网络中，就像“社区”由多个密集团组成一样，网络也应该由多个C-P结构组成。本文提出了一个可扩展的、可以检测多核心结构（不重合）的方法，我们借助人工网络和真实网络阐述我们的算法，例如，在政治论坛网络中的政治倾向以及世界航线网络中发现了明显的C-P结构。

<!--more-->

## I. Introduction

许多复杂系统都可以看做由node和edge组成的图（network），edge表示node之间的关系。网络有微尺度、中尺度和宏观尺度的结构特征，如度，聚类系数，直径等，在中尺度结构中，社区结构（community structure）比较具有代表性，社区是指一组节点：该组组内节点间紧密连接，而与其他组节点稀疏连接。一个社区中的节点通常会共享一些特征（share a role）。社区发现有助于节点分类和网络可视化。

C-P结构是网络的另一个中尺度结构，在这种结构的视角下，我们认为网络是由两组分别称为core和periphery的节点集合构成。尽管定义多种多样，core一般是一组互相紧密连接的节点集合，periphery一般是一组与core节点紧密连接，但组内稀疏链接的节点集合。core和社区都由紧密连接的节点构成，但它们之间有区别：core和它的periphery紧密连接，而社区与社区外的节点则不是。在许多网络中都发现了C-P结构[^11、12、13、15、16、17、18、22、24、25、26、27、28]。例如，在研究者网络中，顶尖研究者往往与顶尖研究者一起发表论文，他们形成一个core，而其他研究者往往会与某个顶尖研究者合作发表论文，这些研究者形成一个periphery。

Borgatti与Everett（以下简称BE）首先定量地提出C-P结构，在离散形式（discrete）C-P模型中，他们提出一种理想化的C-P结构，在这种结构中，core节点与所有节点相连，periphery节点与所有core节点相连，而与periphery节点无连接。虽然“C-P之间的连接程度（connectivity）仅比C-C之间更稀疏”这一说法更加现实，但在本文中，我们仅关注理想化的C-P结构。BE期望将网络中所有节点分配给C或P（assignment
of all nodes in a given network to a core or periphery ），使得网络与理想化的C-P模型最为接近。在BE提出C-P结构的定义之后，许多研究者提出了C-P结构检测的算法[^11-13,15-18,20-22,25,27]这些算法主要关注识别网络中的单C-P结构 。然而，将网络看做由多个C-P结构组成，或许更加合适[^11,14,16,19-21]，这也是当前研究的重点。例如，论文合作网络（co-authorship）可能就由多个研究成员小组（researcher group）组成，研究者往往倾向于与组内的顶尖研究者合作，而不与组内其他研究者合作。这会导致在组内形成C-P结构[^16]，前述研究未能提供一个可扩展的多核检测方法。也有研究关注于相似但类型不同的多C-P结构的检测[^30]。其他算法仅仅关注多核心的检测但并不假定“边缘节点间稀疏连接”[^17,31,32]。网络可以以k-score[^33]、k-trusses[^34]或密集子图（dense subgraphs）[^35,36]的形式拥有多个互斥的core，但是，相关的算法不能指出，边缘节点之间的联系的紧密程度或者，边缘节点属于哪一个核心（to which core a peripheral node belongs）。这个能够检测网络中多个中尺度结构（包括C-P pair）的算法[^19]的计算复杂度很高，而且只适用于小型网络（参见Appendix A）。

我们提出了一个灵活的检测网络中多个无重叠C-P结构的算法，在这些C-P结构中，每个都尽量与理想C-P结构接近，而且还可以自动确定C-P结构的数量和尺寸。许多检测C-P结构的算法都被归结为density-based和transport-based算法[^15,21,25]。density-based算法假定core是紧密连接的节点集合，而transport-based算法认为core是别的节点可以通过较短的路径到达（can be reached from other nodes along short paths ）的节点集合。本研究中，我们使用前者，即density-based算法。

## II. Methods

### A. Algorithm

我们针对多核心情况，对BE[^11]提出的C-P结构进行了扩展。在BE算法中，我们考虑一个具有$N$个节点、$M$条边的网络（以下与图同义），$A =(A_{ij})$是邻接矩阵，如果节点$i$和节点$j$之间有边，令$A_{ij}=1$，否则$A_{ij}=0$。我们假设图是无向无权图，没有自环路（self-loop），也即对所有的$i$和$j$，有$A_{ij}=A_{ji}$并且$A_{ii}=0$。定义$x=(x_1,x_2, ..., x_N)$是长度为$N$的向量，如果节点$i$是边缘节点，则$x_i=0$，否则$x_i=1$。我们定义，网络中理想的C-P结构中：每个的core节点都和core节点或periphery节点相连，每个periphery节点都和所有的core节点相连但不和其他的periphery节点相连。对应的灵界矩阵为$B(x)=(b_{ij}(x))$，如下给出：

$$B_{ij}(x)=\left\{
\begin{aligned}
&1&(x_i=1\ or\ x_j=1,\ and\ i\not=j), \\
&0&(otherwise)
\end{aligned}
\right.      \quad (1)$$

我们使用BE提出的离散模型：即寻找$x$，使得$A$与$B$具有最高的相似度。我们将在Section II C中阐述相似度计算方法。针对多核情况，我们对理想的C-P结构进行扩展，令$C$是C-P pair的个数，$c=(c_1,c_2, ..., c_N)$是长度为N的向量，$c_i\in\{1,2,...,C\}$表示节点$i$属于哪一个C-P pair，这里排除了C-P pair之间交叉以及C-P pair内，core与periphery部分交叉的情况。（也即，任何一个节点，只可能属于某一个C-P，且只可能属于该C-P中的C或P，而不能二者兼是。）对应的$B(c,x)$矩阵定义如下

$$B_{ij}(c,x)=\left\{
\begin{aligned}
&\delta_{c_i,c_j}&(x_i=1\ or\ x_j=1,\ and\ i\not=j), \\
&0&(otherwise)
\end{aligned}
\right.      \quad(2)$$

其中$\delta$是克罗内克（Kronecker ）delta。

我们通过最大化以下参数来寻找$(c,x)$使得$B(c,x)$与$A$最为接近：

$$\begin{aligned}Q^{cp}(c,x)&=\sum^N_{i=1}\sum^{i-1}_{j=1}A_{ij}B_{ij}(c,x)-\sum^N_{i=1}\sum^{i-1}_{j=1}pB_{ij}(c,x)\\
&=\sum^N_{i=1}\sum^{i-1}_{j=1}(A_{ij}-p)(x_i+x_j-x_ix_j)\delta_{c_i,c_j}
\end{aligned}$$

其中，$p=M/[N(N-1)/2]$是网络中边的密度（density of edges）。项$\sum^N_{i=1}\sum^{i-1}_{j=1}A_{ij}B_{ij}(c,x)$表示同时在给定图与理想C-P图共现边的个数。null-model项$\sum^N_{i=1}\sum^{i-1}_{j=1}pB_{ij}(c,x)$是期望的理想C-P图和Erdős Rényi随机图（在该图中，节点以概率$p$互相连接，以下简称ER随机图）的**共现边**（如果给定图的1#和2#节点有边，且理想C-P图的1#和2#节点有边，称该边为两个图的共现边）的个数。$Q^{cp}$的范围是$-M$到$M$。较大的$Q^{cp}$表示给定图与理想C-P图之间的共现边个数比随机情况更多。ER随机图在C-P结构分析中广泛使用[^13,24,28,29,38,39]，与社区发现中的模块化类似（similar to modularity for community detection），我们的定义允许使用多种null model，如configuration model，更多讨论详见section V。

### B. Maximisation of $Q^{cp}$

我们使用标签切换的启发式算法（label switching heuristic ）[^40, 41]来最大化$Q^{cp}$。开始时，我们通过设置$(c_i,x_i)=(i,1)(1\le i\le N)$把每一个节点都分配到一个不同的核心，然后乱序地扫描所有的节点，扫描到的节点$i$时，暂时性地更新$(c_i,x_i)$到它的邻接节点所属的C-P结构，比如$(c_j,1)$，然后计算$Q^{cp}$的增量。我们也会计算将$(c_i,x_i)$更新到$(c_j,0)$时，$Q^{cp}$的增量。注意到，不论$x_i=0$或$x_i=1$，上述两种情况（cases）都会执行。在每种情况下，我们对节点i的所有邻居（neighbours）都执行此方法来计算$Q^{cp}$的增量（increment）。最终，我们将$(c_i,x_i)$更新到使得$Q^{cp}$暂时增量最大的标签（例如，对neighbour $j$，$(c_j,0)$或$(c_j,1)$）。如果某个标签切换过程（relabelling）未能使得$Q^{cp}$增加，就不会更新$(c_i,x_i)$。当所有节点扫描完毕的时候，如果当前轮（round）所有节点的标签都未改变，算法流程结束；否则，重新随机产生一组节点顺序，依照该顺序，重复执行上述过程。

当节点$i$的标签（label）由$(c,x)$更新到$(c',x')$时，$Q^{cp}$的增量由下式给出：

$$[待填写]$$

这里，$\tilde{d}_{i,(c',1)}$是节点i的所有邻居中标签为$(c,x)$的节点个数；$\tilde{N}_{c,x}$是标签为$(c,x)$的节点的数量，对扫描到的节点$i$，公式$(4)$最多会被计算$2d_i$次（$d_i$是节点$i$的度），因此，每轮（round）扫描所有节点的时间复杂度是$O(\sum^N_{i=1}d_i)=O(M)$，所以整个算法的时间复杂度是$O(rM)$（$r$是轮数）。在相同初始条件的情况下，执行20次算法过程，并取使$Q^{cp}$最大的那个。

### C. Significance of the core-periphery structure（C-P结构的显著性）

检测出的C-P结构在统计意义上可能是非显著的[^11,38]，因此，我们把针对单C-P结构检测的统计测试方法推广到多C-P情况中。

在单C-P结构的统计测试中[^38]，我们使用基于皮尔森相关系数[^11]的质量函数来衡量一个C-P结构的显著性，该质量函数的定义如下：

$$【待补充】$$

这里，$p_B=\sum^N_{i=1} \sum^{i-1}_{j=1} B_{ij}(x) / [N(N-1)/2]$。对检测出的C-P结构，如果计算出的$Q^{cp}_{BE}$比在ER随机图模型上计算出的$Q^{cp}_{BE}$值更大，则认为该C-P结构是显著的。（注意，该ER随机图模型的边的数量要与待检测图的边数相等，另外，可以生成多个参数相同的ER图，计算出最大的$Q^{cp}_{BE}$）。使用KL算法（Kernighan-Lin ）[^42]来最大化$Q^{cp}_{BE}$。如果待检测图的$Q^{cp}_{BE}$比随机图的$Q^{cp}_{BE}$大$1-\alpha$，认为该C-P结构的显著性水平为$\alpha$。

在多C-P结构的情形下，我们实质上对检测出的每一个C-P结构均作了类似的显著性测试。对每一个检测到的C-P结构，我们首先计算$Q^{cp}_{BE}$；然后，我们生成3000个与C-P结构图（注：该C-P结构包含的节点所组成的小图）的边和节点数相同的ER随机图模型，在统计边数时，我们只考虑与C-P结构相连的边的个数；其次，我们使用KL算法，通过最大化$Q^{cp}_{BE}$来检测随机矩阵中的单C-P结构；最后，我们对比待检测图C-P结构和随机矩阵的$Q^{cp}_{BE}$，如果某个C-P结构被认定为是不显著的，我们称该结构中包含的节点为残余节点。它们不属于任何一个C-P结构。

如果我们以$\alpha$的显著性水平检测到了C个C-P pair，则至少有一个flase positive（假正例，如，一个非显著的C-P对被检测为显著的）的概率是$1-(1-\alpha)^C$，这个概率随着$C$的增大而增大。为了减轻这种多对比的问题（To remedy this multiple comparison problem ），我们使用Šidák correction方法，我们以$\alpha_1=1-(1-\alpha)^{1/C}$（也即$1-(1-\alpha)^C=\alpha$）的显著性水平检测每一个C-P。并将$\alpha$设为0.01。

我们使用由KL算法得到的最大化的$Q^{cp}_{BE}$来进行显著性检测，其实也可以使用其它的算法来最大化$Q^{cp}_{BE}$。当然，我们也可以使用不同的统计测试方案，*比如，限制在单C-P结构中的$Q^{cp}$*。

## III. Variation of information

对于包含C-P结构的人工网络，我们通过计算$VI$的值来对比网络中的真实C-P结构$(c,x)$和用本算法检测出的C-P结构$(\hat{c},\hat{x})$，$VI$的计算方法如下：

$$[daubuh]$$

这里$P(c,x;\hat{c},\hat{x})$是真实标签为$(c,x)$，预测标签为$(\hat{c},\hat{x})$的节点的比例（the fraction of nodes that have the true label $ (c, x)$ and inferred label $(\hat{c},\hat{x})$）当且仅当$VI$的值为0的时候，检测到的C-P结构和真实的C-P结构相同。我们通过取100次计算的平均值来衡量算法在人工网络上的效果。

## IV. Result



## V. Discussion
