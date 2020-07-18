---
title:  "Recent advances in conversational NLP"
layout: post
date:   2019-03-26 00:00:00
categories: NLP
tags:  Chatbot
syntaxHighlighter: yes
---

论文《Recent advances in conversational NLP :
Towards the standardization of Chatbot building》阅读笔记

From：Maali Mnasri（maali@opla.ai）

# Abstract

chatbot在日常生活中越来越重要，易用程度也在不断提升。本文针对目前的对话系统作了综述性研究，再文章最后讨论了各个实现方法的优缺点对比，并提出了对话系统标准化的思考。

# 1 Introduction

Conversational agents（与后文dialogue system、以及工业和媒体使用的chatbots义同，简称CA）越来越常见，如个人手持设备的个人助理、商业网站的售货机器人等，这些系统旨在通过语音或文本与人类进行流畅的对话沟通。在AI领域，建立智能的CA仍是一个未解决的难题。本文总结了目前流行的对话系统实现方法，并对主流实现方法进行了对比。

尽管距第一个CA被提出已经过去很多年了，但这个领域仍然越来越活跃，这与近年来AI、NLP领域技术的迅速发展有关。目前有很多丰富的方法来实现CA，但能够使研究者专注于CA性能提升的工具却很缺乏，本文第6节会讨论相关问题。

<!--more-->

下文如下组织：

- 分析当下CA设计的SOTA技术
- 关于CA设计标准化提出了新的思考

# 2 Chatbots categories

我们将CA分为两类：聊天机器人（social chatbots）和任务型对话机器人（task oriented chatbots）。

## 2.1 Social chatbots

聊天机器人（也常常被称为chit-chat bots）的娱乐意义多一些，但在最开始，它们的设计目的是作为心理诊疗顾问，甚至有一些现在仍在使用。ELIZA,PARRY,ALICE,CLEVER,微软小冰等在CA领域迈出了第一步。

## 2.2 Task oriented chatbots

我们将任务型对话机器人也分为两类：通用任务型和特殊任务型。

### 2.2.1 Generalist task oriented chatbots

能够回答一些通用问题（和chit-chat类似），可以进行简单的对话，并能够完成一些日常的任务，如设置闹钟、打电话、发短信等。

### 2.2.2 Specialist task oriented chatbots

针对某些特殊领域设计，通常以来这些领域的知识来解决稍微复杂的问题，如预定航班、订餐、分析健康问题等。

# 3 Chatbot building approches

