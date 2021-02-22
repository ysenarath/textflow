/**
 * Annotator Object
 *
 * @param id: ID
 * @param text: Text
 * @returns {{getSelection: (function(): {}), html: (function(): string), setAnnotations: setAnnotations}}
 * @constructor
 */
class Annotator {
    constructor(id, text, options = {}, verbose = false) {
        this.lookout = document.getElementById(id);
        this.text = text;
        this.options = options;
        this.verbose = verbose;
        this.annotations = {};
        this.selection = {};
        this.events = {};
    }

    /**
     * Visualize Text and Annotations in the Element
     *
     * @returns {boolean}
     */
    update() {
        let temp_annotations = [];
        for (let key in this.annotations) {
            temp_annotations.push(this.annotations[key]);
        }
        this.lookout.innerHTML = '';
        temp_annotations.sort((a, b) => {
            return a.span.start - b.span.start
        });
        let tokenSeparator = /(?=\s+)/;
        let html = '';
        // Extract HTML with <span/> Tags for Annotations
        let lastIdx = 0;
        let error = false;
        for (let i = 0; i < temp_annotations.length; i++) {
            let item = temp_annotations[i];
            if (item.span.start < lastIdx) {
                error = true;
                break;
            }
            let tokens = this.text.substr(lastIdx, item.span.start - lastIdx).split(tokenSeparator);
            for (let j = 0; j < tokens.length; j++) {
                html += '<span class="annotation-text">' + tokens[j] + '</span>';
            }
            let options_html = '';
            let has_selection = false;
            for (let j = 0; j < this.options.length; j++) {
                let is_selected = this.options[j].value == item.label;
                if (is_selected) {
                    has_selection = true;
                }
                options_html += '<option value="' + this.options[j].value + '"' + (is_selected ? 'selected' : '')
                    + '>' + this.options[j].label + '</option>'
            }
            if (!has_selection) {
                options_html = '<option selected>Select Option</option>' + options_html
            }
            html +=
                '<div class="annotation-span" style="border-width: 1px; border-color:' + item.color + '">' +
                '<div class="annotation-text">' + this.text.substr(item.span.start, item.span.length) + '</div>' +
                '<div class="annotation-label">' +
                //
                '<div class="field has-addons m-1">' +
                '<div class="control w-100"><div class="select is-small w-100">' +
                '<select class="w-100" data-id="' + item.id + '">' + options_html + '</select>' +
                '</div></div>' +
                '<div class="control"> <button class="button is-small" type="button" data-id="' + item.id + '">' +
                '&times;' +
                '</button></div>' +
                '</div>' +
                //
                '</div></div>';
            lastIdx = item.span.start + item.span.length;
        }
        // Annotation Loading Failed due to Invalid Annotation.
        let tokens;
        if (error) {
            tokens = this.text.split(tokenSeparator);
        } else {
            tokens = this.text.substr(lastIdx).split(tokenSeparator);
        }
        for (let j = 0; j < tokens.length; j++) {
            html += '<span class="annotation-text">' + tokens[j] + '</span>'
        }
        // HTML build success
        this.lookout.innerHTML = html;
        $('.annotation-span select').change((el) => this.selectionLabelChanged(el));
        if (this.verbose)
            console.debug('Updating Annotations... [done]');
        return !error;
    }

    /**
     * Annotate Function - Creates an annotation given the label and color.
     *
     * @param item Annotation information for the selection
     */
    _annotate_selection(item) {
        let backup = {};
        Object.assign(backup, this.annotations);
        if ((typeof this.selection.span !== 'undefined') && this.selection.span !== null &&
            (this.selection.span.end !== this.selection.span.start)) {
            // add selected region as new annotation
            this.annotations[item.id] = {
                id: item.id,
                label: item.label,
                span: {
                    start: this.selection.span.start,
                    length: this.selection.span.end - this.selection.span.start
                }
            };
            // update annotator with new annotation
            let status = this.update();
            // rollback on error
            if (!status) {
                if (this.verbose)
                    console.error('Invalid Annotation: rollback to backup annotations');
                this.annotations = backup;
                this.update();
                throw 'Invalid Selection for Annotation. ' +
                'Only non-overlapping Annotations are Allowed. ' +
                'Check Existing Annotations and Try Again.'
            }
        } else {
            throw 'Invalid Selection for Annotation. Selection should be non-empty.'
        }
    }

