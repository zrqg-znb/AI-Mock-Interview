<template>
  <section class="portal-page">
    <div class="portal-hero">
      <div class="portal-row" style="align-items: flex-end; flex-wrap: wrap">
        <div>
          <p class="portal-chip">报告中心</p>
          <h1 class="portal-section-title" style="font-size: 38px; margin-top: 16px">
            把每次练习都留下来
          </h1>
          <p class="portal-section-subtitle" style="max-width: 760px">
            每次练习结束后，这里都会保留一页总结。你可以回看得分、亮点和下次准备要点，也可以把它当作下一次练习前的笔记。
          </p>
        </div>
        <n-button type="primary" @click="loadData">刷新列表</n-button>
      </div>
    </div>

    <div class="portal-grid cols-3">
      <div v-for="item in reports" :key="item.id" class="portal-card">
        <div class="portal-row" style="align-items: flex-start">
          <div>
            <p class="portal-chip">{{ item.position?.title || '练习岗位' }}</p>
            <h2 class="portal-section-title" style="font-size: 30px; margin-top: 14px">
              {{ item.total_score }} 分
            </h2>
            <p class="portal-section-subtitle">{{ formatDateTime(item.created_at) }}</p>
          </div>
          <n-tag :type="scoreTone(item.total_score)" :bordered="false">{{
            item.archive_status || 'archived'
          }}</n-tag>
        </div>

        <p class="portal-section-subtitle" style="margin-top: 16px">
          {{ compactText(item.overview, 96) }}
        </p>

        <div class="portal-divider" style="margin: 18px 0"></div>
        <div class="portal-grid cols-2">
          <div>
            <p class="portal-kpi__label">表现较好</p>
            <ul class="portal-muted" style="padding-left: 18px; line-height: 1.8">
              <li v-for="tip in item.highlights?.slice(0, 2)" :key="tip">{{ tip }}</li>
            </ul>
          </div>
          <div>
            <p class="portal-kpi__label">接下来可改进</p>
            <ul class="portal-muted" style="padding-left: 18px; line-height: 1.8">
              <li v-for="tip in item.suggestions?.slice(0, 2)" :key="tip">{{ tip }}</li>
            </ul>
          </div>
        </div>

        <div class="portal-row" style="margin-top: 18px">
          <n-button tertiary @click="router.push(`/ai-interview/reports/${item.id}`)"
            >查看详情</n-button
          >
          <n-button type="primary" @click="router.push(`/ai-interview/reports/${item.id}`)"
            >打开报告</n-button
          >
        </div>
      </div>
    </div>

    <n-empty
      v-if="!reports.length"
      description="当前还没有练习报告，去完成一场面试练习吧。"
      class="portal-card"
    >
      <template #extra>
        <n-button type="primary" @click="router.push('/ai-interview/positions')">去开始</n-button>
      </template>
    </n-empty>
  </section>
</template>

<script setup>
import api from '@/api'
import { formatDateTime } from '@/utils'
import { compactText, scoreTone } from '@/views/interview-shared/utils'

const router = useRouter()
const reports = ref([])

onMounted(loadData)

async function loadData() {
  const res = await api.getCandidatePortalReports({ page: 1, page_size: 12 })
  reports.value = res.data || []
}
</script>
