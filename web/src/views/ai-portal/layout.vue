<template>
  <div class="portal-shell">
    <header class="portal-header">
      <div class="portal-header__inner">
        <div class="portal-brand" @click="go('/ai-interview/dashboard')">
          <div class="portal-brand__badge">面</div>
          <div>
            <p class="portal-brand__title">模拟面试练习</p>
            <p class="portal-brand__meta">按真实求职节奏准备材料、练习问答、回看报告</p>
          </div>
        </div>

        <nav class="portal-nav">
          <button
            v-for="item in navItems"
            :key="item.path"
            class="portal-nav__item"
            :class="{ 'is-active': isActive(item.path) }"
            @click="go(item.path)"
          >
            {{ item.label }}
          </button>
        </nav>

        <div class="portal-actions">
          <n-button tertiary type="primary" @click="go('/workbench')">返回后台</n-button>
          <n-dropdown :options="userMenuOptions" @select="handleUserAction">
            <div class="portal-user">
              <n-avatar round size="large" :src="userStore.avatar" />
              <div>
                <p class="portal-user__name">{{ userStore.name || '候选人' }}</p>
                <p class="portal-user__meta">{{ userStore.email || '正在练习中' }}</p>
              </div>
            </div>
          </n-dropdown>
        </div>
      </div>
    </header>

    <main class="portal-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useUserStore } from '@/store'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const navItems = [
  { label: '总览', path: '/ai-interview/dashboard' },
  { label: '简历中心', path: '/ai-interview/resume' },
  { label: '岗位推荐', path: '/ai-interview/positions' },
  { label: '报告中心', path: '/ai-interview/reports' },
]

const userMenuOptions = [
  { label: '总览', key: '/ai-interview/dashboard' },
  { label: '简历中心', key: '/ai-interview/resume' },
  { label: '报告中心', key: '/ai-interview/reports' },
  { type: 'divider', key: 'divider' },
  { label: '退出登录', key: 'logout' },
]

function go(path) {
  if (path !== route.path) {
    router.push(path)
  }
}

function isActive(path) {
  return route.path.startsWith(path)
}

async function handleUserAction(key) {
  if (key === 'logout') {
    await userStore.logout()
    return
  }
  go(key)
}
</script>

<style>
.portal-shell {
  --portal-bg: #f6f1ea;
  --portal-panel: #ffffff;
  --portal-panel-soft: #fcf8f3;
  --portal-line: #eadfd4;
  --portal-line-strong: #dccbbb;
  --portal-text: #3f342c;
  --portal-subtle: #7a6b60;
  --portal-accent: #b46d4e;
  --portal-accent-soft: #f0e2d7;
  display: flex;
  flex-direction: column;
  height: 100dvh;
  min-height: 100dvh;
  overflow: hidden;
  color: var(--portal-text);
  font-family: 'Avenir Next', 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
  background: radial-gradient(circle at top left, rgba(241, 229, 217, 0.85), transparent 30%),
    linear-gradient(180deg, #faf7f2 0%, #f6f1ea 100%);
}

.portal-header {
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 20;
  padding: 20px 28px 0;
  background: linear-gradient(
    180deg,
    rgba(250, 247, 242, 0.96),
    rgba(250, 247, 242, 0.82),
    rgba(250, 247, 242, 0)
  );
  backdrop-filter: blur(10px);
}

.portal-header__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 14px 18px;
  border: 1px solid rgba(220, 203, 187, 0.85);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 10px 32px rgba(93, 67, 47, 0.08);
}

.portal-brand {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 260px;
  cursor: pointer;
}

.portal-brand__badge {
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;
  border: 1px solid var(--portal-line-strong);
  border-radius: 16px;
  background: var(--portal-accent-soft);
  color: var(--portal-accent);
  font-size: 20px;
  font-weight: 700;
}

.portal-brand__title,
.portal-brand__meta,
.portal-user__name,
.portal-user__meta {
  margin: 0;
}

.portal-brand__title {
  font-size: 20px;
  font-weight: 600;
}

