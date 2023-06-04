<script>

export default {
    inject: ['parseErrors'],
    props: ['projectId', 'task'],
    data() {
        if (this.task) {
            const data = this.task;
        } else {
            const data = {
                type: null,
                title: null,
                description: null,
                order: null,
                condition: null,
            };
        }
        return {
            data: data,
            taskTypes: {
                'text-classification': 'Text Classification',
                'sequence-labeling': 'Sequence Labeling',
            },
        }
    },
    methods: {
        getTasks() {

        },
        getTask() {

        },
        createTask() {

        },
        updateTask() {

        },
    }
}
</script>

<template>
    <form>
        <div class="form-group">
            <label for="taskType">Task Type</label>
            <select class="form-control" id="taskType" :v-model="data.type">
                <option v-for="(value, key) in taskTypes" :key="key" :value="key">{{ value }}</option>
            </select>
        </div>
        <div class="form-group">
            <label for="taskTitle">Title</label>
            <input type="text" class="form-control" id="taskTitle" v-model="task.title">
        </div>
        <div class="form-group">
            <label for="taskDescription">Description</label>
            <textarea class="form-control" id="taskDescription" rows="3" v-model="task.description"></textarea>
        </div>
        <div class="form-group">
            <label for="taskOrder">Order</label>
            <input type="number" class="form-control" id="taskOrder" v-model="task.order">
        </div>
        <div class="form-group">
            <label for="taskCondition">Condition</label>
            <input type="text" class="form-control" id="taskCondition" v-model="task.condition">
        </div>
        <button type="createTask" class="btn btn-primary" @click.prevent="createTask">Save</button>
    </form>
</template>