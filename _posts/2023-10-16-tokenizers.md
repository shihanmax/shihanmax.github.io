---
date: 2023-09-16 15:02:12
display: true
layout: post
mathjax: true
syntaxHighlighter: true
tags:
- Transformer
- LLM
title: 语言模型中的tokenizer
---

在自然语言处理（NLP）任务中，分词算法扮演着至关重要的角色。它是语言模型理解文本的基础，通过对文本的切分，模型能够更有效地提取特征、捕捉语义。本文将深入探讨分词算法的不同类型、工作流程以及它们在实际应用中的表现。

## 分词流程

1. 文本归一化

   文本归一化是分词的第一步，它涉及清除文本中的噪声，如多余的换行符、空格等，并进行大小写归一化。对于特定语言，如带有音调的汉语，音调移除也是必要的步骤。归一化的目的是确保文本的一致性，为后续的分词过程打下坚实基础。
2. 预切分

   预切分是基于规则的初步分词过程，通常依赖于空格、标点等自然语言的分隔符。例如，BERT的分词器会基于空格和标点进行切分，而GPT-2在此基础上做了改进，将空格保留为特殊字符。预切分的效果直接影响到后续分词的准确性和效率。
3. 基于分词模型的切分

   这一阶段是分词过程的核心，不同的模型采用不同的算法来实现。例如，BPE、WordPiece和Unigram等方法都是基于子词（subword）的分词方法。这些方法通过合并频繁出现的字符序列来构建词表，能够有效地捕捉词汇之间的关系，并减少未知词（UNK）的出现。
4. 后处理

   后处理阶段通常包括添加特殊token，如开始、结束标记，以及其他辅助性token。这些特殊token对于模型理解句子结构、识别句子边界至关重要。

## 分词粒度的选择

分词粒度一般分为三种：基于字的（char），基于子词的（subword）、基于词的（word）；基于字的分词方式虽然简单，但信息量较少，解码效率也较低。基于词的分词方式虽然词表庞大，但无法有效捕捉相近词之间的关系，并且存在UNK问题。相比之下，基于子词的方法在词表规模和捕捉同源词关系方面取得了平衡，且无UNK问题。

## 典型的子词分词算法（subword）

### BPE（Byte-Pair Encoding）

BPE算法通过迭代合并频繁出现的字符对来扩充词表。它的核心思想是将字符序列视为可合并的单元，通过不断合并出现频率最高的单元，逐步构建出能够表示所有文本的最小词表。这种方法的优势在于它的简单性和高效性。

#### 训练流程

1. 将原始文本数据分段；
2. 对每段文本，进行预切分；
3. 对所有预切分得到的词，进行wordlevel切分，生成原始词表；
4. 在达到退出条件前，循环执行以下步骤；
   1. 统计相邻子词pair的出现次数；
   2. 选择次数最多的一组pair，将其加入词表，同时记录一条合并规则；
   3. 将上述pair的合并更新到每个词的wordlevel切分结果；

#### 推理流程

1. 原始文本预切分
2. 将每个词切分为最小单元
3. 遍历每个merge rule，对每个词，将最小单元进行合并，得到最终结果

#### BPE 示例代码

