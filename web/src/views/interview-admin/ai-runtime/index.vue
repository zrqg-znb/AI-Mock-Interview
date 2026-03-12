<template>
  <CommonPage title="AI 运行状态">
    <template #header>
      <div class="interview-admin-hero">
        <p class="interview-admin-hero__eyebrow">运行状态</p>
        <div class="interview-admin-hero__row">
          <div>
            <h2 class="interview-admin-hero__title">AI 配置状态</h2>
            <p class="interview-admin-hero__desc">
              这里集中展示当前模型配置、最近一次调用记录和连通测试结果，方便演示时快速说明系统是否处于可用状态。
            </p>
            <div class="interview-admin-hero__meta">
              <span class="interview-admin-hero__meta-item">配置可见</span>
              <span class="interview-admin-hero__meta-item">调用留痕</span>
              <span class="interview-admin-hero__meta-item">支持快速自检</span>
            </div>
          </div>
          <div class="interview-admin-hero__actions">
            <n-button secondary @click="loadStatus">刷新状态</n-button>
            <n-button type="primary" :loading="testing" @click="runCheck">执行连通测试</n-button>
          </div>
        </div>
      </div>
    </template>

    <div class="interview-admin-table__content ai-runtime-page">
      <div class="runtime-grid">
        <div class="runtime-card">
          <p class="runtime-card__label">当前状态</p>
          <div class="runtime-card__value-row">
            <strong class="runtime-card__value">{{ status.enabled ? '已启用' : '未启用' }}</strong>
            <n-tag :bordered="false" :type="status.enabled ? 'success' : 'warning'">
              {{ status.enabled ? '可调用' : '待配置' }}
            </n-tag>
          </div>
          <p class="runtime-card__desc">
            只要接口地址、模型名和密钥都已配置，就会在这里显示可调用。
          </p>
        </div>

        <div class="runtime-card">
          <p class="runtime-card__label">服务商</p>
          <strong class="runtime-card__value">{{ status.provider || '-' }}</strong>
          <p class="runtime-card__desc">当前模型：{{ status.model_name || '-' }}</p>
        </div>

        <div class="runtime-card">
          <p class="runtime-card__label">超时设置</p>
          <strong class="runtime-card__value">{{ status.timeout_seconds || 0 }}s</strong>
          <p class="runtime-card__desc">用于题目生成、下一题追问和报告生成的单次请求超时。</p>
        </div>

        <div class="runtime-card">
          <p class="runtime-card__label">最近成功</p>
          <strong class="runtime-card__value runtime-card__value--small">{{
            status.last_success_at || '暂无记录'
          }}</strong>
          <p class="runtime-card__desc">如果近期没有成功记录，可以先执行一次连通测试。</p>
        </div>
      </div>

      <div class="runtime-grid runtime-grid--two">
        <div class="runtime-panel">
          <div class="runtime-panel__head">
            <div>
              <h3 class="runtime-panel__title">配置摘要</h3>
              <p class="runtime-panel__desc">页面只展示脱敏后的关键配置，避免直接暴露敏感信息。</p>
            </div>
          </div>
          <div class="runtime-field-list">
            <div class="runtime-field">
              <span class="runtime-field__key">Base URL</span>
              <span class="runtime-field__value">{{ status.base_url || '-' }}</span>
            </div>
            <div class="runtime-field">
              <span class="runtime-field__key">模型名称</span>
              <span class="runtime-field__value">{{ status.model_name || '-' }}</span>
            </div>
            <div class="runtime-field">
              <span class="runtime-field__key">密钥状态</span>
              <span class="runtime-field__value">{{ status.api_key_masked || '未配置' }}</span>
            </div>
            <div class="runtime-field">
              <span class="runtime-field__key">环境文件</span>
              <span class="runtime-field__value">{{
                (status.env_files || []).join(' / ') || '-'
              }}</span>
            </div>
            <div class="runtime-field">
              <span class="runtime-field__key">日志文件</span>
              <span class="runtime-field__value runtime-field__value--mono">{{
                status.log_file || '-'
              }}</span>
            </div>
          </div>
        </div>

        <div class="runtime-panel">
          <div class="runtime-panel__head">
            <div>
              <h3 class="runtime-panel__title">最近一次生成结果</h3>
              <p class="runtime-panel__desc">
                优先展示最近一次题目生成、追问生成或报告生成记录，演示时更贴近真实业务链路。
              </p>
            </div>
          </div>
          <n-alert
            v-if="latestGenerationLog"
            :type="latestGenerationLog.status === 'success' ? 'success' : 'warning'"
            style="border-radius: 16px"
          >
            <template #header>
              {{ latestGenerationLog.scenario || 'general' }} / {{ latestGenerationLog.timestamp }}
            </template>
            <div style="line-height: 1.8">
              <div>状态：{{ latestGenerationLog.status }}</div>
              <div>耗时：{{ latestGenerationLog.duration_ms || 0 }} ms</div>
              <div v-if="latestGenerationLog.error_message">
                信息：{{ latestGenerationLog.error_message }}
              </div>
            </div>
          </n-alert>
          <n-empty v-else description="还没有生成记录" class="runtime-empty" />
          <div v-if="latestRuntimeCheck" class="runtime-check-note">
            最近连通测试：{{ latestRuntimeCheck.timestamp }} / {{ latestRuntimeCheck.status }}
          </div>
        </div>
      </div>

      <div class="runtime-panel">
        <div class="runtime-panel__head">
          <div>
            <h3 class="runtime-panel__title">最近一次生成日志</h3>
            <p class="runtime-panel__desc">
              保留最近若干次题目生成、下一题追问、报告生成和连通测试的记录。
            </p>
          </div>
        </div>
        <n-data-table
          :loading="loading"
          :columns="columns"
          :data="status.recent_logs || []"
          :pagination="false"
          :scroll-x="980"
        />
      </div>
    </div>
  </CommonPage>
