# OpenClaw 容器手动启动验证指南

适用场景:使用 `docker/Dockerfile.pawbench-openclaw` 构建出的 `openclaw-pawbench:latest` 镜像,手动启动一个容器并验证 OpenClaw 能否端到端工作 —— 无论是连阿里云 DashScope,还是连你**自建的 OpenAI 兼容模型服务**。

构建镜像(在仓库根目录执行):

```bash
docker build -f docker/Dockerfile.pawbench-openclaw -t openclaw-pawbench:latest .
```

---

## 0. 三个实测要点(踩坑记录,务必先看)

| # | 问题 | 正确做法 |
|---|------|----------|
| 1 | 2026.8.x 起 gateway 强制鉴权,客户端无凭据会在建 websocket 前被拒 | 启动 `gateway` 加 `--token`;**客户端命令(`agent`/`agents`/`browser`)在 8.1 没有 `--token` 参数**(传了会报 unknown option),统一用 `export OPENCLAW_GATEWAY_TOKEN=...`(2026.5.x 也认这个变量) |
| 2 | 日志里搜不到 `[gateway] ready`,因为 `[gateway]` 和 `ready` 之间夹着 **ANSI 颜色码** | 只搜 `" ready"`(含前导空格),不要搜完整串 `"[gateway] ready"` |
| 3 | 交互终端下 `python3 -c "多行脚本..."` 常因引号/换行转义问题直接失败 | 把配置脚本用 heredoc 写成 `.py` 文件再执行 |

> 镜像构建时的预热脚本同样受问题 2 影响,已在 `docker/Dockerfile.pawbench-openclaw` 中修复(改为 `grep -q " ready"`)。

---

## 1. 前置条件

- 镜像已构建:`openclaw-pawbench:latest`(内含 openclaw 2026.8.1、Chromium、Xvfb/XFCE4、中文字体、Python 依赖等)。
- 一个可用的模型服务端点,二选一:
  - **自建 OpenAI 兼容端点**(vLLM / Ollama / one-api 等均可),即 `/v1/chat/completions` 接口;
  - **阿里云 DashScope**,且持有真实 API key。
- 网络可达:容器需能访问模型端点(默认 bridge 网络即可)。

> ⚠️ 镜像内置的凭据是构建期占位符 `sk-build-placeholder`。若不替换成真实 key,所有请求都会返回 **401 Incorrect API key**。

---

## 2. 启动容器

### 场景 A:自建 OpenAI 兼容端点

```bash
docker run -it --rm \
  -e MODE=custom \
  -e CUSTOM_BASE_URL="http://你的服务地址:8000/v1" \
  -e CUSTOM_API_KEY="sk-你的key" \
  -e CUSTOM_MODEL="你的模型名" \
  -e OPENCLAW_GATEWAY_TOKEN='MyToken@1234' \
  openclaw-pawbench:latest bash
```

### 场景 B:阿里云 DashScope(qwen)

```bash
docker run -it --rm \
  -e MODE=dashscope \
  -e DASHSCOPE_API_KEY="sk-你的key" \
  -e MODEL_NAME="qwen3.6-plus" \
  -e OPENCLAW_GATEWAY_TOKEN='MyToken@1234' \
  openclaw-pawbench:latest bash
```

说明:

- `OPENCLAW_GATEWAY_TOKEN` 是你自定义的 gateway 鉴权 token,可任意设置;**含特殊字符时务必用单引号包裹**。下文所有命令都通过它引用。
- DashScope 国际站需额外加 `-e DASHSCOPE_INTL=1`,配置脚本会切换到 `dashscope-intl.aliyuncs.com` 端点。

---

## 3. 第一步:清理镜像内置的占位凭据

镜像烘焙的 auth profile 优先级高于配置文件里的 `apiKey`,不清掉会导致 401。进入容器后立即执行:

```bash
rm -f /root/.openclaw/auth-profiles.json \
      /root/.openclaw/auth/profiles.json \
      /root/.openclaw/auth/*.json 2>/dev/null || true
```

---

## 4. 第二步:写入模型配置(脚本文件方式)

