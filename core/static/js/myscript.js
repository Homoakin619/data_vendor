


// var pinModal = document.getElementById('pinModal')
// pinModal.addEventListener('show.bs.modal', function (event) {
  
//   // Button that triggered the modal
//   var button = event.relatedTarget

//   var price = button.getAttribute('data-bs-value');

//   var merchant = button.getAttribute('name');
//   var quantity = button.getAttribute('quantity');
 
//   document.querySelector("input[name='amounts']").value = price;

//   document.querySelector("input[name='merchant']").value = merchant;

//   document.querySelector("input[name='quantity']").value = quantity;
  
  
  
// })


// var style = {
//     base: {
//       // Add your base input styles here. For example:
//       fontSize: '16px',
//       color: '#32325d',
//     },
//   };
  
//   var pay_form = $('#payment-form')
//   if (pay_form.is(":visible")) {

//     var card = elements.create('card', {style: style});
  
//   // Add an instance of the card Element into the `card-element` <div>.
// card.mount('#card-element');

// // Create a token or display an error when the form is submitted.
// var form = document.getElementById('payment-form');
// form.addEventListener('submit', function(event) {
//   event.preventDefault();

//   stripe.createToken(card).then(function(result) {
//     if (result.error) {
//       // Inform the customer that there was an error.
//       var errorElement = document.getElementById('card-errors');
//       errorElement.textContent = result.error.message;
//     } else {
//       // Send the token to your server.
//       stripeTokenHandler(result.token);
//     }
//   });
// });


// function stripeTokenHandler(token) {
//     // Insert the token ID into the form so it gets submitted to the server
//     var form = document.getElementById('payment-form');
//     var hiddenInput = document.createElement('input');
//     hiddenInput.setAttribute('type', 'hidden');
//     hiddenInput.setAttribute('name', 'stripeToken');
//     hiddenInput.setAttribute('value', token.id);
//     form.appendChild(hiddenInput);

//     // Submit the form
//     form.submit();
//   }


//   }



//   var paymentModal = document.getElementById('paymentModal')
//   paymentModal.addEventListener('show.bs.modal', function (event) {
//     // Button that triggered the modal
//     var button = event.relatedTarget
//     // Extract info from data-bs-* attributes
//     var price = button.getAttribute('data-bs-value')
//     // If necessary, you could initiate an AJAX request here
//     // and then do the updating in a callback.
//     var balance = button.getAttribute('balance')
//     console.log(balance)
//     console.log(price)
//     // Update the modal's content.
//     // var modalTitle = paymentModal.querySelector('.modal-title')
//     var modalBodyInput = paymentModal.querySelector(".modal-body input[name='amount']")
  
//     // modalBodyInput.value = price
//     document.querySelector("input[name='amount']").value = price
//   })



// *************************************************************************************
// Tested and working script for single page

// var response = fetch('/payment').then(function(response) {
//     return response.json();
//   }).then(function(responseJson) {
//     var clientSecret = responseJson.client_secret;
//     // Render the form to collect payment details, then
//     // call stripe.confirmCardPayment() with the client secret.

//     // /////////////////////////////////////////////////

//     var elements = stripe.elements();
//     var style = {
//     base: {
//         color: "#32325d",
//     }
//     };

//     var card = elements.create("card", { style: style });
//     card.mount("#card-element");

//     card.on('change', function(event) {
//         var displayError = document.getElementById('card-errors');
//         if (event.error) {
//         displayError.textContent = event.error.message;
//         } else {
//         displayError.textContent = '';
//         }
//     });


//     var form = document.getElementById('payment-form');

//     form.addEventListener('submit', function(ev) {
//     ev.preventDefault();
//     // If the client secret was rendered server-side as a data-secret attribute
//     // on the <form> element, you can retrieve it here by calling `form.dataset.secret`
//     stripe.confirmCardPayment(clientSecret, {
//         payment_method: {
//         card: card,
//         billing_details: {
//             name: 'Jenny Rosen'
//         }
//         }
//     }).then(function(result) {
//         if (result.error) {
//         // Show error to your customer (for example, insufficient funds)
//         console.log(result.error.message);
//         } else {
//         // The payment has been processed!
//         if (result.paymentIntent.status === 'succeeded') {
//             // Show a success message to your customer
//             // There's a risk of the customer closing the window before callback
//             // execution. Set up a webhook or plugin to listen for the
//             // payment_intent.succeeded event that handles any business critical
//             // post-payment actions.
//             alert('Payment success!')
//         }
//         }
//     });
//     });

//     // ////////////////////////////////////////////////
//   });


