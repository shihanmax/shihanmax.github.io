---
title:  "Python中的模块、包、库与导入相关"
layout: post
date: 2022-04-04 14:06:06
tags:  ["编程语言"]
syntaxHighlighter: yes
mathjax: true
---

今天简单梳理一下Python中的模块（Module）、包（Package）、库（Library）的区别，记录有关Python的模块和包导入的问题。

## 模块、包和库

### 模块（Module）

我们知道，当我们关闭Python解释器再重新打开后，原来的解释器中的变量定义、函数的声明等均会消失。如果我们希望持久化地存储我们定义的对象，则可以新建一个文本文件，这个文件称为“脚本”，一般使用单个脚本来处理一些简单的任务。当任务变得复杂，以至于我们需要写多个脚本实现、并且我们希望能够在这些脚本之间共享一些相同的定义以达到复用的目的时，我们就需要引出模块（Module）的定义了。

Python中的模块，定义为一个包含Python定义/声明的文件。文件名就是模块名，后缀为`.py`。在一个模块内部，有一个全局变量`__name__`，其值为模块名，仅当一个模块被运行时，其`__name__`被设置为`__main__`。在一个模块中，我们可以定义任何Python对象，如变量、函数、类等。

每个模块均有自己私有的变量集，对于该模块内定义的变量、函数和类等对象来说，这些变量集是全局的，并且仅在该模块内部生效，因此在模块内编程时，用户不必担心对模块外的变量产生干扰。可以使用`dir()`来查看命名空间中定义了哪些对象。

一般而言，我们可以在模块的最顶部（非强制）导入一些其他的模块。其他模块一旦被导入，即会被加入当前模块的全局符号表中。在程序解释运行阶段，一个模块最多只能被导入一次，如果希望重复导入，可以重启解释器或使用`importlib.reload()`。

### 包（Package）

“包”是Python用来组织模块命名空间的一种方式，可以认为是一组模块的集合，它允许以`.module`的方式来组织和调用模块。如`A.B`表示，在包A中有一个子模块B，这种组织形式的优势在于，各个包的作者不用担心他们各自写出的模块之间互相冲突，即使两个包x和y中定义了相同的模块`foo`，并且在模块中定义了相同的函数`bar()`，我们也可以通过`x.foo.bar()`和`y.foo.bar()`来区分它们。

如果我们希望编写一个包，并且让解释器感知到，我们需要在包的路径下新建一个`__init__.py`文件，它可以为空（一个包可能不包含`__init__.py`文件，这种包称为命名空间包，下文会提到）。也可以在其中定义`__all__`变量来声明该包需要向外暴露的模块，或者自定义一些包的初始化操作。我们可以通过`from package import item`来引用一个包中的内容，这个`item`可以是子包、子模块、或模块中的定义，如类、方法、变量等。当然，如果使用`from package import item.subitem.subsubitem`时，最后一个`subsubitem`必须是一个包或者模块，而不能是模块中的类、方法或变量。

上面提到，我们可以定义一个包根目录下`__init__.py`中的`__all__`变量来控制导入行为，具体地，`__all__`是一个列表，我们可以将该包下一些模块名加入其中，当从另一模块/包中执行`from package import *`时，`__all__`中定义的模块会被导入当前模块/包。如果一个包中的`__all__`未定义，则执行`from package import *`时并不会自动导入该包下的所有模块，仅仅会导入这个包本身，并且会执行`__init__.py`中的初始化代码，如果这个文件中有导入的模块或定义的模块，则会被同步导入进来。

当我们需要做包内的引用时，我们可以使用绝对引用的方式，如`from top_package.sub_package import module`，或者使用相对导入的形式，如`from ..sub_package2 import module2`，值得注意的是，如果一个模块是Python程序的主执行文件，则在该模块中必须使用绝对引用方式。

包有两种形式：“常规包（regular package）”和“命名空间包（namespace package）”，常规包即是上述定义的包，其包含一个`__init__.py`文件，在Python 3.2及之前的版本中，只有常规包，即，如果要定义一个包，则一定要包含`__init__.py`文件。

PEP 420引入了命名空间包的概念，命名空间包则是一组portion的组合，一个portion定义为一个目录下的一组文件，一个portion可能定义在一个压缩文件中、在网络上或者在任何一个Python执行import时能搜索到的地方。命名空间包不需要`__init__.py`文件，更多命名空间包的细节可以参考$^{4}$。

### 库（Library）