按踩坑记录第 3 条,把配置脚本写成文件再执行。在容器内直接粘贴以下整段(heredoc 原样写入 `/tmp/patch_openclaw.py`):

```bash
cat > /tmp/patch_openclaw.py <<'PY'
# -*- coding: utf-8 -*-
"""按环境变量重写 /root/.openclaw/openclaw.json 的 provider 配置。

两种模式(由环境变量 MODE 决定):
  MODE=dashscope  阿里云 DashScope
  MODE=custom     自建 OpenAI 兼容端点
"""
import json
import os
from urllib.parse import urlparse

P = "/root/.openclaw/openclaw.json"
mode = os.environ.get("MODE", "custom")

d = {}
if os.path.exists(P):
    with open(P, encoding="utf-8") as f:
        d = json.load(f)

providers = d.setdefault("models", {}).setdefault("providers", {})
plugins = d.setdefault("plugins", {}).setdefault("entries", {})

# 与评测代码 model_config.py 相同的扩展思考关键词
REASONING_KW = ("o1", "o3", "thinking", "reasoning", "r1", "r2", "a3b")

if mode == "dashscope":
    key = os.environ.get("DASHSCOPE_API_KEY", "")
    base = os.environ.get(
        "DASHSCOPE_BASE_URL",
        "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        if os.environ.get("DASHSCOPE_INTL")
        else "https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    model = os.environ.get("MODEL_NAME", "qwen3.6-plus")
    prov_id = "qwen"
    # 与评测代码一致:清掉残留 provider、禁用内置 qwen/openai 插件,
    # 避免插件用烘焙的占位 key 覆盖正确配置
    for stale in ("openai", "dashscope"):
        providers.pop(stale, None)
        plugins[stale] = {"enabled": False}
    plugins["qwen"] = {"enabled": False}
    meta = {"reasoning": True, "contextWindow": 200000, "maxTokens": 32768}
else:
    base = os.environ["CUSTOM_BASE_URL"]
    key = os.environ.get("CUSTOM_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
    model = os.environ["CUSTOM_MODEL"]
    host = urlparse(base).hostname or "custom"
    prov_id = "custom-" + host.replace(".", "-")
    providers.pop("qwen", None)
    plugins["qwen"] = {"enabled": False}
    meta = {
        "reasoning": any(k in model.lower() for k in REASONING_KW),
        "contextWindow": 128000,
        "maxTokens": 16384,
    }

prov = providers.setdefault(prov_id, {"models": []})
prov.update({
    "api": "openai-completions",
    "baseUrl": base,
    "apiKey": key,
    "auth": "api-key",
})

models = prov["models"]
entry = next((m for m in models if m.get("id") == model), None)
new = {
    "id": model,
    "name": model,
    "input": ["text", "image"],
    "compat": {"supportsTools": True},
}
new.update(meta)
if entry:
    entry.update(new)
else:
    models.append(new)

d.setdefault("agents", {}).setdefault("defaults", {})["model"] = {
    "primary": "%s/%s" % (prov_id, model)
}
d.setdefault("gateway", {})["mode"] = "local"
d.setdefault("tools", {})["allow"] = ["*"]

with open(P, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print("配置完成: provider=%s model=%s baseUrl=%s" % (prov_id, model, base))
PY

python3 /tmp/patch_openclaw.py
```

看到输出 `配置完成: provider=... model=...` 即写入成功。

参数说明:

| 环境变量 | 用途 |
|----------|------|
| `CUSTOM_BASE_URL` | 自建端点地址,必须是 OpenAI 兼容格式(以 `/v1` 结尾) |
| `CUSTOM_API_KEY` | 自建端点的 key(不设时回退到 `OPENAI_API_KEY`) |
| `CUSTOM_MODEL` | 模型名,避免使用别名(如 `qwen`、`gpt-4o`、`claude-*`),防止被评测侧的别名表展开 |
| `contextWindow` / `maxTokens` | 脚本里的默认值可按模型实际规格手改,影响长任务的上下文压缩与截断 |

---

## 5. 第三步:启动 gateway 并等待就绪

