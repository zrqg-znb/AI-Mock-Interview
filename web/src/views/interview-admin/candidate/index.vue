<template>
  <CommonPage title="候选人管理">
    <template #header>
      <div class="interview-admin-hero">
        <p class="interview-admin-hero__eyebrow">候选人档案</p>
        <div class="interview-admin-hero__row">
          <div>
            <h2 class="interview-admin-hero__title">候选人管理</h2>
            <p class="interview-admin-hero__desc">
              维护账号关联、求职方向和简历内容，供推荐、练习与报告环节统一使用。
            </p>
            <div class="interview-admin-hero__meta">
              <span class="interview-admin-hero__meta-item">统一账号关联</span>
              <span class="interview-admin-hero__meta-item">简历文本维护</span>
              <span class="interview-admin-hero__meta-item">求职状态筛选</span>
            </div>
          </div>
          <div class="interview-admin-hero__actions">
            <n-button
              v-permission="'post/api/v1/candidate/create'"
              secondary
              type="primary"
              @click="openAdd"
            >
              新增候选人档案
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
      :get-data="api.getCandidateList"
      :scroll-x="1280"
    >
      <template #queryBar>
        <QueryBarItem label="用户搜索">
          <n-input v-model:value="queryItems.username" clearable placeholder="用户名 / 邮箱" />
        </QueryBarItem>
        <QueryBarItem label="目标岗位">
          <n-input
            v-model:value="queryItems.target_position"
            clearable
            placeholder="例如：数据产品经理"
          />
        </QueryBarItem>
        <QueryBarItem label="求职状态">
          <n-select
            v-model:value="queryItems.job_status"
            clearable
            :options="candidateStatusOptions"
            placeholder="全部状态"
          />
        </QueryBarItem>
      </template>
    </CrudTable>

    <CrudModal
      :visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      width="900px"
      @update:visible="(v) => (modalVisible = v)"
      @save="handleSave"
    >
      <n-form
        ref="modalFormRef"
        :model="modalForm"
        :rules="rules"
        label-placement="left"
        label-width="92"
      >
        <n-grid cols="2" x-gap="16">
          <n-form-item-gi label="关联用户" path="user_id">
            <n-select
              v-model:value="modalForm.user_id"
              :options="userOptions"
              clearable
              filterable
              placeholder="先在系统用户管理里创建账号"
            />
          </n-form-item-gi>
          <n-form-item-gi label="一句话抬头" path="headline">
            <n-input
              v-model:value="modalForm.headline"
              placeholder="例如：偏业务增长的数据产品经理"
            />
          </n-form-item-gi>
          <n-form-item-gi label="目标岗位" path="target_position">
            <n-input
              v-model:value="modalForm.target_position"
              placeholder="例如：用户增长产品经理"
            />
          </n-form-item-gi>
          <n-form-item-gi label="目标城市" path="target_city">
            <n-input v-model:value="modalForm.target_city" placeholder="例如：上海 / Remote" />
          </n-form-item-gi>
          <n-form-item-gi label="工作年限" path="work_years">
            <n-input-number
              v-model:value="modalForm.work_years"
              :min="0"
              :max="20"
              style="width: 100%"
            />
          </n-form-item-gi>
          <n-form-item-gi label="求职状态" path="job_status">
            <n-select v-model:value="modalForm.job_status" :options="candidateStatusOptions" />
          </n-form-item-gi>
          <n-form-item-gi label="教育信息" path="education">
            <n-input
              v-model:value="modalForm.education"
              placeholder="例如：硕士 / 985 / 海外背景"
            />
          </n-form-item-gi>
          <n-form-item-gi label="头像链接" path="avatar">
            <n-input v-model:value="modalForm.avatar" placeholder="https://..." />
          </n-form-item-gi>
          <n-form-item-gi label="技能标签" path="skill_tags" span="2">
            <n-input v-model:value="modalForm.skill_tags" placeholder="多个标签用中文逗号分隔" />
          </n-form-item-gi>
          <n-form-item-gi label="个人优势" path="strengths" span="2">
            <n-input
              v-model:value="modalForm.strengths"
              type="textarea"
              :autosize="{ minRows: 3, maxRows: 4 }"
            />
          </n-form-item-gi>
          <n-form-item-gi label="简历正文" path="resume_text" span="2">
            <n-input
              v-model:value="modalForm.resume_text"
              type="textarea"
              :autosize="{ minRows: 8, maxRows: 12 }"
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
import { candidateStatusOptions, joinTextList } from '@/views/interview-shared/utils'

