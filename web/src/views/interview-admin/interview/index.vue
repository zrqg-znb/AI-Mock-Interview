<template>
  <CommonPage title="面试场次管理">
    <template #header>
      <div class="interview-admin-hero">
        <p class="interview-admin-hero__eyebrow">练习场次</p>
        <div class="interview-admin-hero__row">
          <div>
            <h2 class="interview-admin-hero__title">面试场次管理</h2>
            <p class="interview-admin-hero__desc">
              查看候选人与岗位对应的练习进度，补录上下文并回看问答记录，方便统一复盘。
            </p>
            <div class="interview-admin-hero__meta">
              <span class="interview-admin-hero__meta-item">候选人关联</span>
              <span class="interview-admin-hero__meta-item">轮次进度</span>
              <span class="interview-admin-hero__meta-item">对话回看</span>
            </div>
          </div>
          <div class="interview-admin-hero__actions">
            <n-button
              v-permission="'post/api/v1/interview/create'"
              secondary
              type="primary"
              @click="openAdd"
            >
              新增场次
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
      :get-data="api.getInterviewList"
      :scroll-x="1420"
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
        <QueryBarItem label="状态">
          <n-select v-model:value="queryItems.status" clearable :options="sessionStatusOptions" />
        </QueryBarItem>
      </template>
    </CrudTable>

    <CrudModal
      :visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      width="960px"
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
          <n-form-item-gi label="关联 JD" path="jd_id">
            <n-select
              v-model:value="modalForm.jd_id"
              clearable
              filterable
              :options="availableJDOptions"
            />
          </n-form-item-gi>
          <n-form-item-gi label="状态" path="status">
            <n-select v-model:value="modalForm.status" :options="sessionStatusOptions" />
          </n-form-item-gi>
          <n-form-item-gi label="总轮次" path="total_rounds">
            <n-input-number
              v-model:value="modalForm.total_rounds"
              :min="1"
              :max="8"
              style="width: 100%"
            />
          </n-form-item-gi>
          <n-form-item-gi label="当前轮次" path="current_round">
            <n-input-number
              v-model:value="modalForm.current_round"
              :min="0"
              :max="8"
              style="width: 100%"
            />
          </n-form-item-gi>
          <n-form-item-gi label="上下文摘要" path="context_summary" span="2">
            <n-input
              v-model:value="modalForm.context_summary"
              type="textarea"
              :autosize="{ minRows: 4, maxRows: 6 }"
            />
          </n-form-item-gi>
        </n-grid>
      </n-form>

      <div v-if="detailTurns.length" class="interview-admin-note" style="margin-top: 18px">
        <p class="interview-admin-note__label">对话记录</p>
        <div class="interview-admin-log">
          <div
            v-for="item in detailTurns"
            :key="`${item.created_at}-${item.id}`"
            class="interview-admin-log__item"
          >
            <div class="interview-admin-log__meta">
              <strong class="interview-admin-log__speaker">{{
                item.speaker === 'user' ? '候选人' : '系统提问'
              }}</strong>
              <span>第 {{ item.round_no }} 轮</span>
            </div>
            <p class="interview-admin-log__content">{{ item.content }}</p>
          </div>
        </div>
      </div>
    </CrudModal>
  </CommonPage>
</template>

<script setup>
import { resolveDirective, withDirectives } from 'vue'
import { NButton, NPopconfirm, NTag } from 'naive-ui'
import api from '@/api'
import useCRUD from '@/composables/useCRUD'
import { formatDateTime } from '@/utils'
import { optionLabel, sessionStatusOptions } from '@/views/interview-shared/utils'

defineOptions({ name: '面试场次管理' })

