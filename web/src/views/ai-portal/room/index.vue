<template>
  <section v-if="session" class="portal-page">
    <div class="portal-hero">
      <div class="portal-row" style="align-items: flex-start; flex-wrap: wrap">
        <div style="max-width: 760px">
          <p class="portal-chip">面试练习房间</p>
          <h1 class="portal-section-title" style="font-size: 38px; margin-top: 16px">
            {{ session.position?.title || '模拟面试房间' }}
          </h1>
          <p class="portal-section-subtitle">
            现在按照正常面试节奏进行：先听题、再回答、再进入下一题。语音识别只是帮你记录内容，重点还是让你像平时面试一样把话说明白。
          </p>
          <div class="portal-tag-cloud" style="margin-top: 16px">
            <span class="portal-chip"
              >当前轮次 {{ session.current_round }}/{{ session.total_rounds }}</span
            >
            <span class="portal-chip">岗位匹配 {{ session.position_match?.score || 0 }} 分</span>
            <span class="portal-chip">{{ session.ai_persona?.style || '追问节奏平稳' }}</span>
          </div>
        </div>

        <div class="portal-actions">
          <n-button tertiary @click="router.push('/ai-interview/positions')">返回岗位列表</n-button>
          <n-button type="primary" :disabled="finished" @click="requestNextQuestion"
            >下一题</n-button
          >
          <n-button type="error" :disabled="finished" @click="finishInterview">结束练习</n-button>
        </div>
      </div>
    </div>

    <div class="portal-grid cols-3">
      <div class="portal-card" style="grid-column: span 2">
        <div class="portal-row" style="align-items: flex-start">
          <div>
            <h2 class="portal-section-title">问答记录</h2>
            <p class="portal-section-subtitle">提问和回答都会按时间保留，方便结束后回看。</p>
          </div>
          <n-button quaternary @click="scrollToBottom">滚动到底部</n-button>
        </div>

        <div
          ref="timelineRef"
          class="portal-panel"
          style="margin-top: 18px; min-height: 480px; max-height: 620px; overflow: auto"
        >
          <div
            v-for="item in timeline"
            :key="`${item.created_at}-${item.id || item.segment_index}`"
            style="margin-bottom: 16px"
          >
            <div
              class="portal-row"
              :style="{ justifyContent: item.speaker === 'user' ? 'flex-end' : 'flex-start' }"
            >
              <div
                :style="{
                  maxWidth: '85%',
                  padding: '16px 18px',
                  borderRadius:
                    item.speaker === 'user' ? '18px 18px 6px 18px' : '18px 18px 18px 6px',
                  background: item.speaker === 'user' ? '#f3e4d7' : '#ffffff',
                  border: item.speaker === 'user' ? '1px solid #e0cbb9' : '1px solid #eadfd4',
                }"
              >
                <p class="portal-kpi__label" style="margin-bottom: 8px">
                  {{ item.speaker === 'user' ? '我的回答' : '提问' }}
                </p>
                <div style="line-height: 1.8; white-space: pre-wrap">{{ item.content }}</div>
              </div>
            </div>
          </div>

          <div v-if="interimTranscript" class="portal-row" style="justify-content: flex-end">
            <div
              style="
                max-width: 85%;
                padding: 16px 18px;
                border-radius: 18px 18px 6px 18px;
                border: 1px dashed #d5bca8;
                background: #faf5ef;
              "
            >
              <p class="portal-kpi__label" style="margin-bottom: 8px">正在识别</p>
              <div class="portal-muted">{{ interimTranscript }}</div>
            </div>
          </div>
        </div>

        <div class="portal-grid cols-2" style="margin-top: 18px">
          <div class="portal-panel">
            <p class="portal-kpi__label">手动补录</p>
            <n-input
              v-model:value="manualText"
              type="textarea"
              :autosize="{ minRows: 4, maxRows: 6 }"
              placeholder="如果浏览器不支持语音识别，可以直接把回答补在这里。"
            />
            <n-button type="primary" style="margin-top: 12px" @click="submitManualText"
              >提交这段回答</n-button
            >
          </div>
          <div class="portal-panel">
            <p class="portal-kpi__label">房间控制</p>
            <div class="portal-list" style="margin-top: 10px">
              <n-button
                tertiary
                :type="recognitionActive ? 'warning' : 'primary'"
                @click="toggleRecognition"
              >
                {{ recognitionActive ? '暂停语音识别' : '开启语音识别' }}
              </n-button>
              <n-button tertiary @click="requestNextQuestion">进入下一题</n-button>
              <n-button tertiary @click="finishInterview">结束并查看报告</n-button>
            </div>
            <p class="portal-muted" style="margin-top: 14px">{{ recognitionHint }}</p>
          </div>
        </div>
      </div>

      <div class="portal-card">
        <h2 class="portal-section-title">视频与状态</h2>
        <div class="portal-panel" style="margin-top: 18px; overflow: hidden">
          <video
            ref="videoRef"
            autoplay
            muted
            playsinline
            style="width: 100%; min-height: 240px; border-radius: 18px; background: #f0e8df"
          ></video>
          <n-alert
            v-if="cameraError"
            type="warning"
            style="margin-top: 12px; border-radius: 18px"
            >{{ cameraError }}</n-alert
          >
        </div>

        <div class="portal-grid cols-2" style="margin-top: 18px">
          <div class="portal-kpi">
            <p class="portal-kpi__label">关键词覆盖</p>
            <p class="portal-kpi__value">{{ metrics.keyword_hit_rate || 0 }}</p>
            <n-progress
              type="line"
              :percentage="metrics.keyword_hit_rate || 0"
              :show-indicator="false"
              status="success"
            />
          </div>
          <div class="portal-kpi">
            <p class="portal-kpi__label">回答完整度</p>
            <p class="portal-kpi__value">{{ metrics.completeness || 0 }}</p>
            <n-progress
              type="line"
              :percentage="metrics.completeness || 0"
              :show-indicator="false"
              status="warning"
            />
          </div>
          <div class="portal-kpi">
            <p class="portal-kpi__label">表达节奏</p>
            <p class="portal-kpi__value">{{ metrics.expression_pace || 0 }}</p>
            <n-progress
              type="line"
              :percentage="metrics.expression_pace || 0"
              :show-indicator="false"
              status="success"
            />
          </div>
          <div class="portal-kpi">
            <p class="portal-kpi__label">稳定度</p>
            <p class="portal-kpi__value">{{ metrics.communication_stability || 0 }}</p>
            <n-progress
              type="line"
              :percentage="metrics.communication_stability || 0"
              :show-indicator="false"
              status="success"
            />
          </div>
        </div>

        <div class="portal-panel" style="margin-top: 18px">
          <p class="portal-kpi__label">当前题目</p>
          <p style="line-height: 1.9; margin-top: 10px">
            {{ currentQuestion || '正在等待下一题...' }}
          </p>
        </div>

        <div class="portal-panel" style="margin-top: 18px">
          <p class="portal-kpi__label">已覆盖关键词</p>
          <div class="portal-tag-cloud" style="margin-top: 12px">
            <span v-for="tag in metrics.matched_keywords || []" :key="tag" class="portal-chip">{{
              tag
            }}</span>
            <span v-if="!metrics.matched_keywords?.length" class="portal-muted"
              >回答再多一些，这里会逐步出现关键词。</span
            >
          </div>
        </div>
      </div>
    </div>
  </section>

  <section v-else class="portal-page">
    <div class="portal-card">
      <n-result
        status="warning"
        title="没有找到这场练习"
        description="请从岗位详情或推荐列表进入，这样系统才能带上完整的练习上下文。"
      >
        <template #footer>
          <n-button type="primary" @click="router.push('/ai-interview/positions')"
            >返回岗位推荐</n-button
          >
        </template>
      </n-result>
    </div>
  </section>
