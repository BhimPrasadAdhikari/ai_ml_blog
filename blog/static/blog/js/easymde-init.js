document.addEventListener("DOMContentLoaded", function() {
    var textarea = document.querySelector('textarea[name="content"]');
    if (textarea) {
        new EasyMDE({
            element: textarea
        });
    }
});