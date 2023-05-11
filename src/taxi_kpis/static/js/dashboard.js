fetch('/dashboard')
    .then(response => response.json())
    .then(data => {
        console.log(data)
        document.getElementById('avg_price').innerHTML = data['avg_price_per_mile'];
        document.getElementById('custom_indicator').innerHTML = data.custom_indicator.toFixed(2);

        let paymentTypes = '';
        for (let type in data.payment_type_counts) {
            paymentTypes += '<li>' + type + ': ' + data.payment_type_counts[type] + '</li>';
        }
        document.getElementById('payment_types').innerHTML = paymentTypes;
    })
    .catch(error => console.error(error));


