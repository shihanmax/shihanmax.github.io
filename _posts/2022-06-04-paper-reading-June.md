---
title:  "Paper Reading: 6月"
layout: post
date: 2022-06-04
tags:  ["Paper Reading"]
syntaxHighlighter: yes
mathjax: true
---

[导航：汇总页](/2022/05/14/paper-reading/)

## W1 (2022-06-05)

### [An Empirical Study of Memorization in NLP](https://arxiv.org/pdf/2203.12171.pdf)

#### Motivation

Feldman$^1$提出了长尾理论（long-tail theory）来解释深度学习模型中的“记忆行为”（memorization behavior），NLP领域缺少对其的实验验证。长尾理论认为，在模型训练过程中，训练集中存在的非典型的长尾样本，如果这些样本在测试集中出现过，那么记忆住这些样本对于提升模型的泛化能力就会有帮助。

#### Contribution

本文在三种NLP任务上，通过实验验证了长尾理论的存在性，实验表明，最易被模型记忆的那些样本（top-ranked instances）并非典型的，去掉他们会导致模型在测试集上的效果下降明显。另外，作者提出了一种归因方式，来解释样本为什么会被模型记忆。实验结果证明，那些top-memorized 样本包含的特征往往和类别标签是负相关的。

作者在本文尝试回答3个问题：

1. 在NLP任务中，被模型记忆的样本是否是非典型的样本（atypical instances）
2. 如果模型记住了这些样本，会导致其在测试集上的泛化能力提升吗？
3. 我们是否可以解释，为什么样本会被模型记忆（比如是否可以量化地计算出每个token被记忆的程度）

#### method

作者在情感分类、NLI和文本分类三个任务上进行实验。

首先，对于训练集的某个样本$z=(x,y)$，对其的记忆可以理解为，去掉这个样本后，模型对其的预测结果的变化情况。在$^2$中，作者对一个样本的记忆定义为，去掉这个样本（或减小其在训练集中的权重），对测试集loss的影响。作者参考$^2$的实现，定义了对样本的记忆分数。

在记忆归因方面（即如何更好地认识记忆现象，比如为什么被模型记忆了，哪些部分容易被模型记忆之类的），作者不是仅仅在样本级别分析模型为什么被记住了，在NLP场景下，作者希望从每一个token的角度来分析。作者参考$^3$，定义了基于提督的归隐方法。

## W2 (2022-06-12)

### [Are Prompt-based Models Clueless?](https://aclanthology.org/2022.acl-long.166.pdf)

#### Motivation

基于prompt的模型通过将任务转化为预训练任务类似形式的方式，提高了模型的泛化能力，那么其是否会利用superficial cues呢？本文通过实验，在NLI和阅读理解两类任务上讨论了这一问题。

> Superficial cues can be described as linguistic or non-linguistic characteristics of instances that have nothing to do with the task itself but are tied to a specific task label. These characteristics include lexical overlap, distinct words frequently appearing in the correct choices, and distinctive style of the correct choices.

#### Contribution

作者定义不同任务中的context：对NLI任务，其前提假设（premise）为context，对于阅读理解，其问题（question）作为context。并将任务相关的superficial cues分为两类：

- context superficial cues
- contextless superficial cues

前者表示与context重叠的词汇，后者表示仅在hypothesis（对NLI任务）或multiple-choice（对阅读理解任务）中出现的词汇。

作者通过对MNLI、SNLI、COPA的分析发现，其中包含了更多的表面信息（superficial cues）；并且通过实验验证了基于prompt的模型也依赖superficial cues。

#### method

如何构建包含/不包含superficial cues的测试集呢？作者的做法如下：对于NLI任务，由于HANS数据集可以利用三类信息：lexical overlap、subsequence、constituent，因此不必再进行数据集划分。对于阅读理解任务，作者将多项选择的答案中的token重新随机排列，以此来降低其中包含的语义信息，而迫使模型能够通过superficial cues来完成任务，针对重排列后的数据集，作者使用roberta模型来训练/预测模型，发现其在测试集上的准确率可以达到78%，对于模型分类正确的样本，作者认为其包含了superficial cues，将它们划分到一个集合中；将其与样本划分到另一个集合中。

