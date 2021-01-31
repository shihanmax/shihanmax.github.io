---
title:  "使用Tensotflow同时加载多个模型"
layout: post
date:   2019-03-18 17:38:00
categories: 深度学习
tags:  ["Deep Learning", "Tensorflow", "Machine Learning Library"]
syntaxHighlighter: yes
---

使用单个模型时，一种模型的保存和加载的方式如下：

```python
# 输入/输出定义
x = tf.placeholder(dtype, name)
y = tf.placeholder(dtype, name)

# 权重定义
weight = tf.Variable(shape, dtype)

# op定义
output = some_operation(x, weight)
loss = tf.calc_loss(output, y)
train_op = optimizer.minimize(loss, name)

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    saver = tf.train.Saver()
    
    # do some train 训练
    
    saver.save(sess, "./model/model_path")  # 保存模型
```
<!--more-->

针对上述模型，恢复的方式如下：

```python
saver = tf.train.Saver()

    sess = tf.Session():
    sess.run(tf.global_variables_initializer())
    saver.restore(sess, "./model/model_path")  # 将模型恢复到sess中
        
    output = sess.run([output], feed_dict=feed_dict)  # 使用恢复的模型进行预测
```

对单个模型来说，这么做没有问题，但如果我们训练了多个相同结构的模型，我们期待以如下方式恢复它们：
```python
all_sessions = []
for i in range(model_nums):
	saver = tf.train.Saver()

	sess = tf.Session():
	sess.run(tf.global_variables_initializer())
	saver.restore(sess, "./model/model_path")  # 将模型恢复到sess中

	all_sessions.append(sess)
```
使用上述恢复的session进行预测：
```python
all_result = []
for sess in all_sessions:
	all_result.append(sess.run([output], feed_dict=feed_dict))
```
但这么做会导致参数错误，预测结果异常，原因是多个模型中的变量会发生冲突，原因是将所有的模型变量都加载到同一个线程的默认图中，解决方法是，针对不同的model使用不同的默认图：
```python
class ImportGraph():
    def __init__(self, loc):
        self.graph = tf.Graph()
        self.sess = tf.Session(graph=self.graph)
        with self.graph.as_default():
            saver = tf.train.import_meta_graph("./model/model_path" + '.meta')
            saver.restore(self.sess, "./model/model_path")

    def predict(self, data):
    	return self.sess.run([output], feed_dict=feed_dict)
```
上述方式是从[博客](https://blog.csdn.net/lc013/article/details/84202901)看到的，在我的实验中，并有有成功地将多个模型恢复，我的恢复方式是：
```python
class ImportGraph():
	tf.reset_default_graph()  # The default graph is a property of the current thread. 重置当前线程中的默认图
	self.sess = tf.Session()
    self.sess.run(tf.global_variables_initializer())
    self.saver = tf.train.Saver()
    self.saver.restore(self.sess, "./model/model_path")
```

重要的地方在于tf.reset_default_graph()，tf官方文档给出的解释是：

```
tf.reset_default_graph()
Defined in tensorflow/python/framework/ops.py.

Clears the default graph stack and resets the global default graph.

NOTE: The default graph is a property of the current thread. This function applies only to the current thread. Calling this function while a tf.Session or tf.InteractiveSession is active will result in undefined behavior. Using any previously created tf.Operation or tf.Tensor objects after calling this function will result in undefined behavior.
```