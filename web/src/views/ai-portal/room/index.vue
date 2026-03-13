<template>
  <section v-if="session" class="portal-page">
    <div class="portal-hero">
      <div class="portal-row" style="align-items: flex-start; flex-wrap: wrap">
        <div style="max-width: 760px">
          <p class="portal-chip">面试练习房间 (科大讯飞 ASR 增强版)</p>
          <h1 class="portal-section-title" style="font-size: 38px; margin-top: 16px">
            {{ session.position?.title || '面试练习房间' }}
          </h1>
          <p class="portal-section-subtitle">
            现在按正常面试节奏进行：先听题、再回答、再进入下一题。语音识别由科大讯飞流式接口驱动，准确率更高。
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
          <n-button
            type="primary"
            :disabled="finished || askingNext"
            :loading="askingNext"
            @click="requestNextQuestion"
            >下一题</n-button
          >
          <n-button
            type="error"
            :disabled="finished || finishing"
            :loading="finishing"
            @click="finishInterview"
            >结束练习</n-button
          >
        </div>
      </div>
    </div>

    <div class="cols-3 portal-grid">
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
                  {{ getTurnSpeakerLabel(item) }}
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
              placeholder="可以直接把回答补在这里，或者对 ASR 结果进行微调。"
            />
            <n-button type="primary" style="margin-top: 12px" @click="submitManualText"
              >提交这段回答</n-button
            >
          </div>
          <div class="portal-panel">
            <p class="portal-kpi__label">练习控制</p>
            <div class="portal-list" style="margin-top: 10px">
              <n-button
                tertiary
                :loading="questionAudioLoading"
                :disabled="questionAudioLoading || !currentAiSpeechText"
                @click="playLatestAiSpeech()"
              >
                播放 AI 发言
              </n-button>
              <n-button
                tertiary
                :type="recognitionActive ? 'warning' : 'primary'"
                @click="toggleRecognition"
              >
                {{ recognitionActive ? '停止录音' : '开始回答' }}
              </n-button>
              <n-button
                tertiary
                :loading="askingNext"
                :disabled="askingNext || finished"
                @click="requestNextQuestion"
                >进入下一题</n-button
              >
              <n-button
                tertiary
                :loading="finishing"
                :disabled="finishing || finished"
                @click="finishInterview"
                >结束并查看报告</n-button
              >
            </div>
            <p class="portal-muted" style="margin-top: 14px">{{ questionAudioHint }}</p>
            <p class="portal-muted" style="margin-top: 14px">{{ recognitionHint }}</p>
          </div>
        </div>
      </div>

      <div class="portal-card">
        <h2 class="portal-section-title">摄像头预览与状态</h2>
        <div class="portal-panel" style="margin-top: 18px; overflow: hidden">
          <div
            v-if="cameraError"
            style="
              height: clamp(300px, 36vw, 420px);
              display: flex;
              align-items: center;
              justify-content: center;
              background: #f8f8f8;
            "
          >
            <p class="portal-muted">{{ cameraError }}</p>
          </div>
          <video
            v-else
            ref="videoRef"
            autoplay
            muted
            playsinline
            style="
              width: 100%;
              height: clamp(300px, 36vw, 420px);
              object-fit: cover;
              border-radius: 8px;
            "
          ></video>
        </div>

        <div style="margin-top: 24px">
          <h3 class="portal-kpi__label" style="margin-bottom: 12px">当前实时表现</h3>
          <div class="portal-grid cols-2">
            <div class="portal-panel" style="padding: 16px">
              <p class="portal-muted" style="font-size: 13px">关键词覆盖</p>
              <p class="portal-section-title" style="font-size: 24px; margin-top: 4px">
                {{ displayMetrics.keyword_coverage || 0 }}%
              </p>
            </div>
            <div class="portal-panel" style="padding: 16px">
              <p class="portal-muted" style="font-size: 13px">专业深度</p>
              <p class="portal-section-title" style="font-size: 24px; margin-top: 4px">
                {{ displayMetrics.professional_depth || 0 }}
              </p>
            </div>
            <div class="portal-panel" style="padding: 16px">
              <p class="portal-muted" style="font-size: 13px">逻辑清晰度</p>
              <p class="portal-section-title" style="font-size: 24px; margin-top: 4px">
                {{ displayMetrics.logic_clarity || 0 }}
              </p>
            </div>
            <div class="portal-panel" style="padding: 16px">
              <p class="portal-muted" style="font-size: 13px">录入总字数</p>
              <p class="portal-section-title" style="font-size: 24px; margin-top: 4px">
                {{ displayMetrics.total_words || 0 }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <n-modal v-model:show="finished" :mask-closable="false" style="width: 480px">
      <n-result
        status="success"
        title="练习已结束"
        description="系统正在生成结构化报告，你可以点击下方按钮查看最终评估结果。"
      >
        <template #footer>
          <n-button type="primary" @click="router.push('/ai-interview/reports')"
            >查看历史报告</n-button
          >
        </template>
      </n-result>
    </n-modal>

    <div v-if="!session" style="padding: 120px 0; text-align: center">
      <n-result
        status="404"
        title="未找到面试场次"
        description="请确认你是否是从岗位推荐列表进入的。只有点击'进入练习'才会带上完整的岗位信息。"
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
import { getToken } from '@/utils'

const router = useRouter()
const route = useRoute()
const videoRef = ref(null)
const timelineRef = ref(null)
const session = ref(null)
const timeline = ref([])
const metrics = ref({})
const manualText = ref('')
const interimTranscript = ref('')
const recognitionActive = ref(false)
const recognitionHint = ref('点击“开始回答”启动科大讯飞语音识别。')
const questionAudioLoading = ref(false)
const questionAudioHint = ref('AI 发言支持语音播报。')
const cameraError = ref('')
const finished = ref(false)
const askingNext = ref(false)
const finishing = ref(false)

let mediaStream = null
let segmentIndex = 1

let audioContext = null
let sourceNode = null
let processor = null
let silentGainNode = null
let asrSocket = null
let recognitionConnecting = false
let recognitionStopping = false
let stopWaitPromise = null
let stopWaitResolve = null
let stopWaitTimer = null
let connectTimeoutTimer = null
let questionAudio = null
let questionAudioRequestId = 0
const ASR_FRAME_BYTES = 1280
const questionAudioCache = new Map()

const latestAiTurn = computed(() => {
  const turns = [...timeline.value].reverse()
  return turns.find((item) => item.speaker === 'ai') || null
})

const latestAiTurnKey = computed(() => {
  const turn = latestAiTurn.value
  if (!turn) return ''
  return `${turn.id || ''}:${turn.created_at || ''}:${turn.source || ''}:${turn.content || ''}`
})

const currentAiSpeechText = computed(
  () =>
    latestAiTurn.value?.content ||
    session.value?.current_question?.question ||
    session.value?.opening ||
    ''
)

const displayMetrics = computed(() => {
  const hasInterim = Boolean(interimTranscript.value.trim())
  if (hasInterim || recognitionActive.value) {
    return buildPreviewMetrics()
  }
  return normalizeMetrics(metrics.value)
})

watch(
  latestAiTurnKey,
  (currentKey, previousKey) => {
    if (!currentKey || currentKey === previousKey) return
    void playLatestAiSpeech({ autoplay: true, suppressErrorMessage: true })
  },
  { flush: 'post' }
)

onMounted(() => {
  hydrateSession()
  void setupCamera()
  void nextTick(() => {
    scrollToBottom()
  })
})

onBeforeUnmount(() => {
  void stopRecognition({ submitTranscript: false, waitForFinalResult: false })
  stopQuestionAudioPlayback()
  revokeQuestionAudioCache()
  stopCamera()
})

function hydrateSession() {
  const raw = window.sessionStorage.getItem(`mock-session:${route.params.sessionId}`)
  if (!raw) return
  const data = JSON.parse(raw)
  session.value = data
  timeline.value = data.turns || []
  metrics.value = normalizeMetrics(data.latest_metrics || {})
  const userTurns = timeline.value.filter((item) => item.speaker === 'user')
  segmentIndex = (userTurns[userTurns.length - 1]?.segment_index || 0) + 1
}

function persistSession() {
  if (!session.value?.id) return
  window.sessionStorage.setItem(
    `mock-session:${session.value.id}`,
    JSON.stringify({
      ...session.value,
      turns: timeline.value,
      latest_metrics: normalizeMetrics(metrics.value),
    })
  )
}

async function setupCamera() {
  if (mediaStream) {
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
    }
    return
  }
  if (!navigator.mediaDevices?.getUserMedia) {
    cameraError.value = '当前浏览器不支持摄像头能力，你仍然可以继续进行文字版练习。'
    return
  }
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: {
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    })
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
    }
    cameraError.value = ''
  } catch {
    cameraError.value = '摄像头或麦克风权限被拒绝，请检查浏览器权限设置。'
  }
}

