<template>
  <CommonPage title="面试报告档案">
    <template #header>
      <div class="interview-admin-hero">
        <p class="interview-admin-hero__eyebrow">报告归档</p>
        <div class="interview-admin-hero__row">
          <div>
            <h2 class="interview-admin-hero__title">面试报告档案</h2>
            <p class="interview-admin-hero__desc">
              统一留存每场练习的得分、评价和建议，便于后台筛选，也方便候选人回看历史记录。
            </p>
            <div class="interview-admin-hero__meta">
              <span class="interview-admin-hero__meta-item">结构化报告</span>
              <span class="interview-admin-hero__meta-item">PDF 导出</span>
              <span class="interview-admin-hero__meta-item">归档筛选</span>
            </div>
          </div>
          <div class="interview-admin-hero__actions">
            <n-button
              v-permission="'post/api/v1/report/create'"
              secondary
              type="primary"
              @click="openAdd"
            >
              新增报告
            </n-button>
          </div>
        </div>
      </div>
    </template>

    <CrudTable
      ref="tableRef"
      v-model:queryItems="queryItems"
      class="interview-admin-table__content"
      :columns="columns"
      :get-data="api.getReportList"
      :scroll-x="1380"
    >
      <template #queryBar>
        <QueryBarItem label="候选人">
          <n-select
            v-model:value="queryItems.candidate_id"
            clearable
            filterable
            :options="candidateOptions"
          />
        </QueryBarItem>
        <QueryBarItem label="岗位">
          <n-select
            v-model:value="queryItems.position_id"
            clearable
            filterable
            :options="positionOptions"
          />
        </QueryBarItem>
        <QueryBarItem label="归档状态">
          <n-select
            v-model:value="queryItems.archive_status"
            clearable
            :options="archiveStatusOptions"
          />
        </QueryBarItem>
      </template>
    </CrudTable>

    <CrudModal
      :visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      width="980px"
      @update:visible="(v) => (modalVisible = v)"
      @save="handleSave"
    >
      <n-form
        ref="modalFormRef"
        :model="modalForm"
        :rules="rules"
        label-placement="left"
        label-width="96"
      >
        <n-grid cols="2" x-gap="16">
          <n-form-item-gi label="场次" path="session_id">
            <n-select
              v-model:value="modalForm.session_id"
              filterable
              :options="sessionOptions"
              @update:value="handleSessionChange"
            />
          </n-form-item-gi>
          <n-form-item-gi label="总分" path="total_score">
            <n-input-number
              v-model:value="modalForm.total_score"
              :min="0"
              :max="100"
              style="width: 100%"
            />
          </n-form-item-gi>
          <n-form-item-gi label="候选人" path="candidate_id">
            <n-select
              v-model:value="modalForm.candidate_id"
              filterable
              :options="candidateOptions"
            />
          </n-form-item-gi>
          <n-form-item-gi label="岗位" path="position_id">
            <n-select v-model:value="modalForm.position_id" filterable :options="positionOptions" />
          </n-form-item-gi>
          <n-form-item-gi label="归档状态" path="archive_status">
            <n-select v-model:value="modalForm.archive_status" :options="archiveStatusOptions" />
          </n-form-item-gi>
          <n-form-item-gi label="PDF 地址" path="pdf_url">
            <n-input
              v-model:value="modalForm.pdf_url"
              placeholder="可留空，候选人端支持直接浏览器打印导出"
            />
          </n-form-item-gi>
          <n-form-item-gi label="亮点" path="highlights" span="2">
            <n-input v-model:value="modalForm.highlights" placeholder="多条用中文逗号分隔" />
          </n-form-item-gi>
          <n-form-item-gi label="风险点" path="risks" span="2">
            <n-input v-model:value="modalForm.risks" placeholder="多条用中文逗号分隔" />
          </n-form-item-gi>
          <n-form-item-gi label="改进建议" path="suggestions" span="2">
            <n-input v-model:value="modalForm.suggestions" placeholder="多条用中文逗号分隔" />
          </n-form-item-gi>
          <n-form-item-gi label="推荐岗位" path="recommended_positions" span="2">
            <n-input
              v-model:value="modalForm.recommended_positions"
              placeholder="多条用中文逗号分隔"
            />
          </n-form-item-gi>
          <n-form-item-gi label="综合评价" path="overview" span="2">
            <n-input
              v-model:value="modalForm.overview"
              type="textarea"
              :autosize="{ minRows: 5, maxRows: 7 }"
            />
          </n-form-item-gi>
        </n-grid>
      </n-form>
    </CrudModal>
  </CommonPage>
</template>

<script setup>
import { resolveDirective, withDirectives } from 'vue'
import { NButton, NPopconfirm, NTag } from 'naive-ui'
import api from '@/api'
import useCRUD from '@/composables/useCRUD'
import { formatDateTime } from '@/utils'
import { archiveStatusOptions, joinTextList, scoreTone } from '@/views/interview-shared/utils'

