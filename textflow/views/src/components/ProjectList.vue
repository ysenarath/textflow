<script>
import axios from 'axios';
import { useAuthStore } from '../stores/auth.js'
import ProjectListItem from './ProjectListItem.vue'
import Pagination from './Pagination.vue'

export default {
    setup() {
        const authStore = useAuthStore();
        return {
            authStore
        }
    },
    components: {
        ProjectListItem,
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
        projects() {
            return this.pagination?.items;
        },
    },
    methods: {
        updateProjects() {
            const config = {
                headers: { Authorization: `Bearer ${this.authStore.token}` }
            }
            console.log(config);
            let url = textflow.config.basePath + '/api/projects/';
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
                this.updateProjects();
            },
            deep: true
        }
    },
    mounted: function () {
        this.updateProjects();
    },
}
</script>

<template>
    <div class="list-group list-group-flush mb-3">
        <div class="list-group-item" :class="'py-0'">
            <div class="btn-toolbar justify-content-between">
                <div class="d-flex">
                    <!-- search projects -->
                    <div class="input-group me-3">
                        <input type="text" class="form-control" placeholder="Search projects" aria-label="Search projects"
                            aria-describedby="button-search" v-model="searchQuery" @keyup="updateProjects" />
                        <button class="btn btn-outline-secondary" type="button" id="button-search" @click="updateProjects">
                            <i class="bi bi-search"></i>
                        </button>
                    </div>
                    <div class="input-group me-3" role="group" aria-label="Per page count change dropdown buttons">
                        <div class="input-group-text" id="btnPerPageAddon">
                            <i class="bi bi-list-ol"></i>
                        </div>
                        <button type="button" class="btn btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown"
                            aria-expanded="false">
                            {{ paginationArgs.perPage }}
                            <span class="visually-hidden">Toggle Dropdown</span>
                        </button>
                        <ul class="dropdown-menu">
                            <li v-for="i in 5"><button class="dropdown-item"
                                    @click="paginationArgs.perPage = i * 5">{{ i * 5 }}</button></li>
                        </ul>
                    </div>
                </div>
                <!-- create project -->
                <div class="btn-group">
                    <RouterLink to="/projects/create" class="btn btn-outline-success">
                        <i class="bi bi-plus-square"></i>
                    </RouterLink>
                </div>
            </div>
        </div>
    </div>
    <ul class="list-group border-top border-bottom mb-3">
        <ProjectListItem v-for="(project, index) in projects" :key="project.id" :project="project" :index="index"
            @click="console.log" />
        <!-- <ProjectListItem v-for="i in paginationArgs.perPage" :key="i"
                                        :project=null :index="i" @click="console.log" /> -->
    </ul>
    <Pagination :pagination="pagination" @click="(page) => paginationArgs.page = page" />
</template>