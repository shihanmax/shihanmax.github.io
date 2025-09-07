---
date: 2022-07-04
display_type: none
layout: post
mathjax: true
syntaxHighlighter: true
tags:
- Paper Reading
- Deep Learning
title: A Closer Look at How Fine-tuning Changes BERT
---

基于预训练、finetune的方法，在NLP领域取得了显著的成就，但鲜有研究讨论finetune是如何改变原有的embedding空间的。本文提出了两种归因（probing）方式分析了finetune如何影响预训练模型的。作者提出：finetune增加了不同标签的样本的距离。作者在5个NLP任务上验证了这一假设。通过实验，作者也发现了一些特殊情况，例如“finetune并不总是能够提高模型性能”。