function disableUnavailableDates(vehicleId) {
    var unavailable_dates = {{ unavailable_dates | tojson }};
    var startInput = document.getElementById('modal-bg-date-' + vehicleId);
    var endInput = document.getElementById('modal-end-date-' + vehicleId);

    unavailable_dates.forEach(entry => {
        entry.start_date = new Date(entry.start_date);
        entry.end_date = new Date(entry.end_date);
    });

    function isUnavailable(date) {
        var d = new Date(date);
        return unavailable_dates.some(entry => d >= entry.start_date && d <= entry.end_date);
    }

    function disableDates(input) {
        input.addEventListener('input', function() {
            if (isUnavailable(this.value)) {
                alert('This date is unavailable. Please choose another.');
                this.value = '';  // Limpa o campo se for inválido
            }
        });
    }

    disableDates(startInput);
    disableDates(endInput);
}

{% for vehicle in vehicles %}
        document.getElementById('confirm-dates-{{ vehicle.id }}').addEventListener('click', function() {
            var start_date = document.getElementById('modal-bg-date-{{ vehicle.id }}').value;
            var end_date = document.getElementById('modal-end-date-{{ vehicle.id }}').value;
            var unavailable_dates = {{ unavailable_dates | tojson }};  // Recebe a lista já em formato JSON

            if (!start_date || !end_date) {
                alert('Please, both dates must be selected.');
                return;
            }

            const start = new Date(start_date);
            const end = new Date(end_date);

            if (end <= start) {
                alert('Ending date must be after starting date');
                return;
            }

            unavailable_dates = unavailable_dates.map(entry => ({
                vehicle_id: entry.vehicle_id,
                start_date: new Date(entry.start_date),
                end_date: new Date(entry.end_date)
            }));


            function isDateUnavailable(newStart, newEnd) {
                for (let i = 0; i < unavailable_dates.length; i++) {
                    const reservedStart = unavailable_dates[i].start_date;
                    const reservedEnd = unavailable_dates[i].end_date;

                    if ((newStart < reservedEnd && newEnd > reservedStart)) {
                        return true;
                    }
                }
                return false;
            }
            if (isDateUnavailable(start, end)) {
                alert('These dates are already reserved. Please choose different dates.');
                return;
            }
            const days_difference = Math.ceil((end - start) / (1000 * 3600 * 24));
            const price_per_day = {{ vehicle.price_day }};
            const total = days_difference * price_per_day;

            var start_dt = new Date(start).toLocaleDateString('en-US');
            var end_dt = new Date(end).toLocaleDateString('en-US');

            document.getElementById('total-price-{{ vehicle.id }}').textContent = total;
            document.getElementById('pay-price-{{ vehicle.id }}').textContent = total;
            document.getElementById('pay-ref-price-{{ vehicle.id }}').textContent = total;

            document.getElementById('start-date-{{ vehicle.id }}').textContent = start_dt;
            document.getElementById('end-date-{{ vehicle.id }}').textContent = end_dt;

            document.getElementById('proceed-payment-{{ vehicle.id }}').disabled = false;
        });

        document.getElementById('payment-{{ vehicle.id }}').addEventListener('click', function() {
            var start_date = document.getElementById('modal-bg-date-{{ vehicle.id }}').value;
            var end_date = document.getElementById('modal-end-date-{{ vehicle.id }}').value;

            const data = {
                vehicle_id: {{ vehicle.id }},
                vehicle_model: {{ vehicle.model | tojson }},
                start_date: start_date,
                end_date: end_date,
                total: document.getElementById('pay-price-{{ vehicle.id }}').textContent
            };

            fetch('/create_reservations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Reservation successful!');
                    var reserveModal = bootstrap.Modal.getInstance(document.getElementById('reg-modal-{{ vehicle.id }}'));
                    reserveModal.hide();

                    var payModal = bootstrap.Modal.getInstance(document.getElementById('pay-modal-{{ vehicle.id }}'));
                    if (payModal) {
                        payModal.hide();
                    }

                    document.getElementById('reserve-id-{{ vehicle.id }}').textContent = data.reservation_id;

                    var newPayModal = new bootstrap.Modal(document.getElementById('pay-ref-modal-{{ vehicle.id }}'));
                    newPayModal.show();
                } else {
                    alert('There was an error with your reservation. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while processing your reservation. Please try again later.');
            });
        });

        document.getElementById('pay-ref-{{ vehicle.id }}').addEventListener('click', function() {
            var reserve_id = document.querySelector('#reserve-id-{{ vehicle.id }}').textContent.trim();
            var entity = document.getElementById('entity-{{ vehicle.id }}').dataset.entity;
            var reference = document.getElementById('reference-{{ vehicle.id }}').dataset.reference;
            var amount = document.querySelector('#pay-ref-price-{{ vehicle.id }}').textContent.trim();

            const data = {
                reserve_id: reserve_id,
                entity: entity,
                reference: reference,
                amount: amount
            };

            console.log("Payment data registed", data);

            fetch('/create_payment', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    var payRefModal = bootstrap.Modal.getInstance(document.getElementById('pay-ref-modal-{{ vehicle.id }}'));
                    payRefModal.hide();
                })
                .catch(error => {
                    console.error('An error occurred while processing your payment data. Please try again later.', error);
                });
        });

        document.addEventListener('DOMContentLoaded', function() {
            disableUnavailableDates({{ vehicle.id }});
        });
    {% endfor %}
