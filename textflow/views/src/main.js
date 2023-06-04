// Import our custom CSS
import '../scss/styles.scss'
import 'bootstrap-icons/font/bootstrap-icons.css'

// Import all of Bootstrap's JS
import * as bootstrap from 'bootstrap'
// Load axios as a global variable for all components to use.
import axios from 'axios'
// import local plugins
import errorsPlugin from './plugins/errors'

import './assets/main.css'


import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.provide('textflow', textflow)

app.use(createPinia())
app.use(router)
app.use(errorsPlugin)

app.mount('#app')
