
document.querySelectorAll('.favorite-button').forEach(function (button) {
    button.addEventListener('click', function () {
        var recipeCard = this.parentElement;
        var recipeId = recipeCard.querySelector('a').href.split('/').pop();

        if (this.classList.contains('favorite-button-add')) {
            addToFavorites(recipeId, function () {
                button.classList.remove('favorite-button-add');
                button.classList.add('favorite-button-del');
                button.textContent = 'Удалить из любимого';
            });
        } else {
            removeFromFavorites(recipeId, function () {
                button.classList.remove('favorite-button-del');
                button.classList.add('favorite-button-add');
                button.textContent = 'Добавить в любимое';
            });
        }
    });
});

function addToFavorites(recipeId, callback) {

    fetch(`/api/v1/recipes/${recipeId}/favorites/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        withCredentials: true,
    })
    console.log('Добавить в любимое:', recipeId);
    callback();
}

function removeFromFavorites(recipeId, callback) {
    fetch(`/api/v1/recipes/${recipeId}/favorites/`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        withCredentials: true,
    })
    console.log('Удалить из любимого:', recipeId);
    callback();
}
