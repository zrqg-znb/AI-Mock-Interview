<template>
  <CommonPage title="面试岗位管理">
    <template #header>
      <div class="interview-admin-hero">
        <p class="interview-admin-hero__eyebrow">岗位库</p>
        <div class="interview-admin-hero__row">
          <div>
            <h2 class="interview-admin-hero__title">面试岗位管理</h2>
            <p class="interview-admin-hero__desc">
              维护候选人端展示的岗位卡片、部门信息和推荐状态，保证前后台口径一致。
            </p>
            <div class="interview-admin-hero__meta">
              <span class="interview-admin-hero__meta-item">岗位信息维护</span>
              <span class="interview-admin-hero__meta-item">推荐展示</span>
              <span class="interview-admin-hero__meta-item">难度分层</span>
            </div>
          </div>
          <div class="interview-admin-hero__actions">
            <n-button
              v-permission="'post/api/v1/position/create'"
              secondary
              type="primary"
              @click="openAdd"
            >
              新增岗位
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
      :get-data="api.getPositionList"
      :scroll-x="1280"
    >
      <template #queryBar>
        <QueryBarItem label="关键词">
          <n-input v-model:value="queryItems.keyword" clearable placeholder="岗位 / 方向 / 部门" />
        </QueryBarItem>
        <QueryBarItem label="状态">
          <n-select v-model:value="queryItems.status" clearable :options="positionStatusOptions" />
        </QueryBarItem>
        <QueryBarItem label="难度">
          <n-select v-model:value="queryItems.difficulty" clearable :options="difficultyOptions" />
        </QueryBarItem>
      </template>
    </CrudTable>

    <CrudModal
      :visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      width="860px"
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
          <n-form-item-gi label="岗位名称" path="title">
            <n-input v-model:value="modalForm.title" />
          </n-form-item-gi>
          <n-form-item-gi label="岗位类别" path="category">
            <n-input v-model:value="modalForm.category" placeholder="例如：产品 / 研发 / 运营" />
          </n-form-item-gi>
          <n-form-item-gi label="职级" path="level">
            <n-input v-model:value="modalForm.level" placeholder="例如：P6 / Leader" />
          </n-form-item-gi>
          <n-form-item-gi label="所属部门" path="department">
            <n-input v-model:value="modalForm.department" />
          </n-form-item-gi>
          <n-form-item-gi label="面试难度" path="difficulty">
            <n-select v-model:value="modalForm.difficulty" :options="difficultyOptions" />
          </n-form-item-gi>
          <n-form-item-gi label="岗位状态" path="status">
            <n-select v-model:value="modalForm.status" :options="positionStatusOptions" />
          </n-form-item-gi>
          <n-form-item-gi label="封面链接" path="cover_image" span="2">
            <n-input
              v-model:value="modalForm.cover_image"
              placeholder="可留空，前端会自动使用渐变背景"
            />
          </n-form-item-gi>
          <n-form-item-gi label="岗位标签" path="tags" span="2">
            <n-input v-model:value="modalForm.tags" placeholder="多个标签用中文逗号分隔" />
          </n-form-item-gi>
          <n-form-item-gi label="亮点卖点" path="highlight" span="2">
            <n-input
              v-model:value="modalForm.highlight"
              placeholder="例如：高增长业务、跨团队协作、汇报链路清晰"
            />
          </n-form-item-gi>
          <n-form-item-gi label="岗位简介" path="summary" span="2">
            <n-input
              v-model:value="modalForm.summary"
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
import {
  difficultyOptions,
  joinTextList,
  optionLabel,
  positionStatusOptions,
} from '@/views/interview-shared/utils'

defineOptions({ name: '面试岗位管理' })

const tableRef = ref(null)
const vPermission = resolveDirective('permission')
const queryItems = ref({ keyword: '', status: null, difficulty: null })
const initForm = {
  title: '',
  category: '',
  level: '',
  department: '',
  tags: '',
  difficulty: 'middle',
  cover_image: '',
  summary: '',
  highlight: '',
  is_recommended: true,
  status: 'online',
}
const rules = {
  title: { required: true, message: '请输入岗位名称', trigger: 'blur' },
  summary: { required: true, message: '请输入岗位简介', trigger: 'blur' },
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
  name: '岗位',
  initForm,
  doCreate: api.createPosition,
  doUpdate: api.updatePosition,
  doDelete: api.deletePosition,
  refresh: () => tableRef.value?.handleSearch(),
})

const columns = [
  { title: '岗位名称', key: 'title', width: 180 },
  { title: '类别', key: 'category', width: 120 },
  { title: '职级', key: 'level', width: 100 },
  { title: '部门', key: 'department', width: 120 },
  {
    title: '标签',
    key: 'tags',
    width: 240,
    render(row) {
      return h(
        'div',
        { style: 'display:flex;flex-wrap:wrap;gap:6px' },
        (row.tags || [])
          .slice(0, 5)
          .map((tag) => h(NTag, { bordered: false, type: 'info' }, { default: () => tag }))
      )
    },
  },
  {
    title: '难度',
    key: 'difficulty',
    width: 100,
    render(row) {
      return optionLabel(difficultyOptions, row.difficulty)
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 110,
    render(row) {
      return h(
        NTag,
        { bordered: false, type: row.status === 'online' ? 'success' : 'warning' },
        { default: () => optionLabel(positionStatusOptions, row.status) }
      )
    },
  },
  { title: 'JD 数量', key: 'jd_count', width: 90, align: 'center' },
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
          [[vPermission, 'post/api/v1/position/update']]
        ),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete({ position_id: row.id }) },
          {
            trigger: () =>
              withDirectives(
                h(NButton, { size: 'small', type: 'error' }, { default: () => '删除' }),
                [[vPermission, 'delete/api/v1/position/delete']]
              ),
            default: () => '确认删除这个岗位吗？',
          }
        ),
      ]
    },
  },
]

onMounted(() => {
  tableRef.value?.handleSearch()
})

function openAdd() {
  handleAdd()
  Object.assign(modalForm.value, { ...initForm })
}

function openEdit(row) {
  handleEdit({
    ...row,
    tags: joinTextList(row.tags),
    highlight: joinTextList(row.highlight),
  })
}
</script>
<style scoped src="../shared.css"></style>
