document.addEventListener("DOMContentLoaded", function () {
    const firstBannerElements = ['.first_banner h1', '.first_banner h2'];
    const indexRecipesElements = ['.index_recipes h2', '.index_recipes-button'];
    const cardIndexElements = ['.card_index-large-inner', '.card_index-small-container'];
    const otherElements = ['.index_news'];
    const authorElements = ['.index_author', '.index_author h2'];
    const articlesElement = ['.index_articles', '.card_index-group'];

    const allElements = [
        ...firstBannerElements,
        ...indexRecipesElements,
        ...cardIndexElements,
        ...otherElements,
        ...authorElements,
        ...articlesElement,
    ];

    const elements = document.querySelectorAll(allElements.join(', '));

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.2
    });

    elements.forEach(el => {
        observer.observe(el);
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const clearButtons = document.querySelectorAll('.clear-input');

    clearButtons.forEach(button => {
        button.addEventListener('click', function () {
            const targetId = this.dataset.target;
            const inputField = document.getElementById(targetId);
            inputField.value = '';

            this.closest('form').submit();
        });
    });
});



    // JavaScript для отправки формы фильтрации при изменении select и input.
    document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.querySelector('.filter-form');
    const categorySelect = document.getElementById('category');
    const kitchenSelect = document.getElementById('kitchen');
    const ingredientInput = document.getElementById('ingredient');
    const nameInput = document.getElementById('name');


    categorySelect.addEventListener('change', function() {
    // You can optionally submit the form immediately here, or wait for the "Apply" button
    //filterForm.submit();
});

    kitchenSelect.addEventListener('change', function() {
    //filterForm.submit();
});

    // You can also trigger a form submission on input changes in the ingredient and name fields.
    ingredientInput.addEventListener('input', function() {
    //  filterForm.submit(); // Optional: Submit form on ingredient change
});

    nameInput.addEventListener('input', function() {
    // filterForm.submit(); // Optional: Submit form on name change
});


    // Clear input button functionality (assuming this functionality already exists).
    const clearButtons = document.querySelectorAll('.clear-input');
    clearButtons.forEach(button => {
    button.addEventListener('click', function(event) {
    const target = this.dataset.target;
    document.getElementById(target).value = '';
    filterForm.submit();  // Submit form after clearing input
});
});
});
