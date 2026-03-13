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
      <div class="runtime-overview">
        <div class="runtime-highlight">
          <div class="runtime-highlight__head">
            <div>
              <p class="runtime-card__label">运行总览</p>
              <h3 class="runtime-highlight__title">{{ status.provider || '未识别服务商' }}</h3>
              <p class="runtime-card__desc">
                当前主模型为 {{ status.model_name || '-' }}，基础地址为
                {{ status.base_url || '-' }}。
              </p>
            </div>
            <n-tag :bordered="false" size="large" :type="status.enabled ? 'success' : 'warning'">
              {{ status.enabled ? '当前可调用' : '待补齐配置' }}
            </n-tag>
          </div>

          <div class="runtime-highlight__metrics">
            <div class="runtime-highlight__metric">
              <span class="runtime-highlight__metric-label">最近事件</span>
              <strong class="runtime-highlight__metric-value">
                {{ status.last_event_at || '暂无记录' }}
              </strong>
            </div>
            <div class="runtime-highlight__metric">
              <span class="runtime-highlight__metric-label">环境文件</span>
              <strong class="runtime-highlight__metric-value">
                {{ (status.env_files || []).join(' / ') || '未检测到' }}
              </strong>
            </div>
            <div class="runtime-highlight__metric">
              <span class="runtime-highlight__metric-label">可用链路</span>
              <strong class="runtime-highlight__metric-value">
                {{ serviceCards.filter((item) => item.enabled).length }}/{{
                  serviceCards.length || 0
                }}
              </strong>
            </div>
          </div>
        </div>

        <div class="runtime-mini-grid">
          <div class="runtime-mini-card">
            <p class="runtime-card__label">当前状态</p>
            <strong class="runtime-card__value">{{ status.enabled ? '已启用' : '未启用' }}</strong>
            <p class="runtime-card__desc">模型地址、模型名和密钥都完整时可调用。</p>
          </div>

          <div class="runtime-mini-card">
            <p class="runtime-card__label">超时设置</p>
            <strong class="runtime-card__value">{{ status.timeout_seconds || 0 }}s</strong>
            <p class="runtime-card__desc">用于题目生成、追问生成和报告生成。</p>
          </div>

          <div class="runtime-mini-card">
            <p class="runtime-card__label">最近成功</p>
            <strong class="runtime-card__value runtime-card__value--small">
              {{ status.last_success_at || '暂无记录' }}
            </strong>
            <p class="runtime-card__desc">没有成功记录时建议先执行连通测试。</p>
          </div>

          <div class="runtime-mini-card">
            <p class="runtime-card__label">最近异常</p>
            <strong class="runtime-card__value runtime-card__value--small">
              {{ status.last_error_at || '暂无异常' }}
            </strong>
            <p class="runtime-card__desc">最近一次非 success 事件的时间点。</p>
          </div>
        </div>
      </div>

      <div class="runtime-panel">
        <div class="runtime-panel__head">
          <div>
            <h3 class="runtime-panel__title">模型与语音链路</h3>
            <p class="runtime-panel__desc">
              这里分别展示面试生成模型、讯飞 ASR、讯飞 TTS
              的当前配置状态，便于确认星火/讯飞链路是否完整。
            </p>
          </div>
        </div>
        <div class="runtime-service-grid">
          <div v-for="item in serviceCards" :key="item.key" class="runtime-service-card">
            <div class="runtime-card__value-row">
              <div>
                <p class="runtime-card__label">{{ item.name }}</p>
                <strong class="runtime-card__value runtime-card__value--small">
                  {{ item.model_name || '-' }}
                </strong>
              </div>
              <n-tag :bordered="false" :type="item.enabled ? 'success' : 'warning'">
                {{ item.status_text }}
              </n-tag>
            </div>
            <p class="runtime-card__desc">服务商：{{ item.provider || '-' }}</p>
            <p class="runtime-card__desc">配置：{{ item.detail || '-' }}</p>
            <p class="runtime-card__desc">最近成功：{{ item.last_success_at || '暂无记录' }}</p>
          </div>
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
import { NAlert, NButton, NDataTable, NEmpty, NTag } from 'naive-ui'
import api from '@/api'

defineOptions({ name: 'AI运行状态' })

const loading = ref(false)
const testing = ref(false)
const status = ref({ recent_logs: [] })

const latestGenerationLog = computed(() => status.value.latest_generation_log || null)
const latestRuntimeCheck = computed(() => status.value.latest_runtime_check || null)
const serviceCards = computed(() => status.value.service_cards || [])

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
      window.$message?.success('连通测试成功')
    } else {
      window.$message?.warning(res.data?.message || '连通测试未返回有效结果')
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
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}

.runtime-overview {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 1fr);
  gap: 16px;
  align-items: stretch;
}

.runtime-highlight {
  min-width: 0;
  padding: 24px;
  border: 1px solid #e7d6c6;
  border-radius: 24px;
  background: linear-gradient(135deg, #fffdf9 0%, #f6ede3 100%);
  box-shadow: 0 16px 36px rgba(92, 69, 47, 0.08);
}

.runtime-highlight__head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.runtime-highlight__title {
  margin: 12px 0 0;
  color: #302822;
  font-size: 34px;
  line-height: 1.15;
}

.runtime-highlight__metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
}

.runtime-highlight__metric {
  min-width: 0;
  padding: 14px 16px;
  border: 1px solid rgba(141, 108, 79, 0.12);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.82);
}

.runtime-highlight__metric-label {
  display: block;
  color: #8a7564;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.runtime-highlight__metric-value {
  display: block;
  margin-top: 8px;
  color: #352c25;
  font-size: 16px;
  line-height: 1.6;
  word-break: break-word;
}

.runtime-mini-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.runtime-mini-card {
  min-width: 0;
  padding: 20px;
  border: 1px solid #eadfd4;
  border-radius: 20px;
  background: #fff;
  box-shadow: 0 12px 28px rgba(92, 69, 47, 0.05);
}

.runtime-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  align-items: stretch;
}

.runtime-grid--two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.runtime-service-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.runtime-card,
.runtime-panel,
.runtime-service-card {
  min-width: 0;
  padding: 20px;
  border: 1px solid #eadfd4;
  border-radius: 20px;
  background: #fff;
  box-shadow: 0 12px 28px rgba(92, 69, 47, 0.05);
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
  word-break: break-word;
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
  max-width: 100%;
  word-break: break-word;
}

.runtime-field__value--mono {
  font-family: Menlo, Monaco, Consolas, 'Courier New', monospace;
  font-size: 12px;
  word-break: break-all;
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
  .runtime-overview,
  .runtime-grid,
  .runtime-grid--two,
  .runtime-service-grid {
    grid-template-columns: 1fr;
  }

  .runtime-highlight__metrics,
  .runtime-mini-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .runtime-highlight {
    padding: 20px;
  }

  .runtime-highlight__title {
    font-size: 28px;
  }
}
</style>
