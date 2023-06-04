<!-- for managing projects (creating, updating, monitoring) projects and to see the projects stats -->
<script>
import ProjectCreate from '../components/ProjectCreate.vue';
import ProjectUpdate from '../components/ProjectUpdate.vue';
import ProjectTasks from '../components/ProjectTasks.vue';
import ProjectDocuments from '../components/ProjectDocuments.vue';
import ProjectStats from '../components/ProjectStats.vue';

export default {
    props: ['projectId', 'section'],
    components: {
        ProjectCreate,
        ProjectUpdate,
        ProjectTasks,
        ProjectDocuments,
        ProjectStats,
    },
    computed: {
        currentView() {
            console.log(this.section);
            if (this.section === 'create') {
                return ProjectCreate;
            } else if (this.section === 'update') {
                return ProjectUpdate;
            } else if (this.section === 'tasks') {
                return ProjectTasks;
            } else if (this.section === 'documents') {
                return ProjectDocuments;
            } else {
                return ProjectStats;
            }
        }
    },
    created() {
        this.$watch(
            () => this.$route.params,
            (toParams, previousParams) => {
                this.projectId = toParams.projectId;
                this.section = toParams.section;
            }
        )
    },
}
</script>

<template>
    <component :is="currentView" :projectId="projectId" />
</template>