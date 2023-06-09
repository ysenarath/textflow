<script>
import axios from 'axios'
import { useAuthStore } from '../stores/auth.js'

export default {
    inject: ['Form', 'parseErrors'],
    props: ['projectId', 'taskId'],
    setup() {
        const authStore = useAuthStore()
        return {
            authStore,
        }
    },
    data() {
        return {
            taskForm: null,
            taskFormFields: [
                {
                    type: 'group',
                    class: 'row',
                    fields: [
                        {
                            type: 'group',
                            class: 'col-auto',
                            fields: [
                                {
                                    type: 'group',
                                    class: 'row',
                                    fields: [
                                        {
                                            type: 'group',
                                            class: 'col-auto',
                                            fields: [
                                                {
                                                    name: 'type',
                                                    type: 'select',
                                                    label: 'Task Type',
                                                    choices: [
                                                        {
                                                            label: 'Text Classification',
                                                            value: 'text-classification',
                                                        },
                                                        {
                                                            label: 'Sequence Labeling',
                                                            value: 'sequence-labeling',
                                                        },
                                                    ],
                                                },
                                            ]
                                        },
                                        {
                                            type: 'group',
                                            class: 'col-auto',
                                            fields: [
                                                {
                                                    name: 'order',
                                                    type: 'number',
                                                    label: 'Order',
                                                    placeholder: 'Order',
                                                },
                                            ]
                                        },
                                    ]
                                },
                            ]
                        },
                        {
                            type: 'group',
                            class: 'col',
                            fields: [
                                {
                                    name: 'title',
                                    type: 'text',
                                    label: 'Title',
                                    placeholder: 'Enter a title for the task',
                                },
                            ]
                        },
                    ]
                },
                {
                    name: 'description',
                    type: 'textarea',
                    label: 'Description',
                    placeholder: 'Enter a description for the task',
                },
                {
                    name: 'condition',
                    type: 'textarea',
                    label: 'Condition',
                    default: null,
                    placeholder: 'Enter a condition for the task',
                },
                this.taskId ? {
                    type: 'button',
                    label: 'Update Task',
                    name: 'updateTask',
                } : {
                    type: 'button',
                    label: 'Create Task',
                    name: 'createTask',
                }
            ],
        }
    },
    methods: {
        getTask() {
            const url = textflow.config.basePath + `/api/projects/${this.projectId}/tasks/${this.taskId}`
            const config = {
                headers: { Authorization: `Bearer ${this.authStore.token}` }
            }
            axios.get(url, config)
                .then(response => {
                    console.log(response);
                    this.taskForm.data.title = response.data.title;
                    this.taskForm.data.type = response.data.type;
                    this.taskForm.data.description = response.data.description;
                    this.taskForm.data.order = response.data.order;
                    this.taskForm.data.condition = response.data.condition;
                }).catch(error => {
                    console.log(error);
                });
        },
        createTask() {
            const url = textflow.config.basePath + `/api/projects/${this.projectId}/tasks/`
            const config = {
                headers: { Authorization: `Bearer ${this.authStore.token}` }
            }
            axios.post(url, this.taskForm.data, config)
                .then(response => {
                    console.log(response);
                })
                .catch(error => {
                    console.log(error);
                    this.taskForm.clearErrors();
                    let errors = this.parseErrors(error?.response?.data || null);
                    Object.keys(errors).forEach((key) => {
                        if (key === '/body/title') {
                            this.taskForm.errors.title = errors[key];
                        } else if (key === '/body/type') {
                            this.taskForm.errors.type = errors[key];
                        } else if (key === '/body/description') {
                            this.taskForm.errors.description = errors[key];
                        } else if (key === '/body/order') {
                            this.taskForm.errors.order = errors[key];
                        } else if (key === '/body/condition') {
                            this.taskForm.errors.condition = errors[key];
                        } else {
                            this.taskForm.errors.$other = errors[key];
                        }
                    });
                }).finally(() => {
                    this.submitted = true;
                });
        },
        updateTask() {
            const url = textflow.config.basePath + `/api/projects/${this.projectId}/tasks/${this.taskId}`
            const config = {
                headers: { Authorization: `Bearer ${this.authStore.token}` }
            }
            axios.put(url, this.taskForm.data, config)
                .then(response => {
                    console.log(response);
                })
                .catch(error => {
                    this.taskForm.clearErrors();
                    let errors = this.parseErrors(error?.response?.data || null);
                    Object.keys(errors).forEach((key) => {
                        if (key === '/body/title') {
                            this.taskForm.errors.title = errors[key];
                        } else if (key === '/body/type') {
                            this.taskForm.errors.type = errors[key];
                        } else if (key === '/body/description') {
                            this.taskForm.errors.description = errors[key];
                        } else if (key === '/body/order') {
                            this.taskForm.errors.order = errors[key];
                        } else if (key === '/body/condition') {
                            this.taskForm.errors.condition = errors[key];
                        } else {
                            this.taskForm.errors.$other = errors[key];
                        }
                    });
                }).finally(() => {
                    this.submitted = true;
                });
        },
        action(name) {
            if (name == 'createTask') {
                this.createTask();
            } else if (name == 'updateTask') {
                this.updateTask();
            }
        },
    },
    mounted() {
        this.taskForm = new this.Form([...this.taskFormFields]);
        if (this.taskId) {
            this.getTask();
        }
    }
}
</script>

<template>
    <DefaultForm :id="'taskForm' + projectId" :form="taskForm" @update:form="taskForm" @click:button="action"
        v-if="taskForm">
    </DefaultForm>
</template>