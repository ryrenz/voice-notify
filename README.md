# voice-notify

让 Claude Code 用 AI 角色语音播报任务完成和权限请求。

任务完成时，用 LLM 把最后一轮对话总结成一句话，再用 Fish Audio TTS 以你选择的角色声音播报出来。需要权限确认时，播放角色专属的提示音。

## 功能

- **任务完成播报** — 实时 LLM 总结 + TTS 生成（API 模式），或播放预生成的缓存音频（Cache 模式）
- **权限请求提示** — 自动缓存的角色语音提醒，不重复调用 API
- **13 个内置角色** — 派蒙、迪卢克、钟离、神子、曹操、蜡笔小新等，每个角色有独特的语气和台词

## 快速开始

```bash
# 1. 克隆
git clone https://github.com/ryrenz/voice-notify.git
cd voice-notify

# 2. 安装
chmod +x install.sh && ./install.sh

# 3. 编辑 API Key
nano ~/.claude/voice-notify/.env
# 填入 FISH_API_KEY 和 DEEPSEEK_API_KEY

# 4. 添加 Hook（按照 install.sh 输出的提示操作）
claude /hooks
# Stop hook: python3 ~/.claude/voice-notify/voice_notify.py
# Notification hook: python3 ~/.claude/voice-notify/voice_permission.py
```

完成！Claude Code 每次完成任务或请求权限时，你就能听到角色语音了。

## 配置

### API Key

编辑 `~/.claude/voice-notify/.env`：

```bash
# 必需：Fish Audio TTS
FISH_API_KEY=your_key_here

# API 模式必需：DeepSeek（用于总结对话）
DEEPSEEK_API_KEY=your_key_here

# 可选：使用其他 OpenAI 兼容 API 替代 DeepSeek
# LLM_API_URL=https://api.openai.com/v1/chat/completions
# LLM_API_KEY=your_key
# LLM_MODEL=gpt-4o-mini
```

### 切换角色

编辑 `~/.claude/voice-notify/voices.json`，修改 `"current"` 字段：

```json
{
  "current": "曹操",
  "voices": { ... }
}
```

### 切换模式

```bash
python3 ~/.claude/voice-notify/voice_mode.py cache  # 缓存模式（离线、低延迟）
python3 ~/.claude/voice-notify/voice_mode.py api    # API 模式（实时总结、更自然）
python3 ~/.claude/voice-notify/voice_mode.py        # 查看当前模式
```

### 生成缓存

Cache 模式需要预生成音频。每个角色约需 15 秒：

```bash
python3 ~/.claude/voice-notify/generate_cache.py                     # 全部角色
python3 ~/.claude/voice-notify/generate_cache.py --character 派蒙     # 单个角色
python3 ~/.claude/voice-notify/generate_cache.py --dry-run           # 只看计划
python3 ~/.claude/voice-notify/generate_cache.py --force             # 强制重新生成
```

## 添加自定义角色

1. 去 [Fish Audio](https://fish.audio) 找到你喜欢的声音模型，复制 model_id

2. 在 `voices.json` 添加：
```json
{
  "current": "你的角色名",
  "voices": {
    "你的角色名": {
      "name": "你的角色名",
      "model_id": "从 Fish Audio 复制的 model_id"
    }
  }
}
```

3. 在 `characters.json` 添加角色台词（可选，Cache 模式需要）：
```json
{
  "你的角色名": {
    "permission_prompt": "权限请求时说的话",
    "completion_lines": [
      "任务完成时说的话1",
      "任务完成时说的话2"
    ]
  }
}
```

4. 如果要用 Cache 模式，生成缓存：
```bash
python3 ~/.claude/voice-notify/generate_cache.py --character 你的角色名
```

## 工作原理

```
Claude Code 任务完成（Stop hook）
  │
  ├─ Cache 模式 → 随机选一条预生成音频 → 播放
  │
  └─ API 模式 → 读取对话记录 → LLM 总结成一句话 → Fish Audio TTS → 播放

Claude Code 请求权限（Notification hook）
  │
  └─ 检查缓存 → 没有则生成并缓存 → 播放角色专属提示音
```

## 系统要求

- Python 3.9+
- macOS（afplay）或 Linux（paplay / aplay / mpv）
- curl
- 无需 pip install

## 卸载

```bash
chmod +x uninstall.sh && ./uninstall.sh
# 然后在 Claude Code 中移除 hooks
```

## FAQ

**Q: 两个 API Key 都是必需的吗？**

Cache 模式只需要 FISH_API_KEY（生成缓存时用一次）。API 模式两个都需要。

**Q: 能用 OpenAI / 其他 LLM 替代 DeepSeek 吗？**

可以。在 .env 中设置 `LLM_API_URL`、`LLM_API_KEY`、`LLM_MODEL`，支持任何 OpenAI 兼容接口。

**Q: 怎么临时静音？**

```bash
touch ~/.claude/voice-notify/.voice_mute   # 静音
rm ~/.claude/voice-notify/.voice_mute      # 取消静音
```

**Q: 支持 Windows 吗？**

v1 只支持 macOS 和 Linux。

## License

MIT