function stopCamera() {
  if (!mediaStream) return
  mediaStream.getTracks().forEach((track) => track.stop())
  mediaStream = null
}

function getTurnSpeakerLabel(item) {
  if (item?.speaker === 'user') {
    return '我的回答'
  }
  return item?.source === 'question' ? '提问' : 'AI 发言'
}

function normalizeMetrics(source = {}) {
  return {
    keyword_coverage: source.keyword_coverage ?? source.keyword_hit_rate ?? 0,
    professional_depth: source.professional_depth ?? source.completeness ?? 0,
    logic_clarity: source.logic_clarity ?? source.expression_pace ?? 0,
    total_words: source.total_words ?? source.answer_chars ?? 0,
  }
}

function extractTerms(text) {
  const matches =
    String(text || '')
      .toLowerCase()
      .match(/[a-z0-9+#.]{2,}|[\u4e00-\u9fff]{1,}/g) || []
  return new Set(matches.map((item) => item.trim()).filter(Boolean))
}

function buildPreviewMetrics() {
  const userContents = timeline.value
    .filter((item) => item.speaker === 'user')
    .map((item) => item.content || '')
  const interimText = interimTranscript.value.trim()
  if (interimText) {
    userContents.push(interimText)
  }
  const userText = userContents.join(' ').trim()
  if (!userText) {
    return normalizeMetrics(metrics.value)
  }

  const userTerms = extractTerms(userText)
  const mustHave = session.value?.jd?.must_have_tags || []
  const matched = mustHave.filter((item) => {
    const text = String(item || '').trim()
    if (!text) return false
    return userTerms.has(text.toLowerCase()) || userText.includes(text)
  })
  const totalLength = userText.length
  const answerCount = Math.max(userContents.length, 1)
  const keywordCoverage = mustHave.length
    ? Math.min(100, Math.round((matched.length / mustHave.length) * 100))
    : Math.min(95, 55 + Math.floor(totalLength / 15))

  return {
    keyword_coverage: keywordCoverage,
    professional_depth: Math.min(100, 35 + Math.floor(totalLength / 12)),
    logic_clarity: Math.min(100, 48 + answerCount * 9),
    total_words: totalLength,
  }
}

function buildApiUrl(path) {
  const baseApi = import.meta.env.VITE_BASE_API || '/api/v1'
  return `${baseApi}${path}`
}

function buildAsrSocketUrl() {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${protocol}://${window.location.host}/api/v1/mock_interview/ws/asr`
}

function stopQuestionAudioPlayback({ hint = '', cancelPending = true } = {}) {
  if (cancelPending) {
    questionAudioRequestId += 1
    questionAudioLoading.value = false
  }
  if (questionAudio) {
    questionAudio.pause()
    questionAudio.src = ''
    questionAudio = null
  }
  if (hint) {
    questionAudioHint.value = hint
  }
}

function revokeQuestionAudioCache() {
  for (const url of questionAudioCache.values()) {
    URL.revokeObjectURL(url)
  }
  questionAudioCache.clear()
}

async function fetchQuestionAudioUrl(text) {
  if (questionAudioCache.has(text)) {
    return questionAudioCache.get(text)
  }

  const headers = {
    'Content-Type': 'application/json',
  }
  const token = getToken()
  if (token) {
    headers.token = token
  }

  const response = await fetch(buildApiUrl('/mock_interview/tts'), {
    method: 'POST',
    headers,
    body: JSON.stringify({ text }),
  })

  if (!response.ok) {
    let message = 'AI 语音生成失败，请稍后重试。'
    const contentType = response.headers.get('content-type') || ''
    if (contentType.includes('application/json')) {
      const errorPayload = await response.json()
      message = errorPayload?.detail || errorPayload?.msg || message
    } else {
      const textMessage = await response.text()
      message = textMessage || message
    }
    throw new Error(message)
  }

  const audioBlob = await response.blob()
  const objectUrl = URL.createObjectURL(audioBlob)
  questionAudioCache.set(text, objectUrl)
  return objectUrl
}

function isAutoplayBlockedError(error) {
  return error?.name === 'NotAllowedError'
}

function isPlaybackAbortError(error) {
  return error?.name === 'AbortError'
}

async function playLatestAiSpeech({ autoplay = false, suppressErrorMessage = false } = {}) {
  const speechText = currentAiSpeechText.value.trim()
  if (!speechText) {
    questionAudioHint.value = '当前没有可播报的 AI 发言。'
    return
  }

  const requestId = questionAudioRequestId + 1
  questionAudioRequestId = requestId
  stopQuestionAudioPlayback({ cancelPending: false })
  questionAudioLoading.value = true
  questionAudioHint.value = '正在生成 AI 语音...'

  try {
    const audioUrl = await fetchQuestionAudioUrl(speechText)
    if (requestId !== questionAudioRequestId) {
      return
    }
    const audio = new Audio(audioUrl)
    audio.preload = 'auto'
    questionAudio = audio
    audio.onended = () => {
      if (questionAudio === audio) {
        questionAudio = null
      }
      questionAudioHint.value = 'AI 播报完成。'
    }
    audio.onerror = () => {
      if (questionAudio === audio) {
        questionAudio = null
      }
      questionAudioHint.value = 'AI 音频播放失败，请重试。'
    }
    await audio.play()
    if (requestId !== questionAudioRequestId || questionAudio !== audio) {
      audio.pause()
      return
    }
    questionAudioHint.value = '正在播放 AI 语音...'
  } catch (error) {
    const message = error?.message || 'AI 语音生成失败，请稍后重试。'
    const autoplayBlocked = autoplay && isAutoplayBlockedError(error)
    if (isPlaybackAbortError(error)) {
      return
    }
    stopQuestionAudioPlayback({ cancelPending: false })
    questionAudioHint.value = autoplayBlocked
      ? '浏览器阻止了自动播报，可点击“播放 AI 发言”重试。'
      : message
    if (!suppressErrorMessage && !autoplayBlocked) {
      window.$message?.error(message)
    }
  } finally {
    if (requestId === questionAudioRequestId) {
      questionAudioLoading.value = false
    }
  }
}

function cleanupAudioPipeline() {
  if (processor) {
    processor.onaudioprocess = null
    processor.disconnect()
    processor = null
  }
  if (sourceNode) {
    sourceNode.disconnect()
    sourceNode = null
  }
  if (silentGainNode) {
    silentGainNode.disconnect()
    silentGainNode = null
  }
  if (audioContext) {
    const context = audioContext
    audioContext = null
    void context.close().catch(() => {})
  }
}

function cleanupSocket(close = false) {
  if (!asrSocket) return
  const socket = asrSocket
  asrSocket = null
  if (connectTimeoutTimer) {
    window.clearTimeout(connectTimeoutTimer)
    connectTimeoutTimer = null
  }
  socket.onopen = null
  socket.onmessage = null
  socket.onerror = null
  socket.onclose = null
  if (
    close &&
    (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)
  ) {
    socket.close()
  }
}

function resolveStopWait() {
  if (stopWaitTimer) {
    window.clearTimeout(stopWaitTimer)
    stopWaitTimer = null
  }
  if (stopWaitResolve) {
    const resolve = stopWaitResolve
    stopWaitResolve = null
    stopWaitPromise = null
    resolve()
    return
  }
  stopWaitPromise = null
}

function createStopWaitPromise(timeoutMs = 5000) {
  if (stopWaitPromise) return stopWaitPromise
  stopWaitPromise = new Promise((resolve) => {
    stopWaitResolve = resolve
    stopWaitTimer = window.setTimeout(() => {
      resolveStopWait()
    }, timeoutMs)
  })
  return stopWaitPromise
}

function downsampleTo16k(buffer, inputSampleRate) {
  if (!buffer?.length) return new Int16Array()
  if (inputSampleRate === 16000) {
    return convertFloat32ToInt16(buffer)
  }
  const sampleRateRatio = inputSampleRate / 16000
  const outputLength = Math.max(1, Math.round(buffer.length / sampleRateRatio))
  const output = new Int16Array(outputLength)
  let offsetResult = 0
  let offsetBuffer = 0

  while (offsetResult < outputLength) {
    const nextOffsetBuffer = Math.min(
      buffer.length,
      Math.round((offsetResult + 1) * sampleRateRatio)
    )
    let sum = 0
    let count = 0
    for (let index = offsetBuffer; index < nextOffsetBuffer; index += 1) {
      sum += buffer[index]
      count += 1
    }
    const sample = count ? sum / count : buffer[offsetBuffer] || 0
    const clamped = Math.max(-1, Math.min(1, sample))
    output[offsetResult] = clamped < 0 ? clamped * 0x8000 : clamped * 0x7fff
    offsetResult += 1
    offsetBuffer = nextOffsetBuffer
  }

  return output
}

function convertFloat32ToInt16(buffer) {
  const output = new Int16Array(buffer.length)
  for (let index = 0; index < buffer.length; index += 1) {
    const sample = Math.max(-1, Math.min(1, buffer[index]))
    output[index] = sample < 0 ? sample * 0x8000 : sample * 0x7fff
  }
  return output
}

function sendPcmFrames(pcmData) {
  if (!pcmData?.byteLength || asrSocket?.readyState !== WebSocket.OPEN) return
  const pcmBytes = new Uint8Array(pcmData.buffer.slice(0))
  for (let offset = 0; offset < pcmBytes.byteLength; offset += ASR_FRAME_BYTES) {
    const chunk = pcmBytes.slice(offset, offset + ASR_FRAME_BYTES)
    if (chunk.byteLength) {
      asrSocket.send(chunk.buffer)
    }
  }
}

async function startRecognition() {
  if (recognitionActive.value || recognitionConnecting || recognitionStopping) return
  if (!mediaStream) {
    await setupCamera()
  }
  if (!mediaStream) return

  stopQuestionAudioPlayback({ hint: 'AI 播报已暂停。' })
  cleanupAudioPipeline()
  cleanupSocket(true)
  interimTranscript.value = ''
  recognitionConnecting = true
  recognitionHint.value = '正在连接讯飞语音识别...'

  const socket = new WebSocket(buildAsrSocketUrl())
  socket.binaryType = 'arraybuffer'
  asrSocket = socket
  connectTimeoutTimer = window.setTimeout(() => {
    if (asrSocket !== socket || socket.readyState === WebSocket.OPEN) return
    recognitionConnecting = false
    recognitionHint.value = '连接讯飞语音识别超时，请确认后端服务和前端代理是否已启动。'
    window.$message?.error('连接讯飞语音识别超时，请确认后端服务和前端代理是否已启动。')
    cleanupSocket(true)
  }, 8000)

  socket.onopen = async () => {
    if (asrSocket !== socket) return
    if (connectTimeoutTimer) {
      window.clearTimeout(connectTimeoutTimer)
      connectTimeoutTimer = null
    }
    recognitionConnecting = false
    recognitionActive.value = true
    recognitionHint.value = '正在识别您的语音...'
    try {
      await startAudioProcessing()
    } catch {
      recognitionHint.value = '麦克风初始化失败，请检查浏览器权限。'
      window.$message?.error('麦克风初始化失败，请检查浏览器权限或刷新页面重试。')
      await stopRecognition({ submitTranscript: false, waitForFinalResult: false })
    }
  }

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'asr_result') {
      interimTranscript.value = data.text || ''
      recognitionHint.value = data.is_final
        ? '识别完成，正在整理最终文本...'
        : '正在识别您的语音...'
      return
    }
    if (data.type === 'asr_completed') {
      interimTranscript.value = data.text || interimTranscript.value
      recognitionHint.value = interimTranscript.value
        ? '识别完成，正在提交回答...'
        : '未识别到有效语音。'
      resolveStopWait()
      return
    }
    if (data.type === 'asr_error') {
      recognitionHint.value = data.message || '语音识别失败，请稍后重试。'
      window.$message?.error(recognitionHint.value)
      resolveStopWait()
    }
  }

  socket.onerror = () => {
    if (connectTimeoutTimer) {
      window.clearTimeout(connectTimeoutTimer)
      connectTimeoutTimer = null
    }
    recognitionConnecting = false
    if (!recognitionStopping) {
      recognitionHint.value = '语音识别连接失败，请稍后重试。'
      window.$message?.error('语音识别连接失败，请稍后重试。')
    }
  }

  socket.onclose = () => {
    if (connectTimeoutTimer) {
      window.clearTimeout(connectTimeoutTimer)
      connectTimeoutTimer = null
    }
    if (asrSocket === socket) {
      asrSocket = null
    }
    recognitionConnecting = false
    recognitionActive.value = false
    cleanupAudioPipeline()
    resolveStopWait()
    if (!recognitionStopping && !finished.value) {
      recognitionHint.value = '语音识别已停止。'
    }
  }
}

