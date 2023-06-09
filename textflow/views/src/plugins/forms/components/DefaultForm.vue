<script>
import FormFieldGroup from './FormFieldGroup.vue';

export default {
    props: ['id', 'form'],
    emits: ['update:form', 'click:button'],
    components: {
        FormFieldGroup,
    },
}
</script>

<template>
    <form>
        <FormFieldGroup :id="id" :form="form" @update:form="value => $emit('update:form', value)"
            @click:button="value => $emit('click:button', value)" />
    </form>
</template>