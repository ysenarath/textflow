import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(textflow.config.routerBasePath),
    routes: [
        {
            path: '/',
            name: 'home',
            // component: HomeView,
            component: () => import('../views/HomeView.vue')
        },
        {
            path: '/about',
            name: 'about',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import('../views/AboutView.vue')
        },
        {
            path: '/projects/:projectId/annotate',
            name: 'annotate',
            component: () => import('../views/AnnotateView.vue')
        },
        {
            path: '/projects/:projectId/tasks/create',
            name: 'create-task',
            component: () => import('../views/DashboardView.vue'),
            props: route => Object.assign({
                section: 'create-task',
            }, route.params),
        },
        {
            path: '/projects/:projectId/tasks/:taskId',
            name: 'update-task',
            component: () => import('../views/DashboardView.vue'),
            props: route => Object.assign({
                section: 'update-task',
            }, route.params),
        },
        {
            path: '/projects/:projectId/:section',
            name: 'dashboard',
            component: () => import('../views/DashboardView.vue'),
            props: true,
        },
        {
            path: '/projects/create',
            name: 'create',
            component: () => import('../views/DashboardView.vue'),
            props: route => Object.assign({
                projectId: null,
                section: 'create',
            }, route.params),
        },
        {
            path: '/projects/:projectId',
            name: 'project',
            component: () => import('../views/ProjectView.vue')
        },
    ]
})

export default router
