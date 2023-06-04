<script>
import { RouterLink, RouterView } from 'vue-router'
import Header from './components/Header.vue'
import { useThemeStore } from './stores/theme.js'

export default {
    setup() {
        const themeStore = useThemeStore();
        themeStore.setTheme();
        return { themeStore }
    },
    components: {
        RouterLink,
        RouterView,
        Header,
    },
    methods: {
        login() {
            $('#loginModal').modal('show')
        },
    },
}
</script>

<template>
    <Header></Header>
    <div class="container pt-3">
        <RouterView></RouterView>
    </div>
</template>

<style scoped></style>