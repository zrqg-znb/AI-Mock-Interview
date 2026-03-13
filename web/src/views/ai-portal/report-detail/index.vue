<template>
  <section v-if="report.id" class="portal-page">
    <div class="portal-hero">
      <div class="portal-row" style="align-items: flex-start; flex-wrap: wrap">
        <div style="max-width: 760px">
          <p class="portal-chip">练习报告</p>
          <h1 class="portal-section-title" style="font-size: 40px; margin-top: 16px">
            {{ report.position?.title || '面试练习报告' }}
          </h1>
          <p class="portal-section-subtitle">
            {{ report.overview || '报告生成中，请稍后刷新查看完整结果。' }}
          </p>
          <div class="portal-tag-cloud" style="margin-top: 18px">
            <span class="portal-chip">{{ reportStatusText }}</span>
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

    <div
      v-if="isGenerating"
      class="portal-card"
      style="
        border: 1px solid #ead7bf;
        background: linear-gradient(180deg, #fffaf2 0%, #fbf4ea 100%);
      "
    >
      <div class="portal-row" style="align-items: flex-start">
        <div>
          <h2 class="portal-section-title">报告生成中</h2>
          <p class="portal-section-subtitle">
            你已经完成本次练习。系统正在结合整场对话生成更完整的过程复盘和深度评价，通常 1 到 2
            分钟内可查看。
          </p>
        </div>
        <n-button type="primary" tertiary @click="loadReport">刷新报告</n-button>
      </div>
    </div>

    <div class="portal-grid cols-2">
      <div class="portal-card">
        <div class="portal-row">
          <div>
            <p class="portal-kpi__label">本次得分</p>
            <h2 class="portal-section-title" style="font-size: 44px">
              {{ isGenerating ? '--' : report.total_score }}
            </h2>
            <p class="portal-section-subtitle">
              {{
                isGenerating
                  ? '报告完成后，这里会展示最终总分。'
                  : '这份报告不仅保留结论，也会保留过程和回答深度。'
              }}
            </p>
          </div>
          <div class="portal-score-ring">
            <div style="text-align: center">
              <strong>{{ isGenerating ? '--' : report.total_score }}</strong>
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
        <p class="portal-section-subtitle">重点信息已经按分组整理好，回看时会更直接。</p>
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

    <div v-if="processReview.flow_summary || roundReviews.length" class="portal-grid cols-2">
      <div class="portal-card">
        <h2 class="portal-section-title">过程复盘</h2>
        <p class="portal-section-subtitle" style="margin-top: 12px">
          {{ processReview.flow_summary || '系统会根据整场问答整理对话过程。' }}
        </p>
        <div class="portal-divider" style="margin: 18px 0"></div>
        <p class="portal-kpi__label">深度评价</p>
        <p class="portal-muted" style="line-height: 1.9; margin-top: 10px">
          {{ processReview.depth_assessment || '报告生成后，这里会给出更具体的回答深度评价。' }}
        </p>
      </div>

      <div class="portal-card">
        <h2 class="portal-section-title">对话观察</h2>
        <div class="portal-grid cols-2" style="margin-top: 18px">
          <div class="portal-panel" style="padding: 18px">
            <p class="portal-kpi__label">系统观察</p>
            <ul class="portal-muted" style="padding-left: 18px; line-height: 1.9; margin-top: 12px">
              <li v-for="item in processReview.dialogue_observations || []" :key="item">
                {{ item }}
              </li>
            </ul>
          </div>
          <div class="portal-panel" style="padding: 18px">
            <p class="portal-kpi__label">下一步重点</p>
            <ul class="portal-muted" style="padding-left: 18px; line-height: 1.9; margin-top: 12px">
              <li v-for="item in processReview.next_focus || []" :key="item">{{ item }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <div v-if="roundReviews.length" class="portal-card">
      <div class="portal-row" style="align-items: flex-start">
        <div>
          <h2 class="portal-section-title">逐轮深度评价</h2>
          <p class="portal-section-subtitle">每一轮都保留问题、回答摘要和深度判断，便于回看。</p>
        </div>
      </div>
      <div class="portal-grid cols-2" style="margin-top: 20px">
        <div
          v-for="item in roundReviews"
          :key="item.round_no"
          class="portal-panel"
          style="padding: 20px"
        >
          <div class="portal-row" style="align-items: flex-start">
            <div>
              <p class="portal-kpi__label">第 {{ item.round_no }} 轮</p>
              <h3 class="portal-section-title" style="font-size: 22px; margin-top: 10px">
                {{ item.question || '本轮题目待整理' }}
              </h3>
            </div>
            <div class="portal-score-ring" style="width: 86px; height: 86px">
              <div style="text-align: center">
                <strong>{{ item.depth_score || 0 }}</strong>
                <p style="margin-top: 4px">深度</p>
              </div>
            </div>
          </div>
          <p class="portal-muted" style="margin-top: 14px; line-height: 1.8">
            {{ item.answer_summary || '本轮尚未形成有效回答。' }}
          </p>
          <div class="portal-divider" style="margin: 16px 0"></div>
          <p class="portal-kpi__label">评价</p>
          <p class="portal-muted" style="margin-top: 8px; line-height: 1.8">
            {{ item.depth_comment }}
          </p>
          <p
            v-if="item.matched_keywords?.length"
            class="portal-kpi__label"
            style="margin-top: 14px"
          >
            命中关键词
          </p>
          <div
            v-if="item.matched_keywords?.length"
            class="portal-tag-cloud"
            style="margin-top: 8px"
          >
            <span v-for="tag in item.matched_keywords" :key="tag" class="portal-chip">{{
              tag
            }}</span>
          </div>
          <p class="portal-kpi__label" style="margin-top: 14px">改进建议</p>
          <p class="portal-muted" style="margin-top: 8px; line-height: 1.8">
            {{ item.improvement }}
          </p>
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

    <div v-if="conversationTranscript.length" class="portal-card">
      <div class="portal-row" style="align-items: flex-start">
        <div>
          <h2 class="portal-section-title">对话过程留存</h2>
          <p class="portal-section-subtitle">这里保留整场问答，便于对照报告里的评价逐段回看。</p>
        </div>
      </div>
      <div class="portal-list" style="margin-top: 18px">
        <div
          v-for="(item, index) in conversationTranscript"
          :key="`${item.created_at}-${index}`"
          class="portal-panel"
          style="padding: 18px"
        >
          <div class="portal-row">
            <p class="portal-kpi__label">
              第 {{ item.round_no || 1 }} 轮 /
              {{ item.speaker === 'user' ? '我的回答' : 'AI 发言' }}
            </p>
            <span class="portal-muted">{{ formatDateTime(item.created_at) }}</span>
          </div>
          <div style="margin-top: 10px; line-height: 1.9; white-space: pre-wrap">
            {{ item.content }}
          </div>
        </div>
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
const isGenerating = computed(() => report.value.archive_status === 'generating')
const reportPayload = computed(() => report.value.report_payload || {})
const processReview = computed(() => reportPayload.value.process_review || {})
const roundReviews = computed(() => reportPayload.value.round_reviews || [])
const conversationTranscript = computed(() => reportPayload.value.conversation_transcript || [])
const reportStatusText = computed(() => {
  const status = report.value.archive_status
  if (status === 'generating') return '生成中'
  if (status === 'draft') return '草稿'
  if (status === 'exported') return '已导出'
  return status || '已归档'
})

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
