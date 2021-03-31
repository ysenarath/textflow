/**
 * Operations related to theming.
 *
 * @reference: https://dev.to/wendell_adriel/working-with-multiple-css-themes-5aej
 */
const theme = {
    get: function (def = 'light') {
        const htmlTag = document.getElementsByTagName('html')[0]
        if (htmlTag.hasAttribute('data-theme')) {
            return htmlTag.getAttribute('data-theme')
        }
        if (typeof (Storage) !== "undefined") {
            if (typeof (localStorage.themeName) !== 'undefined') {
                return localStorage.themeName;
            }
        }
        return def;
    },
    set: function (name) {
        const htmlTag = document.getElementsByTagName('html')[0]
        if (htmlTag.hasAttribute('data-theme')) {
            htmlTag.removeAttribute('data-theme')
        }
        htmlTag.setAttribute('data-theme', name)
        localStorage.setItem("themeName", name);
    },
    toggle: function () {
        if (theme.get() === 'light') {
            theme.set('dark');
        } else {
            theme.set('light');
        }
    },
    refresh: function () {
        let t = theme.get();
        theme.set(t);
    }
}