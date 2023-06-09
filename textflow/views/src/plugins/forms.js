import DefaultForm from './forms/components/DefaultForm.vue';
import FormField from './forms/components/FormField.vue';

class Form {
    _fields
    _data
    _errors

    constructor(fields, data, errors) {
        this._fields = fields;
        this._errors = errors || {};
        this._data = this.merge(data, {});
    }

    merge(data, obj, fields = this._fields) {
        fields.forEach(field => {
            if (field.type == 'group') {
                this.merge(data, obj, field.fields);
            } else if (data?.hasOwnProperty(field.name)) {
                obj[field.name] = data[field.name];
            } else if (field.uselist === true) {
                if (!obj.hasOwnProperty(field.name)) {
                    obj[field.name] = [];
                }
                if (field.default === true) {
                    obj[field.name].push(field.value);
                }
            } else if (typeof field.default !== 'undefined') {
                obj[field.name] = field.default;
            }
        });
        return obj;
    }

    get fields() {
        return this._fields;
    }

    get data() {
        return this._data;
    }

    get errors() {
        return this._errors;
    }

    clearErrors() {
        this._errors = {};
    }

    clearData() {
        this._data = this.merge({}, {});
    }
}

export default {
    install(app, options) {
        app.component('DefaultForm', DefaultForm);
        app.component('FormField', FormField);
        app.provide('Form', Form);
    },
}