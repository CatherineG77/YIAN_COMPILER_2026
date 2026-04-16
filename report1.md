# Lab1 Report


位置：`labs/lab1/lex/lexer.an` 的 `emit_word`

## TODO 1


补全内容：

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

所在函数代码：

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

补全逻辑：

- 先把 `String` 转成 `str`，因为查关键字表用的是 `Keyword.from_word(w)`。
- 如果查到关键字，就生成 `TokenData.Kw(...)`。
- 如果查不到，就生成 `TokenData.Ident(text)`。

语法点：

- `match` 用来分类处理返回值。
- `Some as kw` 表示把匹配到的值绑定到 `kw`。
- `TokenData.Kw(...)`、`TokenData.Ident(...)` 是枚举构造。

易错点：

- 不能把所有单词都直接当成 `Ident`。
- `push_token(tokens, ...)` 这里不用写 `&tokens`，因为参数本身已经是 `Vec<Token>* tokens`。
- 关键字判断必须在“读完整个单词后”做，不能边读边判。
## TODO 2

位置：`labs/lab1/lex/lexer.an` 的 `tokenize`

补全内容：

```text
emit_word(&tokens, buf, tok_line, tok_col)
buf = String.new()
```

所在代码片段：

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

补全逻辑：

- 当前字符不再属于标识符时，说明前面的 `buf` 已经是完整单词。
- 调用 `emit_word` 发出 token。
- 清空缓冲区，准备下一个 token。
- 不在这里 `pos += 1`，把当前字符留给下一轮 `Start` 状态处理。

语法点：

- `or` 是逻辑或。
- `b'_'` 是字节字面量。
- `&tokens` 表示把 `tokens` 的地址传给需要指针参数的函数。

易错点：

- `buf` 里已经包含完整单词，不能漏发。
- 这里不能多吃一个字符，否则像 `main(` 里的 `(` 会被跳过。
- 标识符规则是“字母数字下划线”，不能漏掉 `_`。

## TODO 3：`InNumber` 收束

位置：`labs/lab1/lex/lexer.an` 的 `tokenize`

补全内容：

```text
push_token(&tokens, TokenData.Lit(Literal.from_number_text(buf.as_str())), tok_line, tok_col)
buf = String.new()
```

所在代码片段：

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

补全逻辑：

- 数字结束后，要把 `buf` 作为数字字面量发出。
- 具体是整数还是浮点数，不在 lexer 里手写判断，而是交给 `Literal.from_number_text(...)`。
- 发完后清空 `buf`，回到 `Start`。

语法点：

- `TokenData.Lit(...)` 表示字面量 token。
- `buf.as_str()` 把 `String` 转成函数需要的 `str`。

易错点：

- 不能直接写成 `TokenData.Ident(buf)`，数字不是标识符。
- 不要忘记包一层 `Literal.from_number_text(...)`。
- 这里同样不要多写 `pos += 1`。

## TODO 4：`InString` 收束

位置：`labs/lab1/lex/lexer.an` 的 `tokenize`

补全内容：

```text
push_token(&tokens, TokenData.Lit(Literal.from_string_text(buf.as_str())), tok_line, tok_col)
buf = String.new()
```

所在代码片段：

```text
InString {
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
}
```

补全逻辑：

- 遇到结束双引号时，说明字符串正文已经在 `buf` 里。
- 用 `Literal.from_string_text(...)` 构造字符串字面量。
- 发 token 后清空缓冲区。
- 结束引号要 `pos += 1` 吃掉，因为它属于当前字符串的结束标记。

语法点：

- `b'"'` 表示双引号字节。
- `b'\\'` 表示反斜杠字节。
- `elif` 是条件分支。

易错点：

- 不要把结束引号也塞进 `buf`。
- 这里必须吃掉结束引号，否则下一轮还会再次处理它。
- 转义字符分支里是先吃 `\`，再吃后一个字符，两个都要进 `buf`。

## TODO 5：`InChar` 收束

位置：`labs/lab1/lex/lexer.an` 的 `tokenize`

补全内容：

```text
push_token(&tokens, TokenData.Lit(Literal.from_char_text(buf.as_str())), tok_line, tok_col)
buf = String.new()
```

所在代码片段：

```text
InChar {
    if ch == b'\'' {
        push_token(&tokens, TokenData.Lit(Literal.from_char_text(buf.as_str())), tok_line, tok_col)
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
}
```

补全逻辑：

- 字符字面量结束时，`buf` 中保存的是字符内容。
- 调用 `Literal.from_char_text(...)` 生成字符字面量 token。
- 清空 `buf`，切回 `Start`，再吃掉结束单引号。

语法点：

- `b'\''` 是单引号字节，写法容易看花。
- 整体结构和字符串分支几乎一致，只是构造函数换成了 `from_char_text`。

易错点：

- 最容易写错的是把 `from_char_text` 写成 `from_string_text`。
- 结束单引号也必须 `pos += 1` 吃掉。
- 转义字符如 `'\n'` 不能拆坏，`\` 和后面的字符都要保留。

## TODO 6：行列号更新

位置：`labs/lab1/lex/lexer.an` 的 `tokenize`

补全内容：

```text
if bytes[old_pos] == b'\n' {
    line += 1
    col = 1
} else {
    col += 1
}
```

所在代码片段：

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

补全逻辑：

- 本轮扫描实际前进了多少字符，由 `old_pos` 到 `pos` 统一结算。
- 如果读到换行 `\n`，进入下一行，所以 `line += 1`，并把 `col` 重置成 `1`。
- 如果不是换行，只是当前列向右移动一格，所以 `col += 1`。

语法点：

- `while old_pos < pos` 表示把本轮消费掉的每个字符都检查一遍。
- `b'\n'` 是换行字节。

易错点：

- 换行后列号应重置为 `1`，不是 `0`。
- 不能只在某些分支手动更新行列，否则注释、多字符运算符、转义串都容易错位。
- 这里更新的是“扫描后的位置”，而 token 起点要单独用 `tok_line`、`tok_col` 记录。

