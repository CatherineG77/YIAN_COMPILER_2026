# Lab1 Lex Explanation

## 1. 这份实验到底在做什么

这次 lab 的任务，是自己实现一个最基础的编译器前端组件：`词法分析器`，也就是 `Lexer`。

如果你只有 Python 和 C++ 基础，可以先把整个过程理解成下面这样：

1. 读入一整份源代码文本
2. 按照语言规则，把文本切成一个一个“有意义的小块”
3. 给每个小块标上类别和位置
4. 把这些结果输出出来，供后面的编译阶段继续使用

比如这一行代码：

```text
i32 a = 42
```

不会被编译器直接整体处理，而是先切成：

```text
[3:1] <Keyword, i32>
[3:5] <Ident, a>
[3:7] <Keyword, Assign =>
[3:9] <Literal, 42>
```

这里每一小块就叫一个 `Token`。

## 2. 编译器在这个 lab 里分成哪几层

在完整编译器里，常见流程大概是：

1. 词法分析 `Lexing`
2. 语法分析 `Parsing`
3. 语义分析 `Semantic Analysis`
4. 中间代码生成
5. 优化
6. 目标代码生成

你这次只做第 1 步。

可以把它类比成读英文句子：

- 词法分析：先把句子切成一个个单词和标点
- 语法分析：再看这些单词怎么组成句子结构
- 语义分析：再判断这句话在逻辑上是否说得通

所以这个 lab 不负责“理解整段程序”，只负责“把字符流切成 token 流”。

## 3. 词法分析器的输入和输出

### 3.1 输入

输入是一整个源代码字符串：

```text
str source
```

### 3.2 输出

输出是一个 `Vec<Token>`，也就是 `Token` 的动态数组。

每个 `Token` 需要包含：

- token 的类型
- token 的值
- token 在源代码中的起始行号
- token 在源代码中的起始列号

输出格式在实验里固定为：

```text
[line:col] <kind, value>
```

## 4. 这个项目里几个重要文件分别干什么

### 4.1 `labs/lab1/lex/lexer.an`

这是核心文件。

它里面真正实现了词法分析逻辑：

- 维护当前位置
- 维护当前状态
- 识别单词、数字、字符串、字符、符号
- 跳过空白和注释
- 输出 token

### 4.2 `labs/lab1/lex/token.an`

这是“token 类型系统”的定义文件。

它告诉你：

- 有哪些关键字
- 有哪些字面量
- 一个 token 里到底装什么
- token 怎么转成文本输出

### 4.3 `labs/lab1/lex/lexer_main.an`

这是驱动程序，相当于测试入口。

它会：

1. 读取测试文件
2. 调用 `tokenize(source)`
3. 把结果写到 `labs/lab1/output/*.txt`

### 4.4 `labs/lab1/docs/lex.md`

这是实验说明。

你这次补全的 TODO 范围就是它规定的。

## 5. 先学会这个 lab 用到的 YIAN 基本语法

你不用一上来就掌握整门语言，只需要先掌握这几个最常用的东西。

### 5.1 导入

```text
from std.core.string import String
from token import Token, TokenData, Keyword, Literal
```

意思和 Python 的 `from ... import ...` 很像。

### 5.2 函数定义

```text
push_token(Vec<Token>* tokens, TokenData data, u64 line, u64 col) {
    tokens.push(Token.new(data, line, col))
}
```

可以先按这个方式理解：

- 函数名：`push_token`
- 参数列表：
  - `Vec<Token>* tokens`
  - `TokenData data`
  - `u64 line`
  - `u64 col`
- 花括号里是函数体

和 C++ 不太一样的是，这里很多函数前面不显式写返回类型。没有写时，你可以先把它理解成“返回空值”。

如果显式写返回类型，比如：

```text
pub Vec<Token> tokenize(str source) {
    ...
}
```

就表示：

- `pub`：公开
- 返回类型是 `Vec<Token>`
- 参数是 `str source`

### 5.3 变量定义

```text
u64 pos = 0
String buf = String.new()
State state = State.Start
```

格式是：

```text
类型 变量名 = 初始值
```

这点和 C++ 很像。

### 5.4 枚举 `enum`

```text
enum State {
    Start
    InIdent
    InNumber
    InString
    InChar
}
```

这表示 `State` 有 5 种可能的值。

你可以把它理解成 C++ 的枚举加强版。

在这个 lab 里，`State` 表示词法分析器当前正在干什么。

### 5.5 `impl`

```text
impl Keyword {
    static pub Option<Keyword> from_word(str text) {
        ...
    }
}
```

你可以先把 `impl` 理解成“给某个类型绑定方法”。

很像 C++ 里给类写成员函数，或者 Rust 里的 `impl`。

### 5.6 `static pub`

```text
static pub Option<Keyword> from_word(str text)
```

可以理解成：

- `static`：这是类型上的静态方法，不依赖某个实例
- `pub`：公开可用

调用方式是：

```text
Keyword.from_word(w)
```

### 5.7 泛型

```text
Vec<Token>
Option<Keyword>
```

这和 C++ 模板、Python 里的泛型注解有点像：

- `Vec<Token>`：装 `Token` 的动态数组
- `Option<Keyword>`：可能有一个 `Keyword`，也可能没有

### 5.8 `match`

```text
match Keyword.from_word(w) {
    Some as kw {
        ...
    }
    None {
        ...
    }
}
```