.portal-brand__meta {
  margin-top: 4px;
  color: var(--portal-subtle);
  font-size: 12px;
}

.portal-nav {
  display: flex;
  gap: 8px;
  padding: 6px;
  border: 1px solid var(--portal-line);
  border-radius: 999px;
  background: var(--portal-panel-soft);
}

.portal-nav__item {
  border: 0;
  padding: 10px 16px;
  border-radius: 999px;
  background: transparent;
  color: var(--portal-subtle);
  font-size: 14px;
  cursor: pointer;
  transition: 0.2s ease;
}

.portal-nav__item.is-active,
.portal-nav__item:hover {
  background: #fff;
  color: var(--portal-text);
  box-shadow: 0 4px 16px rgba(126, 93, 66, 0.09);
}

.portal-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.portal-user {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 10px 6px 6px;
  border: 1px solid var(--portal-line);
  border-radius: 999px;
  background: var(--portal-panel-soft);
  cursor: pointer;
}

.portal-user__name {
  font-size: 14px;
  font-weight: 600;
}

.portal-user__meta {
  font-size: 12px;
  color: var(--portal-subtle);
}

.portal-main {
  position: relative;
  flex: 1;
  min-height: 0;
  height: 0;
  padding: 18px 28px 40px;
  overflow-x: hidden;
  overflow-y: auto;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
}

.portal-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.portal-hero {
  display: grid;
  gap: 20px;
  padding: 28px;
  border: 1px solid var(--portal-line);
  border-radius: 28px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(252, 248, 243, 0.96));
  box-shadow: 0 18px 40px rgba(93, 67, 47, 0.06);
}

.portal-card,
.portal-panel {
  border: 1px solid var(--portal-line);
  border-radius: 24px;
  background: var(--portal-panel);
  box-shadow: 0 10px 28px rgba(93, 67, 47, 0.05);
}

.portal-card {
  padding: 24px;
}

.portal-panel {
  padding: 20px;
  background: var(--portal-panel-soft);
}

.portal-grid {
  display: grid;
  gap: 18px;
}

.portal-grid.cols-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.portal-grid.cols-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.portal-grid.cols-4 {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.portal-kpi {
  padding: 20px;
  border: 1px solid var(--portal-line);
  border-radius: 22px;
  background: var(--portal-panel-soft);
}

.portal-kpi__label {
  margin: 0 0 8px;
  color: var(--portal-subtle);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.portal-kpi__value {
  margin: 0;
  font-size: 30px;
  font-weight: 700;
}

.portal-section-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  line-height: 1.35;
}

.portal-section-subtitle {
  margin: 8px 0 0;
  color: var(--portal-subtle);
  line-height: 1.75;
}

.portal-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid var(--portal-line);
  border-radius: 999px;
  background: var(--portal-accent-soft);
  color: var(--portal-accent);
  font-size: 12px;
}

.portal-muted {
  color: var(--portal-subtle);
}

.portal-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.portal-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.portal-score-ring {
  display: grid;
  width: 110px;
  height: 110px;
  place-items: center;
  border-radius: 50%;
  border: 1px solid var(--portal-line-strong);
  background: radial-gradient(circle at 30% 30%, #fff, #f4e8dd);
  box-shadow: inset 0 0 0 8px rgba(255, 255, 255, 0.55);
}

.portal-score-ring strong {
  font-size: 32px;
}

.portal-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(180, 109, 78, 0.2), transparent);
}

.portal-tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.portal-table-shell {
  padding: 18px;
  border: 1px solid var(--portal-line);
  border-radius: 24px;
  background: var(--portal-panel-soft);
}

@media (max-width: 1180px) {
  .portal-header {
    padding: 16px 16px 0;
  }

  .portal-header__inner {
    flex-wrap: wrap;
  }

  .portal-main {
    padding: 16px 16px 28px;
  }

  .portal-grid.cols-4,
  .portal-grid.cols-3,
  .portal-grid.cols-2 {
    grid-template-columns: 1fr;
  }

  .portal-nav {
    width: 100%;
    overflow-x: auto;
  }
}
</style>
