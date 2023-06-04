import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

const themeLocalStoreKey = 'textflow.profile.theme';

export const useThemeStore = defineStore('theme', {
    state() {
        return {
            theme: null,
        }
    },
    actions: {
        getPreferredTheme() {
            if (this.theme === null) {
                const storedTheme = localStorage.getItem(themeLocalStoreKey);
                this.theme = storedTheme ? storedTheme : 'auto';
            }
            // function to get preferred theme
            if (['light', 'dark'].includes(this.theme)) {
                return this.theme;
            } else if (this.theme !== 'auto') {
                this.theme = 'auto';
            }
            // theme is 'auto'
            const storedTheme = localStorage.getItem(themeLocalStoreKey);
            if (storedTheme) {
                return storedTheme;
            }
            let systemTheme = 'light';
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                systemTheme = 'dark';
            }
            return systemTheme;
        },
        setTheme(theme = null) {
            if (theme !== null || theme !== undefined) {
                this.theme = theme;
            }
            const browserTheme = this.getPreferredTheme();
            document.documentElement.setAttribute('data-bs-theme', browserTheme)
            this.submit();
        },
        submit() {
            localStorage.setItem(themeLocalStoreKey, this.theme);
            let data = {
                'profile': { 'theme': this.theme }
            }
            // $.ajax({
            //     type: 'POST',
            //     url: "#",
            //     dataType: 'json',
            //     contentType: "application/json; charset=utf-8",
            //     data: JSON.stringify({ data }),
            //     success: function (data) {
            //         console.log(data);
            //     },
            //     error: function (error) {
            //         console.log(error);
            //     }
            // });
        },
    }
});
