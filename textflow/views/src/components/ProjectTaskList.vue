<script>
import axios from 'axios'
import { useAuthStore } from '../stores/auth.js'
import Pagination from './Pagination.vue'

export default {
    inject: ['parseErrors'],
    props: ['projectId'],
    setup() {
        const authStore = useAuthStore()
        return {
            authStore,
        }
    },
    components: {
        Pagination,
    },
    data() {
        return {
            paginationArgs: {
                page: 1,
                perPage: 5,
            },
            searchQuery: '',
            pagination: null,
        }
    },
    computed: {
        tasks() {
            return this.pagination?.items;
        },
    },
    methods: {
        getTasks() {
            const config = {
                headers: { Authorization: `Bearer ${this.authStore.token}` }
            }
            let url = textflow.config.basePath + '/api/projects/' + this.projectId + '/tasks';
            if (this.searchQuery.length > 0) {
                url += '?search=' + this.searchQuery;
            }
            // paginationArgs
            if (this.paginationArgs.page) {
                url += (url.indexOf('?') > -1 ? '&' : '?') + 'page=' + this.paginationArgs.page;
            }
            // per_page
            if (this.paginationArgs.perPage) {
                url += (url.indexOf('?') > -1 ? '&' : '?') + 'per_page=' + this.paginationArgs.perPage;
            }
            return new Promise((resolve, reject) => {
                axios.get(
                    url, config
                ).then((response) => {
                    const page = response.data;
                    console.log(JSON.stringify(page));
                    if (Array.isArray(page)) {
                        this.pagination = {
                            items: page,
                            has_next: false,
                            has_prev: false,
                            next_num: null,
                            pages: 1,
                            prev_num: null,
                            total: page.length,
                        }
                    }
                    else {
                        this.pagination = page;
                    }
                    resolve(response);
                }).catch((error) => {
                    reject(error);
                })
            });
        },
    },
    watch: {
        paginationArgs: {
            handler(newPage, oldPage) {
                this.getTasks();
            },
            deep: true
        }
    },
    mounted() {
        this.getTasks();
    }
}
</script>
<template>
    <div>
        <table class="table">
            <thead>
                <tr>
                    <th scope="col">Task ID</th>
                    <th scope="col">Type</th>
                    <th scope="col">Title</th>
                    <th scope="col">Description</th>
                    <th scope="col">Order</th>
                    <th scope="col">Condition</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="task in tasks" :key="task.id">
                    <th scope="row">{{ task.id }}</th>
                    <td>{{ task.type }}</td>
                    <td>{{ task.title }}</td>
                    <td>{{ task.description }}</td>
                    <td>{{ task.order }}</td>
                    <td>{{ task.condition }}</td>
                </tr>
            </tbody>
        </table>
        <Pagination :pagination="pagination" @click="(page) => paginationArgs.page = page" />
    </div>
</template>