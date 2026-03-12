# AI 模拟面试系统

一个面向演示和业务验证的 AI 模拟面试系统，基于 FastAPI + Vue3 + Naive UI + RBAC 构建，提供“运营后台 + 候选人端”双入口。

一期定位为演示型 MVP：
- 业务数据真实可维护：候选人、岗位、JD、面试场次、面试报告、AI 运行状态都支持后台管理。
- AI 链路真实可调用：题目计划、下一题追问、面试报告已接入真实大模型接口。
- 语音与行为分析偏轻量：浏览器侧语音转文本 + 规则指标包装，保证体验完整、演示可信。
- 候选人端强调产品感：简历中心、岗位推荐、面试房间、报告查看已形成闭环。

## 当前能力

### 运营后台
- 账号与权限：系统账号、权限角色、导航菜单、接口台账、组织部门、操作日志
- 面试运营：候选人管理、岗位管理、JD 管理、面试场次管理、报告归档
- AI 运维：AI 配置状态、最近一次生成日志、连通性检查

### 候选人端
- 首页总览
- 简历中心
- 岗位推荐与岗位详情
- 面试房间（摄像头本地预览、语音识别、下一题）
- 报告历史与报告详情

### AI 闭环
1. 候选人完善简历
2. 系统根据岗位标签和 JD 生成推荐结果
3. 开始模拟面试，生成题目计划
4. 分段提交语音转写文本
5. 根据上下文生成下一题或追问
6. 结束面试后生成结构化报告并归档

## 技术栈

### 后端
- FastAPI
- Tortoise ORM
- Pydantic v2
- MySQL 8
- JWT 鉴权

### 前端
- Vue 3
- Vite
- Naive UI
- Pinia
- Vue Router

## 目录结构

```text
AI-Mock-Interview
├── app/                     # 后端应用
│   ├── api/v1/             # 接口路由
│   ├── controllers/        # 数据控制层
│   ├── models/             # 数据模型
│   ├── schemas/            # 请求/响应结构
│   ├── services/           # 业务编排与 AI 适配
│   └── settings/           # 配置读取
├── migrations/             # 数据库迁移
├── scripts/                # 联调和辅助脚本
├── web/                    # 前端应用
│   ├── src/views/ai-portal/        # 候选人端页面
│   ├── src/views/interview-admin/  # 面试运营后台页面
│   └── src/views/system/           # 系统设置页面
├── .env.example            # 后端环境变量模板
└── run.py                  # 后端启动入口
```

## 环境变量

### 后端 `.env`
先复制模板：

```bash
cp .env.example .env
```

需要至少补齐这些配置：
- `SECRET_KEY`
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `AI_API_KEY`
- `AI_BASE_URL`
- `AI_MODEL_NAME`
- `AI_REQUEST_TIMEOUT`

注意：
- `.env`、`.env.local` 已被 `.gitignore` 忽略，不要提交真实密钥。
- 如果 API Key 曾在聊天、截图或公开记录中暴露，建议立即轮换。

### 前端 `web/.env`
前端标题和本地端口在 `web/.env`：

```bash
VITE_TITLE='AI 模拟面试系统'
VITE_PORT=3100
```

## 本地启动

### 1. 后端启动
要求：
- Python 3.11+
- MySQL 8

推荐方式：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

启动后访问：
- API 文档：[http://127.0.0.1:9999/docs](http://127.0.0.1:9999/docs)
- 后端基地址：`http://127.0.0.1:9999/api/v1`

### 2. 前端启动

```bash
cd web
pnpm install
pnpm dev
```

默认访问：
- 前端开发地址：[http://127.0.0.1:3100](http://127.0.0.1:3100)

## 默认开发账号

系统首次初始化时会自动创建超级管理员：

- 账号：`admin`
- 邮箱：`admin@admin.com`
- 密码：`123456`

仅建议用于本地开发和演示环境，进入系统后请及时修改密码。

## 真实 AI 联调脚本

仓库内置了一条从“开始面试 -> 提交转写 -> 下一题 -> 生成报告 -> 查看 AI 日志”的联调脚本：

```bash
python scripts/mock_interview_e2e.py
```

脚本会：
- 从 `.env` 读取地址和登录信息
- 登录后台账号
- 检查/补齐候选人档案
- 选择推荐岗位，必要时自动创建演示岗位和 JD
- 跑通完整模拟面试链路
- 输出报告摘要和最近一次 AI 生成日志

可选环境变量：
- `MOCK_E2E_BASE_URL`
- `MOCK_E2E_USERNAME`
- `MOCK_E2E_PASSWORD`
- `MOCK_E2E_ROUNDS`
- `MOCK_E2E_POSITION_ID`
- `MOCK_E2E_AUTO_CREATE`

## 页面入口说明

### 后台入口
- 工作台：`/workbench`
- 系统设置：`/system/*`
- 面试运营：`/interview-admin/*`

### 候选人端入口
- 候选人首页：`/ai-interview/dashboard`
- 简历中心：`/ai-interview/resume`
- 岗位推荐：`/ai-interview/positions`
- 报告中心：`/ai-interview/reports`

## 一期范围说明

已实现：
- RBAC 登录与权限菜单
- 候选人、岗位、JD、场次、报告的真实 CRUD
- 候选人端练习闭环
- AI 题目生成、下一题生成、报告生成
- AI 运行状态页与日志记录

暂不包含：
- 自训练模型
- 摄像头视频上传与分析
- 音视频对象存储
- 简历文件解析
- 真流式语音对话基础设施
- 多租户企业端

## 开发说明

### 常用检查

后端语法检查：

```bash
python -B -m py_compile app/settings/config.py app/services/interview_ai.py app/services/mock_interview.py
```

前端代码检查：

```bash
pnpm -C web exec eslint src/views/login/index.vue src/views/workbench/index.vue
```

前端构建：

```bash
pnpm -C web build
```