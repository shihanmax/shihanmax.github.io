---
title:  "Python垃圾回收机制（GC）"
layout: post
date:   2018-10-10 00:00:00
categories: Python
tags:  GC
syntaxHighlighter: yes
---

### Python中的GC机制：

- 以引用计数为主
- 分代回收为辅

python对象的核心是一个结构体：PyObject

```c++
typedef struct_object {
    int ob_refcnt;
    struct_typeobject *ob_type;
} PyObject;

#def Py_INCREF(op) ((op)->ob_refcnt++)
#def Py_DECREF(op)

if (--(op)->ob_refcnt != 0)
    ;
else
    __Py_Dealloc((PyObject *)(op))
```

ob_refcnt 就是为了做引用计数，当一个对象的引用为0时，会被清除。

<!--more-->

Python在合适的时机会对处在链表中的有循环引用的对象引用减1，这样，原本有引用的对象不会被清除，而原本循环引用的对象，其引用计数被置零并回收。

零代链中的无引用对象，将剩余有引用对象挪到一代链，对一代链同理。这三代链子被清理的频率：零代 >> 一代 >> 二代

```python
>>> import gc

>>> gc.get_count()  # 查看当前隔代回收当前状态
(154, 5, 3)
>>> gc.get_threshold()  # 新创建的减去释放掉的如果大于此阈值，触发分代回收
(700, 10, 10)  # 10和10表示：清理10次0代链表后清理一代链表，清理10次一代链表后清理一次二代链表。
>>> gc.collect()  # 显式执行垃圾回收
```

Python和Ruby的标记-清除机制对比：

​	Ruby：一次性创建大量可用对象，用完后标记清除。

​	Python：初始化时才创建对象，一旦引用为0立即清除。



### 一点注意

如果类的__del__方法被重写（未调用父类的del方法），则执行垃圾回收时无法回收该对象。



### 引用计数相关

#### 导致引用计数 +1 的情况

- 对象被创建
- 对象被引用
- 对象被传入函数中
- 对象作为一个元素存放在容器中

#### 导致引用计数 -1 的情况：

- 对象被 del 显式销毁
- 对象被赋予新的对象
- 一个对象离开其作用域（如已经执行完毕的函数中的形参）
- 对象所在的容器被销毁



#### 查看对象的引用计数：

```python
import sys

a = 'Hello world'
sys.getrefcount(a)
```



### 整数对象池

#### 小整数对象池

为了避免整数的频繁申请和销毁内存空间，Python使用了小整数对象池。

[-5, 257)内的整数都在小整数对象池中，他们都已经被提前建立好了，常驻内存，不被回收。



#### 大整数对象池

每一个大整数的定义都会创建一个新的对象。



##### 字符串共享机制（intern）

```python
>>> a1 = 'HelloWorld'
>>> a2 = 'HelloWorld'
>>> a3 = 'HelloWorld'
>>> id(a1) == id(a2) == id(a3)
True
```

a1-a5拥有共同的id（实际指向了同一块内存），但如果字符串中有特殊字符（如空格），则不会触发共享机制共享。
