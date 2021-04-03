---
title:  "Python元类（MetaClass）"
layout: post
date:   2018-10-02 00:00:00
categories: Python
tags:  ["Meta Class", "Language"]
syntaxHighlighter: yes
---

### 元类

类也是对象。

类可以动态创建（不建议这样做）：

```python
def choose_class(name):
    if name == 'foo':
        class Foo(object):
            pass
        return Foo
    else:
        class Bar(object):
            pass
        return Bar
```

类型实际是一个类，如 int、str 等。

<!--more-->

使用 type 创建一个类（强调，这样非常不好）：

```Python
test = type('Dog', (Animal, ), {})
# 参数:(类名，父类元组，属性字典(属性+方法))
```

使用类来创建实例对象，通过元类来创建类，而 type 就是一个元类。int 是创建整型的类，str 是创建字符串的类，type 就是创建类对象的类。

```python
>>> age = 35
>>> age.__class__
int
```



元类决定了类的创建方式。

```python
def upper_attr(future_class_name, future_class_parents, future_class_attr):
    newAttr = {}
    for name, value in future_class.attr.items():
        if not name.startswith('__'):
            newAttr[name.upper()] = value
    return type(future_class_name, future_class_parents, newAttr)

class Foo(object, metaclass=upper_attr):
    bar = 'bip'
```



> 元类是深度的魔法，99%的用户不用使用它，如果你想搞清楚究竟是否需要使用元类，那么你就不需要它，那些实际用到元类的人都非常清楚地知道他们需要做什么，而且不用解释为什么要使用元类。 -- Tim Peters
