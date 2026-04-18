# voice-notify

让 Claude Code 用语音播报任务完成和权限请求。

分两档：**零依赖 5 秒版**（大多数人用这个）、**完整版**（想要角色语音或 LLM 总结用这个）。

---

## 🥇 零依赖 5 秒版

不用 clone、不用装任何东西，直接把下面这段粘到 `~/.claude/settings.json`：

**macOS**：
```json
{
  "hooks": {
    "Stop": [{"hooks": [{"type": "command", "command": "say '任务完成'"}]}],
    "Notification": [{"hooks": [{"type": "command", "command": "say '需要确认'"}]}]
  }
}
```

**Linux**（装了 `speech-dispatcher` 或 `espeak` 的）：
```json
{
  "hooks": {
    "Stop": [{"hooks": [{"type": "command", "command": "spd-say '任务完成'"}]}],
    "Notification": [{"hooks": [{"type": "command", "command": "spd-say '需要确认'"}]}]
  }
}
```

完成。Claude Code 每次完成任务和请求权限时会用系统自带 TTS 播报。

**想要英文？** 把 `'任务完成'` 改成 `'Task complete'`，`'需要确认'` 改成 `'Needs approval'`。

**想换声音？** macOS 可以加 `-v`：`say -v Tingting '任务完成'`（中文女声）。查看所有声音：`say -v '?'`。

**想要更多？** 需要角色语音、LLM 总结刚做了什么这类功能，往下看「完整版」。

---

## 🥈 完整版（角色语音 / LLM 总结）

想要派蒙、御姐、霸总这种二次元角色声音？想让 Claude Code 用角色声音**总结刚刚做了什么**？走这条路。

### 前置：装 Python 3.9+

```bash
# macOS
brew install python@3.12
# 或去 https://www.python.org/downloads/ 下载安装包

# Ubuntu / Debian（通常默认就有）
sudo apt install python3

# Fedora / RHEL
sudo dnf install python3

# Arch
sudo pacman -S python
```

验证：`python3 --version` 显示 3.9+ 即可。

### 安装

```bash
git clone https://github.com/ryrenz/voice-notify.git
cd voice-notify
./install.sh
```

然后把 install.sh 输出的 JSON 粘到 `~/.claude/settings.json`。

默认装完也是本地 TTS 模式（等价于零依赖版），但多了几个可配置选项（自定义话术、切换声音等）。

### 升级到 Fish Audio 角色语音

系统 TTS 声音太呆板？升级到 Fish Audio，**内置 3 种声线**（绿茶音 / 御姐音 / 正太音），想要更多自己加就行。

#### 1. 注册 Fish Audio 账号

前往 https://fish.audio 注册账号。

**获取 API Key**：登录后 → 右上角头像 → API Keys → Create → 复制保存。

#### 2. 找到你想要的声线 Model ID

前往 https://fish.audio/discovery/ 搜索符合你想要声线的模型：

- 按声线类型搜索，例如"萝莉"、"御姐"、"正太"、"霸总"等
- 点进模型详情页
- URL 里最后一段就是 `model_id`
  - 例：`https://fish.audio/m/eacc56f8ab48443fa84421c547d3b60e/` → `eacc56f8ab48443fa84421c547d3b60e`
- 点试听，满意就复制 `model_id`

#### 3. 配置

**填 API Key** —— 编辑 `~/.claude/voice-notify/.env`：

```
FISH_API_KEY=你从 Fish Audio 复制的 key
```

**添加声线** —— 编辑 `~/.claude/voice-notify/voices.json`（key 对应 `characters.json` 里的声线名，需保持一致）：

```json
{
  "backend": "fish",
  "fish": {
    "current": "绿茶音",
    "voices": {
      "绿茶音": {
        "name": "绿茶音",
        "model_id": "从 Fish Audio 复制的 model_id"
      }
    }
  }
}
```

**切换到 Fish 模式**：

```bash
python3 ~/.claude/voice-notify/voice_mode.py fish
```

搞定！下次 Claude Code 完成任务就是绿茶音的声音了。

#### 4. Fish Audio 两种子模式

```bash
python3 ~/.claude/voice-notify/voice_mode.py fish api    # 实时模式：LLM 总结刚做了什么 → Fish TTS 念出来
python3 ~/.claude/voice-notify/voice_mode.py fish cache  # 缓存模式：预生成 10 条固定台词，随机播放
```