    escape(text) {
        return text.replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/'/g, '&#x27;')
    }

    getAnnotation(id) {
        let item = this.annotations[id];
        return {
            id: item.id,
            label: item.label,
            span: {
                start: [...this.text.substr(0, item.span.start)].length,
                length: [...this.text.substr(item.span.start, item.span.length)].length
            }
        }
    }

    putAnnotation(item) {
        this.annotations[item.id] = item;
        this.annotations[item.id] = {
            id: item.id,
            label: item.label,
            span: {
                start: [...this.text].slice(0, item.span.start).join('').length,
                length: [...this.text].slice(item.span.start, item.span.start + item.span.length).join('').length
            }
        };
    }

    initialize() {
        let lookout = this.lookout;
        let events = this.events;

        document.onmouseup = (e) => {
            // todo: fix only update for lookout
            if (typeof e.target !== 'undefined' && e.target !== null &&
                (e.target.nodeName === 'SELECT' || e.target.nodeName === 'OPTION' || e.target.nodeName === 'BUTTON'))
                return;
            try {
                // 0 is reserved annotation id
                this._annotate_selection({id: 0, label: null, color: 'gray'});
            } catch (e) {
                delete this.annotations[0];
                this.update();
                if (this.verbose)
                    console.error(e)
            }
        };

        document.onselectionchange = () => {
            let _selection = null;
            if (document.getSelection().rangeCount > 0) {
                const range = document.getSelection().getRangeAt(0);
                let startNode = range.startContainer;
                let startOffset = range.startOffset;
                if (startNode !== null && startNode.parentNode !== this.lookout) {
                    startNode = startNode.parentNode;
                }
                let endNode = range.endContainer;
                let endOffset = range.endOffset;
                if (endNode !== null && endNode.parentNode !== this.lookout) {
                    endNode = endNode.parentNode;
                }
                if (startNode.parentNode === this.lookout && endNode.parentNode === this.lookout) {
                    let counter = 0;
                    for (let i = 0; i < this.lookout.childNodes.length; i++) {
                        let node = this.lookout.childNodes[i];
                        if (node === startNode) {
                            startOffset = this.escape(startNode.textContent.substr(0, startOffset)).length + counter;
                        }
                        if (node === endNode) {
                            endOffset = this.escape(endNode.textContent.substr(0, endOffset)).length + counter;
                            break;
                        }
                        let textContent = '';
                        if (node.childNodes.length > 1) {
                            textContent = node.childNodes[0].textContent;
                        } else {
                            textContent = node.textContent;
                        }
                        textContent = this.escape(textContent);
                        counter += textContent.length;
                    }
                    _selection = {start: startOffset, end: endOffset};
                }
            }
            if (this.selection.span !== null || _selection !== null) {
                this.selection.span = _selection;
                // notify on selection change observers here
            }
        };

        // # Following code segment did not support Firefox browser -- removing
        // Change Annotation Type Selection
        // $(document).on('change', '.annotation-span select', (el) => {
        // no support for firefox
        // });

        // Delete Annotation Button
        $(document).on('click', '.annotation-span button', (el) => {
            try {
                if (el.target.parentNode.parentNode.parentNode.parentNode.parentNode === lookout) {
                    let id = el.target.getAttribute('data-id');
                    events['delete'](this.getAnnotation(id));
                }
            } catch (e) {
                // ignore event
            }
        });
        this.update();
    }

    // Change Annotation Type Selection
    selectionLabelChanged(el) {
        try {
            if ($(el.target).parents('#' + this.lookout.id).length === 1) {
                let id = el.target.getAttribute('data-id');
                let value = el.target.value;
                if (this.verbose)
                    console.debug('Selection Changed: {ID = ' + id + ', Value = ' + value + '}');
                this.events['update'](this.getAnnotation(id), value);
            }
        } catch (e) {
            // ignore event
            if (this.verbose)
                console.error(e);
        }
    }

    setAnnotations(items) {
        this.annotations = {};
        items.forEach((item) => {
            this.putAnnotation(item);
        });
        this.update();
    }

    addEventListener(condition, func) {
        this.events[condition] = func;
    }
}
