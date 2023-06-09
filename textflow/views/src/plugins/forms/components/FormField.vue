<script>
export default {
    props: ['id', 'field', 'errors', 'modelValue'],
    emits: ['update:modelValue', 'click:button'],
    computed: {
        value: {
            get() {
                return this.modelValue;
            },
            set(value) {
                this.$emit('update:modelValue', value);
            },
        },
    },
}
</script>

<template>
    <div :class="['mb-3', field.horizontal ? 'row' : '']">
        <template v-if="field.type == 'button' || field.type == 'submit'">
            <button :type="field.type" class="btn btn-primary" @click="$emit('click:button', field.name)">{{ field.label }}</button>
        </template>
        <template v-else-if="field.type == 'select'">
            <label :for="id + 'Field' + field.name"
                :class="['form-label', field.horizontal ? 'col-sm-2 col-form-label' : '']" v-if="field?.label">
                {{ field.label }}
            </label>
            <div class="col-sm-10" v-if="field.horizontal">
                <select :class="['form-select', errors ? 'is-invalid' : '']" :id="id + 'Field' + field.name"
                    :multiple="field?.multiple === true" v-model="value">
                    <option v-for="choice in field.choices" :key="id + 'Option' + key" :value="choice.value">
                        {{ choice.label }}
                    </option>
                </select>
                <div :id="id + 'Error' + field.name" class="invalid-feedback d-flex flex-column" v-if="errors">
                    <template v-if="Array.isArray(errors)">
                        <span v-for="(error, key) in errors" :key="id + 'Error' + key">
                            {{ error?.msg || error }}
                        </span>
                    </template>
                    <span v-else>{{ errors?.msg || errors }}</span>
                </div>
            </div>
            <template v-else>
                <select :class="['form-select', errors ? 'is-invalid' : '']" :id="id + 'Field' + field.name"
                    :multiple="field?.multiple === true" v-model="value">
                    <option v-for="choice in field.choices" :key="id + 'Option' + key" :value="choice.value">
                        {{ choice.label }}
                    </option>
                </select>
                <div :id="id + 'Error' + field.name" class="invalid-feedback d-flex flex-column" v-if="errors">
                    <template v-if="Array.isArray(errors)">
                        <span v-for="(error, key) in errors" :key="id + 'Error' + key">
                            {{ error?.msg || error }}
                        </span>
                    </template>
                    <span v-else>{{ errors?.msg || errors }}</span>
                </div>
            </template>
        </template>
        <template v-else-if="field.type == 'textarea'">
            <label :class="['form-label', field.horizontal ? 'col-sm-2 col-form-label' : '']"
                :for="id + 'Field' + field.name" v-if="field?.label">{{ field.label }}</label>
            <div class="col-sm-10" v-if="field.horizontal">
                <textarea :class="['form-control', errors ? 'is-invalid' : '']" :type="field.type"
                    :id="id + 'Field' + field.name" :placeholder="field.placeholder" v-model="value"></textarea>
                <div :id="id + 'Error' + field.name" class="invalid-feedback d-flex flex-column" v-if="errors">
                    <template v-if="Array.isArray(errors)">
                        <span v-for="(error, key) in errors" :key="id + 'Error' + key">
                            {{ error?.msg || error }}
                        </span>
                    </template>
                    <span v-else>{{ errors?.msg || errors }}</span>
                </div>
            </div>
            <template v-else>
                <textarea :class="['form-control', errors ? 'is-invalid' : '']" :type="field.type"
                    :id="id + 'Field' + field.name" :placeholder="field.placeholder" v-model="value"></textarea>
                <div :id="id + 'Error' + field.name" class="invalid-feedback d-flex flex-column" v-if="errors">
                    <template v-if="Array.isArray(errors)">
                        <span v-for="(error, key) in errors" :key="id + 'Error' + key">
                            {{ error?.msg || error }}
                        </span>
                    </template>
                    <span v-else>{{ errors?.msg || errors }}</span>
                </div>
            </template>
        </template>
        <div :class="['form-check', errors ? 'is-invalid' : '', field.horizontal ? 'col-sm-2 col-form-label' : '']"
            v-else-if="field.type == 'checkbox' || field.type == 'radio'">
            <label :class="['form-check-label']" :for="id + 'Field' + field.name + field.value" v-if="field?.label">
                {{ field.label }}
            </label>
            <div class="col-sm-10" v-if="field.horizontal">
                <input :class="['form-check-input']" :type="field.type" :id="id + 'Field' + field.name + field.value"
                    :name="field.name" :value="field.value" v-model="value"
                    :indeterminate="typeof field.default === 'undefined'">
                <div :id="id + 'Error' + field.name" class="invalid-feedback d-flex flex-column" v-if="errors">
                    <template v-if="Array.isArray(errors)">
                        <span v-for="(error, key) in errors" :key="id + 'Error' + key">
                            {{ error?.msg || error }}
                        </span>
                    </template>
                    <span v-else>{{ errors?.msg || errors }}</span>
                </div>
            </div>
            <template v-else>
                <input :class="['form-check-input']" :type="field.type" :id="id + 'Field' + field.name + field.value"
                    :name="field.name" :value="field.value" v-model="value"
                    :indeterminate="typeof field.default === 'undefined'">
                <div :id="id + 'Error' + field.name" class="invalid-feedback d-flex flex-column" v-if="errors">
                    <template v-if="Array.isArray(errors)">
                        <span v-for="(error, key) in errors" :key="id + 'Error' + key">
                            {{ error?.msg || error }}
                        </span>
                    </template>
                    <span v-else>{{ errors?.msg || errors }}</span>
                </div>
            </template>
        </div>
        <template v-else>
            <label :class="['form-label', field.horizontal ? 'col-sm-2 col-form-label' : '']"
                :for="id + 'Field' + field.name" v-if="field?.label">{{ field.label }}</label>
            <div class="col-sm-10" v-if="field.horizontal">
                <input :class="['form-control', errors ? 'is-invalid' : '']" :type="field.type"
                    :id="id + 'Field' + field.name" :placeholder="field.placeholder" v-model="value">
                <div :id="id + 'Error' + field.name" class="invalid-feedback d-flex flex-column" v-if="errors">
                    <template v-if="Array.isArray(errors)">
                        <span v-for="(error, key) in errors" :key="id + 'Error' + key">
                            {{ error?.msg || error }}
                        </span>
                    </template>
                    <span v-else>{{ errors?.msg || errors }}</span>
                </div>
            </div>
            <template v-else>
                <input :class="['form-control', errors ? 'is-invalid' : '']" :type="field.type"
                    :id="id + 'Field' + field.name" :placeholder="field.placeholder" v-model="value">
                <div :id="id + 'Error' + field.name" class="invalid-feedback d-flex flex-column" v-if="errors">
                    <template v-if="Array.isArray(errors)">
                        <span v-for="(error, key) in errors" :key="id + 'Error' + key">
                            {{ error?.msg || error }}
                        </span>
                    </template>
                    <span v-else>{{ errors?.msg || errors }}</span>
                </div>
            </template>
        </template>
    </div>
</template>