<template>
  <AppPage :show-footer="false" class="workbench-page">
    <n-spin :show="loading">
      <div class="workbench-shell">
        <section class="wb-hero">
          <div class="wb-hero__main">
            <div class="wb-hero__welcome">
              <n-avatar round :size="64" :src="userStore.avatar" />
              <div>
                <p class="wb-eyebrow">运营工作台</p>
                <h1 class="wb-title">欢迎回来，{{ userStore.name || '管理员' }}</h1>
                <p class="wb-desc">
                  把候选人、岗位、JD、面试场次、报告归档和 AI
                  运行状态集中看清楚，方便演示和日常巡检。
                </p>
              </div>
            </div>

            <div class="wb-hero__actions">
              <n-button type="primary" @click="go('/interview-admin/interview')"
                >查看面试场次</n-button
              >
              <n-button secondary @click="go('/interview-admin/ai-runtime')">查看 AI 状态</n-button>
              <n-button tertiary @click="go('/ai-interview/dashboard')">打开候选人端</n-button>
            </div>
          </div>

          <div class="wb-hero__aside">
            <div class="wb-aside-card">
              <p class="wb-aside-card__label">AI 服务</p>
              <div class="wb-aside-card__row">
                <strong>{{ overview.aiEnabled ? '已启用' : '待配置' }}</strong>
                <n-tag :bordered="false" :type="overview.aiEnabled ? 'success' : 'warning'">
                  {{ overview.aiProvider || '未识别' }}
                </n-tag>
              </div>
              <p class="wb-aside-card__meta">最近成功：{{ overview.lastSuccessAt }}</p>
            </div>

            <div class="wb-aside-card">
              <p class="wb-aside-card__label">基础就绪度</p>
              <div class="wb-readiness">
                <n-progress
                  type="circle"
                  :percentage="readinessPercent"
                  :stroke-width="10"
                  color="#b46d4e"
                >
                  <span class="wb-readiness__value">{{ readinessPercent }}%</span>
                </n-progress>
              </div>
              <p class="wb-aside-card__meta">
                候选人档案、在线岗位、启用 JD 和 AI 配置已纳入检查。
              </p>
            </div>
          </div>
        </section>

        <section class="wb-metrics">
          <article v-for="item in metricCards" :key="item.key" class="wb-metric-card">
            <p class="wb-metric-card__label">{{ item.label }}</p>
            <div class="wb-metric-card__row">
              <strong class="wb-metric-card__value">{{ item.value }}</strong>
              <span class="wb-metric-card__hint">{{ item.hint }}</span>
            </div>
          </article>
        </section>

        <section class="wb-grid wb-grid--two">
          <n-card title="快捷入口" :bordered="false" class="wb-panel">
            <div class="wb-quick-grid">
              <button
                v-for="item in quickActions"
                :key="item.title"
                type="button"
                class="wb-quick-card"
                @click="go(item.path)"
              >
                <div>
                  <p class="wb-quick-card__title">{{ item.title }}</p>
                  <p class="wb-quick-card__desc">{{ item.desc }}</p>
                </div>
                <span class="wb-quick-card__arrow">进入</span>
              </button>
            </div>
          </n-card>

          <n-card title="今日巡检" :bordered="false" class="wb-panel">
            <div class="wb-check-list">
              <div v-for="item in checklist" :key="item.label" class="wb-check-item">
                <div>
                  <p class="wb-check-item__title">{{ item.label }}</p>
                  <p class="wb-check-item__desc">{{ item.desc }}</p>
                </div>
                <n-tag :bordered="false" :type="item.ok ? 'success' : 'warning'">
                  {{ item.ok ? '正常' : '待处理' }}
                </n-tag>
              </div>
            </div>
          </n-card>
        </section>

        <section class="wb-grid wb-grid--two">
          <n-card title="最近面试场次" :bordered="false" class="wb-panel">
            <div v-if="recentInterviews.length" class="wb-list">
              <article v-for="item in recentInterviews" :key="item.id" class="wb-list-item">
                <div>
                  <div class="wb-list-item__title-row">
                    <strong>{{ item.position?.title || '未命名岗位' }}</strong>
                    <n-tag :bordered="false" :type="getStatusType(item.status)">
                      {{ interviewStatusText[item.status] || item.status || '未知状态' }}
                    </n-tag>
                  </div>
                  <p class="wb-list-item__meta">
                    候选人：{{
                      item.candidate?.headline || item.candidate?.user?.username || '未关联'
                    }}
                  </p>
                  <p class="wb-list-item__meta">场次编号：{{ item.session_no || '-' }}</p>
                </div>
                <span class="wb-list-item__time">{{
                  formatDate(item.updated_at || item.created_at)
                }}</span>
              </article>
            </div>
            <n-empty v-else description="最近还没有面试场次" />
          </n-card>

          <n-card title="最近报告归档" :bordered="false" class="wb-panel">
            <div v-if="recentReports.length" class="wb-list">
              <article v-for="item in recentReports" :key="item.id" class="wb-list-item">
                <div>
                  <div class="wb-list-item__title-row">
                    <strong>{{ item.position?.title || '未命名岗位' }}</strong>
                    <span class="wb-score">{{ item.total_score || 0 }} 分</span>
                  </div>
                  <p class="wb-list-item__meta">
                    候选人：{{
                      item.candidate?.headline || item.candidate?.user?.username || '未关联'
                    }}
                  </p>
                  <p class="wb-list-item__meta">
                    归档状态：{{
                      reportStatusText[item.archive_status] || item.archive_status || '-'
                    }}
                  </p>
                </div>
                <span class="wb-list-item__time">{{ formatDate(item.created_at) }}</span>
              </article>
            </div>
            <n-empty v-else description="最近还没有归档报告" />
          </n-card>
        </section>
      </div>
    </n-spin>
  </AppPage>
