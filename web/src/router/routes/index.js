import i18n from '~/i18n'
const { t } = i18n.global

const Layout = () => import('@/layout/index.vue')
const PortalLayout = () => import('@/views/ai-portal/layout.vue')

export const basicRoutes = [
  {
    path: '/',
    redirect: '/workbench',
    meta: { order: 0 },
  },
  {
    name: t('views.workbench.label_workbench'),
    path: '/workbench',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/workbench/index.vue'),
        name: `${t('views.workbench.label_workbench')}Default`,
        meta: {
          title: t('views.workbench.label_workbench'),
          icon: 'icon-park-outline:workbench',
          affix: true,
        },
      },
    ],
    meta: { order: 1 },
  },
  {
    name: 'AIPortal',
    path: '/ai-interview',
    component: PortalLayout,
    redirect: '/ai-interview/dashboard',
    children: [
      {
        path: 'dashboard',
        component: () => import('@/views/ai-portal/dashboard/index.vue'),
        name: 'AIInterviewDashboard',
        meta: {
          title: '面试练习台',
          icon: 'hugeicons:artificial-intelligence-04',
          affix: true,
        },
      },
      {
        path: 'resume',
        component: () => import('@/views/ai-portal/resume/index.vue'),
        name: 'AIInterviewResume',
        isHidden: true,
        meta: {
          title: '简历中心',
          activeMenu: 'AIInterviewDashboard',
        },
      },
      {
        path: 'positions',
        component: () => import('@/views/ai-portal/positions/index.vue'),
        name: 'AIInterviewPositions',
        isHidden: true,
        meta: {
          title: '岗位推荐',
          activeMenu: 'AIInterviewDashboard',
        },
      },
      {
        path: 'positions/:id',
        component: () => import('@/views/ai-portal/position-detail/index.vue'),
        name: 'AIInterviewPositionDetail',
        isHidden: true,
        meta: {
          title: '岗位详情',
          activeMenu: 'AIInterviewDashboard',
        },
      },
      {
        path: 'room/:sessionId',
        component: () => import('@/views/ai-portal/room/index.vue'),
        name: 'AIInterviewRoom',
        isHidden: true,
        meta: {
          title: '面试房间',
          activeMenu: 'AIInterviewDashboard',
        },
      },
      {
        path: 'reports',
        component: () => import('@/views/ai-portal/reports/index.vue'),
        name: 'AIInterviewReports',
        isHidden: true,
        meta: {
          title: '报告中心',
          activeMenu: 'AIInterviewDashboard',
        },
      },
      {
        path: 'reports/:reportId',
        component: () => import('@/views/ai-portal/report-detail/index.vue'),
        name: 'AIInterviewReportDetail',
        isHidden: true,
        meta: {
          title: '报告详情',
          activeMenu: 'AIInterviewDashboard',
        },
      },
      {
        path: 'reports/session/:sessionId',
        component: () => import('@/views/ai-portal/report-detail/index.vue'),
        name: 'AIInterviewReportSessionDetail',
        isHidden: true,
        meta: {
          title: '报告详情',
          activeMenu: 'AIInterviewDashboard',
        },
      },
    ],
    meta: {
      title: '面试练习台',
      icon: 'hugeicons:artificial-intelligence-04',
      order: 2,
    },
  },
  {
    name: t('views.profile.label_profile'),
    path: '/profile',
    component: Layout,
    isHidden: true,
    children: [
      {
        path: '',
        component: () => import('@/views/profile/index.vue'),
        name: `${t('views.profile.label_profile')}Default`,
        meta: {
          title: t('views.profile.label_profile'),
          icon: 'user',
          affix: true,
        },
      },
    ],
    meta: { order: 99 },
  },
  {
    name: 'ErrorPage',
    path: '/error-page',
    component: Layout,
    redirect: '/error-page/404',
    meta: {
      title: t('views.errors.label_error'),
      icon: 'mdi:alert-circle-outline',
      order: 99,
    },
    children: [
      {
        name: 'ERROR-401',
        path: '401',
        component: () => import('@/views/error-page/401.vue'),
        meta: {
          title: '401',
          icon: 'material-symbols:authenticator',
        },
      },
      {
        name: 'ERROR-403',
        path: '403',
        component: () => import('@/views/error-page/403.vue'),
        meta: {
          title: '403',
          icon: 'solar:forbidden-circle-line-duotone',
        },
      },
      {
        name: 'ERROR-404',
        path: '404',
        component: () => import('@/views/error-page/404.vue'),
        meta: {
          title: '404',
          icon: 'tabler:error-404',
        },
      },
      {
        name: 'ERROR-500',
        path: '500',
        component: () => import('@/views/error-page/500.vue'),
        meta: {
          title: '500',
          icon: 'clarity:rack-server-outline-alerted',
        },
      },
    ],
  },
  {
    name: '403',
    path: '/403',
    component: () => import('@/views/error-page/403.vue'),
    isHidden: true,
  },
  {
    name: '404',
    path: '/404',
    component: () => import('@/views/error-page/404.vue'),
    isHidden: true,
  },
  {
    name: 'Login',
    path: '/login',
    component: () => import('@/views/login/index.vue'),
    isHidden: true,
    meta: {
      title: '系统登录',
    },
  },
]

export const NOT_FOUND_ROUTE = {
  name: 'NotFound',
  path: '/:pathMatch(.*)*',
  redirect: '/404',
  isHidden: true,
}

export const EMPTY_ROUTE = {
  name: 'Empty',
  path: '/:pathMatch(.*)*',
  component: null,
}

const modules = import.meta.glob('@/views/**/route.js', { eager: true })
const asyncRoutes = []
Object.keys(modules).forEach((key) => {
  asyncRoutes.push(modules[key].default)
})

const vueModules = import.meta.glob('@/views/**/index.vue')

export { asyncRoutes, vueModules }