这和 `switch` 有点像，但更强。

它会根据枚举的不同变体分别处理。

这里的意思是：

- 如果结果是 `Some`，把里面的值绑定到变量 `kw`
- 如果结果是 `None`，走另一分支

### 5.9 `Option<T>`

标准库里有：

```text
Option<T> = None 或 Some { T val }
```

你可以把它当成“安全版的可能为空”。

非常像：

- Python 里的“可能是值，也可能是 `None`”
- C++ 里的 `std::optional<T>`

### 5.10 指针参数 `*`

```text
Vec<Token>* tokens
```

这个意思是“传入 `Vec<Token>` 的指针”。

为什么要这样写？

因为函数里要修改原来的 `tokens` 容器，而不是传一份拷贝。

调用时写：

```text
push_token(&tokens, ...)
```

和 C/C++ 里的取地址用法很像。

### 5.11 字符和字节

```text
u8 ch = bytes[pos]
```

这里 `bytes` 是源代码的字节切片，`ch` 是当前字节。

像下面这样：

```text
b'+'
b'\n'
b'"'
```

表示字节字面量。

### 5.12 `String` 和 `str`

这是这份 lab 特别重要的地方。

#### `str`

`str` 是字符串切片，偏“只读视图”。

#### `String`

`String` 是可变字符串，可以往里追加字符。

比如：

```text
String buf = String.new()
buf.push(char(ch))
```

意思是往可变字符串里加一个字符。

#### 二者转换

```text
str w = text.as_str()
```

表示把 `String` 变成 `str` 视图。

原因通常是：某些函数只需要读，不需要改。

## 6. 先学会这个 lab 用到的数据结构

## 6.1 `Token`

在 `token.an` 里：

```text
pub struct Token {
    TokenData data
    u64 line
    u64 col
}
```

意思是一个 token 由三部分组成：

- `data`：这个 token 到底是什么
- `line`：起始行
- `col`：起始列

### 6.2 `TokenData`

```text
pub enum TokenData {
    Kw { Keyword kw }
    Ident { String name }
    Lit { Literal lit }
    Unknown { String text }
    EOF
}
```

它表示 token 的“内容类别”：

- `Kw`：关键字或符号
- `Ident`：标识符
- `Lit`：字面量
- `Unknown`：无法识别的字符
- `EOF`：文件结束

### 6.3 `Keyword`

`Keyword` 不仅包括真正的语言关键字，比如：

- `if`
- `else`
- `while`
- `return`

还包括符号，比如：

- `(`
- `)`
- `+`
- `+=`
- `==`

也就是说，在这个 lab 的设计里：

- 关键字和符号都统一塞进 `Keyword`
- 然后再由 `TokenData.Kw(...)` 包起来

这是一个很常见的实验简化做法。

### 6.4 `Literal`

```text
pub enum Literal {
    Int { u64 value }
    Float { f64 value }
    Char { String text }
    Str { String text }
}
```

表示字面量有四种：

- 整数
- 浮点数
- 字符
- 字符串

这里字符和字符串保存的是“原始文本内容”，不是带引号的整段源码。

比如源码里：

```text
"Hello"
'A'
```

实际保存的是：

- `Hello`
- `A`

## 7. 这个 lexer 的核心思想：有限状态机

这份代码最核心的思想，是 `有限状态机`。

如果你没学过编译原理，可以先用很直观的方式理解：

词法分析器在扫描源码时，不同时间会处在不同“模式”里。

例如：

- 一开始什么都没读，处在 `Start`
- 读到字母后，进入“正在读标识符”的模式 `InIdent`
- 读到数字后，进入“正在读数字”的模式 `InNumber`
- 读到双引号后，进入“正在读字符串”的模式 `InString`
- 读到单引号后，进入“正在读字符”的模式 `InChar`

这就是状态机。

形式化一点说，状态机每次根据：

$$
\text{当前状态} + \text{当前输入字符}
$$

决定：

$$
\text{下一状态} + \text{是否输出 token} + \text{是否前进指针}
$$

这份 lab 里，状态集合是：

$$
\{ Start,\ InIdent,\ InNumber,\ InString,\ InChar \}
$$

## 8. `lexer.an` 从头到尾在做什么

下面我们按代码顺序讲。

## 8.1 顶部导入

```text
from std.core.string import String
from std.core.vec import Vec

from token import Token, TokenData, Keyword, Literal
```

用到的东西分别是：

- `String`：可变字符串缓冲区
- `Vec`：动态数组
- `Token`：输出 token 类型
- `TokenData`：token 的具体内容
- `Keyword`：关键字和符号的枚举
- `Literal`：字面量枚举

## 8.2 `State`

```text
enum State {
    Start
    InIdent
    InNumber
    InString
    InChar
}
```

这是整个状态机的核心。

### 每个状态的意义

#### `Start`

空闲状态，表示“当前还没开始构造一个 token”。

#### `InIdent`

已经读到了标识符或关键字的开头，比如：

```text
main
return
while
```

还要继续往后读，直到遇到不属于这个单词的字符。

#### `InNumber`

已经读到了数字开头，比如：

```text
42
3.14
```

#### `InString`

已经读到了字符串的开头 `"`，要继续读，直到遇到配对的 `"`。

#### `InChar`

已经读到了字符字面量开头 `'`，要继续读，直到遇到配对的 `'`。

## 8.3 `push_token`

