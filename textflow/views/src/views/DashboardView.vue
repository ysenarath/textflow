<!-- for managing projects (creating, updating, monitoring) projects and to see the projects stats -->
<script>
import ProjectCreate from '../components/ProjectCreate.vue';
import ProjectUpdate from '../components/ProjectUpdate.vue';
import ProjectTaskList from '../components/ProjectTaskList.vue';
import ProjectTask from '../components/ProjectTask.vue';
import ProjectDocuments from '../components/ProjectDocuments.vue';
import ProjectStats from '../components/ProjectStats.vue';

export default {
    props: ['projectId', 'taskId', 'section'],
    components: {
        ProjectCreate,
        ProjectUpdate,
        ProjectTaskList,
        ProjectTask,
        ProjectDocuments,
        ProjectStats,
    },
    computed: {
        currentView() {
            console.log(this.section, this.projectId, this.taskId);
            if (this.section === 'create') {
                return ProjectCreate;
            } else if (this.section === 'update') {
                return ProjectUpdate;
            } else if (this.section === 'create-task' || this.section === 'update-task') {
                return ProjectTask;
            } else if (this.section === 'tasks') {
                return ProjectTaskList;
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
                this.taskId = toParams.taskId;
                this.section = toParams.section;
            }
        )
    },
}
</script>

<template>
    <component :is="currentView" :projectId="projectId" :taskId="taskId" />
</template>