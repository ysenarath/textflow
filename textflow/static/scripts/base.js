// From: https://stackoverflow.com/questions/46785393/bulma-dropdown-not-working

// Get all dropdowns on the page that aren't hoverable.
const dropdowns = document.querySelectorAll('.dropdown:not(.is-hoverable)');

if (dropdowns.length > 0) {
    // For each dropdown, add event handler to open on click.
    dropdowns.forEach(function (el) {
        el.addEventListener('click', function (e) {
            e.stopPropagation();
            el.classList.toggle('is-active');
        });
    });

    // If user clicks outside dropdown, close it.
    document.addEventListener('click', function (e) {
        closeDropdowns();
    });
}

/*
 * Close dropdowns by removing `is-active` class.
 */
function closeDropdowns() {
    dropdowns.forEach(function (el) {
        el.classList.remove('is-active');
    });
}

// Close dropdowns if ESC pressed
document.addEventListener('keydown', function (event) {
    let e = event || window.event;
    if (e.key === 'Esc' || e.key === 'Escape') {
        closeDropdowns();
    }
});

// https://bulma.io/documentation/components/navbar/
$(document).ready(function () {
    // Check for click events on the navbar burger icon
    $(".navbar-burger").click(function () {
        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");
    });
});

// https://bulma.io/documentation/elements/notification/
document.addEventListener('DOMContentLoaded', () => {
    (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
        var $notification = $delete.parentNode;

        $delete.addEventListener('click', () => {
            $notification.parentNode.removeChild($notification);
        });
    });
});

/**
 * Operations related to theming.
 *
 * @reference: https://dev.to/wendell_adriel/working-with-multiple-css-themes-5aej
 * @type {{set: theme.set, get: (function(): (*|string)), toggle: theme.toggle}}
 */
const theme = {
    get: function () {
        const htmlTag = document.getElementsByTagName('html')[0]
        if (htmlTag.hasAttribute('data-theme')) {
            return htmlTag.getAttribute('data-theme')
        }
        return 'dark';
    },
    set: function (name) {
        const htmlTag = document.getElementsByTagName('html')[0]
        if (htmlTag.hasAttribute('data-theme')) {
            htmlTag.removeAttribute('data-theme')
        }
        htmlTag.setAttribute('data-theme', name)
    },
    toggle: function () {
        if (this.get() === 'light') {
            this.set('dark');
        } else {
            this.set('light');
        }
    },
}

function toggleTheme() {
    console.log(theme.get());
    theme.toggle();
}
