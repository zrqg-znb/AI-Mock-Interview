export const candidateStatusOptions = [
  { label: '开放求职', value: 'open' },
  { label: '在职观望', value: 'passive' },
  { label: '冲刺面试', value: 'interviewing' },
  { label: '已归档', value: 'archived' },
]

export const positionStatusOptions = [
  { label: '上线中', value: 'online' },
  { label: '草稿', value: 'draft' },
  { label: '暂停', value: 'paused' },
]

export const difficultyOptions = [
  { label: '基础', value: 'easy' },
  { label: '进阶', value: 'middle' },
  { label: '高阶', value: 'hard' },
]

export const sessionStatusOptions = [
  { label: '待开始', value: 'pending' },
  { label: '进行中', value: 'running' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' },
]

export const archiveStatusOptions = [
  { label: '已归档', value: 'archived' },
  { label: '草稿', value: 'draft' },
  { label: '已导出', value: 'exported' },
]

export function joinTextList(value) {
  if (!value) return ''
  if (Array.isArray(value)) return value.join('，')
  return value
}

export function splitTextList(value) {
  if (!value) return []
  if (Array.isArray(value)) return value
  return value
    .split(/[,\n，；;、]+/)
    .map((item) => item.trim())
    .filter(Boolean)
}

export function optionLabel(options, value, fallback = '-') {
  return options.find((item) => item.value === value)?.label || fallback
}

export function scoreTone(score = 0) {
  if (score >= 85) return 'success'
  if (score >= 70) return 'warning'
  return 'error'
}

export function scoreGradient(score = 0) {
  if (score >= 85) return 'linear-gradient(135deg, #f3e7d8 0%, #e3ccb5 100%)'
  if (score >= 70) return 'linear-gradient(135deg, #f7eddc 0%, #ead4bc 100%)'
  return 'linear-gradient(135deg, #f6e6e0 0%, #e7c8bf 100%)'
}

export function compactText(value = '', max = 120) {
  if (!value) return '-'
  if (value.length <= max) return value
  return `${value.slice(0, max)}...`
}
