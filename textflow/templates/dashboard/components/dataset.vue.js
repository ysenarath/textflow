// noinspection JSUnresolvedVariable

Vue.component('dataset-component', {
    data: function () {
        return {
            datasets: [],
            selectedDataset: '',
            groups: [],
            selectedGroup: '',
        }
    },
    methods: {
        saveAs: function (content, filename) {
            const blob = new Blob([JSON.stringify(content, null, 2)], {type: 'application/json'})
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.download = filename;
            a.href = url;
            a.click();
        },
        download: function () {
            let args = '';
            if (this.selectedGroup !== '') {
                args += 'validator=' + this.selectedGroup;
            }
            if (args !== '') args = '?' + args;
            $.get(url_for.download_dataset + args)
                .then((payload) => {
                    if (payload['status'] === 'success') {
                        const fn = this.selectedDataset + '_' + this.selectedGroup + '.json';
                        this.saveAs(payload.data, fn);
                    }
                });
        },
        update: function () {
            $.get(url_for.get_dataset_names).then((payload) => {
                    this.datasets = payload.data;
                    this.selectedDataset = payload.data[0];
                    let args = '';
                    if (this.selectedDataset !== '') {
                        args += 'name=' + this.selectedDataset;
                    }
                    if (args !== '') {
                        args = '?' + args;
                    }
                    $.get(url_for.get_group_names + args).then((payload) => {
                        this.groups = payload.data;
                        this.selectedGroup = 'sys.majority';
                    })
                }
            );
        },
        initialize: function () {
            this.update();
        }
    },
    mounted: function () {
        // Initialize when document is ready
        this.initialize();
    },
    watch: {
        selectedDataset: function (v1, v2) {
            this.update();
        }
    },
    delimiters: ['%{', '}'],
    template: `{% include 'dashboard/components/dataset.html' %}`
})
