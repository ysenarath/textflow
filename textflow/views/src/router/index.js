import { createRouter, createWebHistory } from 'vue-router'
// import HomeView from '../views/HomeView.vue'

const router = createRouter({
    history: createWebHistory(textflow.config.routerBasePath),
    routes: [
        {
            path: '/',
            name: 'home',
            // need not lazy load the home view - frequently used
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
            path: '/projects/:projectId/:section',
            name: 'dashboard',
            component: () => import('../views/DashboardView.vue'),
            props: true,
        },
        {
            path: '/projects/create',
            name: 'create',
            component: () => import('../views/DashboardView.vue'),
            props: { projectId: null, section: 'create' }
        },
        {
            path: '/projects/:projectId',
            name: 'project',
            component: () => import('../views/ProjectView.vue')
        },
    ]
})

export default router
