<script>
export default {
    props: ['project', 'index'],
    emits: ['click'],
    setup() {
        return {}
    },
    data() {
        return {}
    },
    methods: {},
}
</script>
<template>
    <li class="list-group-item border-0 py-0 px-3" @click="$emit('click')">
        <hr class="border p-0 m-0" v-if="index > 0">
        <div class="d-flex w-100 justify-content-between my-1 py-3">
            <div class="d-flex flex-column">
                <h5 class="mb-1" v-if="project">{{ project?.name }}</h5>
                <h5 class="mb-1" v-else disabled>Project Name</h5>
                <small v-if="project">{{ project?.description }}</small>
                <small v-else disabled>Project description will appear here.</small>
            </div>
            <div class="btn-toolbar">
                <div class="btn-group ms-2">
                    <RouterLink :to="`/projects/${project.id}/`" class="btn btn-outline-success" aria-current="page" :disabled="project === null">
                        <i class="bi bi-view-list"></i>
                    </RouterLink>
                </div>
                <div class="btn-group ms-2">
                    <RouterLink :to="`/projects/${project.id}/annotate/`" class="btn btn-outline-success" aria-current="page" :disabled="project === null">
                        <i class="bi bi-tag"></i>
                    </RouterLink>
                </div>
                <div class="btn-group ms-2">
                    <RouterLink :to="`/projects/${project.id}/stat/`" class="btn btn-outline-danger" aria-current="page" :disabled="project === null">
                        <i class="bi bi-pencil-square"></i>
                    </RouterLink>
                </div>
            </div>
        </div>
    </li>
</template>
