// noinspection JSUnresolvedVariable

Vue.component('agreement-component', {
    data: function () {
        return {
            blacklist: [],
            blacklistInput: '',
            agreement: [],
        }
    },
    methods: {
        update: function () {
            let args = '';
            for (let i = 0; i < this.blacklist.length; i++) {
                if (args !== '') args += '&';
                args += 'blacklist=' + this.blacklist[i]
            }
            if (args !== '') args = '?' + args;
            $.get(url_for.get_agreement + args).then((data) => {
                this.agreement = data.data;
            }).catch(console.log);
        },
        initialize: function () {
            this.update();
        }
    },
    mounted: function () {
        // Initialize when document is ready
        this.initialize();
    },
    delimiters: ['%{', '}'],
    template: `{% include 'dashboard/components/agreement.html' %}`
})