<template>
  <section class="resume-page portal-page">
    <div class="portal-hero">
      <div class="portal-row" style="align-items: flex-start; flex-wrap: wrap">
        <div>
          <p class="portal-chip">简历资料</p>
          <h1 class="portal-section-title" style="font-size: 34px; margin-top: 16px">简历中心</h1>
          <p class="portal-section-subtitle" style="max-width: 760px">
            把经历、技能和求职方向写清楚，系统才能给出更靠谱的岗位推荐、练习问题和面试报告。
          </p>
        </div>
        <div class="portal-score-ring">
          <div style="text-align: center">
            <strong>{{ completeness }}</strong>
            <p class="portal-muted" style="margin-top: 6px">准备情况</p>
          </div>
        </div>
      </div>
    </div>

    <div class="cols-2 portal-grid">
      <div class="portal-card">
        <div class="portal-row" style="align-items: flex-start">
          <div>
            <h2 class="portal-section-title">基本信息与求职方向</h2>
            <p class="portal-section-subtitle">
              先把基础资料写完整，后面的推荐、提问重点和报告总结都会围绕这些内容展开。
            </p>
          </div>
          <n-button type="primary" :loading="saving" @click="saveProfile">保存档案</n-button>
        </div>

        <n-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-placement="top"
          style="margin-top: 20px"
        >
          <div class="portal-grid cols-2">
            <n-form-item label="头像 URL" path="avatar">
              <n-input v-model:value="form.avatar" placeholder="https://example.com/avatar.png" />
            </n-form-item>
            <n-form-item label="一句话抬头" path="headline">
              <n-input v-model:value="form.headline" placeholder="例如：偏业务增长的数据产品经理" />
            </n-form-item>
            <n-form-item label="目标岗位" path="target_position">
              <n-input v-model:value="form.target_position" placeholder="例如：数据产品经理" />
            </n-form-item>
            <n-form-item label="目标城市" path="target_city">
              <n-input v-model:value="form.target_city" placeholder="例如：上海 / 杭州 / Remote" />
            </n-form-item>
            <n-form-item label="工作年限" path="work_years">
              <n-input-number
                v-model:value="form.work_years"
                :min="0"
                :max="20"
                style="width: 100%"
              />
            </n-form-item>
            <n-form-item label="求职状态" path="job_status">
              <n-select v-model:value="form.job_status" :options="candidateStatusOptions" />
            </n-form-item>
            <n-form-item label="教育信息" path="education">
              <n-input
                v-model:value="form.education"
                placeholder="例如：985 本科 / 海外硕士 / 自学转行"
              />
            </n-form-item>
            <n-form-item label="技能标签" path="skill_tags">
              <n-input
                v-model:value="form.skill_tags"
                placeholder="用逗号分隔，如：SQL，用户增长，跨团队协作"
              />
            </n-form-item>
          </div>

          <n-form-item label="个人优势" path="strengths">
            <n-input
              v-model:value="form.strengths"
              type="textarea"
              :autosize="{ minRows: 3, maxRows: 5 }"
              placeholder="写下最希望面试官快速记住的优势，例如：项目推进、业务拆解、沟通协调。"
            />
          </n-form-item>

          <n-form-item label="简历正文" path="resume_text">
            <n-input
              v-model:value="form.resume_text"
              type="textarea"
              :autosize="{ minRows: 12, maxRows: 16 }"
              placeholder="粘贴简历正文、项目经历、职责结果和关键指标，按真实表达填写即可。"
            />
          </n-form-item>
        </n-form>
      </div>

      <div class="portal-card">
        <h2 class="portal-section-title">填写情况</h2>
        <p class="portal-section-subtitle">
          这些分数只是帮助你检查信息是否充分，不影响正常保存，也方便你快速补齐缺口。
        </p>

        <div class="portal-grid cols-2" style="margin-top: 18px">
          <div class="portal-kpi">
            <p class="portal-kpi__label">技能信息完整度</p>
            <p class="portal-kpi__value">
              {{ Math.min(96, 30 + splitTextList(form.skill_tags).length * 12) }}
            </p>
            <n-progress
              type="line"
              :percentage="Math.min(96, 30 + splitTextList(form.skill_tags).length * 12)"
              :show-indicator="false"
              color="#9f7b64"
            />
          </div>
          <div class="portal-kpi">
            <p class="portal-kpi__label">项目细节充足度</p>
            <p class="portal-kpi__value">
              {{ projectDetailScore }}
            </p>
            <n-progress
              type="line"
              :percentage="Math.min(95, 18 + (form.resume_text?.length || 0) / 20)"
              :show-indicator="false"
              color="#c19477"
            />
          </div>
          <div class="portal-kpi">
            <p class="portal-kpi__label">个人亮点表达</p>
            <p class="portal-kpi__value">{{ form.strengths ? 82 : 46 }}</p>
            <n-progress
              type="line"
              :percentage="form.strengths ? 82 : 46"
              :show-indicator="false"
              color="#7b8d78"
            />
          </div>
          <div class="portal-kpi">
            <p class="portal-kpi__label">目标岗位清晰度</p>
            <p class="portal-kpi__value">{{ form.target_position ? 88 : 35 }}</p>
            <n-progress
              type="line"
              :percentage="form.target_position ? 88 : 35"
              :show-indicator="false"
              color="#a4846c"
            />
          </div>
        </div>

        <div class="portal-panel" style="margin-top: 18px">
          <div class="portal-row" style="align-items: flex-start">
            <div>
              <p class="portal-kpi__label">这些信息会影响哪些环节？</p>
              <ul class="portal-muted" style="padding-left: 18px; line-height: 1.9">
                <li>技能标签会影响岗位匹配结果和后续提问方向。</li>
                <li>简历正文会作为练习题目和报告总结的主要参考。</li>
                <li>目标岗位与工作年限会影响练习难度和推荐顺序。</li>
              </ul>
            </div>
            <n-avatar
              round
              :size="76"
              :src="form.avatar || 'https://avatars.githubusercontent.com/u/54677442?v=4'"
            />
          </div>
        </div>

        <div class="portal-panel" style="margin-top: 18px">
          <p class="portal-kpi__label">当前技能标签</p>
          <div class="portal-tag-cloud" style="margin-top: 12px">
            <span v-for="tag in splitTextList(form.skill_tags)" :key="tag" class="portal-chip">{{
              tag
            }}</span>
            <span v-if="!splitTextList(form.skill_tags).length" class="portal-muted"
              >还没有填写技能标签</span
            >
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import api from '@/api'
import { candidateStatusOptions, splitTextList } from '@/views/interview-shared/utils'

