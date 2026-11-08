const STORAGE_KEY = "laundry-queue-v1";

const form = document.querySelector("#booking-form");
const rows = document.querySelector("#schedule-rows");
const empty = document.querySelector("#empty-queue");
const message = document.querySelector("#form-message");
const summary = document.querySelector("#queue-summary");
const startInput = document.querySelector("#start-time");
const filterButtons = [...document.querySelectorAll("[data-machine]")];

let bookings = readBookings();
let selectedMachine = "all";

startInput.value = toInputValue(roundToQuarterHour(new Date()));
render();
setInterval(render, 30000);

form.addEventListener("submit", (event) => {
  event.preventDefault();
  message.textContent = "";
  const data = new FormData(form);
  const start = new Date(String(data.get("start")));
  const duration = Number(data.get("duration"));
  const end = new Date(start.getTime() + duration * 60000);
  const machine = String(data.get("machine"));

  const conflict = bookings.find((booking) => {
    if (booking.machine !== machine) return false;
    const existingStart = new Date(booking.start);
    const existingEnd = new Date(booking.end);
    return start < existingEnd && end > existingStart;
  });

  if (conflict) {
    message.textContent = `${machine} is already booked by ${conflict.resident} during that time.`;
    return;
  }

  bookings.push({
    id: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
    resident: String(data.get("resident")).trim(),
    machine,
    start: start.toISOString(),
    end: end.toISOString()
  });
  saveBookings();
  form.reset();
  form.elements.duration.value = "45";
  startInput.value = toInputValue(roundToQuarterHour(new Date()));
  render();
});

rows.addEventListener("click", (event) => {
  const button = event.target.closest("[data-remove]");
  if (!button) return;
  bookings = bookings.filter((booking) => booking.id !== button.dataset.remove);
  saveBookings();
  render();
});

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    selectedMachine = button.dataset.machine;
    filterButtons.forEach((item) => item.classList.toggle("active", item === button));
    render();
  });
});

document.querySelector("#clear-finished").addEventListener("click", () => {
  const now = Date.now();
  bookings = bookings.filter((booking) => new Date(booking.end).getTime() > now);
  saveBookings();
  render();
});

document.querySelector("#add-example").addEventListener("click", () => {
  const base = roundToQuarterHour(new Date());
  bookings = [
    createExample("Room 201 / An", "Washer 1", base, 45),
    createExample("Room 407 / Jo", "Dryer 1", new Date(base.getTime() + 30 * 60000), 60),
    createExample("Room 118 / Li", "Washer 2", new Date(base.getTime() + 75 * 60000), 35)
  ];
  saveBookings();
  render();
});

function render() {
  const visible = bookings
    .filter((booking) => selectedMachine === "all" || booking.machine === selectedMachine)
    .sort((a, b) => a.start.localeCompare(b.start));

  rows.replaceChildren(...visible.map(createRow));
  empty.hidden = visible.length > 0;

  const running = bookings.filter((booking) => statusOf(booking).key === "running").length;
  const upcoming = bookings.filter((booking) => statusOf(booking).key === "upcoming").length;
  summary.textContent = `${bookings.length} bookings · ${running} running · ${upcoming} upcoming`;
}

function createRow(booking) {
  const state = statusOf(booking);
  const row = document.createElement("div");
  row.className = "schedule-row";
  row.innerHTML = `
    <span>${escapeHtml(booking.machine)}</span>
    <span class="resident">${escapeHtml(booking.resident)}</span>
    <span>${formatDateTime(booking.start)}</span>
    <span>${formatDateTime(booking.end)}</span>
    <span class="state ${state.key}">${state.label}</span>
    <div><button class="remove-booking" type="button" data-remove="${booking.id}">Remove</button></div>
  `;
  return row;
}

function statusOf(booking) {
  const now = Date.now();
  const start = new Date(booking.start).getTime();
  const end = new Date(booking.end).getTime();
  if (now >= start && now < end) return { key: "running", label: "Running" };
  if (now < start) return { key: "upcoming", label: "Upcoming" };
  return { key: "finished", label: "Finished" };
}

function createExample(resident, machine, start, minutes) {
  return {
    id: `${machine}-${start.getTime()}`,
    resident,
    machine,
    start: start.toISOString(),
    end: new Date(start.getTime() + minutes * 60000).toISOString()
  };
}

function roundToQuarterHour(date) {
  const next = new Date(date);
  next.setSeconds(0, 0);
  next.setMinutes(Math.ceil(next.getMinutes() / 15) * 15);
  return next;
}

function toInputValue(date) {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 16);
}

function formatDateTime(value) {
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

function readBookings() {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY));
    return Array.isArray(stored) ? stored : [];
  } catch {
    return [];
  }
}

function saveBookings() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(bookings));
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