```python
# basic implementation of BPE algorithm

import itertools
from collections import defaultdict
from transformers import AutoTokenizer
from utils import readlines


gpt2_tokenizer = AutoTokenizer.from_pretrained("gpt2")
pre_tokenize_function = gpt2_tokenizer.backend_tokenizer.pre_tokenizer.pre_tokenize_str


def train_bpe(corpus_path="corpus.txt", max_vocab_size=200):
    """
    max_vocab_size: 预设的最大词表大小
    """
    lines = readlines(corpus_path, skip_nl=True)
    print("\n\n\nlines: ----------------------------------")
    print(lines[:5])

    # 1. pre-tokenize
    pre_tokenized_result = [pre_tokenize_function(line) for line in lines]

    print("\n\n\npre_tokenized_result: ----------------------------------")
    print(pre_tokenized_result[:5])

    # 2. 统计词频
    word2count = defaultdict(int)

    for line in pre_tokenized_result:
        for word, pos in line:
            word2count[word] += 1

    print("\n\n\nword2count: ----------------------------------")
    print(word2count)

    vocab_set = set()

    for word in word2count.keys():
        vocab_set.update(list(word))

    vocab = list(vocab_set)
    print("\n\n\noriginal vocab: ----------------------------------")
    print(len(vocab), vocab)

    word2splits = {word: [c for c in word] for word in word2count.keys()}
    print("\n\n\nword2splits: ----------------------------------")
    print(word2splits)

    def _compute_pair2score(word2splits, word2count):
        """根据预分词的词频 和所有的子词，获得子词pair的出现频率"""
        pair2count = defaultdict(int)
      
        for word, word_count in word2count.items():
            splits = word2splits[word]
          
            if len(splits) == 1:
                continue  # 只有一个子词，跳过不处理
          
            for i in range(len(splits) - 1):
                pair = (splits[i], splits[i + 1])
                pair2count[pair] += word_count
      
        return pair2count

    pair2count = _compute_pair2score(word2splits, word2count)

    print("\n\n\npair2count: ----------------------------------")
    print(pair2count)

    def _get_most_high_freq_pair(pair2count):
        """获得出现频次最高的pair"""
        max_pair = max(pair2count.items(), key=lambda x: x[1])
        return max_pair

    highest_freq_pair = _get_most_high_freq_pair(pair2count)

    print("\n\n\nhighest_freq_pair: ----------------------------------")
    print(highest_freq_pair)

    # 合并pair，记录合并规则
    merge_rules = []

    vocab.append("".join(highest_freq_pair[0]))  # 注意，加入合并后的，不删除
    merge_rules.append(highest_freq_pair[0])

    print("\n\n\nh updated vocab: ----------------------------------")
    print(vocab)

    def _merge_pair(word2splits, subword0, subword1):
        """更新词表后，更新word2splits"""
      
        new_word2splits = {}
      
        for word, split in word2splits.items():
            if len(split) == 1:
                new_word2splits[word] = split  
                continue
          
            i = 0
          
            while i < len(split) - 1:
                if split[i] == subword0 and split[i + 1] == subword1:
                    split = split[:i] + [subword0 + subword1] + split[i + 2:]
                else:
                    i += 1

            new_word2splits[word] = split
      
        return new_word2splits

    word2splits = _merge_pair(word2splits, highest_freq_pair[0][0], highest_freq_pair[0][1])

    print("\n\n\n updated word2splits: ----------------------------------")
    print(word2splits)

    while len(vocab) < max_vocab_size:
        print(f"vocab size: {len(vocab)}")
      
        pair2count = _compute_pair2score(word2splits, word2count)
        highest_freq_pair = _get_most_high_freq_pair(pair2count)

        print("\n\n\nhighest_freq_pair: ----------------------------------")
        print(highest_freq_pair)

        vocab.append("".join(highest_freq_pair[0]))  # 注意，加入合并后的，不删除
        merge_rules.append(highest_freq_pair[0])

        print("\n\n\nupdated vocab: ----------------------------------")
        print(f"vocab: {vocab}\n")
        print(f"merge rules: {merge_rules}\n")

        word2splits = _merge_pair(word2splits, highest_freq_pair[0][0], highest_freq_pair[0][1])

    return vocab, merge_rules


def inference_bpe(merge_rules, sentence):
    # 1. pre-tokenize
    words = [word for word, _ in pre_tokenize_function(sentence)]
    print(words)
  
    # 2. split to char level
    splits = [[c for c in word] for word in words]
  
    # 3. apply merge rules
    for rule in merge_rules:
        for word_idx, split in enumerate(splits):
            i = 0
            while i < len(split) - 1:
                if split[i] == rule[0] and split[i+1] == rule[1]:
                    split = split[:i] + ["".join(rule)] + split[i+2:]
                else:
                    i += 1
                  
            splits[word_idx] = split
    # print(sum(splits), [])
  
    print(splits)
    tokenized_tokens = list(itertools.chain(*splits))
    print(tokenized_tokens)
    return tokenized_tokens


vocab, merge_rules = train_bpe(corpus_path="corpus.txt", max_vocab_size=200)
print(vocab)
print(merge_rules)

tokenized = inference_bpe(merge_rules, "Then Alice went to the rabbit hole after six hours waiting.")

```

