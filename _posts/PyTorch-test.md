---
date: 2022-05-01 23:02:34
display_type: none
layout: post
mathjax: true
syntaxHighlighter: true
tags:
- Deep Learning
- PyTorch
- 源码阅读
title: PyTorch源码阅读
---

| 模型         | 训练数据量 | 训练数据构成                | tokenizer | 词表大小 | 位置编码 | 激活函数 | attention                     | Layer normalization        |
| ------------ | ---------- | --------------------------- | --------- | -------- | -------- | -------- | ----------------------------- | -------------------------- |
| GPT3         | 300B       |                             | BPE       | 25k      |          | GeLU     | MHA                           | Pre-Norm                   |
| Llama        | 1T/1.4T    | 英语为主的拉丁语系          | BPE       | 32k      | RoPE     | SwiGLU   | MQA                           | RMSNorm                    |
| Llama2       | 2T         | 英语为主的拉丁语系          | BPE       | 32k      | RoPE     | SwiGLU   | GQA on 70B<br />MHA otherwise | RMSNorm                    |
| baichuan-7B  | 1.2T       | 中英                        | BPE       | 64k      | RoPE     | GeLU     |                               |                            |
| baichuan-13B | 2.6T       | 中英、多语言                | BPE       | 125k     | ALiBi    | SwiGLU   |                               |                            |
| Bloom        | 350B       | 46种类自然语言+13种编程语言 |           | 250k     | ALiBi    | GeLU     |                               |                            |
| ChatGLM-6B   | 1T         | 中英1:1                     |           | 130k     |          | GeLU     |                               |                            |
| ChatGLM2-6B  | 1.4T       | 中英1:1                     |           | 65k      |          | SwiGLU   | MQA                           |                            |
| Qwen-14B     | 3T         | 中英                        | BPE       | 152k     | RoPE     | SwiGLU   |                               | Pre-LayerNorm<br />RMSNorm |
| Yi-6B        | 3T         | 双语言语料库                | BPE       | 64k      | RoPE ABF | SwiGLU   | GQA                           |                            |