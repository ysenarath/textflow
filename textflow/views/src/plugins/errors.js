class Errors {
    constructor() {
        this.errors = {};
    }

    put(error) {
        let loc = error?.loc;
        if (!loc) {
            loc = [];
        }
        loc = '/' + loc.join('/');
        if (!this.errors.hasOwnProperty(loc)) {
            this.errors[loc] = [];
        }
        this.errors[loc].push(error);
    }

    parse(data) {
        if (typeof data === 'undefined' || data === null) {
            this.put({
                'loc': null,
                'msg': 'Unknown error.',
                'ctx': data,
            });
        } else if (typeof data === 'string') {
            this.put({ 'loc': null, 'msg': data });
        } else if (Array.isArray(data)) {
            for (const e of data) {
                this.parse(e);
            }
        } else if (typeof data === 'object') {
            if (data.hasOwnProperty('detail')) {
                this.parse(data['detail'])
            } else {
                this.put({
                    'loc': data['loc'] || null,
                    'msg': data['msg'] || 'Unknown error.',
                    'ctx': data,
                });
            }
        } else {
            this.put({
                'loc': null,
                'msg': 'Unknown error.',
                'ctx': data,
            });
        }
        return this.errors;
    }
}


export default {
    install(app, options) {
        app.provide('parseErrors', (data) => {
            return new Errors().parse(data)
        });
    }
}