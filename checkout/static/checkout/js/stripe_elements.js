/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

// Retrieve public key and client secret from the DOM
var stripe_public_key = document.getElementById('id_stripe_public_key').textContent.trim();
var client_secret = document.getElementById('id_client_secret').textContent.trim();

// Initialize Stripe
var stripe = Stripe(stripe_public_key);
var elements = stripe.elements();

// Define styling for the card element
var style = {
    base: {
        color: '#000', 
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4' 
        }
    },
    invalid: {
        color: '#dc3545', 
        iconColor: '#dc3545' 
    }
};

// Create and mount the card element
var card = elements.create('card', {style: style});
card.mount('#card-element');

// Handle real-time validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        errorDiv.innerHTML = html;
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submission
var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    card.update({ 'disabled': true }); // Disable card input
    document.getElementById('submit-button').setAttribute('disabled', true);

    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
        }
    }).then(function(result) {
        if (result.error) {
            // Display error message to the user
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>
            `;
            errorDiv.innerHTML = html;

            // Re-enable card input and button
            card.update({ 'disabled': false });
            document.getElementById('submit-button').removeAttribute('disabled');
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                // Submit the form if the payment is successful
                form.submit();
            }
        }
    });
});