</template>

<script setup>
import api from '@/api'

const router = useRouter()
const route = useRoute()
const videoRef = ref(null)
const timelineRef = ref(null)
const session = ref(null)
const timeline = ref([])
const metrics = ref({})
const currentQuestion = ref('')
const manualText = ref('')
const interimTranscript = ref('')
const recognitionActive = ref(false)
const recognitionHint = ref('如果浏览器支持语音识别，系统会自动尝试开启；不支持时也可以手动补录。')
const cameraError = ref('')
const finished = ref(false)

let mediaStream = null
let recognition = null
let segmentIndex = 1

onMounted(async () => {
  hydrateSession()
  await setupCamera()
  setupRecognition()
  await nextTick()
  scrollToBottom()
})

onBeforeUnmount(() => {
  stopCamera()
  stopRecognition()
})

function hydrateSession() {
  const raw = window.sessionStorage.getItem(`mock-session:${route.params.sessionId}`)
  if (!raw) return
  const data = JSON.parse(raw)
  session.value = data
  timeline.value = data.turns || []
  metrics.value = data.latest_metrics || {}
  currentQuestion.value =
    data.current_question?.question || data.turns?.slice(-1)?.[0]?.content || ''
  const userTurns = timeline.value.filter((item) => item.speaker === 'user')
  segmentIndex = (userTurns[userTurns.length - 1]?.segment_index || 0) + 1
}