本章介绍两种主流的CA设计方法：基于规则的和基于数据的。前者在设计时主要依赖模式-动作规则（[pattern-action](https://stackoverflow.com/questions/380724/what-is-the-action-design-pattern)），而后者则需要大量的对话语料。

## 3.1 rule-based chatbots

基于规则的CA使用前缀规则进行设计，它按照特定的规则与用户交互，例如，如果用户的话中包含 [Hello”, ”Good morning”, ”Hi”] 中的一个，则CA应该回复"Hello"。规则对话机器人由于设计简单、能够完成简单的额任务，目前很受欢迎，但对复杂任务则需要设计大量的人工规则，很费时费力。ELIZA是第一个规则对话系统，设计目的是为了模仿一位心理诊疗师，它的设计原则是应用模式和转变规则（applying pattern and transform rules），每一条转换规则都对应一个关键词，关键词按"特别->一般"来排序。针对每一条用户的话，chatbot通过对照知识库，按照转变规则来寻找排序最靠前的关键词。以下面的一句话为例：

$$You \space hate\space me$$

这句话和如下的模式匹配：

$$(0\space YOU\space 0\space ME)$$

0表示一段文字的长度变量，我们假设关键词YOU使用下述的转变规则：

$$(\space YOU\space 0\space ME) \rightarrow (WHAT\space MAKES \space YOU \space THINK\space I\space 3\space YOU)$$

3表示用户的话中的第3个词，本例中也就是"hate"，应用转变规则后，规则对话机器人应该返回如下答案：

$$WHAT\space MAKES \space YOU \space THINK\space I\space hate\space YOU$$

在ELIZA后，PARRY系统也使用了类似的规则系统，不同的是，PARRY在设计时加入了影响变量（affect variables），能够表现出生气、害怕等情绪。

## 3.2 Data-driven chatbots

目前多数CA使用基于数据驱动的手段。它依赖大量的对话语料，不需要手工规则设计，我们接下来介绍基于信息抽取的对话机器人和基于机器学习的对话机器人。

### 3.2.1 Information retrieval based chatbots

Clever-Bot设计于1988年，1997年发布，它依赖数据库中与问题相似的答案来回答人类的问题。就像一个搜索引擎一样。针对用户的问题Q，IR CA会从数据库中寻找与Q最相近的问答对(Q',R')，将其回答返回给用户。那么如何衡量语句之间的相似性？一种方式是基于字向量计算余弦距离；另外一些基于TF-IDF的检索模型使用discourse tree和RST（Rhetorical Structure Theory）来对语句生成或相似答案进行建模。除了一些对话语料之外，也可以使用WikiAnswers、YahooAnswers、推特对话等构建语料库。

### 3.2.2 Machine learning based chatbots

目前，主要的深度学习方法有seq2seq learning和强化学习两种，下面分别介绍。

#### 3.2.2.1 Seq2seq learning

Seq2seq使用RNN对复杂语段进行建模，用于机器翻译、图片描述、语音识别、文本摘要、自动问答等领域。在机器翻译领域的成功显示出Seq2seq技术的优越性。在对话机器人设计中，类似地，可以看作将用户的话翻译为机器人的回答。seq2seq模型可以对输入和输出进行映射，二者的长度可以不同，技术上，它由一个编码器和一个解码器组成，编码器接收输入，并把他转化为中间向量（context vector），中间向量被输入到解码器中，得到seq2seq的输出。seq2seq可以回答简单的问题，抽取相关信息，并具有一些简单的推理能力，但还不能进行合理的对话。（显然，由于RNN的设计特点，长距离特征的保持和记忆的能力与Attention模型有一定的差距。）

后来也有研究者在seq2seq模型中加入对用户情绪的建模，在语句生成阶段考虑到了情绪的影响。

#### 3.2.2.2 Reinforcement learning

强化学习使机器能够像人一样学习，也即通过与环境的交互，最大化某种累计奖励。

在神经网络建模流行之前，人们将对话系统建模为一个马尔可夫决策过程（Markov Decision Processes
，MDPs），为了使用强化学习，使用一组与对话相关的状态来表示对话系统。目标是最大化通过满足用户请求而得到的奖励。后来，使用部分可见马尔可夫决策过程来对对话建模（Partially Observed Markov Decision Pro-
cesses ，POMDPs），此方法假设对话有一个初始状态$s_0$，后续的状态由前一个状态和前一轮action $a_t$决定：

$$p(s_t \mid s_{t-1}, a_{t-1})$$

为了将SLU模块误差考虑进来，$s_t$部分可见，至此，每一轮的用户输入转化为概率$p(o_t \mid s_t)$，其中$o_t$是$t$时刻的观察状态。观察概率和转移概率由对话模型$M$决定。可能的系统action将转移给策略模型，在对话过程中，如果系统执行了正确的action，会得到相应的奖励。

### 3.2.3 Hybrid approches

有研究将上述方法结合，如Alibaba购物机器人，使用IR手段检索最合适的几个答案，并通过seq2seq对它们进行重排序，并生成答案。

# 4 Chatbots evaluation

对对话系统进行人工评估耗费巨大，一些IR based CA可以使用简单的PR指标进行评估。自动化的方法BLEU、ROUGE等分别用于机器翻译和文本摘要，他们通过计算系统输出和参考答案之间的n-gram重合度来评估。对话系统中，这些评估方式可以计算系统回答和人类回答的匹配度。但这种方式也有缺点，在一些场景下，两段文本可能n-gram完全没有重合，但语义却是相似的。

困惑度（Perplexity）也可以用来做CA评估，它最开始用于评估语言模型，我们假设测试集由$w_1,w_2,…,w_n$组成，那么语言模型预测出这些词的困惑度为：

$$Perplexity=e^{-\frac{1}{N} \sum log( P_{w_i})}$$

意味着，Perplexity越小越好。

# 5 Discussion

各种类型的CA都各有优缺点，应该根据已有的数据（数据量、结构化/非结构化）和CA的用途来决定使用哪一种。

机器学习占据了目前对话领域的主流，而强化学习在对话系统设计中已经广泛使用，编码-解码学习成为主流。

强化学习使得模型更能对长距离多轮回话进行建模，因为如果长轮次会话中模型出现错误决策时，也会受到惩罚。但强化学习有两个缺点：

1. 需要大量的训练时间和训练轮次
2. 不是语言生成的最佳选项

生成式seq2seq模型已经部分克服了上述缺点，但他也有一些缺点，如倾向于生成安全回答，而且无法考虑重复现象，如：

> Cus: Goodbye!
>
> Bot: Goodbye!
>
> Cus: Goodbye!
>
> Bot: Goodbye!
>
> ...

强化学习和seq2seq结合的策略有望解决上述问题。

# 6 Opinion piece : towards the standardization of the field

关于当前对话机器人设计的思考：目前许多研究者在设计对话系统时，由于没有统一框架和标准，大家都是在重复造轮子，其实有一些模块是可以复用的，所以下面的对话机器人研究是否能够着眼于基础架构的搭建，然后使研究者以插件的形式设计对话机器人。

# 7 Conclusion

单一模型不能解决实际问题，模型整合才能更好适应工业需求。

对话框架的标准化。



# 后记-阅读心得

1. 关于chatbot设计方面作了综述，基本框架与《自然语言处理综论》中相关章节基本相似，其中seq2seq相关部分并没有提到目前SOTA的Attention模型；
2. 多轮对话没有涉及；
3. 副标题是Towards the standardization of Chatbot building，但仅指出了目前chatbot设计不统一的现象，关于对话系统设计标准化，作者其实可以写的更丰富些。



