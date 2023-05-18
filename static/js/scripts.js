
function validatePasswords(event) {
  var passwordInput = document.getElementById('password');
  var confirmPasswordInput = document.getElementById('confirm_password');
  var passwordError = document.getElementById('password-error');

  if (passwordInput.value !== confirmPasswordInput.value) {
    event.preventDefault();
    passwordError.textContent = 'Passwords do not match';
  } else {
    passwordError.textContent = '';
  }
}
async function makeReservation() {
  const name = document.getElementById('name').value;
  const phone = document.getElementById('phone').value;
  const email = document.getElementById('email').value;
  const datetime = document.getElementById('datetime').value;
  const guests = document.getElementById('guests').value;

  if (name && phone && email && datetime && guests) {
    const reservationData = {
      name: name,
      phone: phone,
      email: email,
      datetime: datetime,
      guests: guests
    };

    try {
      const response = await fetch('/api/reservations', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(reservationData)
      });

      if (response.ok) {
        const jsonResponse = await response.json();
        alert(jsonResponse['message']);
      } else {
        alert(
            'An error occurred while making the reservation. Please try again.');
      }
    } catch (error) {
      console.error('Error:', error);
      alert(
          'An error occurred while making the reservation. Please try again.');
    }
  } else {
    alert('Please fill in all fields to make a reservation.');
  }
}


async function makeReservationLoggedIn(name, phone, email) {
  const datetime = document.getElementById('datetime').value;
  const guests = document.getElementById('guests').value;

  if (name && phone && email && datetime && guests) {
    const reservationData = {
      name: name,
      phone: phone,
      email: email,
      datetime: datetime,
      guests: guests
    };

    try {
      const response = await fetch('/api/reservations', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(reservationData)
      });

      if (response.ok) {
        const jsonResponse = await response.json();
        alert(jsonResponse['message']);
      } else {
        alert(
            'An error occurred while making the reservation. Please try again.');
      }
    } catch (error) {
      console.error('Error:', error);
      alert(
          'An error occurred while making the reservation. Please try again.');
    }
  } else {
    alert('Please fill in all fields to make a reservation.');
  }
}