### BBPE(Byte-level BPE)

与BPE的区别是：切分与合并的粒度是utf-8编码级别，即需要先对原文本进行utf-8编码。

### WordPiece

WordPiece算法是BPE的一个变种，区别在于子词pair的分数计算，BPE是直接取pair数量最高的；WordPiece是pair数量除以两个子词的频率之积，即$score = \frac{N_{pair}}{N_{sub_1} \* N_{sub_2}}$

### Unigram

Unigram算法是一种基于概率的分词方法。它通过计算每个子串的负对数概率来构建词表。Unigram的核心在于它能够为每个子串分配一个重要性分数，从而在构建词表时优先保留那些信息量大的子串。

#### 训练过程

1. 将语料按行分割，并进行预分词（对于中文，切分为字，对于使用空格来分割的语言，直接使用空格split）；此时可以得到所有词（word）；
2. 根据现有的词，拆分出所有的子词，即针对每一个词（假设长度为n），均从中取长度[2,n-1]的子串，并统计所有子串的出现频率（注意，长度为1的子串一直保留）；根据频率，计算出每个子串的负对数概率；
3. 在到达退出条件（如词表长度仍大于某一个设定值）之前，重复以下：
   1. 计算当前语料库的分数（所有token的负对数似然，需要使用DP实现encode_word：计算某个token的负对数似然的方法，是unigram分词算法的核心，本质是基于model中所有的子词，用动态规划计算出负对数似然最小的那一组sub word；（如：hello 是该划分为 h e ll o 还是 he llo 还是其他的））
   2. 遍历语料库中的每一个token，计算将其删掉之后，整个语料库的分数；
   3. 至此得到所有token的重要程度（信息量），按从大到小，删去负对数似然较大的一批token（如10%，认为这部分token不常见）；
   4. 更新模型；

#### 推理过程

1. 对语料进行预分词；
2. 针对每一个切分后的词执行上述步骤3.1中的encode_word，得到该词的切分方式；
3. 将所有词的切分结果拼接在一起，即得到最终的结果；

#### unigram 示例代码