```text
push_token(Vec<Token>* tokens, TokenData data, u64 line, u64 col) {
    tokens.push(Token.new(data, line, col))
}
```

### 作用

这是一个统一的“发 token”函数。

你不用每次都手写：

```text
tokens.push(Token.new(...))
```

只需要调用：

```text
push_token(...)
```

### 参数解释

- `Vec<Token>* tokens`
  - token 数组的指针
  - 这样函数里 push 进去，外面的数组会真的被修改
- `TokenData data`
  - token 的具体内容
- `u64 line`
  - token 起始行号
- `u64 col`
  - token 起始列号

### 返回值

没有显式返回值，本质上是一个“执行动作”的辅助函数。

## 8.4 `emit_symbol`

```text
emit_symbol(Vec<Token>* tokens, str sym, u64 line, u64 col) {
    match Keyword.from_symbol(sym) {
        None { panic("unreachable symbol") }
        Some as kw {
            push_token(tokens, TokenData.Kw(kw.val), line, col)
        }
    }
}
```

### 作用

把一个符号文本，比如：

- `"+"`
- `"=="`
- `"("`

转换成对应的 `Keyword`，然后发出 token。

### 为什么不直接手写 `push_token`

因为不同符号都已经在 `Keyword.from_symbol(...)` 里定义好了映射关系。

比如：

- `"+" -> Keyword.Plus`
- `">=" -> Keyword.GreaterEqual`

复用这个映射，比自己在每个地方手写枚举值更安全。

### `panic("unreachable symbol")` 是什么意思

意思是：

- 如果你传进来的 `sym` 理论上应该都是合法符号
- 如果居然查不到，就说明程序逻辑有 bug
- 那就直接报错停掉

这里的 `"unreachable"` 可以理解成“按设计不应该发生”。

## 8.5 `emit_word`

这是你补的第一个 TODO。

代码：

```text
emit_word(Vec<Token>* tokens, String text, u64 line, u64 col) {
    str w = text.as_str()
    match Keyword.from_word(w) {
        Some as kw {
            push_token(tokens, TokenData.Kw(kw.val), line, col)
        }
        None {
            push_token(tokens, TokenData.Ident(text), line, col)
        }
    }
}
```

### 这个函数要解决什么问题

在源码里，像这些东西一开始看起来都只是“字母开头的单词”：

```text
if
while
return
main
sum_odd
```

但它们并不属于同一类：

- `if`、`while`、`return` 是关键字
- `main`、`sum_odd` 是普通标识符

所以当我们读完一个“单词”之后，必须做一次分类判断。

### 为什么先写

```text
str w = text.as_str()
```

因为 `Keyword.from_word(...)` 的参数类型是 `str`，而传进来的 `text` 是 `String`。

所以这里是在做类型适配：

- `String` 适合构造、拼接
- `str` 适合只读查询

### 为什么用 `match Keyword.from_word(w)`

因为 `from_word(w)` 返回的是：

```text
Option<Keyword>
```

也就是：

- 有可能找到关键字，对应 `Some`
- 也可能找不到，对应 `None`

### `Some as kw` 到底是什么意思

这表示：

- 如果返回值是 `Some`
- 就把里面包着的关键字取出来
- 绑定到变量 `kw`

注意这里的 `kw` 不是直接的 `Keyword`，而是一个带字段的匹配结果，所以后面取值写的是：

```text
kw.val
```

### 为什么关键字要发成

```text
TokenData.Kw(kw.val)
```

因为 `TokenData.Kw(...)` 这个变体里面要求装的是 `Keyword`。

### 为什么普通单词要发成

```text
TokenData.Ident(text)
```

因为它不是语言保留字，只是用户自己定义的名字。

例如：

- 变量名
- 函数名
- 类型名

### 这个 TODO 的核心思想

一句话总结：

> 先把“字母串”读出来，再查表判断它到底是关键字还是标识符。

这是词法分析里非常标准的一步。

## 8.6 `tokenize`

这是整个 lab 最核心的函数。

签名：

```text
pub Vec<Token> tokenize(str source)
```

意思是：

- 输入：源代码字符串 `source`
- 输出：token 动态数组

## 9. `tokenize` 里的每一个变量都是什么意思

### 9.1 `Vec<Token> tokens = Vec<Token>.new()`

创建一个空数组，用来存放所有输出 token。

### 9.2 `u8[] bytes = source.as_slice()`

把整个字符串转换成字节切片。

为什么不直接按字符处理？

因为 lexer 最底层通常就是按“当前位置的字节”逐个往前扫，这样实现最直接。

### 9.3 `u64 len = bytes.len()`

源码总长度。

### 9.4 `u64 pos = 0`

当前扫描位置。

你可以把它理解成“读指针”。

### 9.5 `u64 line = 1`

当前扫描点所在行号。

### 9.6 `u64 col = 1`

当前扫描点所在列号。

### 9.7 `u64 tok_line = 1`, `u64 tok_col = 1`

当前正在构造的 token 的起始位置。

这是一个特别重要的设计。

为什么需要单独记？

因为：

- `line`, `col` 会随着扫描不断变化
- 但一个 token 的输出位置，必须是“它开始出现时”的位置

例如识别 `return`：

- 读第一个字母 `r` 时，它起点是 `(5, 9)`
- 读完整个单词后，当前列可能已经变到更后面了
- 但输出 token 时，仍然要写 `(5, 9)`

所以必须在 token 开始时把起点单独存下来。

