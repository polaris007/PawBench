# PAWBENCH_KEEP_CONTAINER 使用说明

## 用途

Task 执行完毕后默认会销毁 Docker 容器。设置 `PAWBENCH_KEEP_CONTAINER=1` 可跳过删除步骤，保留容器以便 `docker exec` 进入内部查看文件、排查问题。

## 用法

```bash
# 环境变量方式（推荐）
PAWBENCH_KEEP_CONTAINER=1 python run_bench.py --tasks T053 --model dashscope/qwen3.6-plus --agents openclaw

# 或者 export 后再运行
export PAWBENCH_KEEP_CONTAINER=1
python run_bench.py --tasks T053 --model dashscope/qwen3.6-plus --agents openclaw
```

## 进入容器

Task 执行完毕后，日志中会打印容器的完整名称和进入命令，例如：

```
[backend] PAWBENCH_KEEP_CONTAINER is set — keeping container 'pawbench-openclaw-T053_email_triage-abc12345' running for inspection.
           docker exec -it pawbench-openclaw-T053_email_triage-abc12345 bash
```

直接复制命令执行即可：

```bash
docker exec -it pawbench-openclaw-T053_email_triage-abc12345 bash
```

## 常用排查操作

进入容器后，可以检查以下内容：

| 用途 | 命令 |
|------|------|
| 查看 Agent 工作区 | `ls -la /app/working/workspaces/default/` |
| 查看 OpenClaw 运行时目录 | `ls -la /tmp/openclaw/` |
| 查看 OpenClaw 配置 | `cat /root/.openclaw/openclaw.json` |
| 查看 Agent Session 记录 | `ls -la /root/.openclaw/agents/<agent_id>/sessions/` |
| 查看 Gateway 日志 | `cat /tmp/openclaw_gateway.log` |

## 注意事项

1. **手动清理**：保留的容器不会自动删除，需要手动清理：
   ```bash
   docker rm -f pawbench-openclaw-<task_id>-<suffix>
   ```

2. **并发模式**（`--concurrency > 1`）下每个 task 会创建独立的容器，均会保留。

3. **仅限 Docker 环境**：`PAWBENCH_ENV=local` 模式下（无 Docker）该设置不生效。

4. **与 `--save-workspace` 的关系**：两者互补——
   - `--save-workspace` 把工作区文件保存到宿主机目录
   - `PAWBENCH_KEEP_CONTAINER` 保留完整的容器环境，可以检查运行时的进程状态、文件系统等
