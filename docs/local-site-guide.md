# 本地启动 PawBench 网站

`site/` 目录是 PawBench 官方网站（[PawBench](https://agentscope-ai.github.io/PawBench/)）的完整 Astro 源码，包含 Leaderboard、Slice 切片分析、Tasks 任务库等所有页面。

## 数据流向

```
data/pawbench-v1.0/tasks/*.md    ──┐
                                   ├── build_tasks.py ──→ site/src/data/tasks.json + stats.json
result/<run>/<model>/<harness>/  ──┤
  (T*/output/metrics.json           ├── aggregate_results.py ──→ submissions/<run>__<model>__<harness>.json
   或 <harness>/<ts>.json)          │
                                   └── build_leaderboard.py ──→ site/src/data/leaderboard.json
```

**注意**：`aggregate_results.py` 硬编码读 `result/` 目录，但 `run_bench.py` 默认输出到 `results/`（多一个 s）。需要创建目录链接解决。

## 前提条件

### 1. Node.js（site/ 目录）

`site/` 是 Astro + React 项目。如果删除了 `site/node_modules`，需重新安装：

```powershell
cd site
npm install
```

### 2. Python + pyyaml

数据构建脚本是 Python 编写的，需要安装 PyYAML：

```powershell
pip install pyyaml
```

### 3. result/ 目录

创建目录链接，让脚本能找到你的原始结果：

```powershell
New-Item -ItemType Junction -Path "D:\workplace\github\PawBench\result" -Target "D:\workplace\github\PawBench\results"
```

如果之后重新跑 `run_bench.py` 产生了新结果在 `results/`，软链接会自动可见，无需重复操作。

## 启动步骤

```powershell
# 1. 构建数据（生成 site/src/data/*.json）
cd site
npm run build:data

# 2. 启动开发服务器
npm run dev
```

访问 `http://localhost:4321` 即可。

## 页面说明

| 路由 | 功能 |
|------|------|
| `/` | 首页 Leaderboard，Model × Harness 评分矩阵 |
| `/slice` | 按能力维度/数据集/复杂度/模态等切片分析 |
| `/tasks` | 全部 150 个任务列表及筛选 |

## 常见问题

### WSL 不能复用 Windows 的 node_modules

Windows 和 WSL（Linux）的 `node_modules` 不兼容：
- 原生 C++ 模块编译为不同平台的 `.node` 二进制文件
- 路径分隔符不同（`\` vs `/`）
- `.bin/` 可执行文件缺少 Linux 执行权限

需要在 WSL 中重新 `npm install`。

### build:data 报错找不到 result/

确认 `result/` 目录存在且指向正确：

```powershell
ls D:\workplace\github\PawBench\result
```

应该能看到时间戳子目录（如 `20260709_141906/`）。

### 局域网其他机器无法访问开发服务器

`astro dev` 默认只监听 `localhost`（`::1`），局域网内其他机器无法访问。需添加 `--host` 参数：

```powershell
# 启动开发服务器并监听所有网络接口
npm run dev -- --host
```

之后其他机器通过你的局域网 IP 访问，如 `http://192.168.x.x:4321`。

### 页面加载后数据为空

检查控制台是否有 404，确认 `npm run build:data` 成功执行，并且 `site/src/data/` 下生成了 `tasks.json`、`stats.json`、`leaderboard.json` 三个文件。
