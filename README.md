# YIAN 编译器课程实验

本仓库包含课程提供的 YIAN 编译工具，以及使用 YIAN 完成的四个编译器实验：词法分析、语法分析、语义分析和 LLVM IR 生成。

## 项目做了什么

项目分为两层：

1. **主机编译器与框架**：`compiler/`、`scripts/`、`lian/`、`lib/` 是课程提供的基础设施。Python 编译入口将 YIAN `.an` 文件转换为 LLVM 后端产物，并调用 Clang 生成本机可执行文件。
2. **学生实验实现**：`labs/lab1` 到 `labs/lab4` 中的 `.an` 文件使用 YIAN 编写，逐步实现教学语言的编译流程。

实验流程：

```text
教学语言源程序
  → Lexer：Token 与位置
  → Parser：抽象语法树 AST
  → Sema：作用域、符号和类型检查，生成 HIR
  → Translator：LLVM IR
  → Clang：本机可执行程序
```

实验处理的教学语言是简化语法，不能将 `docs/grammar/` 中主机 YIAN 的全部语言特性视为实验编译器已经支持的功能。

本 README 的复现整理和 `scripts/check_public_tests.py` 为本次维护新增，不计入上述课程基础设施或四次原始实验提交。

## 我的实验工作

根据 `CatherineG77` 的四个实验提交整理；课程提供的主机编译器、LIAN 和标准库保留原作者署名。

| 阶段 | 个人完成的主要内容 | 对应提交 |
| --- | --- | --- |
| Lab1 词法分析 | 补全词法分类、Token 收束、行列号更新，整理实验报告 | `c301ec3` |
| Lab2 语法分析 | 补全 enum、变量声明、for、Pratt 二元表达式、前缀/主表达式/后缀解析 | `5640df4` |
| Lab3 语义分析 | 补全 while/for 降级、变量查找、字段自动解引用与加法类型检查 | `b0ff043` |
| Lab4 LLVM 生成 | 补全 if 分支、动态分配、赋值、数组/指针索引、加法和不可达基本块删除 | `c08bc4e` |

Lab4 的不可达基本块删除是从入口出发遍历控制流图，并不表示实现了完整的 SSA 优化器。

## 目录结构

```text
compiler/                 课程提供的 Python 主机编译器
  frontend/               Tree-sitter 前端及必需解析库
  analysis/               主机编译器分析过程
  backend/                LLVM 后端
scripts/
  yian_compiler.py         编译命令入口
  compiler_api.py          编译与链接管线
  check_public_tests.py    独立验证所有公开实验样例
labs/
  lab1/lex/               词法实验实现
  lab2/parse/             语法实验实现
  lab3/sema/              语义实验实现
  lab4/translate/         LLVM 翻译实验实现
  lab*/test_cases/        公开输入
  lab1~3/test_results/    参考结果
  lab*/docs/              实验要求与评分标准
lian/                    必需的 LIAN 框架
lib/                     YIAN 标准库
docs/                    主机语言及编译工具文档
ide-support/             VS Code 语法高亮插件
licenses/                原项目许可证
report1.md               Lab1 实验报告
explanation.md           Lab1 分析笔记
requirements.txt         固定版本 Python 依赖
```

`tests/yian_workspace/` 是编译时生成的工作区。普通编译会刷新它，不能将它作为永久保存自写文件的目录。

## 复现环境

已经验证的环境：**Ubuntu 24.04 x86_64、Python 3.12.3、Clang 18.1.3**。

首次安装基础工具：

```bash
sudo apt update
sudo apt install -y git python3 python3-venv clang build-essential
```

克隆本仓库后，进入包含 `requirements.txt` 的仓库根目录，再执行：

