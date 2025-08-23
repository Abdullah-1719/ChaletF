<script>
  // --- State ---
  let reservations = {}; // will come from server
  let current = new Date();

  // --- API helpers ---
  async function fetchReservations() {
    const res = await fetch("/api/reservations");
    reservations = await res.json();
  }

  async function createReservation(name, date) {
    const res = await fetch("/api/reservations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, date })
    });
    return res.json();
  }

  async function updateReservation(originalDate, newName, newDate) {
    const res = await fetch(`/api/reservations/${originalDate}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newName, date: newDate })
    });
    return res.json();
  }

  async function deleteReservation(date) {
    const res = await fetch(`/api/reservations/${date}`, { method: "DELETE" });
    return res.json();
  }

  async function searchReservations(query) {
    const res = await fetch(`/api/reservations/search?name=${encodeURIComponent(query)}`);
    return res.json();
  }

  // --- Calendar rendering (same as before) ---
  function pad(n){ return String(n).padStart(2,'0'); }
  function ymd(d){ return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`; }

  function buildCalendar(date) {
    const calendar = document.getElementById('calendar');
    const monthDisplay = document.getElementById('monthDisplay');
    calendar.innerHTML = '';

    const year = date.getFullYear();
    const month = date.getMonth();
    const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    const dow = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

    monthDisplay.textContent = `${monthNames[month]} ${year}`;

    dow.forEach(d => {
      const h = document.createElement('div');
      h.className = 'dow';
      h.textContent = d;
      calendar.appendChild(h);
    });

    const first = new Date(year, month, 1);
    const startOffset = first.getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    for (let i = 0; i < startOffset; i++) {
      const e = document.createElement('div');
      e.className = 'day empty';
      calendar.appendChild(e);
    }

    const today = new Date(); today.setHours(0,0,0,0);

    for (let day = 1; day <= daysInMonth; day++) {
      const cell = document.createElement('div');
      cell.className = 'day';

      const num = document.createElement('div');
      num.className = 'num';
      num.textContent = day;
      cell.appendChild(num);

      const thisDate = new Date(year, month, day);
      const key = ymd(thisDate);

      if (reservations[key]) {
        cell.classList.add('booked');
        const nameEl = document.createElement('div');
        nameEl.className = 'resv-name';
        nameEl.textContent = reservations[key].name;
        cell.appendChild(nameEl);
        cell.title = `Reserved by: ${reservations[key].name}`;
      } else {
        cell.classList.add('available');
        if (thisDate >= today) {
          cell.addEventListener('click', () => {
            const input = document.getElementById('checkin');
            input.value = key;
            document.getElementById('reserve').scrollIntoView({ behavior: 'smooth', block: 'start' });
          });
        } else {
          cell.classList.remove('available');
          cell.style.background = '#f1f1f1';
          cell.style.color = '#9aa0a6';
          cell.style.cursor = 'not-allowed';
          cell.title = 'Past date';
        }
      }

      if (ymd(thisDate) === ymd(today)) cell.classList.add('today');
      calendar.appendChild(cell);
    }
  }

  // --- Form handlers ---
  function showConfirmation(data) {
    const modal = document.getElementById('confirmationModal');
    const details = document.getElementById('bookingDetails');
    const checkinDate = new Date(data.checkin).toLocaleDateString();
    details.innerHTML = `<p><strong>Name:</strong> ${data.name}</p><p><strong>Reservation Date:</strong> ${checkinDate}</p>`;
    modal.style.display = 'block';
  }
  function closeModal(){ document.getElementById('confirmationModal').style.display = 'none'; }

  // --- Search results ---
  function renderSearchResults(list){
    const resultsDiv = document.getElementById('reservationResults');
    if (!Object.keys(list).length) {
      resultsDiv.innerHTML = '<p style="color:#6b7280">No reservations found for this name.</p>';
      return;
    }
    let html = '<h3 style="margin-bottom:8px">Your Reservations</h3>';
    Object.entries(list).forEach(([dateString, reservation]) => {
      const formatted = new Date(dateString).toLocaleDateString(undefined, { weekday:'long', year:'numeric', month:'long', day:'numeric' });
      html += `
        <div class="reservation-item">
          <div class="reservation-details">
            <div><strong>Name:</strong> ${reservation.name}</div>
            <div><strong>Date:</strong> ${formatted}</div>
            <div style="color:#6b7280">Key: ${dateString}</div>
          </div>
          <div class="actions">
            <button class="btn warn" onclick="editReservation('${dateString}')">Edit</button>
            <button class="btn danger" onclick="cancelReservation('${dateString}')">Cancel</button>
          </div>
        </div>`;
    });
    resultsDiv.innerHTML = html;
  }

  window.cancelReservation = async function(dateString){
    if (!reservations[dateString]) return alert('Reservation not found.');
    if (confirm('Cancel this reservation?')) {
      await deleteReservation(dateString);
      await fetchReservations();
      buildCalendar(current);
      document.getElementById('reservationResults').innerHTML = '<p style="color:#16a34a">Reservation cancelled. Search again to refresh.</p>';
    }
  }

  window.editReservation = function(dateString){
    const r = reservations[dateString];
    const resultsDiv = document.getElementById('reservationResults');
    const todayStr = new Date().toISOString().split('T')[0];
    resultsDiv.innerHTML = `
      <div class="section" style="padding:16px;">
        <h3 style="margin-bottom:10px;">Edit Reservation</h3>
        <div class="form-grid">
          <div>
            <label>Name</label>
            <input id="editName" value="${r.name}" />
          </div>
          <div>
            <label>New Date</label>
            <input type="date" id="editDate" value="${dateString}" min="${todayStr}" />
          </div>
        </div>
        <div class="actions" style="margin-top:12px;">
          <button class="btn" onclick="saveEdit('${dateString}')">Save Changes</button>
          <button class="btn light" onclick="document.getElementById('searchBtn').click()">Cancel</button>
        </div>
      </div>`;
  }

  window.saveEdit = async function(original){
    const newName = document.getElementById('editName').value.trim();
    const newDate = document.getElementById('editDate').value;
    if (!newName || !newDate) return alert('Please complete all fields.');
    const resp = await updateReservation(original, newName, newDate);
    if (resp.error) return alert(resp.error);
    await fetchReservations();
    buildCalendar(current);
    document.getElementById('searchBtn').click();
    alert('Reservation updated successfully!');
  }

  // --- Init ---
  document.addEventListener('DOMContentLoaded', async () => {
    await fetchReservations();
    const dateInput = document.getElementById('checkin');
    const todayStr = new Date().toISOString().split('T')[0];
    dateInput.min = todayStr;

    // calendar controls
    document.getElementById('prevBtn').addEventListener('click', async () => { current.setMonth(current.getMonth() - 1); buildCalendar(current); });
    document.getElementById('nextBtn').addEventListener('click', async () => { current.setMonth(current.getMonth() + 1); buildCalendar(current); });
    document.getElementById('todayBtn').addEventListener('click', async () => { current = new Date(); buildCalendar(current); });

    buildCalendar(current);

    // form submit
    document.getElementById('reservationForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const form = e.currentTarget;
      const name = form.name.value.trim();
      const checkin = form.checkin.value;
      if (!name || !checkin) return alert('Please complete the form.');
      const chosen = new Date(checkin); const today = new Date(); today.setHours(0,0,0,0);
      if (chosen < today) return alert('Reservation date cannot be in the past.');
      if (reservations[checkin]) return alert('This date is already reserved. Please choose another.');

      const resp = await createReservation(name, checkin);
      if (resp.error) return alert(resp.error);
      await fetchReservations();
      buildCalendar(current);
      showConfirmation({ name, checkin });
      form.reset();
    });

    // close modal
    document.getElementById('closeModalBtn').addEventListener('click', closeModal);
    window.addEventListener('click', (e) => { if (e.target.id === 'confirmationModal') closeModal(); });

    // search
    document.getElementById('searchBtn').addEventListener('click', async () => {
      const q = document.getElementById('searchName').value.trim();
      if (!q) return alert('Please enter a name to search.');
      const found = await searchReservations(q);
      renderSearchResults(found);
    });
  });
</script>