```python
# basic implementation of unigram tokenization

from collections import defaultdict
import copy
import math


corpus = [
    "This is the Hugging Face Course.",
    "This chapter is about tokenization.",
    "This section shows several tokenizer algorithms.",
    "Hopefully, you will be able to understand how they are trained and generate tokens.",
]

word_freq = defaultdict(int)

# 预切分
for sentence in corpus:
    for word in sentence.split():
        word = "_" + word
      
        word_freq[word] += 1
          
print(f"word_freq: {word_freq}\n")

char_freq = defaultdict(int)
subword_freq = defaultdict(int)

for word, freq in word_freq.items():
    for i in range(len(word)):
        char_freq[word[i]] += freq
      
        for j in range(i + 2, len(word) + 1):  # i+2
            subword_freq[word[i:j]] += freq  # 统计所有子词的频率


print(f"char_freq: {char_freq}\n")
print(f"subword_freq: {subword_freq}\n")

# Sort subwords by frequency
sorted_subword_freq = sorted(subword_freq.items(), key=lambda x: x[1], reverse=True)

print(f"sorted_subword_freq: {sorted_subword_freq[:10]} ... \n")


token_freq = {
    i[0]: i[1] for i in 
    list(char_freq.items()) + sorted_subword_freq[:300 - len(char_freq)]  # 截断subword_freq 以保证初始状态下为300个token
}

print(f"token_freq: {token_freq} ...\n")

total_freq = 0
for k, v in token_freq.items():
    total_freq += v


model = {
    token: -math.log(freq / total_freq) for token, freq in token_freq.items()
}

print(model)


def encode_word(word, model):
    # [[start, score]]
  
    best_segmentations = [[0, 1]] + [[None, None] for _ in range(len(word))]
  
    for start_idx in range(len(word)):
        best_score_at_start = best_segmentations[start_idx][1]
      
        for end_idx in range(start_idx + 1, len(word) + 1):
            curr_token = word[start_idx: end_idx]
          
            if curr_token in model and best_score_at_start is not None:
                score = model[curr_token] + best_score_at_start
              
                if best_segmentations[end_idx][1] is None or best_segmentations[end_idx][1] > score:
                    best_segmentations[end_idx] = [start_idx, score]
  
    segmentation = best_segmentations[-1]
  
    # print(segmentation)

    if segmentation[1] is None:
        return ["UNK"], None

    score = segmentation[1]
    start = segmentation[0]
    end = len(word)
  
    tokens = []
  
    while start != 0:
        tokens.append(word[start: end])
        next_start = best_segmentations[start][0]
        end = start
        start = next_start
  
    tokens.append(word[0: end])
    tokens = tokens[::-1]  # reverse it
    return tokens, score


print(encode_word("hello", model))
print(encode_word("word", model))
print(encode_word("Hopefully", model))
print(encode_word("This", model))


def compute_loss(model):
    loss = 0
  
    for word, freq in model.items():
        _, word_loss = encode_word(word, model)
        loss += word_loss * freq
  
    return loss


def compute_scores(model):
    # 计算每一个词删去后，语料库的loss
    scores = {}
  
    model_loss = compute_loss(model)
  
    for token, score in model.items():
        if len(token) == 1:
            continue
      
        model_without_token = copy.deepcopy(model)
        model_without_token.pop(token)
      
        scores[token] = compute_loss(model_without_token) - model_loss
  
    return scores


percent_to_remove = 0.1  # 每次删去10%的token

while len(model) > 100:
    print("- - " * 12)
  
    scores = compute_scores(model)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1])
  
    for i in range(int(len(model) * percent_to_remove)):
        token_freq.pop(sorted_scores[i][0])
        print(f"remove token: {sorted_scores[i][0]}")
  
    subword_freq_sum = sum([freq for token, freq in token_freq.items()])
    model = {token: -math.log(freq / subword_freq_sum) for token, freq in token_freq.items()}
print(model)


def tokenize(text, model):
    pre_tokenized_text = ["_" + i for i in text.split()]
  
    encoded_words = [encode_word(word, model)[0] for word in pre_tokenized_text]
  
    return sum(encoded_words, [])


tokenized_res = tokenize("Hi how are you today", model)
print(tokenized_res)
```

## 总结

本文简单回顾了几种基于子词的分词方法。

## 参考

1. [从词到数：Tokenizer与Embedding串讲](https://zhuanlan.zhihu.com/p/631463712)
2. [大模型基础组件 - Tokenizer](https://zhuanlan.zhihu.com/p/651430181)
3. [\[BTTB\] BPE：从 Byte 到 Byte，到 No BPE](http://mp.weixin.qq.com/s?__biz=MzUxMjE1NzA2MA==&mid=2247484943&idx=1&sn=273e2d573f353c63861588af5b72aa58&chksm=f969f2e4ce1e7bf2cd76a63135ceddb0d9d9f0924635c04d821d2fcfa01b725c6ba12f449393&mpshare=1&scene=1&srcid=0624xbITtjH7utO83SsGdKg2&sharer_sharetime=1687603891661&sharer_shareid=4d61eb092eb8afde38dc3915177e1290#rd)
4. [Byte Pair Encoding and Data Structures](https://guillaume-be.github.io/2021-09-16/byte_pair_encoding)