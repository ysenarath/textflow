<script>
import axios from 'axios';
import { useAuthStore } from '../stores/auth.js'
import Pagination from './Pagination.vue'

export default {
    setup() {
        const authStore = useAuthStore();
        return {
            authStore
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
        projects() {
            return this.pagination?.items;
        },
    },
    methods: {
        getProjects() {
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
                this.getProjects();
            },
            deep: true
        }
    },
    mounted: function () {
        this.getProjects();
    },
}
</script>

<template>
    <div class="list-group list-group-flush mb-3">
        <div class="list-group-item p-0">
            <div class="btn-toolbar justify-content-between">
                <div class="d-flex">
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
    <div class="table-responsive">
        <table class="table table-hover w-100">
            <thead>
                <tr>
                    <th scope="col" style="width:0%;">#</th>
                    <th scope="col" style="min-width: 56px;">Name</th>
                    <th scope="col" style="min-width: 56px;">Description</th>
                    <th scope="col" style="width:0%; min-width: 158px;">Actions</th>
                </tr>
            </thead>
            <tbody class="table-group-divider">
                <tr v-for="(project, index) in projects" :key="project.id">
                    <th scope="row">{{ index }}</th>
                    <td>{{ project.name }}</td>
                    <td>{{ project.description }}</td>
                    <td class="d-flex flex-nowrap">
                        <RouterLink :to="`/projects/${project.id}/`" class="btn btn-outline-success me-2"
                            aria-current="page" :disabled="project === null">
                            <i class="bi bi-view-list"></i>
                        </RouterLink>
                        <RouterLink :to="`/projects/${project.id}/annotate/`" class="btn btn-outline-success me-2"
                            aria-current="page" :disabled="project === null">
                            <i class="bi bi-tag"></i>
                        </RouterLink>
                        <RouterLink :to="`/projects/${project.id}/stat/`" class="btn btn-outline-danger" aria-current="page"
                            :disabled="project === null">
                            <i class="bi bi-pencil-square"></i>
                        </RouterLink>
                    </td>
                </tr>
            </tbody>
        </table>
        <div class="mt-auto">
            <Pagination :pagination="pagination" @click="(page) => paginationArgs.page = page" />
        </div>
    </div>
</template>