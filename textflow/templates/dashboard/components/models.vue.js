// noinspection JSUnresolvedVariable

Vue.component('models-component', {
    data: function () {
        return {
            datasets: [],
            selectedDataset: '',
            estimators: [],
            selectedEstimator: '',
        }
    },
    methods: {
        train: function () {
            $.post({
                type: "POST",
                url: url_for.estimator_fit,
                data: JSON.stringify({
                    dataset: this.selectedDataset,
                    estimator: this.selectedEstimator,
                }),
                contentType: 'application/json;charset=UTF-8',
            }).then(console.log);
        },
        update: function () {
            $.get(url_for.get_dataset_names).then((payload) => {
                this.datasets = payload.data;
                this.selectedDataset = payload.data[0];
            });
            $.get(url_for.get_estimator_names).then((payload) => {
                this.estimators = payload.data;
                this.selectedEstimator = payload.data[0];
            });
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
    template: `{% include 'dashboard/components/models.html' %}`
})
