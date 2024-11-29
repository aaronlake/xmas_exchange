document.getElementById('submit').addEventListener('click', function() {
  const codeInput = document.getElementById('code');
  const code = codeInput.value.trim().toUpperCase();

  // Replace with your actual API endpoint
  const apiEndpoint = 'https://kytphi0459.execute-api.us-east-2.amazonaws.com/prod/code';

  if (code.length !== 4) {
    displayMessage('Please enter a valid 4-digit code.', true);
    return;
  }

  fetch(`${apiEndpoint}?code=${code}`)
    .then(response => response.json())
    .then(data => {
      if (data.giftee) {
        displayMessage(`Your giftee is: ${data.giftee}`, false);
        launchConfetti();
      } else {
        displayMessage(data.message || 'Invalid code.', true);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      displayMessage('An error occurred. Please try again later.', true);
    });
});

function displayMessage(message, isError) {
  const messageEl = document.getElementById('message');
  messageEl.style.color = isError ? 'red' : 'green';
  messageEl.textContent = message;
}

function launchConfetti() {
  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 }
  });
}