async function startAudioProcessing() {
  audioContext = new (window.AudioContext || window.webkitAudioContext)()
  await audioContext.resume()
  const inputSampleRate = audioContext.sampleRate
  sourceNode = audioContext.createMediaStreamSource(mediaStream)
  processor = audioContext.createScriptProcessor(2048, 1, 1)
  silentGainNode = audioContext.createGain()
  silentGainNode.gain.value = 0

  processor.onaudioprocess = (event) => {
    if (!recognitionActive.value || recognitionStopping || asrSocket?.readyState !== WebSocket.OPEN)
      return
    const pcmData = downsampleTo16k(event.inputBuffer.getChannelData(0), inputSampleRate)
    if (!pcmData.length) return
    sendPcmFrames(pcmData)
  }

  sourceNode.connect(processor)
  processor.connect(silentGainNode)
  silentGainNode.connect(audioContext.destination)
}

async function flushInterimTranscript() {
  const content = interimTranscript.value.trim()
  if (!content) return
  await submitSegment(content)
  interimTranscript.value = ''
  recognitionHint.value = '本段回答已提交。'
}

async function stopRecognition({ submitTranscript = true, waitForFinalResult = true } = {}) {
  if (recognitionStopping) {
    if (stopWaitPromise) {
      await stopWaitPromise
    }
    if (submitTranscript) {
      await flushInterimTranscript()
    }
    return
  }

  const socket = asrSocket
  const hasActiveResources = Boolean(socket || processor || audioContext || sourceNode)
  cleanupAudioPipeline()
  recognitionConnecting = false
  recognitionActive.value = false

  if (!hasActiveResources) {
    if (submitTranscript) {
      await flushInterimTranscript()
    }
    if (!finished.value && !submitTranscript) {
      recognitionHint.value = '语音识别已停止。'
    }
    return
  }

  recognitionStopping = true
  try {
    if (socket && waitForFinalResult && socket.readyState === WebSocket.OPEN) {
      recognitionHint.value = '正在结束录音并等待最终转写...'
      const waiting = createStopWaitPromise()
      socket.send(JSON.stringify({ type: 'end_stream' }))
      await waiting
    }
  } finally {
    cleanupSocket(true)
    recognitionStopping = false
  }

  if (submitTranscript) {
    await flushInterimTranscript()
  } else if (!finished.value) {
    recognitionHint.value = '语音识别已停止。'
  }
}