本文得出以下结论：

1. 在MNLI、SNLI和COPA数据集上，prompt-based模型会利用superficial cues；
2. 在COPA数据集上，当训练样本小于32个样本时，prompt-based模型不会利用superficial cues，但当增加样本数量时，模型在包含/不包含contextless superficial cues的数据集上的性能差距会增加；


## W3 (2022-06-19)

### [ON LAYER NORMALIZATION IN THE TRANSFORMER ARCHITECTURE](https://openreview.net/attachment?id=B1x8anVFPr&name=original_pdf)

#### Motivation

Transformer结构在NLP领域的应用十分广泛，在训练此类模型时，我们一般需要对学习率进行warmup操作，即在开始练时，先设置一个极小的学习率，再以一个预设的增长曲线缓慢增加学习率。在实践中，这一过程的设置对模型最终效果是至关重要的。

训练一个基于Transformer的模型，需要小心设置学习率和其warmup策略，文章$^{4,5}$的研究佐证了这一观点，并且，由于初始学习率较小，也会导致训练时间延长。

#### Contribution

本文探究“为什么学习率warmup策略对训练过程如此重要”，发现LayerNorm层的位置可能是其中的一个重要影响因素。原生Transformer 的实现中，LayerNorm层位于残差网络的后方（也称为post-LN transformer），当把LN层置于残差网络后方时，接近输出层的参数的梯度的期望较大，如果不使用warmup策略，以一个较大的学习率开始训练过程的话，可能会导致优化过程不稳定，进而影响模型性能，加入warmup策略可以减弱这一倾向。基于以上结论，作者考虑LN的位置可能是比较重要的，因此，作者研究了另一种transformer的变体，它将LN置于残差网络内部，并在此网络上尝试不使用warmup策略。简言之，本文主要贡献有以下：

- 研究了两种transformer的变体（post-LN transformer和pre-LN transformer）在初始训练阶段的梯度情况，以展示在post-LN transformer中warmup策略如此重要的原因
- 作者证明，warmup的重要性源于LN层的位置，pre-LN transformer可以在不使用warmup策略的情况下，达到比肩post-Transformer的效果，同时能够缩短模型收敛所用的时间。

![xx-LN trm](http://qiniu.shihanmax.top/20220620002127_5q3f4Z_%E6%88%AA%E5%B1%8F2022-06-20%20%E4%B8%8A%E5%8D%8812.21.16.jpeg)

#### method

1. 作者首先使用post-LN transformer在De-EN翻译任务上，对比了设置不同学习率、不同warmup设置的情况下，loss和BLEU分数的情况，表明对post-LN transformer而言，学习率和其warmup策略的设置十分重要；
2. 通过理论和实验分析，对比了post-LN transformer、pre-LN transformer和使用warmup策略的post-LN transformer的隐藏层的参数的梯度的模，实验表明，post-LN transformer的值最大，表明其参数波动最大，优化难度也最大，pre-LN transformer能够显著减弱波动程度，（越接近输出层，二者的对比越明显）。而在post-LN transformer实验中加入warmup策略后，参数的波动程度大大减弱；
3. 通过实验证明，warmup策略对于pre-LN transformer不再重要；
4. pre-LN transformer的收敛速度优于post-LN transformer；
5. 作者通过实验证明，尽管RAdam优化器可以在post-LN transformer上在不使用warmup策略时也可以高效完成训练，但在pre-LN transformer上，其和Adam优化器的区别并不明显。

### refs

1. [Does learning require memorization? a short tale about a long tail](https://arxiv.org/abs/1906.05271)
2. [Understanding black-box predictions via influence function`s](https://arxiv.org/abs/1703.04730)
3. [Axiomatic attribution for deep networks](http://proceedings.mlr.press/v70/sundararajan17a/sundararajan17a.pdf)
4. [Attention is all you need]()
5. [Training tips for the transformer model]()
