import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'
// import { compile } from 'vue'
// import { meta } from //'eslint-plugin-vue'Uncaught TypeError: __require.resolve is not a function at node_modules/eslint-plugin-vue/lib/configs/base.js (base.js:7:19) 



const routes = [
    // 公共路由
    {
        path: '/',
        redirect: '/index',
        meta: { requiresAuth: false }
    },
    {
        path: '/index',
        name: 'index',
        component: () => import('@/views/Index.vue'),
        meta: { 
            title: '首页',
            requiresAuth: false 
        }
    },
    // 认证路由
    {
        path: '/login',
        name: 'login',
        component: () => import('@/views/auth/Login.vue'),
        meta: {
            title: '登录',
            guestOnly: true, // 只允许未登录用户访问
            transition: 'fade'
        }
    },
    {
        path: '/register',
        name: 'register',
        component: () => import('@/views/auth/Register.vue'),
        meta: {
            title: '注册',
            guestOnly: true // 只允许未登录用户访问
        }
    },
    {
        path: '/logout',
        name: 'logout',
        component: () => import('@/views/auth/Logout.vue'),
        meta: {
            title: '登出',
            requiresAuth: true // 只允许已登录
        }
    },
    // 用户路由
    {
        path: '/dashboard',
        name: 'dashboard',
        component: () => import('@/views/Drones/Dashboard.vue'),
        meta: {
            title: '无人机系统',
            requiresAuth: true,
            permissions: ['user']
        },
        children: [
            {
                path: 'drone/create',
                name: 'drone-create',  // 添加名称
                component: () => import('@/views/Drones/DroneForm.vue'),
                meta: {
                    title: '创建无人机'
                }
            },
            {
                path: 'drone/:id',
                name: 'drone-detail',  // 添加名称
                component: () => import('@/views/Drones/DroneDetail.vue'),
                props: true,
                meta: {
                    title: '无人机详情'
                }
            },
            {
                path: 'drone/:id/edit',
                name: 'drone-edit',    // 添加名称
                component: () => import('@/views/Drones/DroneForm.vue'),
                props: route => ({ droneId: route.params.id }),
                meta: {
                    title: '编辑无人机'
                }
            },
            {
                path: 'mission/:id',
                name: 'mission-detail',  // 添加名称
                component: () => import('@/views/Drones/MissionDetail.vue'),
                props: route => ({ missionId: route.params.id }),
                meta: {
                    title: '任务详情'
                }
            },
            {
                path: 'target/:id',
                name: 'target-detail',  // 添加名称
                component: () => import('@/views/Drones/TargetDetail.vue'),
                props: route => ({ targetId: route.params.id }),
                meta: {
                    title: '目标详情'
                }
            }
        ]
    },
    // 个人中心
    {
        path: '/profile',
        name: 'profile',
        component: () => import('@/views/Profile.vue'),
        meta: {
            title: '个人中心',
            requiresAuth: true // 只允许已登录用户访问
        }
    },
    // 404处理
    {
        path: '/:pathMatch(.*)*',
        name: 'not-found',
        component: () => import('@/views/NotFound.vue'),
        meta: { title: '404 Not Found - 页面未找到' }
    }
]

const router = createRouter({
    // 为了让路由使用 history 模式，需要使用 createWebHistory
    history: createWebHistory(),
    routes,

    // 滚动行为
    scrollBehavior(to, from, savedPosition) {
        return savedPosition || { top: 0 }
    }
})

// 导航守卫 - 权限控制 (修复无限重定向问题)
router.beforeEach((to, from, next) => {
    // 动态设置标题
    document.title = to.meta.title || '1'

    // 安全获取用户信息
    let user = null
    try {
        user = JSON.parse(localStorage.getItem('user'))
    } catch (error) {
        console.error('用户信息解析失败:', error)
        localStorage.removeItem('user')
    }

    // 获取路由元信息（支持嵌套路由）
    const isAuthenticated = store.getters['auth/isAuthenticated']
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
    const guestOnly = to.matched.some(record => record.meta.guestOnly)
    const permissions = to.matched.reduce((acc, record) => 
        record.meta.permissions || acc, 
        []
    )

    console.log(isAuthenticated)

    // 权限验证流程
    switch (true) {
        // 需要登录但未登录
        case requiresAuth && !isAuthenticated:
            return next({
                name: 'login',
                query: { redirect: to.fullPath }
            })
        
        // 已登录访问游客页面
        case guestOnly && isAuthenticated:
            return next({
                name: 'index',
                query: { noBack: true } // 防止返回死循环
            })
        
        // // 权限不足
        // case permissions.length > 0 && (!user || !permissions.includes(user.role)):
        //     return next({ name: 'not-found' })
        
        // 正常通行
        default:
            next()
    }
})

// 路由错误处理
router.onError((error) => {
    console.error('路由错误', error)
})

export default router