</template>

<script setup>
import api from '@/api'
import { useUserStore } from '@/store'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const overview = ref({
  candidateTotal: 0,
  onlinePositionTotal: 0,
  runningInterviewTotal: 0,
  reportTotal: 0,
  activeJDTotal: 0,
  aiEnabled: false,
  aiProvider: '-',
  lastSuccessAt: '暂无记录',
})
const recentInterviews = ref([])
const recentReports = ref([])

const interviewStatusText = {
  pending: '待开始',
  running: '进行中',
  completed: '已完成',
}

const reportStatusText = {
  archived: '已归档',
  draft: '草稿',
}

const quickActions = [
  {
    title: '候选人管理',
    desc: '查看候选人档案、简历和求职状态。',
    path: '/interview-admin/candidate',
  },
  {
    title: '岗位管理',
    desc: '维护推荐岗位、难度和展示信息。',
    path: '/interview-admin/position',
  },
  {
    title: 'JD 管理',
    desc: '统一维护岗位要求、评分维度和提示词。',
    path: '/interview-admin/jd',
  },
  {
    title: '报告档案',
    desc: '回看结构化报告和导出链接。',
    path: '/interview-admin/report',
  },
  {
    title: 'AI 运行状态',
    desc: '确认模型配置、最近日志和连通结果。',
    path: '/interview-admin/ai-runtime',
  },
  {
    title: '候选人端',
    desc: '进入推荐、面试房间和报告查看页面。',
    path: '/ai-interview/dashboard',
  },
]

const metricCards = computed(() => [
  {
    key: 'candidateTotal',
    label: '候选人档案',
    value: overview.value.candidateTotal,
    hint: '已建档',
  },
  {
    key: 'onlinePositionTotal',
    label: '在线岗位',
    value: overview.value.onlinePositionTotal,
    hint: '推荐中',
  },
  {
    key: 'runningInterviewTotal',
    label: '进行中场次',
    value: overview.value.runningInterviewTotal,
    hint: '实时状态',
  },
  {
    key: 'reportTotal',
    label: '报告归档',
    value: overview.value.reportTotal,
    hint: '累计生成',
  },
])