const formRef = ref(null)
const saving = ref(false)
const form = ref({
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
})

const rules = {
  target_position: { required: true, message: '请填写目标岗位', trigger: 'blur' },
  resume_text: { required: true, message: '请填写简历正文', trigger: 'blur' },
}

const projectDetailScore = computed(() =>
  Math.floor(Math.min(95, 18 + (form.value.resume_text?.length || 0) / 20))
)

const completeness = computed(() => {
  const fields = [
    form.value.headline,
    form.value.resume_text,
    form.value.skill_tags,
    form.value.target_position,
    form.value.target_city,
    form.value.education,
    form.value.strengths,
  ]
  const filled = fields.filter(Boolean).length
  return Math.min(98, filled * 14 + Math.min(14, form.value.work_years * 2))
})

onMounted(loadProfile)

async function loadProfile() {
  const res = await api.getCandidatePortalProfile()
  const profile = res.data
  if (!profile) return
  form.value = {
    avatar: profile.avatar || '',
    headline: profile.headline || '',
    resume_text: profile.resume_text || '',
    skill_tags: Array.isArray(profile.skill_tags)
      ? profile.skill_tags.join('，')
      : profile.skill_tags || '',
    work_years: profile.work_years || 0,
    education: profile.education || '',
    target_position: profile.target_position || '',
    target_city: profile.target_city || '',
    job_status: profile.job_status || 'open',
    strengths: profile.strengths || '',
    is_active: profile.is_active !== false,
  }
}

function saveProfile() {
  formRef.value?.validate(async (errors) => {
    if (errors) return
    saving.value = true
    try {
      await api.saveCandidatePortalProfile(form.value)
      $message.success('候选人档案已更新')
    } finally {
      saving.value = false
    }
  })
}
</script>

<style scoped>
.resume-page .portal-hero {
  padding: 24px;
}

.resume-page .portal-chip {
  background: #f5ede4;
  color: #986949;
}

.resume-page .portal-score-ring {
  width: 98px;
  height: 98px;
  background: radial-gradient(circle at 30% 30%, #fff, #f7efe7);
  box-shadow: inset 0 0 0 6px rgba(255, 255, 255, 0.7);
}

.resume-page .portal-kpi__value {
  font-size: 28px;
}

.resume-page :deep(.n-progress) {
  margin-top: 14px;
}

@media (max-width: 900px) {
  .resume-page .portal-hero {
    padding: 20px;
  }
}
</style>
