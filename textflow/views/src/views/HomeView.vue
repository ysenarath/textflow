<script>
import Homepage from '../components/Homepage.vue'
import ProjectList from '../components/ProjectList.vue'
import { useAuthStore } from '../stores/auth.js'

import * as bootstrap from 'bootstrap'

export default {
    setup() {
        const authStore = useAuthStore()
        return {
            authStore,
        }
    },
    components: {
        Homepage,
        ProjectList,
    },
    computed: {
        currentView() {
            if (this.authStore.token === null) {
                return Homepage;
            } else {
                const loginModal = document.getElementById('loginModal');
                if (loginModal !== null) {
                    new bootstrap.Modal(loginModal).hide();
                }
                const modalBackdrop = document.getElementsByClassName('modal-backdrop');
                if (modalBackdrop?.length > 0) {
                    modalBackdrop[0].remove();
                }
                return ProjectList;
            }
        }
    },
    data() {
        return {}
    }
}
</script>

<template>
    <component :is="currentView" />
</template>
