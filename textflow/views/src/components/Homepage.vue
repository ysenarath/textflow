<script>
import { useAuthStore } from '../stores/auth.js'

export default {
    inject: ['parseErrors'],
    setup() {
        const authStore = useAuthStore()
        return {
            authStore,
        }
    },
    data() {
        return {
            loginForm: {
                data: {
                    username: {
                        value: null,
                    },
                    password: {
                        value: null,
                    },
                },
                submitted: false,
                errors: null,
                visible: true,
            },
        }
    },
    computed: {
        hasLoginFormErrors() {
            return this.loginForm.errors?.length > 0;
        }
    },
    methods: {
        clearLoginFormErrors() {
            this.loginForm.submitted = false;
            this.loginForm.errors = null;
        },
        validate() {
            return true;
        },
        login() {
            this.loginForm.submitted = false;
            if (!this.validate()) {
                return;
            }
            const username = this.loginForm.data.username.value
            const password = this.loginForm.data.password.value
            this.authStore.login(username, password).then((response) => {
                console.log(response);
            }).catch((error) => {
                let errors = this.parseErrors(error?.response?.data || null);
                Object.keys(errors).forEach((key) => {
                    if (key == '/') {
                        this.loginForm.errors = errors[key];
                    }
                })
                console.log(this.loginForm.errors);
            }).finally(() => {
                this.loginForm.submitted = true;
            });
        },
    },
}
</script>

<template>
    <div class="py-5 text-center">
        <h1 class="display-5 fw-bold text-body-emphasis">
            TextFlow
        </h1>
        <div class="col-lg-6 mx-auto">
            <p class="lead mb-4">
                TextFlow is a web application for annotating text data.
                It is designed to be simple and intuitive to use.
            </p>
        </div>
    </div>
    <div class="row py-5 m-0">
        <div class="col d-flex align-items-start">
            <div>
                <h3 class="fs-2">Annotate</h3>
                <p>Annotate text data with a simple and intuitive interface.</p>
            </div>
        </div>
        <div class="col d-flex align-items-start">
            <div>
                <h3 class="fs-2">Model</h3>
                <p>
                    Connect with your favorite machine learning framework to train models.
                </p>
            </div>
        </div>
        <div class="col d-flex align-items-start">
            <div>
                <h3 class="fs-2">
                    Evaluate
                </h3>
                <p>
                    Evaluate the agreement between annotators while annotation is in progress.
                </p>
            </div>
        </div>
    </div>
    <div id="loginModal" class='modal fade' data-bs-backdrop="static" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5" id="staticBackdropLabel">Login</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form method="POST" @submit.prevent="login" novalidate>
                        <div class="form-floating mb-4">
                            <input type="text" name="username" size="24" class="form-control" placeholder="Username"
                                :class="loginForm.submitted ? (hasLoginFormErrors ? 'is-invalid' : 'is-valid') : ''"
                                @change="clearLoginFormErrors" v-model="loginForm.data.username.value" />
                            <label for="username">Username</label>
                        </div>
                        <div class="form-floating mb-4">
                            <input type="password" name="password" size="24" class="form-control" placeholder="Password"
                                :class="loginForm.submitted ? (hasLoginFormErrors ? 'is-invalid' : 'is-valid') : ''"
                                @change="clearLoginFormErrors" v-model="loginForm.data.password.value" />
                            <label for="password">Password</label>
                        </div>
                        <div class="form-floating d-flex justify-content-between">
                            <input type="text" class="is-invalid" hidden>
                            <span class="invalid-feedback" v-if="hasLoginFormErrors">
                                <span v-for="error in loginForm.errors">
                                    {{ error.msg }}
                                </span>
                            </span>
                            <input class="btn btn-primary is-invalid mr-3 ms-auto" type="submit" value="Login" />
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped></style>
