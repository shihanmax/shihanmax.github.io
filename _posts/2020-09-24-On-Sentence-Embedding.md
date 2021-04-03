---
title:  "On Sentence Embedding"
layout: post
date: 2020-09-24 23:34:18
categories: NLP
tags:  ["Deep Learning", "Embedding"]
syntaxHighlighter: yes
Mathjax: true
---

This article will briefly introduce some papers on document representation.

## 1. A SIMPLE BUT TOUGH-TO-BEAT BASELINE FOR SENTENCE EMBEDDINGS

### model

This article proposed a method for acquiring sentence embedding called SIF. The method is very simple: for the document collection, first, for each document, the word vector is weighted and averaged with the word frequency as the weight, now we have the representations of each document. Let's say the number of documents is $D$ and the dimension of the word vector is $E$. Then we get the document set representation matrix $M: D\times E$. Then, perform SVD on the matrix $M$, subtracting its projection in the principal component direction, as the final sentence representation.

### mathematical formulation

$$v_{s} \leftarrow \frac{1}{|s|} \sum_{w \in s} \frac{a}{a+p(w)} v_{w}$$

$$v_{s} \leftarrow v_{s}-u u^{\top} v_{s}$$

todo: theoretical analysis

## 2. A STRUCTURED SELF-ATTENTIVE SENTENCE EMBEDDING

At present, the research on paragraph/sentence representation is not rich enough comparing with word embeddings. Research on sentence representation is usually divided into two categories:
1. Sentence-level semantic models trained through unsupervised methods, such as SkipThought, paragraphVector, Recursive auto-encoders, Sequential Denoising Autoencoders (SDAE) FastSent, etc.
2. Obtained through supervised training in specific downstream tasks, involving models such as recurrent networks, recursive networks, and convolutional networks;

This paper proposes a self-attention mechanism for sentences to replace the max/avg pooling operation over tokens at each time step after a traditional RNN layer, and at the same time, it can extract different levels of sentence semantic information.

### the proposed model

The sentence representation model proposed in this article is divided into two parts:
1. Bidirectional LSTM layer

2. Self-attention layer

For sentence: $S=(w_1, w_2, ..., w_n)$, where $w_i$ represents the $d$-dimensional word embedding of the $i$-th word. $S$ can be expressed as a matrix $S_{n \times d}$ without any relationship along the rows.

Then input $S$ into the bidirectional LSTM:

$$\begin{aligned} \overrightarrow{h_{t}} &=\overrightarrow{L S T M}\left(w_{t}, \overrightarrow{h_{t-1}}\right) \\ \overleftarrow{h_{t}} &=\overleftarrow{L S T M}\left(w_{t}, \overleftarrow{h_{t+1}}\right) \end{aligned}$$

After concat the output of each time step toward the forward and backward directions, the representation matrix $H_{n \times 2u}=(h_1, h_2, ..., h_n)$ is obtained, where $u$ is the hidden dimension of LSTM.
Because it is planned to encode the variable-length sequence into a fixed-size representation vector, it is necessary to aggregate the representation vector of each token of the variable-length sequence, attention mechanism is used to calculate the weight of each token. The weight vector calculation method is as follows:

$$\mathbf{a}=\operatorname{softmax}\left(\mathbf{w}_{\mathbf{s} 2} \tanh \left(W_{s 1} H^{T}\right)\right)$$

$W_{s1}:d_a \times 2u$，$w_{s2}: 1 \times d_a$，$d_a$ is a hyper-parameter.

At this time, $\mathbf{a}$ is a vector of $1\times n$, which represents the weight of each token in the weighted average process. Perform weighted average for each token in the representation matrix $H$ to get the sentence representation $m$ of $1 \times d$.

For longer sentences or sentences that contain different descriptions or contexts, sometimes we want to express the sentence from different point of views. In order to achieve this, the author replace the vector $w_ {s2}: 1 \times d_a$ with a matrix $W_{s2}: r\times d_a$, which do the same thing like multi-head attention. Note that at this time softmax should be executed line by line.