async function toggleRecognition() {
  try {
    if (recognitionActive.value || recognitionConnecting) {
      await stopRecognition()
    } else {
      await startRecognition()
    }
  } catch {
    window.$message?.error('语音识别处理失败，请稍后重试。')
  }
}

async function submitSegment(content) {
  if (!content || finished.value || !session.value?.id) return
  const res = await api.submitMockInterviewSegment({
    session_id: session.value.id,
    content,
    segment_index: segmentIndex,
  })
  timeline.value.push(res.data.turn)
  metrics.value = normalizeMetrics(res.data.metrics || metrics.value)
  segmentIndex += 1
  manualText.value = ''
  persistSession()
  await nextTick()
  scrollToBottom()
}

async function submitManualText() {
  await submitSegment(manualText.value.trim())
}

async function requestNextQuestion() {
  if (finished.value || askingNext.value) return
  try {
    await stopRecognition()
  } catch {
    window.$message?.error('当前回答还没有成功提交，请稍后再试。')
    return
  }

  askingNext.value = true
  try {
    const res = await api.nextMockInterviewQuestion({ session_id: session.value.id })
    if (res.data.completed) {
      window.$message?.info('题目已经完成，可以结束练习并查看报告了。')
      return
    }
    session.value = {
      ...session.value,
      ...(res.data.session || {}),
      current_round: res.data.round_no,
      current_question: {
        question: res.data.question,
        focus: res.data.focus,
        stage: res.data.stage,
      },
    }
    timeline.value.push({
      id: `ai-${Date.now()}`,
      created_at: new Date().toISOString(),
      speaker: 'ai',
      content: res.data.question,
      source: 'question',
    })
    persistSession()
    await nextTick()
    scrollToBottom()
  } finally {
    askingNext.value = false
  }
}

async function finishInterview() {
  if (finished.value || finishing.value) return
  try {
    await stopRecognition()
  } catch {
    window.$message?.error('最后一段回答提交失败，请先重试后再结束练习。')
    return
  }

  finishing.value = true
  try {
    const res = await api.finishMockInterview({ session_id: session.value.id })
    finished.value = true
    window.sessionStorage.removeItem(`mock-session:${session.value.id}`)
    if (res.data?.message) {
      window.$message?.success(res.data.message)
    }
    router.push('/ai-interview/reports')
  } finally {
    finishing.value = false
  }
}

function scrollToBottom() {
  if (!timelineRef.value) return
  timelineRef.value.scrollTop = timelineRef.value.scrollHeight
}
</script>
