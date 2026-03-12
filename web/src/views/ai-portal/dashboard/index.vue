<template>
  <section class="portal-page">
    <div class="portal-hero">
      <div class="portal-row" style="align-items: flex-start; flex-wrap: wrap">
        <div style="max-width: 720px">
          <p class="portal-chip">练习首页</p>
          <h1 class="portal-section-title" style="font-size: 40px; margin-top: 16px">
            把准备工作做扎实，再按真实面试的节奏练一遍。
          </h1>
          <p class="portal-section-subtitle" style="max-width: 680px">
            这里像一个求职准备台：先完善简历，再挑岗位，最后进入练习房间和回看报告。重点放在信息是否清楚、流程是否顺手。
          </p>
          <n-space style="margin-top: 18px">
            <n-button type="primary" size="large" @click="router.push('/ai-interview/positions')"
              >查看岗位推荐</n-button
            >
            <n-button tertiary size="large" @click="router.push('/ai-interview/resume')"
              >完善简历</n-button
            >
            <n-button quaternary size="large" @click="router.push('/ai-interview/reports')"
              >查看报告</n-button
            >
          </n-space>
        </div>

        <div class="portal-score-ring">
          <div style="text-align: center">
            <strong>{{ dashboard.readiness_score }}</strong>
            <p class="portal-muted" style="margin: 6px 0 0">准备度</p>
          </div>
        </div>
      </div>

      <div class="cols-4 portal-grid">
        <div class="portal-kpi">
          <p class="portal-kpi__label">简历状态</p>
          <p class="portal-kpi__value">{{ dashboard.profile_ready ? '已就绪' : '待完善' }}</p>
          <p class="portal-muted">先把经历、技能和目标岗位写完整，后面的推荐才更靠谱。</p>
        </div>
        <div class="portal-kpi">
          <p class="portal-kpi__label">练习场次</p>
          <p class="portal-kpi__value">{{ dashboard.interview_count }}</p>
          <p class="portal-muted">每一场都会保留问答记录与最终报告。</p>
        </div>
        <div class="portal-kpi">
          <p class="portal-kpi__label">报告数量</p>
          <p class="portal-kpi__value">{{ dashboard.report_count }}</p>
          <p class="portal-muted">练习完可以回看亮点、风险点和改进建议。</p>
        </div>
        <div class="portal-kpi">
          <p class="portal-kpi__label">平均得分</p>
          <p class="portal-kpi__value">{{ dashboard.average_score }}</p>
          <p class="portal-muted">用同一套口径帮助你观察自己的变化。</p>
        </div>
      </div>
    </div>

    <n-alert v-if="!dashboard.profile_ready" type="warning" style="border-radius: 20px">
      你的候选人档案还不够完整。建议先补齐目标岗位、技能标签和项目经历，再开始练习，这样岗位推荐和练习总结会更贴近真实求职场景。
    </n-alert>

    <div class="portal-grid cols-2">
      <div class="portal-card">
        <div class="portal-row" style="align-items: flex-start">
          <div>
            <h2 class="portal-section-title">适合先练的岗位</h2>
            <p class="portal-section-subtitle">
              根据当前简历信息整理出的练习入口，方便你先从更有把握的岗位开始。
            </p>
          </div>
          <n-button text type="primary" @click="router.push('/ai-interview/positions')"
            >全部查看</n-button
          >
        </div>

        <div class="portal-list" style="margin-top: 20px">
          <div v-for="item in dashboard.featured_positions" :key="item.id" class="portal-panel">
            <div class="portal-row" style="align-items: flex-start">
              <div>
                <h3 style="margin: 0 0 8px; font-size: 20px">{{ item.title }}</h3>
                <p class="portal-muted" style="margin: 0 0 8px">
                  {{ item.category || '岗位方向' }} / {{ item.department || '业务团队' }}
                </p>
                <div class="portal-tag-cloud">
                  <span v-for="tag in item.tags?.slice(0, 4)" :key="tag" class="portal-chip">{{
                    tag
                  }}</span>
                </div>
              </div>
              <div style="min-width: 96px; text-align: right">
                <n-tag :bordered="false" :type="scoreTone(item.score)">{{ item.score }} 分</n-tag>
                <p class="portal-muted" style="margin-top: 10px">匹配度</p>
              </div>
            </div>
            <p class="portal-section-subtitle" style="margin-top: 14px">
              {{ compactText(item.recommend_reason, 90) }}
            </p>
            <n-button
              quaternary
              type="primary"
              style="margin-top: 12px"
              @click="router.push(`/ai-interview/positions/${item.id}`)"
            >
              查看岗位详情
            </n-button>
          </div>
        </div>
      </div>

      <div class="portal-card">
        <div class="portal-row" style="align-items: flex-start">
          <div>
            <h2 class="portal-section-title">最近一次练习报告</h2>
            <p class="portal-section-subtitle">
              练习结束后会整理成一页总结，方便你回看和准备下一次。
            </p>
          </div>
          <n-button v-if="dashboard.latest_report" text type="primary" @click="openLatestReport"
            >打开详情</n-button
          >
        </div>

        <template v-if="dashboard.latest_report">
          <div class="portal-panel" style="margin-top: 20px">
            <div class="portal-row" style="align-items: center">
              <div>
                <p class="portal-chip">
                  {{ dashboard.latest_report.position?.title || '练习岗位' }}
                </p>
                <h3 style="margin: 16px 0 8px; font-size: 28px">
                  {{ dashboard.latest_report.total_score }} 分
                </h3>
                <p class="portal-muted">{{ compactText(dashboard.latest_report.overview, 120) }}</p>
              </div>
              <div class="portal-score-ring">
                <div style="text-align: center">
                  <strong>{{ dashboard.latest_report.total_score }}</strong>
                  <p style="margin: 6px 0 0">本次得分</p>
                </div>
              </div>
            </div>
            <div class="portal-divider" style="margin: 20px 0"></div>
            <div class="portal-grid cols-2">
              <div>
                <p class="portal-kpi__label">表现较好的地方</p>
                <ul class="portal-muted" style="padding-left: 18px; line-height: 1.8">
                  <li v-for="item in dashboard.latest_report.highlights?.slice(0, 3)" :key="item">
                    {{ item }}
                  </li>
                </ul>
              </div>
              <div>
                <p class="portal-kpi__label">接下来可以改进</p>
                <ul class="portal-muted" style="padding-left: 18px; line-height: 1.8">
                  <li v-for="item in dashboard.latest_report.suggestions?.slice(0, 3)" :key="item">
                    {{ item }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </template>

        <n-empty
          v-else
          description="还没有练习记录，先去完成一次面试练习吧。"
          style="margin-top: 36px"
        >
          <template #extra>
            <n-button type="primary" @click="router.push('/ai-interview/positions')"
              >去开始</n-button
            >
          </template>
        </n-empty>
      </div>
    </div>
  </section>
</template>

<script setup>
import api from '@/api'
import { compactText, scoreTone } from '@/views/interview-shared/utils'

const router = useRouter()
const dashboard = ref({
  profile_ready: false,
  readiness_score: 0,
  interview_count: 0,
  report_count: 0,
  average_score: 0,
  latest_report: null,
  featured_positions: [],
})

onMounted(async () => {
  const res = await api.getCandidatePortalDashboard()
  dashboard.value = res.data || dashboard.value
})

function openLatestReport() {
  if (!dashboard.value.latest_report?.id) return
  router.push(`/ai-interview/reports/${dashboard.value.latest_report.id}`)
}
</script>
