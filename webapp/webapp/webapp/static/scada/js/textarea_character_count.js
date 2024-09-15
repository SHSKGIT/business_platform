// for any textarea max length dynamic update
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('comment');
    const counter = document.querySelector('.char-counter');
    const maxLength = textarea.getAttribute('maxlength');

    // Update counter as the user types
    textarea.addEventListener('input', function() {
        const currentLength = textarea.value.length;
        counter.textContent = `${currentLength} / ${maxLength}`;
    });
});