</template>

<script setup>
import { NButton, NDataTable, NEmpty, NTag } from 'naive-ui'
import api from '@/api'

defineOptions({ name: 'AI运行状态' })

const loading = ref(false)
const testing = ref(false)
const status = ref({ recent_logs: [] })

const latestGenerationLog = computed(() => status.value.latest_generation_log || null)
const latestRuntimeCheck = computed(() => status.value.latest_runtime_check || null)

const columns = [
  {
    title: '时间',
    key: 'timestamp',
    width: 180,
  },
  {
    title: '场景',
    key: 'scenario',
    width: 160,
  },
  {
    title: '状态',
    key: 'status',
    width: 120,
    render(row) {
      return h(
        NTag,
        {
          bordered: false,
          type:
            row.status === 'success' ? 'success' : row.status === 'disabled' ? 'warning' : 'error',
        },
        { default: () => row.status || '-' }
      )
    },
  },
  {
    title: '模型',
    key: 'model_name',
    width: 150,
  },
  {
    title: '耗时(ms)',
    key: 'duration_ms',
    width: 120,
  },
  {
    title: '说明',
    key: 'error_message',
    minWidth: 320,
    ellipsis: { tooltip: true },
    render(row) {
      return row.error_message || '-'
    },
  },
]

onMounted(loadStatus)

async function loadStatus() {
  loading.value = true
  try {
    const res = await api.getAIRuntimeStatus({ limit: 20 })
    status.value = res.data || { recent_logs: [] }
  } finally {
    loading.value = false
  }
}

async function runCheck() {
  testing.value = true
  try {
    const res = await api.runAIRuntimeCheck()
    if (res.data?.ok) {
      $message.success('连通测试成功')
    } else {
      $message.warning(res.data?.message || '连通测试未返回有效结果')
    }
    await loadStatus()
  } finally {
    testing.value = false
  }
}
</script>

<style scoped src="../shared.css"></style>
<style scoped>
.ai-runtime-page {
  gap: 20px;
}

.runtime-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.runtime-grid--two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.runtime-card,
.runtime-panel {
  padding: 20px;
  border: 1px solid #eadfd4;
  border-radius: 20px;
  background: #fff;
}

.runtime-card__label,
.runtime-field__key {
  margin: 0;
  color: #8a7564;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.runtime-card__value-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 10px;
}

.runtime-card__value {
  display: block;
  margin-top: 10px;
  color: #302822;
  font-size: 28px;
  line-height: 1.3;
}

.runtime-card__value--small {
  font-size: 18px;
}

.runtime-card__desc,
.runtime-panel__desc {
  margin: 10px 0 0;
  color: #74675b;
  line-height: 1.75;
}

.runtime-panel__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.runtime-panel__title {
  margin: 0;
  color: #352c25;
  font-size: 20px;
  font-weight: 600;
}

.runtime-field-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.runtime-field {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #eadfd4;
}

.runtime-field:last-child {
  padding-bottom: 0;
  border-bottom: 0;
}

.runtime-field__value {
  color: #3f342c;
  text-align: right;
}

.runtime-field__value--mono {
  font-family: Menlo, Monaco, Consolas, 'Courier New', monospace;
  font-size: 12px;
}

.runtime-check-note {
  margin-top: 16px;
  padding: 12px 14px;
  border: 1px solid #efe4d9;
  border-radius: 14px;
  background: #fbf6f1;
  color: #6d5d51;
  line-height: 1.6;
}

.runtime-empty {
  padding: 14px 0;
  background: #faf7f2;
  border-radius: 16px;
}

:deep(.n-data-table-wrapper) {
  overflow: hidden;
  border: 1px solid #eadfd4;
  border-radius: 16px;
}

@media (max-width: 1100px) {
  .runtime-grid,
  .runtime-grid--two {
    grid-template-columns: 1fr;
  }
}
</style>
