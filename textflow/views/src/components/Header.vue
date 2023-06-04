<script>
import { useAuthStore } from '../stores/auth.js'
import { useThemeStore } from '../stores/theme.js'
import { useNavStore } from '../stores/navigation.js'

import * as bootstrap from 'bootstrap'

export default {
    setup() {
        const themeStore = useThemeStore();
        const authStore = useAuthStore();
        const navStore = useNavStore();
        return {
            themeStore,
            authStore,
            navStore,
        }
    },
    methods: {
        showLoginModal() {
            new bootstrap.Modal('#loginModal').show();
        },
        logout() {
            this.authStore.logout();
        },
    },
}
</script>

<template>
    <nav class="navbar navbar-expand-lg bg-body-tertiary z-3" role="navigation" aria-label="main navigation">
        <div class="container">
            <RouterLink class="navbar-brand" to="/">
                <img src="/public/long-logo.png" height="28" alt="TextFlow Logo">
            </RouterLink>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
                aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav flex-row flex-wrap">
                    <!-- and url_path is not none -->
                    <li class="nav-item" v-for="navItem in navStore.navItems">
                        <RouterLink :to="navItem.to" class="nav-link" aria-current="page"
                            v-if="!(authStore.isAuthenticated && navItem.hideIfLoggedIn) & navItem.isRouterLink">
                            {{ navItem.label }}
                        </RouterLink>
                        <a :href="navItem.href" class="nav-link" aria-current="page"
                            v-else-if="!(authStore.isAuthenticated && navItem.hideIfLoggedIn)">
                            {{ navItem.label }}
                        </a>
                    </li>
                </ul>
                <ul class="navbar-nav flex-row flex-wrap ms-md-auto">
                    <li class="nav-item py-2 py-lg-1 col-12 col-lg-auto">
                        <div class="vr d-none d-lg-flex h-100 mx-lg-2 text-white"></div>
                        <hr class="d-lg-none my-2 text-white-50">
                    </li>
                    <li class="nav-item dropdown">
                        <button class="btn btn-link nav-link py-2 px-0 px-lg-2 dropdown-toggle d-flex align-items-center"
                            data-bs-toggle="dropdown" aria-expanded="false" aria-label="Toggle theme (auto)">
                            <i id="navbar-theme-icon" class="bi-sun-fill me-1" v-if="themeStore.theme == 'light'"></i>
                            <i id="navbar-theme-icon" class="bi-moon-stars-fill me-1" v-if="themeStore.theme == 'dark'"></i>
                            <i id="navbar-theme-icon" class="bi-circle-half me-1" v-if="themeStore.theme == 'auto'"></i>
                        </button>
                        <ul class="dropdown-menu">
                            <li><button class="dropdown-item" @click="themeStore.setTheme('light')"><i
                                        class="bi-sun-fill me-2"></i>Light</button></li>
                            <li><button class="dropdown-item" @click="themeStore.setTheme('dark')"><i
                                        class="bi-moon-stars-fill me-2"></i>Dark</button></li>
                            <li><button class="dropdown-item" @click="themeStore.setTheme('auto')"><i
                                        class="bi-circle-half me-2"></i>Auto</button></li>
                        </ul>
                    </li>
                    <li class="nav-item py-2 py-lg-1 col-12 col-lg-auto">
                        <div class="vr d-none d-lg-flex h-100 mx-lg-2 text-white"></div>
                        <hr class="d-lg-none my-2 text-white-50">
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" role="button" data-bs-toggle="offcanvas" href="#notificationsOffcanvas">
                            <i id="navbar-theme-icon" class="bi-bell me-1"></i>
                        </a>
                    </li>
                    <li class="nav-item py-2 py-lg-1 col-12 col-lg-auto">
                        <div class="vr d-none d-lg-flex h-100 mx-lg-2 text-white"></div>
                        <hr class="d-lg-none my-2 text-white-50">
                    </li>
                    <li class="nav-item" v-if="authStore.token === null">
                        <button type="button" class="nav-link" @click="showLoginModal">
                            <i id="navbar-theme-icon" class="bi-box-arrow-in-right me-1"></i>
                            <span>Login</span>
                        </button>
                    </li>
                    <li class="nav-item" v-else>
                        <button type="button" class="nav-link" @click="logout">
                            <i id="navbar-theme-icon" class="bi-box-arrow-in-left me-1"></i>
                            <span>Logout</span>
                        </button>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
</template>

<style scoped></style>
