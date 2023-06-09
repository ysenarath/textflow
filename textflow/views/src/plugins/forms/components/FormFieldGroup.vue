<script>
import FormField from './FormField.vue';

export default {
    props: ['id', 'form', 'fields'],
    emits: ['update:form', 'click:button'],
    components: {
        FormField,
    },
    data() {
        return {
            fields: this.fields || this.form.fields,
        }
    },
    methods: {
        getErrors(field) {
            if (this.form.errors) {
                return this.form.errors[field.name] || null;
            }
            return null;
        },
        getValue(field) {
            if (this.form.data) {
                return this.form.data[field.name] || null;
            }
            return null;
        },
        setValue(field, value) {
            this.form.errors[field.name] = null;
            this.form.data[field.name] = value;
            this.$emit('update:form', this.form);
        },
    },
}
</script>

<template>
    <template v-for="(field, key) in fields" :key="id + 'Form' + key">
        <div :class="field.class ? field.class : ''" v-if="field.type === 'group'">
            <FormFieldGroup :id="id" :form="form" :fields="field.fields" @update:form="value => $emit('update:form', value)"
                @click:button="value => $emit('click:button', value)">
            </FormFieldGroup>
        </div>
        <FormField :id="id + 'Field' + key" :field="field" :errors="getErrors(field)" :modelValue="getValue(field)"
            @update:modelValue="value => setValue(field, value)" @click:button="value => $emit('click:button', value)"
            v-else />
    </template>
</template>