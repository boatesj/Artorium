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
