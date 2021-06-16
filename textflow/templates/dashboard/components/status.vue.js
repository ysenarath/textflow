// noinspection JSUnresolvedVariable

Vue.component('status-component', {
    data: function () {
        return {
            num_documents: 0,
            num_completed: 0,
            num_remaining: 0,
            percentage: 0,
        }
    },
    methods: {
        initialize: function () {
            $.get(url_for.get_status)
                .then((payload) => {
                    this.num_documents = payload.data['num_documents'];
                    this.num_completed = payload.data['num_completed'];
                    this.num_remaining = payload.data['num_remaining'];
                    this.percentage = payload.data['percentage'];
                }).catch(console.log);
        }
    },
    mounted: function () {
        // Initialize when document is ready
        this.initialize();
    },
    delimiters: ['%{', '}'],
    template: `{% include 'dashboard/components/status.html' %}`
})
