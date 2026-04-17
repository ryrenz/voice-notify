# voice-notify

让 Claude Code 用语音播报任务完成和权限请求。

## 快速开始（30 秒零配置）

```bash
git clone https://github.com/ryrenz/voice-notify.git
cd voice-notify
./install.sh
```

然后把下面这段加到 `~/.claude/settings.json` 的 hooks：

```json
{
  "hooks": {
    "Stop": [
      {"hooks": [{"type": "command", "command": "python3 ~/.claude/voice-notify/voice_notify.py"}]}
    ],
    "Notification": [
      {"hooks": [{"type": "command", "command": "python3 ~/.claude/voice-notify/voice_permission.py"}]}
    ]
  }
}
```

完成。每次 Claude Code 完成任务会说"任务完成"，请求权限会说"需要你的确认"，用系统自带的声音。

## 进阶：换成二次元角色语音（Fish Audio）

系统声音太死板？可以升级到 Fish Audio TTS，用派蒙、迪卢克、曹操等角色的声音播报。

### 步骤

**1. 注册 Fish Audio 账号**

去 https://fish.audio 注册账号，在设置页找到 API Key，复制保存。

**2. 找到你喜欢的角色模型 ID**

- 访问 https://fish.audio/zh-CN/text-to-speech/?modality=tts
- 搜索角色名（比如"派蒙"、"迪卢克"、"曹操"）
- 点进模型页面，URL 里的最后一段就是 `model_id`
  - 例如：`https://fish.audio/zh-CN/m/eacc56f8ab48443fa84421c547d3b60e/` → model_id = `eacc56f8ab48443fa84421c547d3b60e`
- 复制 model_id

**3. 配置 API Key**

编辑 `~/.claude/voice-notify/.env`：
```bash
FISH_API_KEY=your_fish_audio_key_here
```

**4. 切换到 Fish Audio 模式**

```bash
python3 ~/.claude/voice-notify/voice_mode.py fish
```

**5.（可选）添加自定义角色**

编辑 `~/.claude/voice-notify/voices.json`：
```json
{
  "backend": "fish",
  "fish": {
    "current": "你的角色名",
    "voices": {
      "你的角色名": {
        "name": "你的角色名",
        "model_id": "从 Fish Audio 复制的 ID"
      }
    }
  }
}
```

### Fish Audio 两种子模式

```bash
python3 ~/.claude/voice-notify/voice_mode.py fish api    # 实时模式：LLM 总结 + TTS（需要额外的 DEEPSEEK_API_KEY）
python3 ~/.claude/voice-notify/voice_mode.py fish cache  # 缓存模式：预生成 10 条台词随机播放
```

Cache 模式需要先生成缓存：
```bash
python3 ~/.claude/voice-notify/generate_cache.py --character 派蒙
```

## 配置

### 本地模式的声音和文本

编辑 `voices.json` 的 `local` 段：
```json
{
  "local": {
    "voice": "Tingting",
    "completion_text": "任务完成",
    "permission_text": "需要你的确认"
  }
}
```

macOS 常用中文声音：`Tingting`（中文女声）、`Sinji`（粤语）、`Meijia`（台湾腔）。
查看全部可用声音：`say -v '?'`。

### 查看当前模式

```bash
python3 ~/.claude/voice-notify/voice_mode.py
```

### 临时静音
```bash
touch ~/.claude/voice-notify/.voice_mute     # 静音
rm ~/.claude/voice-notify/.voice_mute        # 取消静音
```

## 系统要求

- Python 3.9+
- macOS 或 Linux
  - macOS: 自带 `say`（零依赖）
  - Linux: 需要 `speech-dispatcher` 或 `espeak`
- curl（仅 Fish Audio 模式需要）

## FAQ

**Q: 真的完全不用 API key 就能用吗？**

是的。默认 local 模式用系统 TTS，macOS 自带，Linux 装个 espeak 就行。

**Q: Fish Audio 免费吗？**

Fish Audio 新账号送一些额度。重度使用按字符数收费。

**Q: 能用 OpenAI 替代 DeepSeek 做总结吗？**

可以。在 `.env` 中设置 `LLM_API_URL`、`LLM_API_KEY`、`LLM_MODEL`，支持任何 OpenAI 兼容接口。

**Q: 本地模式也能用 LLM 总结吗？**

可以。如果 `.env` 里配置了 `DEEPSEEK_API_KEY` 或 `LLM_API_KEY`，local 模式会把静态文本替换成对 Claude 最后一轮对话的一句话总结，然后用系统 TTS 读出来。

**Q: 为什么 Claude Code hook 要手动加？**

自动修改 settings.json 风险太大（可能破坏已有配置）。手动粘贴几行 JSON 更安全。

## 卸载

```bash
chmod +x uninstall.sh && ./uninstall.sh
# 然后在 Claude Code 中移除 hooks
```

## License

MIT