async function setupCamera() {
  if (!navigator.mediaDevices?.getUserMedia) {
    cameraError.value = '当前浏览器不支持摄像头能力，你仍然可以继续进行文本版练习。'
    return
  }
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
    }
  } catch (error) {
    cameraError.value = '摄像头权限被拒绝或设备不可用，但不影响继续完成这场练习。'
  }
}

function stopCamera() {
  if (!mediaStream) return
  mediaStream.getTracks().forEach((track) => track.stop())
  mediaStream = null
}

function setupRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    recognitionHint.value = '当前浏览器不支持语音识别，请使用手动补录方式继续。'
    return
  }

  recognition = new SpeechRecognition()
  recognition.lang = 'zh-CN'
  recognition.continuous = true
  recognition.interimResults = true

  recognition.onresult = (event) => {
    let interim = ''
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript.trim()
      if (!transcript) continue
      if (event.results[i].isFinal) {
        interimTranscript.value = ''
        submitSegment(transcript)
      } else {
        interim += transcript
      }
    }
    interimTranscript.value = interim
  }

  recognition.onend = () => {
    if (recognitionActive.value && !finished.value) {
      try {
        recognition.start()
      } catch (error) {
        recognitionActive.value = false
      }
    }
  }

  toggleRecognition(true)
}

function toggleRecognition(forceStart = false) {
  if (!recognition) return
  if (recognitionActive.value && !forceStart) {
    stopRecognition()
    return
  }
  try {
    recognition.start()
    recognitionActive.value = true
    recognitionHint.value = '语音识别已开启，系统会把稳定识别到的句子按段记录下来。'
  } catch (error) {
    recognitionHint.value = '浏览器阻止了自动开启语音识别，请点击按钮重试或使用手动补录。'
  }
}

function stopRecognition() {
  if (!recognition) return
  recognitionActive.value = false
  try {
    recognition.stop()
  } catch (error) {
    console.log(error)
  }
}

async function submitSegment(content) {
  if (!content || finished.value) return
  const res = await api.submitMockInterviewSegment({
    session_id: session.value.id,
    content,
    segment_index: segmentIndex,
  })
  timeline.value.push(res.data.turn)
  metrics.value = res.data.metrics || metrics.value
  segmentIndex += 1
  manualText.value = ''
  await nextTick()
  scrollToBottom()
}

async function submitManualText() {
  await submitSegment(manualText.value.trim())
}

async function requestNextQuestion() {
  if (finished.value) return
  const res = await api.nextMockInterviewQuestion({ session_id: session.value.id })
  if (res.data.completed) {
    $message.info('题目已经完成，可以结束练习并生成报告了。')
    return
  }
  currentQuestion.value = res.data.question
  session.value = {
    ...session.value,
    ...(res.data.session || {}),
    current_round: res.data.round_no,
  }
  timeline.value.push({
    id: `ai-${Date.now()}`,
    created_at: new Date().toISOString(),
    speaker: 'ai',
    content: res.data.question,
  })
  window.sessionStorage.setItem(
    `mock-session:${session.value.id}`,
    JSON.stringify({ ...session.value, turns: timeline.value })
  )
  await nextTick()
  scrollToBottom()
}

async function finishInterview() {
  if (finished.value) return
  const res = await api.finishMockInterview({ session_id: session.value.id })
  finished.value = true
  stopRecognition()
  const report = res.data.report
  if (report?.id) {
    router.push(`/ai-interview/reports/${report.id}`)
  }
}

function scrollToBottom() {
  if (!timelineRef.value) return
  timelineRef.value.scrollTop = timelineRef.value.scrollHeight
}
</script>
