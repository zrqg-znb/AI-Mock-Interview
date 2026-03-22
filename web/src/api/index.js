import { request } from '@/utils'

export default {
  login: (data) => request.post('/base/access_token', data, { noNeedToken: true }),
  getUserInfo: () => request.get('/base/userinfo'),
  getUserMenu: () => request.get('/base/usermenu'),
  getUserApi: () => request.get('/base/userapi'),
  // profile
  updatePassword: (data = {}) => request.post('/base/update_password', data),
  // users
  getUserList: (params = {}) => request.get('/user/list', { params }),
  getUserById: (params = {}) => request.get('/user/get', { params }),
  createUser: (data = {}) => request.post('/user/create', data),
  updateUser: (data = {}) => request.post('/user/update', data),
  deleteUser: (params = {}) => request.delete('/user/delete', { params }),
  resetPassword: (data = {}) => request.post('/user/reset_password', data),
  // role
  getRoleList: (params = {}) => request.get('/role/list', { params }),
  createRole: (data = {}) => request.post('/role/create', data),
  updateRole: (data = {}) => request.post('/role/update', data),
  deleteRole: (params = {}) => request.delete('/role/delete', { params }),
  updateRoleAuthorized: (data = {}) => request.post('/role/authorized', data),
  getRoleAuthorized: (params = {}) => request.get('/role/authorized', { params }),
  // menus
  getMenus: (params = {}) => request.get('/menu/list', { params }),
  createMenu: (data = {}) => request.post('/menu/create', data),
  updateMenu: (data = {}) => request.post('/menu/update', data),
  deleteMenu: (params = {}) => request.delete('/menu/delete', { params }),
  // apis
  getApis: (params = {}) => request.get('/api/list', { params }),
  createApi: (data = {}) => request.post('/api/create', data),
  updateApi: (data = {}) => request.post('/api/update', data),
  deleteApi: (params = {}) => request.delete('/api/delete', { params }),
  refreshApi: (data = {}) => request.post('/api/refresh', data),
  // depts
  getDepts: (params = {}) => request.get('/dept/list', { params }),
  createDept: (data = {}) => request.post('/dept/create', data),
  updateDept: (data = {}) => request.post('/dept/update', data),
  deleteDept: (params = {}) => request.delete('/dept/delete', { params }),
  // auditlog
  getAuditLogList: (params = {}) => request.get('/auditlog/list', { params }),
  // ai runtime admin
  getAIRuntimeStatus: (params = {}) => request.get('/ai_runtime/status', { params }),
  runAIRuntimeCheck: (data = {}) => request.post('/ai_runtime/test', data),
  // candidate admin
  getCandidateList: (params = {}) => request.get('/candidate/list', { params }),
  getCandidateById: (params = {}) => request.get('/candidate/get', { params }),
  createCandidate: (data = {}) => request.post('/candidate/create', data),
  updateCandidate: (data = {}) => request.post('/candidate/update', data),
  deleteCandidate: (params = {}) => request.delete('/candidate/delete', { params }),
  // position admin
  getPositionList: (params = {}) => request.get('/position/list', { params }),
  getPositionById: (params = {}) => request.get('/position/get', { params }),
  createPosition: (data = {}) => request.post('/position/create', data),
  updatePosition: (data = {}) => request.post('/position/update', data),
  deletePosition: (params = {}) => request.delete('/position/delete', { params }),
  // jd admin
  getJDList: (params = {}) => request.get('/jd/list', { params }),
  getJDById: (params = {}) => request.get('/jd/get', { params }),
  createJD: (data = {}) => request.post('/jd/create', data),
  updateJD: (data = {}) => request.post('/jd/update', data),
  deleteJD: (params = {}) => request.delete('/jd/delete', { params }),
  // interview admin
  getInterviewList: (params = {}) => request.get('/interview/list', { params }),
  getInterviewById: (params = {}) => request.get('/interview/get', { params }),
  createInterview: (data = {}) => request.post('/interview/create', data),
  updateInterview: (data = {}) => request.post('/interview/update', data),
  deleteInterview: (params = {}) => request.delete('/interview/delete', { params }),
  // report admin
  getReportList: (params = {}) => request.get('/report/list', { params }),
  getReportById: (params = {}) => request.get('/report/get', { params }),
  createReport: (data = {}) => request.post('/report/create', data),
  updateReport: (data = {}) => request.post('/report/update', data),
  deleteReport: (params = {}) => request.delete('/report/delete', { params }),
  // candidate portal
  getCandidatePortalProfile: () => request.get('/candidate_portal/profile'),
  saveCandidatePortalProfile: (data = {}) => request.post('/candidate_portal/profile', data),
  getCandidatePortalDashboard: () => request.get('/candidate_portal/dashboard'),
  getCandidatePortalReports: (params = {}) => request.get('/candidate_portal/reports', { params }),
  // recommendation and mock interview
  getJobRecommendList: (params = {}) => request.get('/job_recommend/list', { params }),
  getJobRecommendDetail: (params = {}) => request.get('/job_recommend/detail', { params }),
  startMockInterview: (data = {}) =>
    request.post('/mock_interview/start', data, { timeout: 45000 }),
  submitMockInterviewSegment: (data = {}) => request.post('/mock_interview/submit_segment', data),
  submitExpressionFrame: (data = {}) => request.post('/mock_interview/submit_expression_frame', data),
  nextMockInterviewQuestion: (data = {}) =>
    request.post('/mock_interview/next_question', data, { timeout: 30000 }),
  finishMockInterview: (data = {}) =>
    request.post('/mock_interview/finish', data, { timeout: 45000 }),
  getMockInterviewReport: (params = {}) => request.get('/mock_interview/report', { params }),
}
