document.querySelectorAll('.add-filter').forEach(function (addFilterButton) {
    addFilterButton.addEventListener('click', function () {
        if (this.previousElementSibling.value === '') return

        var filterInput = document.createElement('input');
        filterInput.type = 'text';
        filterInput.placeholder = this.previousElementSibling.placeholder;
        filterInput.value = this.previousElementSibling.value;
        this.previousElementSibling.value = '';

        var deleteButton = document.createElement('button');
        deleteButton.className = 'del-filter';
        deleteButton.innerText = '✖';
        deleteButton.addEventListener('click', function () {
            this.parentElement.parentElement.removeChild(this.parentElement);
        });

        var container = document.createElement('div');
        container.className = 'inputs';
        container.appendChild(filterInput);
        container.appendChild(deleteButton);

        this.parentElement.parentElement.appendChild(container);
    });
});

document.querySelector('form.search').addEventListener('submit', function (event) {
    event.preventDefault()

    var name = document.querySelector('form.search input').value

    var ingredients = []
    document.querySelectorAll('.ingredients input').forEach(function (input) {
        if (input.value !== '') {
            ingredients.push(input.value);
        }
    });
    var tags = []
    document.querySelectorAll('.tags input').forEach(function (input) {
        if (input.value !== '') {
            tags.push(input.value);
        }
    });

    let searchQuery = `/?`
    if (name !== '')
        searchQuery += `name=${name}`

    for (let ingredient of ingredients) {
        searchQuery += `&ingredients=${ingredient}`
    }

    for (let tag of tags) {
        searchQuery += `&tags=${tag}`
    }

    location.replace(searchQuery);
    console.log('Поиск:', searchQuery);
});

