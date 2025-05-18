document.addEventListener('DOMContentLoaded', function () {
    const decreaseServingsButton = document.getElementById('decrease-servings');
    const increaseServingsButton = document.getElementById('increase-servings');
    const currentServingsSpan = document.getElementById('current-servings');
    let currentServings = 1;
    const ingredientItems = document.querySelectorAll('.ingredient-item');

    function initializeServings() {
        // Находим первое блюдо
        if (ingredientItems.length > 0) {
            // Находим кол-во порций первого ингредиента
            const baseServings = parseFloat(ingredientItems[0].dataset.baseServings);
            currentServings = baseServings;
        } else {
            currentServings = 1;
        }
        currentServingsSpan.textContent = currentServings;
        updateIngredients(currentServings); // Обновляем ингредиенты при загрузке страницы
    }

    initializeServings();

    decreaseServingsButton.addEventListener('click', function () {
        if (currentServings > 1) {
            currentServings--;
            updateIngredients(currentServings);
        }
    });

    increaseServingsButton.addEventListener('click', function () {
        currentServings++;
        updateIngredients(currentServings);
    });

    function updateIngredients(servings) {
        currentServingsSpan.textContent = servings;

        ingredientItems.forEach(item => {
            const baseWeight = parseFloat(item.dataset.baseWeight);
            const baseServings = parseFloat(item.dataset.baseServings);
            let newWeight = (baseWeight / baseServings) * servings;

            // Ограничиваем количество знаков после запятой
            newWeight = parseFloat(newWeight.toFixed(2)); // Округляем до 2 знаков после запятой

            item.querySelector('.ingredient-weight').textContent = newWeight + ' ' + item.querySelector('.ingredient-weight').textContent.split(' ')[1]; // Добавляем единицы измерения
        });
    }
});