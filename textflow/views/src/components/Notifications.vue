<script>
import { useNotificationsStore } from '../stores/notifications';

export default {
    setup() {
        const notificationsStore = useNotificationsStore();
        return {
            notificationsStore: notificationsStore,
        };
    },
    computed: {
        notifications() {
            return this.notificationsStore.notifications;
        },
    },
}
</script>
<template>
    <div class="offcanvas offcanvas-end" tabindex="-1" id="notificationsOffcanvas"
        aria-labelledby="notificationsOffcanvasLabel">
        <div class="offcanvas-header">
            <h5 class="offcanvas-title" id="notificationsOffcanvasLabel">Notifications</h5>
            <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
        </div>
        <div class="offcanvas-body">
            <a class="panel-block has-background-white" v-if="notifications.length > 0">
                <span class="panel-icon">
                    <i class="fas fa-info-circle"></i>
                </span>
            </a>
            <a class="panel-block has-background-white" v-else>
                <div class="content">
                    <p class="has-text-weight-light has-text-centered">
                        <span>You have no active notificaions at the moment.</span><br>
                        <span>Check back later.</span>
                    </p>
                </div>
            </a>
        </div>
    </div>
</template>