Finally we got the attention score matrix $A: r\times n$, and do the dot product with the representation matrix $H$ to get the final representation matrix $M$ of the sentence:

$$M=AH$$

### penalty term

In order to avoid the loss of diversity of multi-head attention, a penalty item needs to be added to the matrix $A$. The author found in the experiment that using KL divergence to measure the diversity between weights is not stable (a large number of items are close to 0 in $A$ after softmax, This leads to numerical instability in the calculation of KL divergence). In addition, it is obvious that KL divergence cannot be achieved if we want each row vector to focus on a single characteristic as much as possible. The author used the following penalties:

$$P=\left\|\left(A A^{T}-I\right)\right\|_{F}^{2}$$

This penalty item will be minimized together with loss of downstream tasks during traing.

### summary

The advantage of the method proposed in this paper is that it can force the attention to be calculated from different angles during the training process, and it can overcome the problem of long-distance dependence to a certain extent. The disadvantage is that this method is relatively dependent on downstream tasks, and can only be trained in a supervised manner, and has limited compatibility between different tasks.

## 3. Distributed Representations of Sentences and Documents

The shortcomings of the current method of obtaining sentence embedding:

- bag-of-words model
  - lost order info
  - less semantic

- bag-of-n-grams
- data sparsity
- high-dimensionality
- less semantic

This paper proposes an unsupervised sentence embedding training method for variable length text: Paragraph Vector.

There are two training methods for Paragraph Vector:

### 1. A distributed memory model

For corpus C, suppose it contains $N$ paragraphs, and the embedding dimension of each paragraph is $p$; the corpus contains $M$ words, and the embedding dimension of each word is $q$; The number of parameters the model needs to learn is $N \times p + M \times q$, each paragraph is mapped to a paragraph id (that is, we can treat paragraphs in the corpus as special words).

During the training, for a paragraph, we select a sliding window W. The text in the window is called context, which is the basic unit of training. The context in the same paragraph shares the paragraph embedding, and the words in the entire corpus share words embedding. For context C, use its paragraph vector to concatenate the word embedding of each word in C to predict what the next word of this context is.

At prediction time, for the set of paragraphs to be predicted $\{P\}_{n}$, first, add it to corpus C (that is, add $n$ rows to the paragraph matrix),  then continue to execute the training process on new corpus until convergence, with word embedding fixed.

In this training method, the paragraph vector plays a memory role of the topic and other information of the paragraph, so it is called PV-DM (Distributed Memory Paragraph Vectors).

### 2. Distributed bag of words
Another method of PV training is as follows, which is similar to training the skip-gram model in Word2vec. In the training process, a window W is sampled from the paragraph P, and given the paragraph vector of the paragraph to which the window belongs, predict the random sampling word w from the window. This method named PV-DBOW because it ignores the order of words.

Experimental results show that combining the sentence vectors obtained by these two methods can get more stable and better results.

### futher observations
1. The effect of PV-DM is better than PV-DBOW
2. In PV-DM, concat paragraph vectors and word embedding could achive better result
3. The selection of window size requires cross-validation
4. The time cost to obtain the paragraph vector is high, but this problem can be alleviated by parallel computing.




Refs.

[1. A SIMPLE BUT TOUGH-TO-BEAT BASELINE FOR SENTENCE EMBEDDINGS]( https://openreview.net/pdf?id=SyK00v5xx)

[2. Implementation of SIF](https://github.com/PrincetonML/SIF/blob/master/src/SIF_embedding.py)

[3. A STRUCTURED SELF-ATTENTIVE SENTENCE EMBEDDING ](https://arxiv.org/pdf/1703.03130)

[4. Distributed Representations of Sentences and Documents]( http://cn.arxiv.org/pdf/1405.4053.pdf)
