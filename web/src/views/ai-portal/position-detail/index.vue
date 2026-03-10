<template>
  <section v-if="detail.id" class="portal-page">
    <div class="portal-hero">
      <div class="portal-row" style="align-items: flex-start; flex-wrap: wrap">
        <div style="max-width: 760px">
          <p class="portal-chip">岗位详情</p>
          <h1 class="portal-section-title" style="font-size: 40px; margin-top: 16px">
            {{ detail.title }}
          </h1>
          <p class="portal-section-subtitle">
            {{ detail.category || '岗位方向' }} / {{ detail.department || '业务团队' }} /
            {{ detail.level || '常规职级' }}
          </p>
          <p class="portal-section-subtitle" style="margin-top: 16px">
            {{ detail.summary || '你可以先通读岗位要求，再决定是否把它作为下一场练习的目标。' }}
          </p>
          <n-space style="margin-top: 18px">
            <n-button tertiary @click="router.push('/ai-interview/positions')"
              >返回岗位列表</n-button
            >
            <n-button type="primary" size="large" @click="startInterview">开始这场练习</n-button>
          </n-space>
        </div>

        <div class="portal-score-ring">
          <div style="text-align: center">
            <strong>{{ detail.score || 0 }}</strong>
            <p style="margin-top: 6px">匹配度</p>
          </div>
        </div>
      </div>
    </div>

    <div class="portal-grid cols-2">
      <div class="portal-card">
        <h2 class="portal-section-title">为什么推荐这个岗位</h2>
        <p class="portal-section-subtitle">先看整体匹配，再判断要不要立刻开始练习。</p>
        <div class="portal-grid cols-3" style="margin-top: 20px">
          <div
            v-for="metric in detail.heat_map || []"
            :key="metric.label"
            class="portal-kpi"
            style="padding: 16px"
          >
            <p class="portal-kpi__label">{{ metric.label }}</p>
            <p class="portal-kpi__value" style="font-size: 22px">{{ metric.value }}</p>
            <n-progress
              type="line"
              :percentage="metric.value"
              :show-indicator="false"
              status="success"
            />
          </div>
        </div>
        <div class="portal-panel" style="margin-top: 18px">
          <p class="portal-kpi__label">推荐说明</p>
          <p class="portal-section-subtitle" style="margin-top: 10px">
            {{ detail.recommend_reason }}
          </p>
        </div>
      </div>

      <div class="portal-card">
        <h2 class="portal-section-title">简历和岗位的对应关系</h2>
        <div class="portal-panel" style="margin-top: 18px">
          <p class="portal-kpi__label">岗位标签</p>
          <div class="portal-tag-cloud" style="margin-top: 12px">
            <span v-for="tag in detail.tags || []" :key="tag" class="portal-chip">{{ tag }}</span>
          </div>
        </div>
        <div class="portal-panel" style="margin-top: 18px">
          <p class="portal-kpi__label">已经覆盖的能力点</p>
          <div class="portal-tag-cloud" style="margin-top: 12px">
            <n-tag
              v-for="tag in detail.matched_tags || []"
              :key="tag"
              type="success"
              :bordered="false"
              >{{ tag }}</n-tag
            >
          </div>
        </div>
        <div class="portal-panel" style="margin-top: 18px">
          <p class="portal-kpi__label">建议准备的内容</p>
          <div class="portal-tag-cloud" style="margin-top: 12px">
            <n-tag
              v-for="tag in detail.missing_tags || []"
              :key="tag"
              type="warning"
              :bordered="false"
              >{{ tag }}</n-tag
            >
          </div>
        </div>
      </div>
    </div>

    <div class="portal-grid cols-2">
      <div class="portal-card">
        <h2 class="portal-section-title">岗位要求摘要</h2>
        <div class="portal-panel" style="margin-top: 18px">
          <p class="portal-kpi__label">必备技能</p>
          <div class="portal-tag-cloud" style="margin-top: 12px">
            <span
              v-for="tag in detail.active_jd?.must_have_tags || []"
              :key="tag"
              class="portal-chip"
              >{{ tag }}</span
            >
          </div>
        </div>
        <div class="portal-panel" style="margin-top: 18px">
          <p class="portal-kpi__label">加分项</p>
          <div class="portal-tag-cloud" style="margin-top: 12px">
            <span
              v-for="tag in detail.active_jd?.bonus_tags || []"
              :key="tag"
              class="portal-chip"
              >{{ tag }}</span
            >
          </div>
        </div>
      </div>

      <div class="portal-card">
        <h2 class="portal-section-title">开始练习前，你会看到什么</h2>
        <ul class="portal-muted" style="line-height: 2; padding-left: 20px; margin-top: 18px">
          <li>进入房间后会自动拉起摄像头预览，只在本地展示，不会上传视频。</li>
          <li>系统先给出一组问题，再根据你的回答逐步继续下一题。</li>
          <li>练习结束后会生成一份便于回看的总结报告。</li>
        </ul>
        <n-button type="primary" style="margin-top: 18px" @click="startInterview"
          >就从这个岗位开始</n-button
        >
      </div>
    </div>
  </section>
</template>

<script setup>
import api from '@/api'

const router = useRouter()
const route = useRoute()
const detail = ref({})

onMounted(loadDetail)

async function loadDetail() {
  const res = await api.getJobRecommendDetail({ position_id: route.params.id })
  detail.value = res.data || {}
}

async function startInterview() {
  const res = await api.startMockInterview({ position_id: detail.value.id, total_rounds: 5 })
  const session = res.data
  window.sessionStorage.setItem(`mock-session:${session.id}`, JSON.stringify(session))
  router.push(`/ai-interview/room/${session.id}`)
}
</script>