### 9.8 `State state = State.Start`

初始状态是 `Start`。

### 9.9 `String buf = String.new()`

缓冲区，存放“当前正在读的 token 文本”。

比如：

- 读标识符时，`buf` 可能是 `"main"`
- 读数字时，`buf` 可能是 `"3.14"`
- 读字符串时，`buf` 可能是 `"Hello\n"`

## 10. 主循环 `loop`

```text
loop {
    ...
}
```

这可以理解成一个无限循环，直到你自己 `break`。

整个词法分析过程就是：

- 不断看当前字符
- 根据状态决定怎么处理
- 移动位置
- 直到读完整个文件

## 11. 文件结束时的处理

这一段非常重要：

```text
if pos >= len {
    match state {
        InIdent { ... }
        InNumber { ... }
        InString { ... }
        InChar { ... }
        _ {}
    }
    push_token(&tokens, TokenData.EOF, line, col)
    break
}
```

### 为什么需要这段

因为最后一个 token 可能恰好顶到文件结尾。

例如文件最后是：

```text
return 0
```

如果没有这段逻辑，那么：

- `0` 已经被读进 `buf`
- 但由于后面没有新的字符来触发“结束数字”的分支
- 这个数字 token 就永远不会被发出去

所以到文件末尾时，要根据当前状态决定是否把 `buf` 收尾成 token。

### 为什么最后还要加 `EOF`

`EOF` 表示 End Of File。

它告诉后续阶段：

> 输入已经结束了。

很多编译器都会显式加一个 EOF token。

## 12. `old_pos` 和 `ch`

```text
u64 old_pos = pos
u8 ch = bytes[pos]
```

### `ch`

当前字符对应的字节。

### `old_pos`

记录“这一轮开始前的位置”。

为什么需要它？

因为这轮处理过程中，`pos` 可能会移动多次。

例如：

- 读一个普通字符时，`pos += 1`
- 读 `+=` 时，`pos += 2`
- 跳过整行注释时，`pos` 可能直接跳很多格

最后更新行列号时，就要知道：

- 这一轮到底从哪里移动到了哪里

这正是 `old_pos` 的作用。

## 13. `match state`：根据当前状态处理当前字符

整个 lexer 的核心就在这里：

```text
match state {
    Start { ... }
    InIdent { ... }
    InNumber { ... }
    InString { ... }
    InChar { ... }
}
```

这和“人读代码”的行为非常像。

### 当我什么都没在读时

看当前字符是：

- 空白
- 字母
- 数字
- 引号
- 操作符

### 当我已经在读标识符时

继续看下一个字符是否还属于标识符。

### 当我已经在读数字时

继续看下一个字符是否还属于数字。

这就是状态机思想。

## 14. `Start` 状态详解

`Start` 可以理解成“我现在没有正在拼接的 token”。

### 14.1 空白字符

```text
if ch.is_ascii_whitespace() {
    pos += 1
}
```

### 作用

跳过空白。

包括：

- 空格
- 制表符
- 换行

### 为什么不输出 token

因为本实验要求跳过空白，不把它们当 token。

### 14.2 字母开头：进入标识符状态

```text
elif ch.is_ascii_alpha() {
    tok_line = line
    tok_col = col
    state = State.InIdent
    buf = String.new()
    buf.push(char(ch))
    pos += 1
}
```

### 每一步都在做什么

#### `tok_line = line`, `tok_col = col`

记录这个 token 的起始位置。

#### `state = State.InIdent`

表示：我们已经确认它是一个“单词”开头，接下来进入读标识符/关键字的状态。

#### `buf = String.new()`

新建缓冲区。

#### `buf.push(char(ch))`

把当前字符先放进去。

注意 `ch` 是字节 `u8`，而 `push` 需要字符类型，所以要：

```text
char(ch)
```

这表示从字节转换成字符。

#### `pos += 1`

当前字符已经消费掉了，扫描位置向前走一格。

### 14.3 数字开头：进入数字状态

```text
elif ch.is_ascii_digit() {
    tok_line = line
    tok_col = col
    state = State.InNumber
    buf = String.new()
    buf.push(char(ch))
    pos += 1
}
```

逻辑和标识符几乎完全一样，只是状态变成 `InNumber`。

### 14.4 双引号开头：进入字符串状态

```text
elif ch == b'"' {
    tok_line = line
    tok_col = col
    state = State.InString
    buf = String.new()
    pos += 1
}
```

### 为什么这里不把引号本身放进 `buf`

因为实验里字符串 token 的值是不带外层双引号的。

例如源码：

```text
"Hello"
```

最后输出的应该是：

```text
<Literal, Hello>
```

而不是带引号。

### 14.5 单引号开头：进入字符状态

```text
elif ch == b'\'' {
    tok_line = line
    tok_col = col
    state = State.InChar
    buf = String.new()
    pos += 1
}
```

逻辑和字符串类似。

### 14.6 符号处理

从 `+` 一直到 `>` 这一大段，都是在识别操作符和分隔符。

例如：

```text
+   +=
-   -=
*   *=
/   /=
%   %=
=   ==
<   <=   <<   <<=
>   >=   >>   >>=
```

### 这里的通用模式

以 `+` 为例：

```text
elif ch == b'+' {
    if pos + 1 < len and bytes[pos + 1] == b'=' {
        emit_symbol(&tokens, "+=", line, col)
        pos += 2
    } else {
        emit_symbol(&tokens, "+", line, col)
        pos += 1
    }
}
```

