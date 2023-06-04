import { defineStore } from 'pinia'

export const useNotificationsStore = defineStore('notifications', {
    state() {
        return {
            notifications: [],
        }
    },
    actions: {
    },
})