defineOptions({ name: '面试报告档案' })

const tableRef = ref(null)
const vPermission = resolveDirective('permission')
const queryItems = ref({ candidate_id: null, position_id: null, archive_status: null })
const candidateOptions = ref([])
const positionOptions = ref([])
const sessionOptions = ref([])
const sessionMap = ref({})
const initForm = {
  session_id: null,
  candidate_id: null,
  position_id: null,
  total_score: 75,
  dimension_scores: {},
  overview: '',
  highlights: '',
  risks: '',
  suggestions: '',
  recommended_positions: '',
  archive_status: 'archived',
  pdf_url: '',
  report_payload: {},
}
const rules = {
  session_id: { required: true, type: 'number', message: '请选择场次', trigger: 'change' },
  candidate_id: { required: true, type: 'number', message: '请选择候选人', trigger: 'change' },
  position_id: { required: true, type: 'number', message: '请选择岗位', trigger: 'change' },
  overview: { required: true, message: '请输入综合评价', trigger: 'blur' },
}

const {
  modalVisible,
  modalTitle,
  modalLoading,
  modalForm,
  modalFormRef,
  handleAdd,
  handleEdit,
  handleDelete,
  handleSave,
} = useCRUD({
  name: '面试报告',
  initForm,
  doCreate: api.createReport,
  doUpdate: api.updateReport,
  doDelete: api.deleteReport,
  refresh: () => tableRef.value?.handleSearch(),
})

const columns = [
  {
    title: '岗位',
    key: 'position.title',
    width: 180,
    render(row) {
      return row.position?.title || '-'
    },
  },
  {
    title: '候选人',
    key: 'candidate.target_position',
    width: 180,
    render(row) {
      return row.candidate?.target_position || row.candidate?.headline || '-'
    },
  },
  {
    title: '总分',
    key: 'total_score',
    width: 110,
    render(row) {
      return h(
        NTag,
        { bordered: false, type: scoreTone(row.total_score) },
        { default: () => `${row.total_score} 分` }
      )
    },
  },
  {
    title: '归档状态',
    key: 'archive_status',
    width: 120,
  },
  {
    title: '综合评价',
    key: 'overview',
    width: 360,
    ellipsis: { tooltip: true },
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 170,
    render(row) {
      return formatDateTime(row.created_at)
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 190,
    fixed: 'right',
    render(row) {
      return [
        withDirectives(
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              style: 'margin-right:8px;',
              onClick: () => openEdit(row.id),
            },
            { default: () => '编辑' }
          ),
          [[vPermission, 'post/api/v1/report/update']]
        ),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete({ report_id: row.id }) },
          {
            trigger: () =>
              withDirectives(
                h(NButton, { size: 'small', type: 'error' }, { default: () => '删除' }),
                [[vPermission, 'delete/api/v1/report/delete']]
              ),
            default: () => '确认删除这份报告吗？',
          }
        ),
      ]
    },
  },
]

onMounted(async () => {
  await Promise.all([loadCandidates(), loadPositions(), loadSessions()])
  tableRef.value?.handleSearch()
})

async function loadCandidates() {
  const res = await api.getCandidateList({ page: 1, page_size: 999 })
  candidateOptions.value = (res.data || []).map((item) => ({
    label: `${item.user?.username || '候选人'} / ${item.target_position || '未设置目标岗位'}`,
    value: item.id,
  }))
}

async function loadPositions() {
  const res = await api.getPositionList({ page: 1, page_size: 999 })
  positionOptions.value = (res.data || []).map((item) => ({ label: item.title, value: item.id }))
}

async function loadSessions() {
  const res = await api.getInterviewList({ page: 1, page_size: 999 })
  const map = {}
  sessionOptions.value = (res.data || []).map((item) => {
    map[item.id] = item
    return { label: `${item.session_no} / ${item.position?.title || '未知岗位'}`, value: item.id }
  })
  sessionMap.value = map
}

function openAdd() {
  handleAdd()
  Object.assign(modalForm.value, { ...initForm })
}

async function openEdit(id) {
  const res = await api.getReportById({ report_id: id })
  handleEdit({
    ...res.data,
    candidate_id: res.data?.candidate?.id || res.data?.candidate_id,
    position_id: res.data?.position?.id || res.data?.position_id,
    highlights: joinTextList(res.data?.highlights),
    risks: joinTextList(res.data?.risks),
    suggestions: joinTextList(res.data?.suggestions),
    recommended_positions: joinTextList(res.data?.recommended_positions),
  })
}

function handleSessionChange(sessionId) {
  const session = sessionMap.value[sessionId]
  if (!session) return
  modalForm.value.candidate_id = session.candidate?.id || session.candidate_id
  modalForm.value.position_id = session.position?.id || session.position_id
}
</script>
<style scoped src="../shared.css"></style>