defineOptions({ name: '候选人管理' })

const tableRef = ref(null)
const vPermission = resolveDirective('permission')
const queryItems = ref({ username: '', target_position: '', job_status: null })
const userOptions = ref([])

const initForm = {
  user_id: null,
  avatar: '',
  headline: '',
  resume_text: '',
  skill_tags: '',
  work_years: 0,
  education: '',
  target_position: '',
  target_city: '',
  job_status: 'open',
  strengths: '',
  is_active: true,
}

const rules = {
  user_id: { required: true, type: 'number', message: '请选择关联用户', trigger: 'change' },
  target_position: { required: true, message: '请输入目标岗位', trigger: 'blur' },
  resume_text: { required: true, message: '请输入简历正文', trigger: 'blur' },
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
  name: '候选人档案',
  initForm,
  doCreate: api.createCandidate,
  doUpdate: api.updateCandidate,
  doDelete: api.deleteCandidate,
  refresh: () => tableRef.value?.handleSearch(),
})

const columns = [
  {
    title: '用户账号',
    key: 'user.username',
    width: 140,
    render(row) {
      return h('div', [
        h('div', { style: 'font-weight:600' }, row.user?.username || '-'),
        h('div', { style: 'font-size:12px;opacity:.65' }, row.user?.email || '-'),
      ])
    },
  },
  { title: '职业抬头', key: 'headline', width: 180, ellipsis: { tooltip: true } },
  { title: '目标岗位', key: 'target_position', width: 150 },
  { title: '城市', key: 'target_city', width: 100 },
  { title: '年限', key: 'work_years', width: 80, align: 'center' },
  {
    title: '技能标签',
    key: 'skill_tags',
    width: 260,
    render(row) {
      return h(
        'div',
        { style: 'display:flex;flex-wrap:wrap;gap:6px' },
        (row.skill_tags || [])
          .slice(0, 5)
          .map((tag) => h(NTag, { bordered: false, type: 'info' }, { default: () => tag }))
      )
    },
  },
  {
    title: '状态',
    key: 'job_status',
    width: 120,
    render(row) {
      const label =
        candidateStatusOptions.find((item) => item.value === row.job_status)?.label ||
        row.job_status
      return h(NTag, { bordered: false, type: 'success' }, { default: () => label })
    },
  },
  {
    title: '统计',
    key: 'stats',
    width: 140,
    render(row) {
      return h('div', [
        h('div', `场次 ${row.interview_count || 0}`),
        h('div', { style: 'opacity:.65' }, `报告 ${row.report_count || 0}`),
      ])
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    fixed: 'right',
    render(row) {
      return [
        withDirectives(
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              style: 'margin-right: 8px;',
              onClick: () => openEdit(row),
            },
            { default: () => '编辑' }
          ),
          [[vPermission, 'post/api/v1/candidate/update']]
        ),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete({ candidate_id: row.id }) },
          {
            trigger: () =>
              withDirectives(
                h(NButton, { size: 'small', type: 'error' }, { default: () => '删除' }),
                [[vPermission, 'delete/api/v1/candidate/delete']]
              ),
            default: () => '确认删除这个候选人档案吗？',
          }
        ),
      ]
    },
  },
]

onMounted(async () => {
  await loadUserOptions()
  tableRef.value?.handleSearch()
})

async function loadUserOptions() {
  const res = await api.getUserList({ page: 1, page_size: 999 })
  userOptions.value = (res.data || []).map((item) => ({
    label: `${item.username} / ${item.email}`,
    value: item.id,
  }))
}

function openAdd() {
  handleAdd()
  Object.assign(modalForm.value, { ...initForm })
}

function openEdit(row) {
  handleEdit({
    ...row,
    skill_tags: joinTextList(row.skill_tags),
  })
}
</script>
<style scoped src="../shared.css"></style>
