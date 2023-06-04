// stores/token.js
import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
    state: () => {
        let tokenData = JSON.parse(localStorage.getItem('textflow.auth.token'));
        return {
            expires_at: tokenData?.expires_at || null,
            access_token: tokenData?.access_token || null,
            refresh_token: tokenData?.refresh_token || null,
        };
    },
    getters: {
        token(state) {
            const currentTimestamp = new Date().getTime();
            // !state.expires_at means the token never expires
            if (!state.expires_at || currentTimestamp < state.expires_at) {
                return state.access_token;
            }
            return null;
        },
        isAuthenticated(state) {
            return state.token !== null;
        },
    },
    actions: {
        login(username, password) {
            var authRequestForm = new FormData();
            authRequestForm.append('username', username);
            authRequestForm.append('password', password);
            return new Promise((resolve, reject) => {
                axios.post(
                    textflow.config.basePath + '/api/tokens/',
                    authRequestForm,
                ).then((response) => {
                    const tokenData = response.data;
                    // expires_in is in seconds, convert to milliseconds
                    if (tokenData.expires_in) {
                        tokenData.expires_at = new Date().getTime() + tokenData.expires_in * 1000;
                    } else {
                        tokenData.expires_at = null;
                    }
                    this.access_token = tokenData.access_token;
                    this.refresh_token = tokenData.refresh_token;
                    this.expires_at = tokenData.expires_at;
                    localStorage.setItem('textflow.auth.token', JSON.stringify({
                        access_token: this.access_token,
                        refresh_token: this.refresh_token,
                        expires_at: this.expires_at,
                    }));
                    resolve(response);
                }).catch((error) => {
                    reject(error);
                })
            });
        },
        logout() {
            this.expires_at = null;
            this.access_token = null;
            this.refresh_token = null;
        },
    }
});