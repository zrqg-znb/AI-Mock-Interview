<template>
  <CommonPage title="岗位 JD 管理">
    <template #header>
      <div class="interview-admin-hero">
        <p class="interview-admin-hero__eyebrow">岗位要求</p>
        <div class="interview-admin-hero__row">
          <div>
            <h2 class="interview-admin-hero__title">岗位 JD 管理</h2>
            <p class="interview-admin-hero__desc">
              为同一岗位维护多版 JD、技能要求和评分维度，方便控制不同练习场景的口径。
            </p>
            <div class="interview-admin-hero__meta">
              <span class="interview-admin-hero__meta-item">多版本管理</span>
              <span class="interview-admin-hero__meta-item">技能要求</span>
              <span class="interview-admin-hero__meta-item">启停切换</span>
            </div>
          </div>
          <div class="interview-admin-hero__actions">
            <n-button
              v-permission="'post/api/v1/jd/create'"
              secondary
              type="primary"
              @click="openAdd"
            >
              新增 JD
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
      :get-data="api.getJDList"
      :scroll-x="1380"
    >
      <template #queryBar>
        <QueryBarItem label="岗位">
          <n-select
            v-model:value="queryItems.position_id"
            clearable
            filterable
            :options="positionOptions"
            placeholder="全部岗位"
          />
        </QueryBarItem>
        <QueryBarItem label="关键词">
          <n-input v-model:value="queryItems.keyword" clearable placeholder="JD 内容关键词" />
        </QueryBarItem>
        <QueryBarItem label="启用状态">
          <n-select v-model:value="queryItems.is_active" clearable :options="activeOptions" />
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
          <n-form-item-gi label="所属岗位" path="position_id">
            <n-select
              v-model:value="modalForm.position_id"
              filterable
              :options="positionOptions"
              placeholder="请选择岗位"
            />
          </n-form-item-gi>
          <n-form-item-gi label="版本号" path="version">
            <n-input-number
              v-model:value="modalForm.version"
              :min="1"
              :max="99"
              style="width: 100%"
            />
          </n-form-item-gi>
          <n-form-item-gi label="必备技能" path="must_have_tags" span="2">
            <n-input
              v-model:value="modalForm.must_have_tags"
              placeholder="多个标签用中文逗号分隔"
            />
          </n-form-item-gi>
          <n-form-item-gi label="加分技能" path="bonus_tags" span="2">
            <n-input v-model:value="modalForm.bonus_tags" placeholder="多个标签用中文逗号分隔" />
          </n-form-item-gi>
          <n-form-item-gi label="评分维度" path="scoring_dimensions" span="2">
            <n-input
              v-model:value="modalForm.scoring_dimensions"
              placeholder="例如：专业能力，表达沟通，岗位匹配，稳定度"
            />
          </n-form-item-gi>
          <n-form-item-gi label="补充提示" path="prompt_hint" span="2">
            <n-input
              v-model:value="modalForm.prompt_hint"
              type="textarea"
              :autosize="{ minRows: 3, maxRows: 4 }"
            />
          </n-form-item-gi>
          <n-form-item-gi label="JD 正文" path="jd_text" span="2">
            <n-input
              v-model:value="modalForm.jd_text"
              type="textarea"
              :autosize="{ minRows: 10, maxRows: 14 }"
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
import { compactText, joinTextList } from '@/views/interview-shared/utils'

defineOptions({ name: 'InterviewJDAdmin' })

const tableRef = ref(null)
const vPermission = resolveDirective('permission')
const positionOptions = ref([])
const activeOptions = [
  { label: '启用', value: true },
  { label: '停用', value: false },
]
const queryItems = ref({ position_id: null, keyword: '', is_active: null })
const initForm = {
  position_id: null,
  version: 1,
  jd_text: '',
  must_have_tags: '',
  bonus_tags: '',
  scoring_dimensions: '专业能力，表达沟通，岗位匹配，稳定度',
  prompt_hint: '',
  is_active: true,
}
const rules = {
  position_id: { required: true, type: 'number', message: '请选择所属岗位', trigger: 'change' },
  jd_text: { required: true, message: '请输入 JD 正文', trigger: 'blur' },
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
  name: '岗位JD',
  initForm,
  doCreate: api.createJD,
  doUpdate: api.updateJD,
  doDelete: api.deleteJD,
  refresh: () => tableRef.value?.handleSearch(),
})

const columns = [
  {
    title: '所属岗位',
    key: 'position.title',
    width: 180,
    render(row) {
      return row.position?.title || '-'
    },
  },
  { title: '版本', key: 'version', width: 90, align: 'center' },
  {
    title: '必备技能',
    key: 'must_have_tags',
    width: 260,
    render(row) {
      return h(
        'div',
        { style: 'display:flex;flex-wrap:wrap;gap:6px' },
        (row.must_have_tags || [])
          .slice(0, 5)
          .map((tag) => h(NTag, { bordered: false, type: 'success' }, { default: () => tag }))
      )
    },
  },
  {
    title: '评分维度',
    key: 'scoring_dimensions',
    width: 220,
    render(row) {
      return joinTextList(row.scoring_dimensions)
    },
  },
  {
    title: 'JD 摘要',
    key: 'jd_text',
    width: 320,
    ellipsis: { tooltip: true },
    render(row) {
      return compactText(row.jd_text, 80)
    },
  },
  {
    title: '启用',
    key: 'is_active',
    width: 90,
    render(row) {
      return h(
        NTag,
        { bordered: false, type: row.is_active ? 'success' : 'warning' },
        { default: () => (row.is_active ? '启用' : '停用') }
      )
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
              style: 'margin-right:8px;',
              onClick: () => openEdit(row),
            },
            { default: () => '编辑' }
          ),
          [[vPermission, 'post/api/v1/jd/update']]
        ),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete({ jd_id: row.id }) },
          {
            trigger: () =>
              withDirectives(
                h(NButton, { size: 'small', type: 'error' }, { default: () => '删除' }),
                [[vPermission, 'delete/api/v1/jd/delete']]
              ),
            default: () => '确认删除这个 JD 吗？',
          }
        ),
      ]
    },
  },
]

onMounted(async () => {
  await loadPositionOptions()
  tableRef.value?.handleSearch()
})

async function loadPositionOptions() {
  const res = await api.getPositionList({ page: 1, page_size: 999 })
  positionOptions.value = (res.data || []).map((item) => ({ label: item.title, value: item.id }))
}

function openAdd() {
  handleAdd()
  Object.assign(modalForm.value, { ...initForm })
}

function openEdit(row) {
  handleEdit({
    ...row,
    must_have_tags: joinTextList(row.must_have_tags),
    bonus_tags: joinTextList(row.bonus_tags),
    scoring_dimensions: joinTextList(row.scoring_dimensions),
  })
}
</script>
<style scoped src="../shared.css"></style>