const readinessPercent = computed(() => {
  const checks = [
    overview.value.candidateTotal > 0,
    overview.value.onlinePositionTotal > 0,
    overview.value.activeJDTotal > 0,
    overview.value.aiEnabled,
  ]
  const passed = checks.filter(Boolean).length
  return Math.round((passed / checks.length) * 100)
})

const checklist = computed(() => [
  {
    label: '候选人档案准备',
    desc:
      overview.value.candidateTotal > 0
        ? '当前已有候选人档案，可直接进入推荐链路。'
        : '还没有候选人档案，建议先创建演示账号和简历。',
    ok: overview.value.candidateTotal > 0,
  },
  {
    label: '岗位与 JD 准备',
    desc:
      overview.value.onlinePositionTotal > 0 && overview.value.activeJDTotal > 0
        ? '岗位与启用 JD 已具备，支持开始练习。'
        : '岗位或 JD 仍不完整，可能影响推荐和出题质量。',
    ok: overview.value.onlinePositionTotal > 0 && overview.value.activeJDTotal > 0,
  },
  {
    label: 'AI 生成服务',
    desc: overview.value.aiEnabled
      ? `当前已接入 ${overview.value.aiProvider}，可生成题目和报告。`
      : '尚未检测到可用 AI 配置，建议先检查环境变量。',
    ok: overview.value.aiEnabled,
  },
])

onMounted(loadWorkbench)

async function loadWorkbench() {
  loading.value = true
  try {
    const [candidateRes, positionRes, runningRes, jdRes, reportRes, interviewRes, aiRes] =
      await Promise.allSettled([
        api.getCandidateList({ page: 1, page_size: 1 }),
        api.getPositionList({ page: 1, page_size: 1, status: 'online' }),
        api.getInterviewList({ page: 1, page_size: 1, status: 'running' }),
        api.getJDList({ page: 1, page_size: 1, is_active: true }),
        api.getReportList({ page: 1, page_size: 5 }),
        api.getInterviewList({ page: 1, page_size: 5 }),
        api.getAIRuntimeStatus({ limit: 5 }),
      ])

    overview.value = {
      candidateTotal: takeTotal(candidateRes),
      onlinePositionTotal: takeTotal(positionRes),
      runningInterviewTotal: takeTotal(runningRes),
      reportTotal: takeTotal(reportRes),
      activeJDTotal: takeTotal(jdRes),
      aiEnabled: aiRes.status === 'fulfilled' ? Boolean(aiRes.value.data?.enabled) : false,
      aiProvider: aiRes.status === 'fulfilled' ? aiRes.value.data?.provider || '-' : '-',
      lastSuccessAt:
        aiRes.status === 'fulfilled' ? aiRes.value.data?.last_success_at || '暂无记录' : '暂无记录',
    }

    recentReports.value = reportRes.status === 'fulfilled' ? reportRes.value.data || [] : []
    recentInterviews.value =
      interviewRes.status === 'fulfilled' ? interviewRes.value.data || [] : []
  } catch (error) {
    $message.error('工作台数据加载失败，请稍后重试。')
  } finally {
    loading.value = false
  }
}

function takeTotal(result) {
  return result.status === 'fulfilled' ? Number(result.value.total || 0) : 0
}

function go(path) {
  router.push(path)
}

function getStatusType(status) {
  if (status === 'completed') return 'success'
  if (status === 'running') return 'warning'
  if (status === 'pending') return 'default'
  return 'info'
}

function formatDate(value) {
  if (!value) return '-'
  return String(value).slice(0, 16).replace('T', ' ')
}
</script>

