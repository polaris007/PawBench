# 部署手册

## 工具简介

PawBench（🐾）是一个面向 Agent（智能体）AI 的 **模型 × Harness（运行框架）协同评测基准**。它通过 150 个真实任务、9 个模型、3 种 Harness，配合任务切片与诊断轨迹，帮助使用者区分一个 Agent 失败到底来自模型推理、工具缺失、技能发现薄弱、工作区感知不足、网页访问脆弱，还是完成判定过于宽松，而非只能得到一个笼统的最终通过率。

本手册用于指导如何在**离线内网环境**中部署并运行 PawBench，包括导入 Docker 镜像、准备独立的 Python 运行环境、安装依赖、配置评测参数，并启动对指定模型与任务集的自动化评测。整套流程不依赖外网访问，适合在隔离的安全环境中开展 Agent 能力评测。

## 第 1 步：在内网服务器搭建环境

将所有文件复制到某个目录，如 `/path/to/pawbench`。

### 1.1 导入 Docker 镜像

```bash
docker load -i pawbench-openclaw_4.14.tar
docker load -i pawbench-openclaw_5.28.tar
docker images | grep pawbench-openclaw   # 确认导入成功
```

### 1.2 解压 standalone Python

```bash
tar -xzf cpython-3.11.15+20260610-x86_64-unknown-linux-gnu-install_only.tar.gz -C /opt/python311
export PATH=/opt/python311/install/bin:$PATH
python3 --version
```

可将上述 `export` 写入 `~/.bashrc` 以便持久化。

### 1.3 创建 Python 虚拟环境

```bash
cd /path/to/PawBench
python3 -m venv venv
source venv/bin/activate
```

### 1.4 安装 PawBench 依赖（离线模式）

```bash
unzip wheelhouse311.zip
pip install --no-index --find-links=wheelhouse311 -r requirements.txt
```

> `--no-index` 禁止 pip 访问网络，`--find-links` 指向本地 wheel 目录。

## 第 2 步：配置PawBench环境

解压PawBenchSrc.tar.gz，并配置.env

```bash
tar -xzf PawBenchSrc.tar.gz
cp prod.env PawBenchSrc/.env
```

---

## 第 3 步：运行评测

### 测试环境

```bash
source venv/bin/activate
cd PawBenchSrc
python run_bench.py \
  --agents openclaw \
  --docker-image pawbench-openclaw:4.14 \
  --tasks T053 \
  --verbose \
  --save-workspace
```

### 运行所有任务

```bash
# 评测OpenClaw 4.14，并发10个容器，单个版本全部任务运行完成估计5小时左右
python run_bench.py \
  --agents openclaw \
  --docker-image pawbench-openclaw:4.14 \
  --concurrency 10 \
  --verbose \
  --save-workspace
# 评测OpenClaw 5.28
python run_bench.py \
  --agents openclaw \
  --docker-image pawbench-openclaw:5.28 \
  --concurrency 10 \
  --verbose \
  --save-workspace
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--agents openclaw` | 使用 OpenClaw harness |
| `--docker-image pawbench-openclaw:4.14` | 指定上一步构建的 Docker 镜像 |
| `--model deepseek-v4-flash-normal` | 指定模型名称，会覆盖 `.env` 中的 `OPENAI_MODEL` |
| `--concurrency 10` | 并发启动 10 个容器同时评测 |
| `--verbose` | 输出详细日志 |
| `--save-workspace` | 保存每个任务的 agent workspace，便于事后复盘 |


