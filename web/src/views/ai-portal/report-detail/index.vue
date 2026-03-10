<template>
  <section v-if="report.id" class="portal-page">
    <div class="portal-hero">
      <div class="portal-row" style="align-items: flex-start; flex-wrap: wrap">
        <div style="max-width: 760px">
          <p class="portal-chip">练习报告</p>
          <h1 class="portal-section-title" style="font-size: 40px; margin-top: 16px">
            {{ report.position?.title || '模拟面试报告' }}
          </h1>
          <p class="portal-section-subtitle">{{ report.overview }}</p>
          <div class="portal-tag-cloud" style="margin-top: 18px">
            <span class="portal-chip">{{ report.archive_status || 'archived' }}</span>
            <span class="portal-chip">{{ formatDateTime(report.created_at) }}</span>
            <span class="portal-chip">场次 #{{ report.session_id }}</span>
          </div>
        </div>

        <div class="portal-actions">
          <n-button tertiary @click="router.push('/ai-interview/reports')">返回报告中心</n-button>
          <n-button type="primary" @click="exportPdf">导出 PDF</n-button>
        </div>
      </div>
    </div>

    <div class="portal-grid cols-2">
      <div class="portal-card">
        <div class="portal-row">
          <div>
            <p class="portal-kpi__label">本次得分</p>
            <h2 class="portal-section-title" style="font-size: 44px">{{ report.total_score }}</h2>
            <p class="portal-section-subtitle">
              这份报告更像一页练习总结，帮助你知道下一次应该重点改哪里。
            </p>
          </div>
          <div class="portal-score-ring">
            <div style="text-align: center">
              <strong>{{ report.total_score }}</strong>
              <p style="margin-top: 6px">总分</p>
            </div>
          </div>
        </div>

        <div class="portal-panel" style="margin-top: 20px">
          <p class="portal-kpi__label">分项得分</p>
          <div class="portal-list" style="margin-top: 16px">
            <div v-for="(value, key) in report.dimension_scores || {}" :key="key">
              <div class="portal-row">
                <span>{{ key }}</span>
                <strong>{{ value }}</strong>
              </div>
              <n-progress
                type="line"
                :percentage="value"
                :show-indicator="false"
                status="success"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="portal-card">
        <h2 class="portal-section-title">能力概览</h2>
        <p class="portal-section-subtitle">
          不做复杂的炫技图表，直接把重点信息整理成清晰的分组，回看更省心。
        </p>
        <div class="portal-grid cols-2" style="margin-top: 20px">
          <div v-for="(value, key) in report.dimension_scores || {}" :key="key" class="portal-kpi">
            <p class="portal-kpi__label">{{ key }}</p>
            <p class="portal-kpi__value" style="font-size: 24px">{{ value }}</p>
            <p class="portal-muted">
              {{ value >= 85 ? '表现稳定' : value >= 70 ? '有提升空间' : '建议重点练习' }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <div class="portal-grid cols-3">
      <div class="portal-card">
        <h2 class="portal-section-title">表现较好的地方</h2>
        <ul class="portal-muted" style="padding-left: 18px; line-height: 1.9; margin-top: 16px">
          <li v-for="item in report.highlights || []" :key="item">{{ item }}</li>
        </ul>
      </div>
      <div class="portal-card">
        <h2 class="portal-section-title">需要留意的地方</h2>
        <ul class="portal-muted" style="padding-left: 18px; line-height: 1.9; margin-top: 16px">
          <li v-for="item in report.risks || []" :key="item">{{ item }}</li>
        </ul>
      </div>
      <div class="portal-card">
        <h2 class="portal-section-title">下次练习建议</h2>
        <ul class="portal-muted" style="padding-left: 18px; line-height: 1.9; margin-top: 16px">
          <li v-for="item in report.suggestions || []" :key="item">{{ item }}</li>
        </ul>
      </div>
    </div>

    <div class="portal-card">
      <div class="portal-row" style="align-items: flex-start">
        <div>
          <h2 class="portal-section-title">接下来可以继续练的岗位</h2>
          <p class="portal-section-subtitle">如果你还想继续练习，可以从这些相关岗位开始。</p>
        </div>
        <n-button tertiary @click="router.push('/ai-interview/positions')">继续练习</n-button>
      </div>
      <div class="portal-tag-cloud" style="margin-top: 18px">
        <span v-for="item in report.recommended_positions || []" :key="item" class="portal-chip">{{
          item
        }}</span>
      </div>
    </div>
  </section>
</template>

<script setup>
import api from '@/api'
import { formatDateTime } from '@/utils'

const route = useRoute()
const router = useRouter()
const report = ref({})

onMounted(loadReport)

async function loadReport() {
  const params = route.params.reportId
    ? { report_id: route.params.reportId }
    : { session_id: route.params.sessionId }
  const res = await api.getMockInterviewReport(params)
  report.value = res.data || {}
}

function exportPdf() {
  window.print()
}
</script>
