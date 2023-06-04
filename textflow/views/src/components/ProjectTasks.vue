<script>
import axios from 'axios'
import { useAuthStore } from '../stores/auth.js'

export default {
    inject: ['parseErrors'],
    props: ['projectId'],
    setup() {
        const authStore = useAuthStore()
        return {
            authStore,
        }
    },
    data() {
        return {
            tasks: [],
        }
    },
    methods: {
        getTasks() {
            const url = textflow.config.basePath + '/api/projects/' + this.projectId + '/tasks'
            const config = {
                headers: { Authorization: `Bearer ${this.authStore.token}` }
            }
            axios.get(url, config)
                .then(response => {
                    this.tasks = response.data;
                });
        },
    }
}
</script>
<template>
    <div>
        <h2>Tasks</h2>
        <div v-for="task in tasks" :key="task.id">
        </div>
        Create Task
    </div>
</template>