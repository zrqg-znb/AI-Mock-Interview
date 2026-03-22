# 面试过程表情总结方案 (基于 DeepFace)

## 1. 方案摘要
采用“前端定时轻量截帧 + 后端 DeepFace 异步分析 + 报告期大模型总结”的方案。前端在面试过程中（例如每10秒）截取摄像头画面的缩略图发送至后端。后端使用轻量级的开源表情识别库（DeepFace）快速分析基础情绪并记录。面试结束时，后端统计情绪分布（如：平静 70%、微笑 20%、紧张 10%），交由现有的大模型在生成最终复盘报告时，顺带输出一段关于候选人表情管理和从容度的自然语言总结。

## 2. 现状分析
- **前端**：已实现摄像头视频流预览 (`videoRef`)，但未提取帧数据发送。
- **后端**：目前仅处理语音文本（ASR 和 TTS），缺乏图像或视频处理逻辑。
- **数据库**：`InterviewSession` 模型记录了面试的对话轮次和实时指标，但没有保存表情数据的字段。
- **生成报告**：目前的 AI Prompt 主要基于对话文本生成复盘，没有视觉维度的输入。

## 3. 详细实施步骤

### 3.1 后端依赖与模型库引入
- 在 `requirements.txt` 中添加 `deepface` 和 `opencv-python-headless` 等必要依赖。
- 考虑到 DeepFace 初次运行会下载权重，可以在项目启动时或第一次请求时自动拉取极轻量的表情权重（如基于 OpenCV/Keras 的轻量情绪模型）。

### 3.2 数据库模型更新
- 在 `app/models/interview.py` 的 `InterviewSession` 模型中，新增一个 JSON 字段 `expression_records`，用于以列表形式记录整个面试过程中的时间戳和情绪结果（例如 `[{"time": "10:01", "emotion": "happy"}]`）。
- 运行 `aerich migrate` 和 `aerich upgrade` 生成并应用数据库迁移脚本。

### 3.3 后端分析服务与接口
- **新建服务**：创建 `app/services/expression_service.py`，封装对 `DeepFace.analyze` 的调用。配置参数 `enforce_detection=False` 以避免未检测到人脸时报错，并指定 `actions=['emotion']` 以加快分析速度。
- **新增接口**：在 `app/api/v1/mock_interview/mock_interview.py` 中新增 `POST /submit_expression_frame` 接口。
  - **入参**：`session_id` 和 `image_base64`。
  - **逻辑**：解码 base64 图片，调用 `expression_service` 获取主导情绪（dominant emotion），将其追加保存到对应 `session` 的 `expression_records` 中。

### 3.4 前端定时截帧改造
- 在 `web/src/views/ai-portal/room/index.vue` 中：
  - 新增一个隐藏的 `<canvas>` 用于截取视频帧。
  - 在开启摄像头（或开始答题）后，启动一个定时器（`setInterval`，建议每 10 秒一次）。
  - 定时器触发时，将 `videoRef` 当前画面绘制到 canvas 上，并压缩尺寸（如 320x240）以降低网络带宽和后端处理压力。
  - 将压缩后的图片转为 `image/jpeg` 的 base64 字符串，调用后端的 `/submit_expression_frame` 接口。

### 3.5 报告生成逻辑集成
- 在 `app/services/mock_interview.py` 的 `build_report` 方法中：
  - 读取 `session` 的 `expression_records`，统计各项情绪出现的频次占比（例如：neutral 75%, happy 15%, fear 10%）。
  - 将此统计数据作为附加信息（`expression_stats`）注入到大模型的 `user_prompt` 中。
  - 调整系统 Prompt，要求大模型在生成复盘报告时（如在 `overview` 或 `process_review.dialogue_observations` 中），结合情绪分布数据，对候选人的表情管理、自信度和沟通状态进行简短的评价。

## 4. 假设与决策
- **速度与成本优先**：不采用每次调用 GPT-4o Vision API 的方式，而是采用后端的轻量级 DeepFace 库，零 API 成本且响应极快。
- **容错处理**：截帧模糊或未完全露脸时，不强求精准识别，容许存在部分 "neutral" 或无法识别的帧，因为最终要的是一个整体比例的宏观总结。
- **异步与非阻塞**：前端发送截帧请求是完全异步的，不需要等待后端识别结果返回即可继续，不影响面试者的作答流畅度。

## 5. 验证步骤
1. 安装依赖并执行数据库迁移。
2. 启动前后端服务，进入模拟面试房间。
3. 检查浏览器的 Network 面板，确认每隔设定时间有向 `/submit_expression_frame` 发送图片的请求。
4. 查看后端日志，确认 DeepFace 正确输出了情绪结果（如 `happy`, `neutral`）。
5. 结束面试，检查生成的评估报告，确认文本中包含对候选人表情和状态的总结。