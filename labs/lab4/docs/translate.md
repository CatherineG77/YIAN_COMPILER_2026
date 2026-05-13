# 代码生成实验说明（Translate）

## 1. 实验目标

本实验要求你基于给定模板实现代码生成器（Translator），将语义分析阶段输出的 HIR 翻译为 LLVM IR。通过本实验，你将掌握：

- 如何把带有语义信息的 AST 转换为目标中间表示。
- 如何把高层语言结构映射为 LLVM 的基本块、指令和类型。
- 如何处理变量、控制流、指针和内存分配等底层语义。

## 2. 实验环境

同 Lab 1。

## 3. 代码介绍

### 3.1 目录与文件

- 实验代码：`labs/lab4/translate/*.an`
- 翻译器核心：`labs/lab4/translate/translator.an`
- LLVM 指令封装：`labs/lab4/translate/llvm.an`
- 测试输入：`labs/lab4/test_cases/01.an ~ 10.an`

### 3.2 主流程

核心流程如下：

1. `main.an::main()` 读取测试输入文件。
2. `parser.an::Parser` 将源代码解析为 AST。
3. `sema.an::Sema` 将 AST 解析为带语义信息的 HIR。
4. `translator.an::Translator` 将 HIR 翻译为 LLVM IR。
5. 最终写入输出文件（`labs/lab4/ll/xx.ll`）。

### 3.3 数据结构

在 `llvm.an` 中

- **LLType**：LLVM 类型的字符串包装，例如 `i32`、`i8*`、`{ i8*, i64 }`。
- **LLValue**：LLVM 值，包含名字和类型，例如 `%_0 : i32`。
- **LLBasicBlock**：基本块，保存一串 LLVM 指令和后继块。
- **LLFunction**：LLVM 函数，包含入口块、普通基本块、返回类型和参数列表。
- **LLModule**：LLVM 模块，包含类型声明、外部函数声明、全局字符串和函数定义。
- **LLBuilder**：LLVM 指令构造器，负责向当前基本块中写入指令。

关于 LLVM 的入门知识参见[LLVM文档](llvm.md)

### 3.4 算法思路

代码生成的核心是 `Translator::translate()` 方法，其主要流程如下：

1. 先执行 `lower_types()`，把 HIR 的类型全部映射成 LLVM 类型。
2. 再遍历所有 HIR 函数，逐个调用 `translate_func()`。
3. 在翻译函数时：
	 1. 为局部变量分配栈空间。
	 2. 将参数保存到对应局部变量地址。
	 3. 递归翻译函数体中的每条语句和表达式。
4. 最后由 `LLModule.export()` 将 LLVM IR 导出为文本。
   1. 导出前会进行一些处理, 包括死代码消除等.

### 3.5 死代码消除

在 `LLModule.export()` 中会调用 `dead_code_elimination` 方法进行死代码消除。死代码的定义是：**在程序执行过程中永远不会被执行到的代码**。或者说：**CFG 中, 不包含函数入口结点的连通分量中的代码**。

### 3.6 需要补全的 TODO

在 `translator.an` 中

- `translate_if`：将 `if` 翻译成 then/else/merge 基本块
- `translate_assign`：完成赋值表达式的求值与写回
- `translate_index_lvalue`：完成数组/指针索引的左值寻址
- `translate_add`：完成普通加法与指针算术分流
- `translate_dyn`：完成动态分配、大小计算和类型转换

在 `llvm.an` 中

- `dead_code_elimination`：完成死代码消除算法

### 3.7 测试

你可以通过下面的方式测试你的代码生成器：

1. 修改 `labs/lab4/translate/main.an` 中所包含的测试名(你也可以构造自己的测试)
2. 命令行执行：`scripts/yian_compiler.py labs/lab4/translate`
3. 执行生成的可执行文件, 将会在 `labs/lab4/ll/` 目录下生成对应的 LLVM IR 文件
   1. 同时也会在 `labs/lab4/ast/` 和 `labs/lab4/hir/` 目录下生成对应的 AST 和 HIR 输出文件, 供你调试使用
4. 命令行执行：`python labs/lab4/test_all.py`，该脚本会自动编译并运行生成的 LLVM IR 文件，检查运行结果是否正确。
   1. 运行后会在 `labs/lab4/bin/` 下生成可执行文件。
   2. `main` 函数返回值为 0 表示测试通过, 返回值为 1 表示测试失败。
5. 因为一些神秘小 BUG, 你需要自己创建 `labs/lab4/ll/`, `labs/lab4/ast/` 和 `labs/lab4/hir/` 目录, 否则输出文件无法生成。

---

## 4. 实验要求

### 4.1 功能要求

至少满足以下能力：

- 正确把 HIR 类型翻译成 LLVM 类型
- 正确处理局部变量分配与参数入栈
- 正确处理 `if`、`loop`、`break`、`continue` 等控制流
- 正确处理赋值、索引、字段访问、函数调用等表达式
- 正确处理指针运算和动态内存分配
- 正确生成可被 `clang` 编译的 LLVM IR

### 4.2 输出要求

- 输出文件为 LLVM IR 文本
- 输出目录为 `labs/lab4/ll/`
- 生成的 IR 应能被 `clang` 进一步编译

### 4.3 提交要求

提交内容：

- 你的 `labs/lab4/translate/translator.an`
- 你的 `labs/lab4/translate/llvm.an`
- 实验报告（可选）
	- 可以包含你对 HIR 到 LLVM IR 翻译过程的理解
	- 可以包含你对控制流、指针和内存模型的总结
	- 可以包含你在实现过程中遇到的挑战和解决方案
	- 你的分数主要由测试结果决定，实验报告不作为加分项

---

## 5. 测试与评测规则

你将拿到 `01-10` 号测试，这些测试同时作为评分依据。

- 输入：`labs/lab4/test_cases/01.an` ~ `10.an`
- LLVM 输出：`labs/lab4/ll/01.ll` ~ `10.ll`
- 可执行文件：`labs/lab4/bin/01` ~ `10`
- 参考答案：无答案, 可执行文件返回值为 0 表示测试通过, 返回值为 1 表示测试失败。

---

## 6. 评分标准（100 分）

- 公共测试 01-10：每题 10 分，共 100 分
- 评分依据：**生成的可执行文件返回值为 0**

---

## 7. 学术诚信

- 禁止抄袭。
- 可以使用 AI 辅助工具，但你最好知道自己生成的 LLVM IR 在做什么。