- **api 模式**额外需要 DeepSeek 或 OpenAI API Key（在 `.env` 里填 `DEEPSEEK_API_KEY`，或 `LLM_API_URL` + `LLM_API_KEY` + `LLM_MODEL`）。
- **cache 模式**台词来自 `characters.json`，先生成缓存：

  ```bash
  python3 ~/.claude/voice-notify/generate_cache.py --character 绿茶音
  ```

  `characters.json` 内置 3 种声线模板（绿茶音 / 御姐音 / 正太音），每种配了 10 条代表性台词。它只是一份台词库，**不包含任何 model_id**，你需要自己去 Fish Audio 找符合该声线的模型，把 `model_id` 填到 `voices.json`。想要更多声线，直接照着格式往 `characters.json` 加即可。

---

## 配置细节

### 本地模式：自定义声音和话术

编辑 `~/.claude/voice-notify/voices.json` 的 `local` 段：

```json
{
  "local": {
    "voice": "Tingting",
    "completion_text": "任务完成",
    "permission_text": "需要你的确认"
  }
}
```

**macOS 中文声音**：`Tingting`（大陆中文女声）、`Sinji`（粤语）、`Meijia`（台湾中文）。
查看系统可用所有声音：`say -v '?'`。

**Linux**：`voice` 字段设为 `zh`（espeak 中文），或 `auto` 用系统默认。

### 临时静音

```bash
touch ~/.claude/voice-notify/.voice_mute   # 静音
rm ~/.claude/voice-notify/.voice_mute      # 取消
```

### 切换模式

```bash
python3 ~/.claude/voice-notify/voice_mode.py local       # 切回本地
python3 ~/.claude/voice-notify/voice_mode.py fish        # Fish Audio
python3 ~/.claude/voice-notify/voice_mode.py             # 查看当前
```

> 如果切到 `fish` 时 `voices.json` 里还没配角色或没填 `FISH_API_KEY`，voice-notify 会自动回落到本地 TTS，保证你始终能听到提示音。

---

## 系统要求

| 路径 | 依赖 |
|------|------|
| 零依赖版 | macOS（自带 `say`）或 Linux（`spd-say` / `espeak`） |
| 完整版 | 上面 + Python 3.9+ |
| Fish Audio 角色语音 | 完整版 + `curl` + Fish Audio API key |

Linux 安装 TTS：

```bash
sudo apt install speech-dispatcher   # 推荐，支持中文
# 或
sudo apt install espeak
```

完整版零 Python 第三方依赖，不需要 `pip install`。

---

## 工作原理

```
Claude Code 事件触发
  │
  ├─ Stop（任务结束）──→ voice_notify.py
  │                        ├─ backend=local  → say/espeak 说固定话术（或 LLM 总结）
  │                        └─ backend=fish   → LLM 总结 + Fish TTS / 或播放缓存
  │
  └─ Notification（权限请求）──→ voice_permission.py
                                 ├─ backend=local → say/espeak
                                 └─ backend=fish  → 播放缓存的角色提示音
```

---

## 卸载

```bash
./uninstall.sh
```

然后在 `~/.claude/settings.json` 里删除对应的 hooks。

---

## FAQ

**Q: 默认模式真的不用任何 API Key？**
对。macOS 的 `say` 和 Linux 的 `espeak` 都是系统自带 / 免费的。

**Q: Fish Audio 收费吗？**
注册送免费额度，重度使用按字符数付费，详见 fish.audio 定价。

**Q: `characters.json` 里 3 种声线的 model_id 呢？**
仓库里不分发 model_id —— 请自己去 https://fish.audio/discovery/ 按声线类型挑一个顺耳的模型，复制 ID 粘到 `voices.json`。

**Q: 只有 3 个声线模板？**

对。默认只保留绿茶音、御姐音、正太音三个台词模板（Cache 模式用）。想要更多，自己往 `~/.claude/voice-notify/characters.json` 加就行，格式参考现有的三个。

**Q: 能用 OpenAI 代替 DeepSeek 吗？**
可以。在 `.env` 里设置 `LLM_API_URL` / `LLM_API_KEY` / `LLM_MODEL`，支持任何 OpenAI 兼容 API。

**Q: 为什么 Hook 要手动加到 `settings.json`？**
自动改 JSON 容易破坏你已有的配置。手动粘贴更安全。

**Q: Windows 支持吗？**
v1 只支持 macOS 和 Linux。欢迎 PR。

---

## License

MIT
