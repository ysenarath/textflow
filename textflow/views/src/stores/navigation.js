import { defineStore } from 'pinia'

export const useNavStore = defineStore('navigation', {
    state() {
        return {
            items: [
                { label: 'Home', to: '/', isRouterLink: true },
                { label: 'About', to: '/about', isRouterLink: true, hideIfLoggedIn: true },
            ],
        }
    },
    getters: {
        navItems() {
            return this.items
        },
    },
})