const tableRef = ref(null)
const vPermission = resolveDirective('permission')
const queryItems = ref({ candidate_id: null, position_id: null, status: null })
const candidateOptions = ref([])
const positionOptions = ref([])
const jdOptions = ref([])
const detailTurns = ref([])
const initForm = {
  candidate_id: null,
  position_id: null,
  jd_id: null,
  status: 'pending',
  current_round: 0,
  total_rounds: 5,
  context_summary: '',
}
const rules = {
  candidate_id: { required: true, type: 'number', message: '请选择候选人', trigger: 'change' },
  position_id: { required: true, type: 'number', message: '请选择岗位', trigger: 'change' },
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
  name: '面试场次',
  initForm,
  doCreate: api.createInterview,
  doUpdate: api.updateInterview,
  doDelete: api.deleteInterview,
  refresh: () => tableRef.value?.handleSearch(),
})

const availableJDOptions = computed(() => {
  if (!modalForm.value.position_id) return jdOptions.value
  return jdOptions.value.filter((item) => item.positionId === modalForm.value.position_id)
})

const columns = [
  { title: '场次编号', key: 'session_no', width: 200 },
  {
    title: '候选人',
    key: 'candidate.target_position',
    width: 180,
    render(row) {
      return h('div', [
        h('div', row.candidate?.target_position || '-'),
        h('div', { style: 'font-size:12px;opacity:.65' }, row.candidate?.headline || '-'),
      ])
    },
  },
  {
    title: '岗位',
    key: 'position.title',
    width: 160,
    render(row) {
      return row.position?.title || '-'
    },
  },
  {
    title: '进度',
    key: 'progress',
    width: 120,
    render(row) {
      return `${row.current_round || 0} / ${row.total_rounds || 0}`
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 110,
    render(row) {
      const type =
        row.status === 'completed' ? 'success' : row.status === 'running' ? 'warning' : 'default'
      return h(
        NTag,
        { bordered: false, type },
        { default: () => optionLabel(sessionStatusOptions, row.status, row.status) }
      )
    },
  },
  {
    title: '开始时间',
    key: 'started_at',
    width: 170,
    render: (row) => formatDateTime(row.started_at),
  },
  {
    title: '结束时间',
    key: 'ended_at',
    width: 170,
    render: (row) => (row.ended_at ? formatDateTime(row.ended_at) : '-'),
  },
  { title: '报告ID', key: 'report_id', width: 100, align: 'center' },
  {
    title: '操作',
    key: 'actions',
    width: 210,
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
            { default: () => '查看/编辑' }
          ),
          [[vPermission, 'post/api/v1/interview/update']]
        ),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete({ interview_id: row.id }) },
          {
            trigger: () =>
              withDirectives(
                h(NButton, { size: 'small', type: 'error' }, { default: () => '删除' }),
                [[vPermission, 'delete/api/v1/interview/delete']]
              ),
            default: () => '确认删除这个场次吗？',
          }
        ),
      ]
    },
  },
]

onMounted(async () => {
  await Promise.all([loadCandidates(), loadPositions(), loadJDs()])
  tableRef.value?.handleSearch()
})

async function loadCandidates() {
  const res = await api.getCandidateList({ page: 1, page_size: 999 })
  candidateOptions.value = (res.data || []).map((item) => ({
    label: `${item.user?.username || '候选人'} / ${item.target_position || '未设置岗位'}`,
    value: item.id,
  }))
}

async function loadPositions() {
  const res = await api.getPositionList({ page: 1, page_size: 999 })
  positionOptions.value = (res.data || []).map((item) => ({ label: item.title, value: item.id }))
}

async function loadJDs() {
  const res = await api.getJDList({ page: 1, page_size: 999 })
  jdOptions.value = (res.data || []).map((item) => ({
    label: `${item.position?.title || '岗位'} / V${item.version}`,
    value: item.id,
    positionId: item.position_id,
  }))
}

function openAdd() {
  detailTurns.value = []
  handleAdd()
  Object.assign(modalForm.value, { ...initForm })
}

async function openEdit(id) {
  const res = await api.getInterviewById({ interview_id: id })
  detailTurns.value = res.data?.turns || []
  handleEdit({
    ...res.data,
    jd_id: res.data?.jd?.id || res.data?.jd_id || null,
  })
}
</script>
<style scoped src="../shared.css"></style>