库可以看做是一组相关的包的集合，如`matplotlib`库、Python标准库等，一般指一组包、模块的集合。另一个更广泛的名词是框架（Framework），如果我们要解决特定领域内的某些问题，可能需要使用到多个库，这里会牵涉到对多个库的功能的整合，这这个整体成为一个抽象的框架（非正式定义）。

## 导入（Import）相关

Python模块之间的互相互相访问可以通过import机制来实现。我们可以通过`import xx`、`importlib.import_module()`或`__import__()`进行引用。import操作包含两步操作：

1. 寻找相关的模块
2. 将搜索结果加入当前命名空间中

`import xx`即是对`__import__()`方法的调用，其返回值用于相关命名空间的绑定操作。当一个模块被首次导入时，Python会寻找对应的模块，如果寻找到了则创建一个模块对象（module object）并初始化之，否则抛出`ModuleNotFoundError`异常。

Python中只有一种模块对象（module object），无论这个模块是用Python、C还是其他任何语言实现的。包也是模块（但并不是所有的模块都是包），二者区别在于模块是否具有`__path__`属性。

上文提到，模块之间互相引用时，有相对引用和绝对引用两种方式，PEP 8推荐一般情况下使用绝对引用方式，但相对引用也是组织包结构的一种有效方式。在执行import操作时，Python会到import path下去搜索相关的模块和包，具体地，Python首先会查看模块缓存以确定当前包/模块是否已经被导入了，如果是，则去`built-in`模块下寻找，否则，会从以下路径中寻找：

1. 当前脚本所在路径
2. PYTHONPATH环境变量中的值
3. 安装包相关的路径（如使用pip、conda安装的一些库的路径）

直至找到，否则抛出异常。

以下举一个简单的例子，考虑以下包结构：

```bash
people/
│
├── eat.py
├── sleep.py
└── main.py
```

上述定义了一个`people`包，包含`eat`模块和`sleep`模块，`main`模块，其中`main`模块为该包内部的执行入口，各个模块定义如下：

```python
# in eat.py
def eat(thing):
    print(f"I eat {thing}")

# in sleep.py
def sleep(hours):
    print(f"I sleep {hours} hours.")

# in main.py
import eat
import sleep

if __name__ == "__main__":
    eat.eat("apple")
    sleep.sleep(8)
```

上述使用绝对引用的方式，在`main`模块中引用了`eat`模块和`sleep`模块，在包内执行`main.py`时，没有任何问题。如果有一天，有其他人希望在这个包外部实现一个调用接口，希望能够调用`main`这个模块，它的结构可能是这个样子的：

```bash
out/
│
├── people/
│   ├── eat.py
│   ├── sleep.py
│   └── main.py
│
└── out_caller.py
```

`out_caller`的实现为：

```python
# in out_caller.py
from out.people import main

main()
```

在这种情况下，执行`out_caller.py`时，会从`main`模块中抛出异常，提示`eat`模块找不到，原因是，当我们从`people`包外部执行`out_caller.py`时，import path发生了变化，原本通过绝对路径引入的`main`模块，其所在路径不再被import path包含时，自然也就找不到相关的模块了，这个时候，我们需要将`main.py`内容修改为相对路径引入，如下：

```python
# in main.py
from . import eat, sleep

if __name__ == "__main__":
    eat.eat("apple")
    sleep.sleep(8)
```

再次执行`out_caller.py`就不会再抛异常了。
但是，这时候，我们从`people`包内部又不能直接执行`main.py`了。解决办法之一是通过`try...except...`来同时尝试两种import，但需要注意的是，一个包中不能既有相对引用又有绝对引用。

```python
# in main.py
try:
    import eat, sleep
except ImportError:
    from . import eat, sleep


if __name__ == "__main__":
    eat.eat("apple")
    sleep.sleep(8)
```

这种实现就可以满足包内和包外两种调用方式了。

最后附上一些PEP 8中有关import的规范：

```markdown
Keep imports at the top of the file.
Write imports on separate lines.
Organize imports into groups: first standard library imports, then third-party imports, and finally local application or library imports.
Order imports alphabetically within each group.
Prefer absolute imports over relative imports.
Avoid wildcard imports like from module import *.
```

## References

1. [Python Doc: Module](https://docs.python.org/3/tutorial/modules.html)
2. [KimConnect](https://kimconnect.com/python-module-vs-package-vs-library-vs-framework/)
3. [Python Doc: The import system](https://docs.python.org/3/reference/import.html)
4. [portion](https://docs.python.org/3/glossary.html#term-portion)
5. [PEP 420](https://peps.python.org/pep-0420/)
6. [Python import: Advanced Techniques and Tips](https://realpython.com/python-import/)
