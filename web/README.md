# 前端说明

这是 AI 模拟面试系统的前端项目，基于 Vue 3 + Vite + Naive UI。

## 主要页面
- `/login`：运营后台登录页
- `/workbench`：工作台
- `/system/*`：系统设置
- `/interview-admin/*`：面试运营后台
- `/ai-interview/*`：候选人端

## 本地启动

```bash
cd web
pnpm install
pnpm dev
```

## 前端环境变量

`web/.env`：

```bash
VITE_TITLE='AI 模拟面试系统'
VITE_PORT=3100
```

`web/.env.development` 和 `web/.env.production` 控制代理、公网路径和 API 前缀。

## 构建

```bash
pnpm build
```

## 代码检查

```bash
pnpm exec eslint src/views/login/index.vue src/views/workbench/index.vue
```
