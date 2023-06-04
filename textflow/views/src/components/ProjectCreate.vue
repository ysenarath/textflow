<script>
import axios from 'axios'
import { useAuthStore } from '../stores/auth.js'

export default {
    inject: ['parseErrors'],
    props: [],
    setup() {
        const authStore = useAuthStore()
        return {
            authStore,
        }
    },
    data() {
        // ProjectBase
        return {
            data: {
                name: null,
                description: null,
                redundancy: null,
                guideline: null,
            },
            errors: null,
            submitted: false,
        }
    },
    methods: {
        createProject() {
            this.errors = null;
            const url = textflow.config.basePath + '/api/projects/'
            const config = {
                headers: { Authorization: `Bearer ${this.authStore.token}` }
            }
            axios.post(url, this.data, config)
                .then(response => {
                    console.log(response);
                })
                .catch(error => {
                    this.errors = {}
                    let errors = this.parseErrors(error?.response?.data || null);
                    console.log(JSON.stringify(error?.response?.data));
                    Object.keys(errors).forEach((key) => {
                        if (key === '/body/name') {
                            this.errors.name = errors[key];
                        } else if (key === '/body/description') {
                            this.errors.description = errors[key];
                        } else if (key === '/body/redundancy') {
                            this.errors.redundancy = errors[key];
                        } else if (key === '/body/guideline') {
                            this.errors.guideline = errors[key];
                        } else {
                            this.errors.$other = errors[key];
                        }
                    });
                }).finally(() => {
                    this.submitted = true;
                });
        },
        valueUpdated() {
            this.submitted = false;
            this.errors = null;
        },
    },
}
</script>
<template>
    <form @keydown="valueUpdated">
        <div class="form-group mb-3">
            <label for="name">Project Name</label>
            <input type="text" class="form-control" id="name" v-model="data.name"
                :class="submitted ? (errors?.name ? 'is-invalid' : 'is-valid') : ''">
            <!-- show errors -->
            <div v-if="submitted && errors?.name" class="invalid-feedback">
                {{ errors.name[0]?.msg }}
            </div>
        </div>
        <div class="form-group mb-3">
            <label for="description">Project Description</label>
            <textarea class="form-control" id="description" v-model="data.description"
                :class="submitted ? (errors?.description ? 'is-invalid' : 'is-valid') : ''"></textarea>
            <div v-if="submitted && errors?.description" class="invalid-feedback">
                {{ errors.description[0]?.msg }}
            </div>
        </div>
        <div class="form-group mb-3">
            <label for="redundancy">Redundancy</label>
            <input type="number" class="form-control" id="redundancy" v-model="data.redundancy"
                :class="submitted ? (errors?.redundancy ? 'is-invalid' : 'is-valid') : ''">
            <div v-if="submitted && errors?.redundancy" class="invalid-feedback">
                {{ errors.redundancy[0]?.msg }}
            </div>
        </div>
        <div class="form-group mb-3">
            <label for="guideline">Guideline</label>
            <textarea class="form-control" id="guideline" v-model="data.guideline"
                :class="submitted ? (errors?.guideline ? 'is-invalid' : 'is-valid') : ''"></textarea>
            <div v-if="submitted && errors?.guideline" class="invalid-feedback">
                {{ errors.guideline[0]?.msg }}
            </div>
        </div>
        <button type="submit" class="btn btn-primary" @click.prevent="createProject">Create</button>
    </form>
</template>