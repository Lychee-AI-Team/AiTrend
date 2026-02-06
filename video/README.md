# AiTrend 视频生成模块

将每日AI热点数据自动转化为视频内容。

## 功能流程

```
1. 热点精选 (selector.py)
   └─> 从24小时数据中精选5-10条热点

2. 脚本生成 (llm_processor.py) 
   └─> 使用 Gemini LLM 生成视频播报脚本

3. 语音合成 (tts_generator.py)
   └─> 使用 Minimax TTS 生成配音

4. 数据转换 (script_converter.py)
   └─> 转换为 Remotion 输入格式

5. 视频渲染 (Remotion)
   └─> 生成最终视频
```

## 目录结构

```
video/
├── src/                    # Remotion 源码
│   ├── compositions/       # 视频合成
│   ├── components/         # 视频组件
│   └── styles/            # 样式
├── scripts/               # Python 处理脚本
│   ├── selector.py        # 热点精选
│   ├── llm_processor.py   # LLM 脚本生成
│   ├── tts_generator.py   # TTS 语音合成
│   ├── script_converter.py # 数据转换
│   └── video_pipeline.py  # 主流程
├── config/                # 配置文件
├── assets/                # 静态资源
│   ├── audio/            # 生成的音频
│   ├── bgm/              # 背景音乐
│   └── fonts/            # 字体
└── data/                  # 数据目录
    ├── input/            # 输入数据
    └── output/           # 输出视频
```

## 环境变量

必需环境变量（与 AiTrend 共享）：
- `GEMINI_API_KEY` - Google Gemini API Key
- `GEMINI_MODEL` - Gemini 模型名称（默认: gemini-2.0-flash）

视频模块专用：
- `MINIMAX_API_KEY` - Minimax TTS API Key
- `MINIMAX_VOICE_ID` - 音色ID（默认: mastercui）

## 使用方法

### 完整流程

```bash
# 运行完整视频生成流程
cd AiTrend/video/scripts
python3 video_pipeline.py --date 2026-02-06
```

### 分步执行

```bash
# 1. 热点精选
python3 selector.py \
  --input ../data/input/daily_raw_2026-02-06.json \
  --output ../data/selected_2026-02-06.json

# 2. 生成脚本
python3 llm_processor.py \
  --input ../data/selected_2026-02-06.json \
  --output ../data/script_2026-02-06.json

# 3. 生成语音
python3 tts_generator.py \
  --script ../data/script_2026-02-06.json \
  --output ../assets/audio/2026-02-06

# 4. 数据转换
python3 script_converter.py \
  --script ../data/script_2026-02-06.json \
  --audio ../assets/audio/2026-02-06/metadata.json \
  --output ../data/remotion_input_2026-02-06.json
```

## 技术栈

- **内容生成**: Google Gemini (gemini-2.0-flash / gemini-3-flash-preview)
- **语音合成**: Minimax TTS (speech-2.8-hd)
- **视频渲染**: Remotion + React + TypeScript

## 注意事项

1. 视频生成后存储在 `data/output/`，不自动发布
2. 发布环节需要人工审核后手动上传
3. 自动发布功能暂不开发