```bash
/usr/bin/python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

即使终端显示 Conda `(base)`，也使用上面的明确路径。此后的 Python 命令统一使用 `.venv/bin/python`。

仓库自带的下列动态库是运行依赖，必须随源码保留：

- `compiler/frontend/yian_lang_x86_64.so`
- `compiler/frontend/yian_lang_arm64.so`
- `lian/lib/langs_linux.so`

普通复现不需要重建解析器，也不需要另外安装 LLVM 开发包、Bison 或 Flex。当前验证范围为 Linux x86_64，不承诺 ARM 或原生 Windows 能直接运行。

## 一条命令验证全部公开实验

在仓库根目录执行：

```bash
.venv/bin/python scripts/check_public_tests.py
```

脚本会在临时项目副本中创建全新的输出目录，并顺序进行以下验证：

| 检查 | 成功标准 |
| --- | --- |
| Hello World | 编译成功，运行输出 `Hello, World!` |
| Lab1 | 01–06 六份 Token 输出与参考答案逐行一致，允许末尾空行差异 |
| Lab2 | 01–06 六份 AST 输出与参考答案逐行一致，允许末尾空行差异 |
| Lab3 | 六个公开样例均无运行时错误；另报告参考输出匹配数量，课程要求不以完全一致为必要条件 |
| Lab4 | 本次生成完整的 01–10 LLVM IR，Clang 编译成功，十个程序均返回 0 |

成功时最后显示：

```text
ALL PUBLIC TESTS PASSED
Logs and generated files: /tmp/yian-public-tests-...
```

只有全部检查通过才返回退出码 0。日志、AST、HIR、LLVM IR 和可执行文件保留在提示的临时目录，便于检查；验证脚本不会覆盖原项目的实验输出。

最近一次验证结果：2026-11-05，Hello World 正常；Lab1、Lab2、Lab3 各 6/6 输出与公开参考结果一致；Lab4 10/10 程序返回 0。该结果只覆盖仓库提供的公开样例，不代表隐藏测试结果。

Lab1 原入口包含 07–10，但仓库没有提供这些隐藏输入。公开复现入口已将这四项注释，避免读缺失文件导致崩溃；词法分析算法没有因此改动。获得相应输入后可重新启用。

## 手动分阶段运行

以下命令会更新原项目的生成工作区与实验输出。在仓库根目录顺序执行，不要同时并行启动多个编译任务。

```bash
mkdir -p build \
  labs/lab1/output labs/lab2/output labs/lab3/output \
  labs/lab4/ll labs/lab4/ast labs/lab4/hir

# 验证主机编译器
.venv/bin/python scripts/yian_compiler.py labs/lab1/test_cases/hello.an --output build/hello
./build/hello

# Lab1：词法分析
.venv/bin/python scripts/yian_compiler.py labs/lab1/lex --output build/lab1
./build/lab1

# Lab2：语法分析
.venv/bin/python scripts/yian_compiler.py labs/lab2/parse --output build/lab2
./build/lab2

# Lab3：语义分析
.venv/bin/python scripts/yian_compiler.py labs/lab3/sema --output build/lab3
./build/lab3

# Lab4：LLVM IR 生成及执行检查
.venv/bin/python scripts/yian_compiler.py labs/lab4/translate --output build/lab4
./build/lab4
.venv/bin/python labs/lab4/test_all.py
```

Lab4 原检查脚本成功时输出 `All executables returned 0.`。需要完整验证时使用统一检查脚本，它还会确认十个输入对应的 IR 和程序齐全，避免旧产物或缺少用例导致误判。

只导出主机编译器的 LLVM IR 示例：

```bash
.venv/bin/python scripts/yian_compiler.py labs/lab1/test_cases/hello.an --target ll --output build/hello.ll
```

## 提交说明与署名

- `.venv/`、缓存、`build/`、实验生成输出和 `tests/yian_workspace/` 无需提交。
- 保留 `compiler/`、`scripts/`、`labs/`、`lian/`、`lib/`、文档、依赖清单及上述三个 `.so`。
- `.gitignore` 含 `labs/`：现有已跟踪的实验文件仍正常提交；新实验文件或全新 Git 仓库需要精确使用 `git add -f`，避免漏传源码和公开测试。
- 保留根 `LICENSE.txt`、`licenses/`，以及 LIAN 自己的 `LICENSE.txt`、`CREDITS.txt`。本仓库包含课程框架与第三方代码，个人成果主要是上表列出的实验补全内容。