<style scoped>
.workbench-page {
  background: linear-gradient(180deg, #f7f4ef 0%, #f2ede6 100%);
}

.workbench-shell {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.wb-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(320px, 0.9fr);
  gap: 18px;
  padding: 22px;
  border: 1px solid #e7ddd3;
  border-radius: 24px;
  background: linear-gradient(180deg, #fffdfa 0%, #f8f3ed 100%);
  box-shadow: 0 12px 28px rgba(89, 69, 50, 0.06);
}

.wb-hero__main,
.wb-hero__aside {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.wb-hero__welcome {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.wb-eyebrow,
.wb-metric-card__label,
.wb-aside-card__label,
.wb-score {
  margin: 0;
  color: #8a7564;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.wb-title {
  margin: 6px 0 0;
  color: #312822;
  font-size: 30px;
  line-height: 1.3;
}

.wb-desc {
  margin: 10px 0 0;
  max-width: 720px;
  color: #74675b;
  line-height: 1.8;
}

.wb-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.wb-hero__actions :deep(.n-button) {
  border-radius: 14px;
}

.wb-hero__aside {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.wb-aside-card,
.wb-metric-card,
.wb-panel,
.wb-quick-card {
  border: 1px solid #eadfd4;
  border-radius: 20px;
  background: #fff;
}

.wb-aside-card {
  padding: 18px;
}

.wb-aside-card__row,
.wb-metric-card__row,
.wb-list-item__title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.wb-aside-card__row strong,
.wb-metric-card__value {
  color: #302822;
  font-size: 28px;
  line-height: 1.2;
}

.wb-aside-card__meta,
.wb-check-item__desc,
.wb-list-item__meta,
.wb-quick-card__desc,
.wb-list-item__time,
.wb-readiness__value,
.wb-metric-card__hint {
  color: #74675b;
}

.wb-aside-card__meta {
  margin: 12px 0 0;
  line-height: 1.7;
}

.wb-readiness {
  display: flex;
  justify-content: center;
  margin: 12px 0;
}

.wb-readiness__value {
  font-size: 16px;
  font-weight: 600;
}

.wb-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.wb-metric-card {
  padding: 18px 20px;
}

.wb-metric-card__row {
  margin-top: 10px;
  align-items: flex-end;
}

.wb-grid {
  display: grid;
  gap: 18px;
}

.wb-grid--two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.wb-panel {
  overflow: hidden;
  box-shadow: 0 8px 22px rgba(89, 69, 50, 0.04);
}

.wb-panel :deep(.n-card-header) {
  padding-bottom: 0;
}

.wb-panel :deep(.n-card__content) {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.wb-quick-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.wb-quick-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  width: 100%;
  padding: 18px;
  text-align: left;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.wb-quick-card:hover {
  border-color: #d8c5b4;
  box-shadow: 0 10px 24px rgba(89, 69, 50, 0.08);
  transform: translateY(-2px);
}

.wb-quick-card__title,
.wb-check-item__title,
.wb-list-item strong {
  margin: 0;
  color: #312822;
  font-size: 16px;
}

.wb-quick-card__desc,
.wb-check-item__desc,
.wb-list-item__meta {
  margin: 8px 0 0;
  line-height: 1.7;
}

.wb-quick-card__arrow {
  flex-shrink: 0;
  color: #b46d4e;
  font-size: 13px;
  font-weight: 600;
}

.wb-check-list,
.wb-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.wb-check-item,
.wb-list-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  border: 1px solid #efe4da;
  border-radius: 18px;
  background: #fcfaf7;
}

.wb-list-item__time {
  flex-shrink: 0;
  font-size: 12px;
  white-space: nowrap;
}

.wb-score {
  color: #b46d4e;
  font-weight: 700;
}

@media (max-width: 1180px) {
  .wb-hero,
  .wb-grid--two,
  .wb-metrics,
  .wb-hero__aside,
  .wb-quick-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .wb-hero,
  .wb-metric-card,
  .wb-check-item,
  .wb-list-item,
  .wb-quick-card {
    padding: 16px;
  }

  .wb-title {
    font-size: 24px;
  }

  .wb-list-item,
  .wb-check-item,
  .wb-quick-card,
  .wb-aside-card__row,
  .wb-metric-card__row,
  .wb-list-item__title-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .wb-list-item__time {
    white-space: normal;
  }
}
</style>
