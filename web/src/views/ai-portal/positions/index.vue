<template>
  <section class="portal-page">
    <div class="portal-hero">
      <div class="portal-row" style="align-items: flex-end; flex-wrap: wrap">
        <div>
          <p class="portal-chip">岗位推荐</p>
          <h1 class="portal-section-title" style="font-size: 38px; margin-top: 16px">
            先从适合自己的岗位开始练
          </h1>
          <p class="portal-section-subtitle" style="max-width: 760px">
            这里会根据你的简历、目标岗位和现有经历，整理出一批更适合作为模拟练习入口的岗位。先选一个最顺手的，不必一开始就追求最难的题。
          </p>
        </div>
        <div class="portal-actions" style="margin-left: auto">
          <n-input
            v-model:value="keyword"
            placeholder="搜索岗位、方向、部门"
            clearable
            style="width: 280px"
            @keyup.enter="loadData"
          />
          <n-button type="primary" @click="loadData">刷新列表</n-button>
        </div>
      </div>
    </div>

    <div class="portal-grid cols-2">
      <div v-for="item in positions" :key="item.id" class="portal-card">
        <div class="portal-row" style="align-items: flex-start">
          <div>
            <p class="portal-chip">{{ optionLabel(difficultyOptions, item.difficulty, '进阶') }}</p>
            <h2 class="portal-section-title" style="margin-top: 16px">{{ item.title }}</h2>
            <p class="portal-section-subtitle">
              {{ item.category || '岗位方向' }} / {{ item.department || '业务团队' }} /
              {{ item.level || '常规职级' }}
            </p>
          </div>
          <div style="text-align: right; min-width: 120px">
            <div
              class="portal-score-ring"
              :style="{ width: '96px', height: '96px', background: scoreGradient(item.score) }"
            >
              <div style="text-align: center">
                <strong style="font-size: 30px">{{ item.score }}</strong>
                <p style="margin: 4px 0 0">匹配分</p>
              </div>
            </div>
          </div>
        </div>

        <div class="portal-tag-cloud" style="margin-top: 16px">
          <span v-for="tag in item.tags?.slice(0, 6)" :key="tag" class="portal-chip">{{
            tag
          }}</span>
        </div>

        <p class="portal-section-subtitle" style="margin-top: 18px">{{ item.recommend_reason }}</p>

        <div class="portal-grid cols-3" style="margin-top: 18px">
          <div
            v-for="metric in item.heat_map || []"
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

        <div class="portal-row" style="margin-top: 18px; align-items: flex-start">
          <div style="flex: 1">
            <p class="portal-kpi__label">简历里已经体现的点</p>
            <div class="portal-tag-cloud" style="margin-top: 8px">
              <n-tag
                v-for="tag in item.matched_tags?.slice(0, 5)"
                :key="tag"
                type="success"
                :bordered="false"
                >{{ tag }}</n-tag
              >
              <span v-if="!item.matched_tags?.length" class="portal-muted"
                >如果信息还不够，可以先去补充简历。</span
              >
            </div>
          </div>
          <div style="flex: 1">
            <p class="portal-kpi__label">面试前建议补一补</p>
            <div class="portal-tag-cloud" style="margin-top: 8px">
              <n-tag
                v-for="tag in item.missing_tags?.slice(0, 4)"
                :key="tag"
                type="warning"
                :bordered="false"
                >{{ tag }}</n-tag
              >
              <span v-if="!item.missing_tags?.length" class="portal-muted"
                >当前信息已经足够支撑一场练习。</span
              >
            </div>
          </div>
        </div>

        <div class="portal-row" style="margin-top: 18px">
          <n-button tertiary @click="router.push(`/ai-interview/positions/${item.id}`)"
            >查看详情</n-button
          >
          <n-button type="primary" @click="startInterview(item.id)">开始练习</n-button>
        </div>
      </div>
    </div>

    <n-empty
      v-if="!positions.length"
      description="没有找到合适的岗位，先补全简历中心或换个关键词试试。"
      class="portal-card"
    />
  </section>
</template>

<script setup>
import api from '@/api'
import { difficultyOptions, optionLabel, scoreGradient } from '@/views/interview-shared/utils'

const router = useRouter()
const keyword = ref('')
const positions = ref([])
const loading = ref(false)

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const res = await api.getJobRecommendList({ keyword: keyword.value, page_size: 12 })
    positions.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function startInterview(positionId) {
  try {
    const res = await api.startMockInterview({ position_id: positionId, total_rounds: 5 })
    const session = res.data
    window.sessionStorage.setItem(`mock-session:${session.id}`, JSON.stringify(session))
    router.push(`/ai-interview/room/${session.id}`)
  } catch (error) {
    console.error(error)
  }
}
</script>