逻辑是：

1. 先看当前字符是不是 `+`
2. 如果下一个字符存在，并且是 `=`
3. 那么识别成两个字符的复合符号 `+=`
4. 否则就识别成单字符符号 `+`

### 为什么一定要先判断长的，再判断短的

这是词法分析里的“最长匹配”思想。

例如看到：

```text
>=
```

应该识别成一个 token `>=`，而不是两个 token：

- `>`
- `=`

所以：

- 先尝试匹配长符号
- 不行再退回短符号

### 14.7 注释

```text
elif ch == b'/' {
    if pos + 1 < len and bytes[pos + 1] == b'/' {
        pos += 2
        while pos < len and bytes[pos] != b'\n' {
            pos += 1
        }
    } ...
}
```

### 作用

识别单行注释：

```text
// something
```

### 具体逻辑

1. 当前字符是 `/`
2. 看下一个是不是 `/`
3. 如果是，说明遇到了 `//`
4. 从这里开始一直跳过，直到行尾换行符

### 为什么换行符不在 `while` 里一起吃掉

因为这里希望：

- 注释内容跳过
- 但换行本身保留给后面的统一行列更新逻辑处理

这样位置统计更稳定。

### 14.8 `Unknown`

```text
String unk = String.new()
unk.push(char(ch))
push_token(&tokens, TokenData.Unknown(unk), line, col)
pos += 1
```

如果一个字符：

- 不是空白
- 不是字母
- 不是数字
- 不是引号
- 不是已知符号

那就把它当 `Unknown`。

这是最基本的错误兜底手段。

## 15. `InIdent` 详解

这是你补的第二类 TODO 之一。

代码：

```text
InIdent {
    if ch.is_ascii_alphanumeric() or ch == b'_' {
        buf.push(char(ch))
        pos += 1
    } else {
        emit_word(&tokens, buf, tok_line, tok_col)
        buf = String.new()
        state = State.Start
    }
}
```

### 这个状态在干什么

你已经知道当前 token 是一个“单词”了，现在要继续向后读，直到这个单词结束。

### 为什么条件是

```text
ch.is_ascii_alphanumeric() or ch == b'_'
```

因为标识符内部允许：

- 字母
- 数字
- 下划线

例如：

```text
main
sum1
sum_odd
```

### 为什么遇到不属于标识符的字符时，不立刻 `pos += 1`

这是一个非常关键的思想。

假设源码是：

```text
main(
```

当你在 `InIdent` 里看到 `(` 时，说明：

- `main` 已经结束了
- 但 `(` 本身是下一个 token 的开始

所以这里不能把 `(` 吃掉。

正确做法是：

1. 先把当前 `buf` 发出去
2. 状态切回 `Start`
3. 不移动 `pos`
4. 下一轮循环再由 `Start` 状态重新处理这个 `(`

这叫“当前字符不属于本 token，但属于下一个 token”。

### 为什么这里调用 `emit_word`

因为 `buf` 只是“一个读完的单词”。

它可能是：

- `if`
- `return`
- `main`

必须交给 `emit_word(...)` 去判断到底是关键字还是标识符。

### 为什么清空 `buf`

因为当前这个 token 已经结束了，缓冲区要为下一个 token 做准备。

### 这个 TODO 的一句话总结

> 在 `InIdent` 状态里，不断积累合法字符；一旦结束，就把整个单词交给 `emit_word` 分类输出。

## 16. `InNumber` 详解

这是你补的第二类 TODO 之二。

代码：

```text
InNumber {
    if ch.is_ascii_digit() or ch == b'.' {
        buf.push(char(ch))
        pos += 1
    } else {
        push_token(&tokens, TokenData.Lit(Literal.from_number_text(buf.as_str())), tok_line, tok_col)
        buf = String.new()
        state = State.Start
    }
}
```

### 这个状态在做什么

持续读取数字字面量。

比如：

- `42`
- `3.14`

### 为什么这里允许 `.`

因为这个 lab 支持简单浮点数。

例如：

```text
3.14
```

### `Literal.from_number_text(...)` 是什么

它定义在 `token.an`：

```text
static pub Self from_number_text(str text) {
    if text.contains_char('.') {
        return Literal.Float(text.parse<f64>())
    }
    return Literal.Int(text.parse<u64>())
}
```

逻辑非常直接：

1. 如果文本里含有 `.`，就当浮点数
2. 否则当整数

### 为什么要写成

```text
TokenData.Lit(...)
```

因为数字字面量属于 token 的 `Lit` 这一类。

### 为什么这里也不能吃掉当前不合法字符

同 `InIdent` 的原因一样。

例如：

```text
42)
```

读到 `)` 时：

- `42` 结束了
- `)` 是下一个 token

所以这轮只发数字，不前进 `pos`。

### 这个 TODO 的一句话总结

> 数字状态负责把整段数字文本收集完整，然后调用 `Literal.from_number_text(...)` 统一构造数字字面量。

## 17. `InString` 详解

这是你补的第二类 TODO 之三。

代码核心：

```text
if ch == b'"' {
    push_token(&tokens, TokenData.Lit(Literal.from_string_text(buf.as_str())), tok_line, tok_col)
    buf = String.new()
    state = State.Start
    pos += 1
} elif ch == b'\\' {
    buf.push(char(ch))
    pos += 1
    if pos < len {
        buf.push(char(bytes[pos]))
        pos += 1
    }
} else {
    buf.push(char(ch))
    pos += 1
}
```

