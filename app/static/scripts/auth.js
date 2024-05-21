const forms = document.querySelectorAll('form.auth');

for (const form of forms) {
    form.addEventListener('submit', function (event) {
        event.preventDefault();

        const data = new URLSearchParams()
        for (const pair of new FormData(this)) {
            data.append(pair[0], pair[1])
        }
        
        console.log(form.attributes.location.value)

        fetch(form.attributes.location.value, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: data,
            withCredentials: true,
        }).then(function (response) {
            if (response.status === 200) {
                location.replace('/')
            }
        })
    })
}