```bash
export OPENCLAW_DISABLE_BONJOUR=1

nohup openclaw gateway --token "$OPENCLAW_GATEWAY_TOKEN" >/tmp/gw.log 2>&1 &
echo $! > /tmp/gw.pid

# 注意:只搜 " ready",不能搜 "[gateway] ready"(中间有 ANSI 颜色码)
ok=""
for i in $(seq 1 60); do
  if grep -q " ready" /tmp/gw.log 2>/dev/null; then ok=1; break; fi
  sleep 1
done
if [ -n "$ok" ]; then
  echo "gateway 已就绪"
else
  echo "gateway 60 秒内未就绪,查看日志排查:"
  tail -30 /tmp/gw.log
fi
```

停止 gateway 的方式:

```bash
kill "$(cat /tmp/gw.pid 2>/dev/null)" 2>/dev/null; pkill -9 -f 'openclaw gateway' 2>/dev/null; true
```

---

## 6. 第四步:端到端验证

**前提:`export OPENCLAW_GATEWAY_TOKEN=...`(与启动 gateway 的 `--token` 一致)。注意 8.1 的 `agent`/`agents`/`browser` 命令不接受 `--token` 参数,凭据一律走环境变量:**

```bash
# 1. 确认 gateway 里注册的 agent 列表
openclaw agents list

# 2. 确认默认模型配置
openclaw config get agents.defaults.model.primary

# 3. 发送一条冒烟消息(等价于评测 runner 的调用方式)
cd /app/working/workspaces/default
timeout 300 openclaw agent \
  --message '请只回复两个字母:OK' 2>&1 | tail -20
```

模型回复 `OK` 即端到端打通。

浏览器能力(可选)验证:

```bash
openclaw browser doctor
```

---

## 7. 补充:用自建模型跑正式评测

手动验证通过后,正式评测不需要上面的手动步骤 —— runner 会自动完成同样的注入流程:

```bash
export CUSTOM_BASE_URL="http://你的服务地址:8000/v1"
export CUSTOM_API_KEY="sk-你的key"

python run_bench.py --agent openclaw --model "custom/你的模型名"
```

也可用 `--base-url` / `--api-key` 逐次覆盖。runner 对 `custom/` 前缀模型的处理逻辑:

1. `custom/<model>` 被翻译为 `custom-<主机名>/<model>` 作为 openclaw 的 provider id;
2. 自动写入 openclaw.json(apiKey、baseUrl、`auth: api-key`);
3. 每个任务运行前清除镜像烘焙的占位 auth profile 并注入真实 key。

详见 `pawbench/agents/impl/openclaw_agent.py` 的 `setup()` 与 `_configure_openclaw_json()`。

---

## 8. 常见问题排查

| 现象 | 原因与处理 |
|------|-----------|
| **401 Incorrect API key** | 占位凭据没清干净,或顺序不对。必须**先删 auth-profiles 再启 gateway**(见第 3、5 步);内置 qwen 插件会在 gateway 启动时加载烘焙 profile 并覆盖正确配置 |
| **CLI 连接被拒 / 无响应** | 未 `export OPENCLAW_GATEWAY_TOKEN`,或其值与启动 gateway 的 `--token` 不一致。注意 8.1 的 `agent`/`agents`/`browser` 命令**不接受 `--token` 参数** |
| **gateway 启动后 20 秒左右崩溃** | bonjour 插件(mDNS 组播)在 Docker 默认 bridge 网络下不被支持。启动前务必 `export OPENCLAW_DISABLE_BONJOUR=1` |
| **首次 CLI 调用卡住 1~2 分钟** | openclaw 在安装插件运行时依赖,属正常现象(镜像已预热,通常数秒内完成),不要提前 kill |
| **grep 搜不到 ready 日志** | ANSI 颜色码插在 `[gateway]` 与 `ready` 之间,改搜 `" ready"` |
| **`python3 -c "多行脚本"` 报语法错** | 交互终端的引号/换行转义问题,写成 `.py` 文件再执行(本指南全程采用该方式) |
| **模型不支持工具调用报错** | 端点必须是 OpenAI 兼容的 `chat/completions`;Anthropic 原生格式端点请改用 `anthropic/<模型名>` 并配 `--base-url` |