### 这个状态在干什么

已经读到了开头的双引号，接下来要把字符串内容读完整。

### 分三种情况

#### 情况 1：遇到结束双引号

```text
if ch == b'"'
```

表示字符串结束。

这时要：

1. 把 `buf` 里的字符串内容发成 token
2. 清空 `buf`
3. 回到 `Start`
4. `pos += 1` 吃掉这个结束引号

### 为什么这里要 `pos += 1`

因为这个双引号属于当前字符串 token 的结束边界，不是下一个 token 的起点。

和 `InIdent`、`InNumber` 不同，这个字符本身就是当前 token 的一部分边界，所以要消费掉。

#### 情况 2：遇到反斜杠 `\`

```text
elif ch == b'\\'
```

这说明可能遇到了转义序列，比如：

- `\n`
- `\"`
- `\\`

代码做法是：

1. 先把 `\` 放进 `buf`
2. 再把后一个字符也放进 `buf`

所以源码：

```text
"Hello\n"
```

最终 `buf` 中存的是：

```text
Hello\n
```

注意：这里没有把 `\n` 真的转换成换行字符，而是保留原始文本形式。

这和当前 `Literal.Str { String text }` 的设计是一致的。

#### 情况 3：普通字符

直接追加到 `buf`。

### `Literal.from_string_text(...)`

定义在 `token.an`：

```text
static pub Self from_string_text(str text) {
    return Literal.Str(String.from(text))
}
```

也就是把内容包装成字符串字面量。

### 这个 TODO 的一句话总结

> 字符串状态不断收集字符串内容，遇到结束引号时发出字符串字面量 token；遇到反斜杠时把转义序列按原样成对收集。

## 18. `InChar` 详解

这是你补的第二类 TODO 之四。

逻辑和 `InString` 几乎完全平行，只是结束符从双引号变成了单引号。

代码核心：

```text
if ch == b'\'' {
    push_token(&tokens, TokenData.Lit(Literal.from_char_text(buf.as_str())), tok_line, tok_col)
    buf = String.new()
    state = State.Start
    pos += 1
} elif ch == b'\\' {
    ...
} else {
    ...
}
```

### `Literal.from_char_text(...)`

定义：

```text
static pub Self from_char_text(str text) {
    return Literal.Char(String.from(text))
}
```

表示把字符字面量内容包装成 `Literal.Char`。

### 为什么字符和字符串都保存“原始文本”

因为这个 lab 不需要真的去解释转义序列，只需要词法层面正确识别 token。

也就是说，这个阶段重点是：

- 这是不是一个字符字面量？
- 它从哪里开始，到哪里结束？

而不是：

- 它最终运行时代表哪个 Unicode 码点？

### 这个 TODO 的一句话总结

> 字符状态是字符串状态的单字符版本，遇到结束单引号时发出字符字面量 token。

## 19. 行列号更新

这是你补的第三类 TODO。

代码：

```text
while old_pos < pos {
    if bytes[old_pos] == b'\n' {
        line += 1
        col = 1
    } else {
        col += 1
    }
    old_pos += 1
}
```

### 这是整个 lab 最容易“看懂代码但没真正理解”的地方之一

你一定要真正理解它。

### 为什么不在每个分支里直接修改 `line` 和 `col`

因为不同分支对 `pos` 的推进长度不一样：

- 普通字符可能前进 1
- `+=` 前进 2
- `>>=` 前进 3
- 注释可能前进很多

如果你在每个分支里都手动维护行列，很容易漏掉或写乱。

所以这里用了一个更稳的设计：

1. 这轮开始时记录 `old_pos`
2. 逻辑分支只负责改 `pos`
3. 这轮结束后，再统一把 `[old_pos, pos)` 之间所有真正吃掉的字符逐个更新到行列号上

这是一种很经典的实现方式。

### 为什么换行时是

```text
line += 1
col = 1
```

因为实验要求列号是从 `1` 开始记。

所以一旦遇到换行：

- 行数加一
- 下一行第一个字符的列号重新从 1 开始

### 为什么普通字符是 `col += 1`

因为读过一个普通字符之后，扫描位置自然往右移动一列。

### 这里和 token 起始位置是什么关系

不要混淆：

- `line`, `col`：当前扫描指针的位置
- `tok_line`, `tok_col`：当前 token 开始时的位置

词法分析的关键就是：

- 扫描中动态维护当前坐标
- token 开始时单独记住起点

### 这个 TODO 的一句话总结

> 不在分支里零散地更新坐标，而是在每轮扫描后，统一根据实际消费过的字符区间来更新行列号。

## 20. `token.an` 里你必须理解的函数

## 20.1 `Keyword.from_word(str text)`

### 作用

把一个单词字符串映射成关键字。

例如：

```text
"if"     -> Some(Keyword.If)
"return" -> Some(Keyword.Return)
"main"   -> None
```

### 为什么 `main` 返回 `None`

因为 `main` 不是保留字，只是用户自定义名字。

### 这个函数本质上是什么

就是一个“关键字查表函数”。

## 20.2 `Keyword.from_symbol(str text)`

### 作用

把符号文本映射成枚举值。

例如：

```text
"+"   -> Some(Keyword.Plus)
"+="  -> Some(Keyword.PlusAssign)
"("   -> Some(Keyword.LParen)
```

### 它为什么重要

因为 lexer 在识别出具体符号文本后，不想自己再手动决定枚举值。

统一查表更清晰。

## 20.3 `Literal.from_number_text(str text)`

### 作用

把数字文本转成字面量对象。

### 当前简化规则

```text
有 '.' -> Float
没有 '.' -> Int
```

### 这意味着什么

这说明本实验模板实现的是“简化版 lexer”：

- 支持简单十进制整数
- 支持简单小数浮点数

没有完整覆盖语言文档里所有复杂数字形式。

## 20.4 `ToString`

在 `token.an` 里，很多类型实现了 `ToString`：

- `Keyword`
- `Literal`
- `TokenData`
- `Token`

### 作用

让这些对象可以统一转成文本输出。

比如 `Token.to_string()` 最终生成：

```text
[3:5] <Ident, main>
```

这其实就是测试结果文件里的格式。

## 21. `lexer_main.an` 在做什么

## 21.1 `write_tokens`

```text
write_tokens(str output_path, Vec<Token>* tokens) {
    String out = String.new()
    out += "=== Lexer Output ===\n"
    for token in *tokens {
        out += token.to_string()
        out.push_str("\n")
    }
    write_file(output_path, out.as_str())
}
```

### 作用

把 token 列表写入文件。

### 过程

1. 新建字符串 `out`
2. 先加头部：

```text
=== Lexer Output ===
```

3. 遍历每个 token
4. 调用 `token.to_string()`
5. 每个 token 后面补一个换行
6. 写入目标文件

### `for token in *tokens`

这里的 `tokens` 是指针，所以先 `*tokens` 解引用，再迭代。

这点有一点 C/C++ 的味道。

## 21.2 `main`

### 作用

批量跑测试。

### 具体逻辑

1. 构建测试编号列表 `01` 到 `10`
2. 对每个编号：
   - 生成输入路径
   - 生成输出路径
   - 读源码
   - 调 `tokenize`
   - 写结果
   - 打印提示

### 为什么即使没有 `07-10` 的公开样例，它也还写了 `07-10`

因为实验评分会用隐藏测试。

## 22. 这份 lexer 的完整运行流程

以这一段代码为例：

```text
i32 main() {
    return 0
}
```

可以大致这样理解：

### 第一步：读到 `i`

- 当前状态：`Start`
- `i` 是字母
- 进入 `InIdent`
- `buf = "i"`

### 第二步：继续读 `3`、`2`

- 状态仍然是 `InIdent`
- 都属于标识符内容
- `buf = "i32"`

### 第三步：读到空格

- 空格不属于标识符
- 调 `emit_word("i32")`
- 查表发现这是关键字
- 输出：

```text
<Keyword, i32>
```

- 状态回到 `Start`

### 第四步：读 `main`

- 同理进入 `InIdent`
- 最终输出 `<Ident, main>`

### 第五步：读 `(`

- 在 `Start` 中识别符号
- 输出 `<Keyword, LParen (>`

### 第六步：读 `)`

- 输出 `<Keyword, RParen )>`

### 第七步：读 `{`

- 输出 `<Keyword, LBrace {>`

### 第八步：读 `return`

- 进入 `InIdent`
- 结束时查表发现是关键字
- 输出 `<Keyword, return>`

### 第九步：读 `0`

- 进入 `InNumber`
- 结束时调用 `Literal.from_number_text("0")`
- 输出 `<Literal, 0>`

### 第十步：读 `}`

- 输出 `<Keyword, RBrace }>`

### 第十一步：文件结束

- 输出 `<EOF>`

## 23. 你补的每个 TODO，为什么必须这么写

这里我再用“问题 -> 为什么 -> 如果不这么写会怎样”的方式总结一遍。

## 23.1 TODO 1：`emit_word`

### 问题

读完一个字母串后，怎么判断它到底是关键字还是普通标识符？

### 你的做法

```text
match Keyword.from_word(w) {
    Some as kw {
        push_token(tokens, TokenData.Kw(kw.val), line, col)
    }
    None {
        push_token(tokens, TokenData.Ident(text), line, col)
    }
}
```

### 为什么对

因为关键字和标识符在扫描阶段长得很像，都可能是“字母开头的一串字符”。

所以必须“先读完整，再查关键字表”。

### 如果不这么写会怎样

如果你把所有单词都当 `Ident`，那么：

- `if`
- `while`
- `return`

都会被识别错。

如果你把所有单词都当关键字，那普通变量名又会全部出错。

## 23.2 TODO 2：`InIdent` 收束

### 问题

什么时候一个标识符结束？

### 你的做法

当遇到“不再属于标识符”的字符时：

1. 发出当前单词 token
2. 清空缓冲区
3. 切回 `Start`
4. 不消费当前字符

### 为什么对

因为这个结束字符通常正是下一个 token 的开始。

### 如果错误地 `pos += 1`

你会把下一个 token 的第一个字符丢掉。

例如：

```text
main(
```

如果在 `InIdent` 结束时把 `(` 吃掉，下一轮就再也看不到它了。

## 23.3 TODO 3：`InNumber` 收束

### 问题

数字读完之后怎么生成字面量 token？

### 你的做法

```text
push_token(&tokens, TokenData.Lit(Literal.from_number_text(buf.as_str())), tok_line, tok_col)
```

### 为什么对

因为：

- 数字属于 `Literal`
- 而具体是整数还是浮点数，交给 `Literal.from_number_text(...)` 判断

这比在 `lexer.an` 里手写两套逻辑更清楚。

## 23.4 TODO 4：`InString` 收束

### 问题

字符串遇到结束双引号时该怎么办？

### 你的做法

1. 用 `Literal.from_string_text(...)` 构造字符串字面量
2. 发 token
3. 清空缓冲区
4. 切回 `Start`
5. 吃掉结束引号

### 为什么这里必须吃掉结束引号

因为这个引号属于当前字符串的结束标记，不应该留给下一轮重复处理。

## 23.5 TODO 5：`InChar` 收束

### 问题

字符字面量遇到结束单引号时该怎么办？

### 你的做法

和字符串同理。

### 为什么逻辑几乎一样

因为字符和字符串在词法层面的边界行为本来就很相似：

- 都有开始引号
- 都有结束引号
- 都可能有转义字符

## 23.6 TODO 6：行列号更新

### 问题

怎么保证每个 token 的位置都准确？

### 你的做法

统一根据本轮实际消费掉的字符区间更新：

```text
while old_pos < pos { ... }
```

### 为什么这是更稳的写法

因为 lexer 不同分支前进步数不同，统一后处理能大幅减少漏更新和重复更新。

### 如果在各分支里手动维护

你会很容易在：

- 复合运算符
- 注释
- 转义字符

这些地方出现行列错位。

## 24. 你在这个 lab 里真正学到的编译器知识

如果你把上面的内容真正理解了，你已经掌握了这些核心概念：

### 24.1 Token

源代码不是直接处理的，而是先切成 token 序列。

### 24.2 Lexer

lexer 的职责是：

- 读取字符流
- 识别 token 边界
- 给 token 分类
- 记录位置信息

### 24.3 最长匹配

例如：

- `>=` 应优先识别成一个 token
- 而不是 `>` 加 `=`

### 24.4 状态机

lexer 的本质不是“随便写几个 if”，而是：

- 在不同状态下对同一个字符采取不同处理

### 24.5 缓冲区

很多 token 不是单个字符，需要先积累文本，再统一发出。

### 24.6 延迟分类

像单词这种东西，往往要先收集完整，再决定它属于哪一类。

### 24.7 位置跟踪

编译器不仅要知道“读到了什么”，还要知道“它在哪儿”。

这在后面的错误提示中非常重要。

## 25. 你现在已经可以自己解决什么类型的问题

如果下次再给你一个同难度 lab，你应该已经可以自己处理这些任务：

1. 看懂一个简化 lexer 模板
2. 识别哪些状态是“开始状态”，哪些是“读取中状态”
3. 自己补齐 token 收束逻辑
4. 自己实现关键字查表
5. 自己实现复合运算符的最长匹配
6. 自己维护行列号
7. 自己分析为什么一个 token 被错分
8. 对照输出文件定位是“分类错了”还是“位置错了”

## 26. 以后你做这类题的通用思考模板

下次你再遇到类似 lab，可以按这套顺序思考。

### 第一步：先问自己，这个 lexer 输出什么

- token 类型有哪些
- 每个 token 是否要带值
- 是否要带位置信息

### 第二步：列出状态

至少先想：

- 空闲状态
- 标识符状态
- 数字状态
- 字符串状态
- 注释状态

### 第三步：想清楚 token 的开始条件

例如：

- 字母开头 -> 标识符
- 数字开头 -> 数字
- `"` -> 字符串
- `'` -> 字符

### 第四步：想清楚 token 的结束条件

例如：

- 标识符遇到非字母数字下划线就结束
- 数字遇到非数字就结束
- 字符串遇到未转义双引号就结束

### 第五步：区分“当前字符属于谁”

这是最关键的一步。

当读到某个字符时，问自己：

- 它属于当前 token 吗？
- 它是下一个 token 的开始吗？
- 它应该现在吃掉，还是留给下一轮？

### 第六步：最后统一检查位置更新

如果输出的 token 值都对，但测试仍然错，很可能是行列号错了。

## 27. 这份 lab 当前实现的范围边界

为了你认知更完整，我还要提醒你：

这份实验模板实现的是“简化版 lexer”，不是完整 YIAN 语言词法系统。

例如当前版本：

- 支持简单整数
- 支持简单小数
- 支持字符串和字符
- 支持基础关键字和符号

但对语言文档里更完整的特性，可能没有全覆盖，比如：

- 更复杂数字格式
- 某些额外词法边界

这不是你没学会，而是 lab 本身就做了简化。

你要学会区分：

- “实验要求的简化版本”
- “真实语言的完整规范”

这是做编译器实验时非常重要的能力。

## 28. 最后的总总结

你这次补全的代码，本质上是在做这样一件事：

> 把一整段源代码，按 YIAN 的基础词法规则，从左到右扫描，切分成一个个 token，并精确记录每个 token 的起始位置。

而你补的所有 TODO，本质上都围绕三个核心问题：

1. 一个单词读完后，怎么区分它是关键字还是标识符
2. 一个正在读取中的 token，什么时候结束，结束时怎么发出
3. 扫描位置变了以后，怎么正确更新行号和列号

如果你已经真正理解了这三个问题，那么你其实已经跨过了编译原理入门里最关键的一步。

你不是“记住了几段代码”，而是已经开始理解 lexer 为什么要这么设计了。

