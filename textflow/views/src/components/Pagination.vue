<script>
export default {
    props: ['pagination'],
    emits: ['click'],
    methods: {},
}
</script>
<template>
    <nav aria-label="Project page navigation">
        <ul class="pagination justify-content-center my-0">
            <li class="page-item" :class="{ disabled: !pagination?.has_prev }">
                <button type="button" class="page-link" @click="$emit('click', pagination.prev_num)">
                    <i class="bi bi-caret-left"></i>
                </button>
            </li>
            <li class="page-item" :class="{ active: pagination?.page == page }" v-for="page in pagination?.pages || 0">
                <button type="button" class="page-link" @click="$emit('click', page)">{{ page }}</button>
            </li>
            <li class="page-item" :class="{ disabled: !pagination?.has_next }">
                <button type="button" class="page-link" @click="$emit('click', pagination.next_num)">
                    <i class="bi bi-caret-right"></i>
                </button>
            </li>
        </ul>
    </nav>
</template>