/* app.js — unified frontend behaviour */

/* API root */
const API = window.location.origin + "/api";

/* ================= ACTIVITY LOG ================= */
function logActivity(action){
  const logs = JSON.parse(localStorage.getItem("gym_logs") || "[]");
  logs.unshift({
    action,
    time: new Date().toLocaleString()
  });
  localStorage.setItem("gym_logs", JSON.stringify(logs.slice(0, 50)));
}

/* ================= AUTH helpers ================= */
function requireAuth(){
  if (location.pathname.endsWith("/login.html") || location.pathname === "/login.html") return;
  if (location.pathname.endsWith("/signup.html") || location.pathname === "/signup.html") return;

  if (localStorage.getItem("gym_authenticated") !== "1"){
    window.location.href = "/login.html";
  }
}

function logout(){
  logActivity("User logged out");
  localStorage.removeItem("gym_authenticated");
  localStorage.removeItem("gym_auth_email");
  localStorage.removeItem("gym_role");
  window.location.href = "/login.html";
}

/* ================= ROLE GUARD ================= */
function requireAdmin(){
  const role = localStorage.getItem("gym_role");
  if(role !== "admin"){
    alert("Access denied: Admins only.");
    window.location.href = "/dashboard.html";
  }
}

/* Hide admin-only links for members */
document.addEventListener("DOMContentLoaded", ()=>{
  if(localStorage.getItem("gym_role") !== "admin"){
    document.querySelectorAll(".admin-only").forEach(el => el.remove());
  }
});

/* ================= Sidebar active highlight ================= */
function highlightSidebar(){
  const current = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".sidebar-nav a").forEach(a=>{
    if (a.getAttribute("href") === current) {
      a.style.background = "rgba(255,77,77,0.12)";
      a.style.fontWeight = "700";
    }
  });
}

/* ================= Dark mode ================= */
function toggleDarkMode(){
  document.body.classList.toggle("dark");
  localStorage.setItem("darkMode", document.body.classList.contains("dark") ? "1":"0");
}

function initDark(){
  if (localStorage.getItem("darkMode")==="1") document.body.classList.add("dark");
}

/* escape */
function esc(s){ 
  return String(s ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

/* ---------- MEMBERS ---------- */
async function loadMembers(){
  const el = document.getElementById("membersTable");
  if(!el) return;
  const res = await fetch(`${API}/members`);
  const data = await res.json();
  let html = `<tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Plan</th></tr>`;
  data.forEach(m=>{
    html += `<tr>
      <td>${m.id}</td>
      <td>${esc(m.name)}</td>
      <td>${esc(m.email)}</td>
      <td>${esc(m.phone)}</td>
      <td>${m.plan_id||"None"}</td>
    </tr>`;
  });
  el.innerHTML = html;
}

async function postMember(form){
  const body = {
    name: form.name.value,
    email: form.email.value,
    phone: form.phone.value,
    plan_id: form.plan_id.value || null
  };
  const res = await fetch(`${API}/members`, { 
    method:"POST", 
    headers:{ "Content-Type":"application/json" }, 
    body: JSON.stringify(body) 
  });
  if(!res.ok) { alert("Failed to add member"); return; }
  logActivity("New member added");
  form.reset();
  loadMembers();
}

/* ---------- TRAINERS ---------- */
async function loadTrainers(){
  const el = document.getElementById("trainersTable");
  if(!el) return;
  const res = await fetch(`${API}/trainers`);
  const data = await res.json();
  let html = `<tr><th>ID</th><th>Name</th><th>Specialization</th><th>Salary</th></tr>`;
  data.forEach(t => html += `<tr>
    <td>${t.id}</td>
    <td>${esc(t.name)}</td>
    <td>${esc(t.specialization)}</td>
    <td>${t.salary}</td>
  </tr>`);
  el.innerHTML = html;
}

async function postTrainer(form){
  const body = { 
    name: form.name.value, 
    specialization: form.specialization.value, 
    salary: parseFloat(form.salary.value) || 0 
  };
  const res = await fetch(`${API}/trainers`, { 
    method: "POST", 
    headers:{"Content-Type":"application/json"}, 
    body: JSON.stringify(body) 
  });
  if(!res.ok) { alert("Failed add trainer"); return; }
  logActivity("Trainer added");
  form.reset(); 
  loadTrainers();
}

/* ---------- EQUIPMENT ---------- */
async function loadEquipment(){
  const el = document.getElementById("equipmentTable");
  if(!el) return;
  const res = await fetch(`${API}/equipment`);
  const data = await res.json();
  let html = `<tr><th>ID</th><th>Name</th><th>Category</th><th>Qty</th><th>Condition</th></tr>`;
  data.forEach(e=> html += `<tr>
    <td>${e.id}</td>
    <td>${esc(e.name)}</td>
    <td>${esc(e.category)}</td>
    <td>${e.quantity}</td>
    <td>${esc(e.condition)}</td>
  </tr>`);
  el.innerHTML = html;
}

async function postEquipment(form){
  const body = { 
    name: form.name.value, 
    category: form.category.value, 
    quantity: parseInt(form.quantity.value)||0, 
    condition: form.condition.value 
  };
  const res = await fetch(`${API}/equipment`, { 
    method:"POST", 
    headers:{"Content-Type":"application/json"}, 
    body: JSON.stringify(body) 
  });
  if(!res.ok){ alert("Failed"); return; }
  logActivity("Equipment added");
  form.reset(); 
  loadEquipment();
}

/* ---------- PLANS ---------- */
async function loadPlans(){
  const el = document.getElementById("plansTable");
  if(!el) return;
  const res = await fetch(`${API}/plans`);
  const data = await res.json();
  let html = `<tr><th>ID</th><th>Name</th><th>Price</th><th>Duration days</th></tr>`;
  data.forEach(p=> html += `<tr>
    <td>${p.id}</td>
    <td>${esc(p.name)}</td>
    <td>${p.price}</td>
    <td>${p.duration_days}</td>
  </tr>`);
  el.innerHTML = html;
}

async function postPlan(form){
  const body = { 
    name: form.name.value, 
    price: parseFloat(form.price.value)||0, 
    duration_days: parseInt(form.duration_days.value)||30 
  };
  const res = await fetch(`${API}/plans`, { 
    method:"POST", 
    headers:{"Content-Type":"application/json"}, 
    body: JSON.stringify(body) 
  });
  if(!res.ok) { alert("Failed add plan"); return; }
  logActivity("Plan added");
  form.reset(); 
  loadPlans();
}

/* ---------- PAYMENTS ---------- */
async function loadPayments(){
  const el = document.getElementById("paymentsTable");
  if(!el) return;
  const res = await fetch(`${API}/payments`);
  const data = await res.json();
  let html = `<tr><th>ID</th><th>Member</th><th>Amount</th><th>Method</th><th>Date</th></tr>`;
  data.forEach(p=> html += `<tr>
    <td>${p.id}</td>
    <td>${esc(p.member_name||("ID:"+p.member_id))}</td>
    <td>${p.amount}</td>
    <td>${esc(p.method||"")}</td>
    <td>${p.date}</td>
  </tr>`);
  el.innerHTML = html;
}

async function postPayment(form){
  const body = { 
    member_id: parseInt(form.member_id.value), 
    amount: parseFloat(form.amount.value)||0, 
    method: form.method.value 
  };
  const res = await fetch(`${API}/payments`, { 
    method:"POST", 
    headers:{"Content-Type":"application/json"}, 
    body: JSON.stringify(body) 
  });
  if(!res.ok) { alert("Failed to add payment"); return; }
  logActivity("Payment recorded");
  form.reset(); 
  loadPayments();
}

/* ---------- ATTENDANCE ---------- */
async function loadAttendance(){
  const el = document.getElementById("attendanceTable");
  if(!el) return;
  const res = await fetch(`${API}/attendance`);
  const data = await res.json();
  let html = `<tr><th>ID</th><th>Member</th><th>Status</th><th>Date</th></tr>`;
  data.forEach(a=> html += `<tr>
    <td>${a.id}</td>
    <td>${esc(a.member_name||("ID:"+a.member_id))}</td>
    <td>${esc(a.status)}</td>
    <td>${a.date}</td>
  </tr>`);
  el.innerHTML = html;
}

async function postAttendance(form){
  const body = { 
    member_id: parseInt(form.member_id.value), 
    status: form.status.value 
  };
  const res = await fetch(`${API}/attendance`, { 
    method:"POST", 
    headers:{"Content-Type":"application/json"}, 
    body: JSON.stringify(body) 
  });
  if(!res.ok) { alert("Failed add attendance"); return; }
  logActivity("Attendance marked");
  form.reset(); 
  loadAttendance();
}

/* ======================================================
   SIGNUP
====================================================== */
async function handleSignup(){
  const form = document.getElementById("signupForm");
  if(!form) return;

  form.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const msg = document.getElementById("signupMsg");

    const body = {
      name: suName.value.trim(),
      gender: suGender.value,
      age: suAge.value.trim(),
      phone: suPhone.value.trim(),
      email: suEmail.value.trim().toLowerCase(),
      password: suPassword.value.trim(),
    };
    const confirm = suConfirm.value.trim();

    if(Object.values(body).includes("") || !confirm){
      msg.innerText = "Please fill all fields.";
      return;
    }
    if(body.password !== confirm){
      msg.innerText = "Passwords do not match.";
      return;
    }

    msg.innerText = "Creating account...";

    const res = await fetch(`${API}/auth/signup`, {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify(body)
    });

    if(!res.ok){
      msg.innerText = "Signup failed";
      return;
    }

    logActivity("New member signed up");
    msg.innerText = "Account created! Redirecting...";
    setTimeout(()=> location.href="login.html", 1500);
  });
}

/* ======================================================
   INIT
====================================================== */
document.addEventListener("DOMContentLoaded", ()=>{
  initDark(); 
  highlightSidebar();
  handleSignup();
  requireAuth();

  if(membersTable) loadMembers();
  if(trainersTable) loadTrainers();
  if(equipmentTable) loadEquipment();
  if(plansTable) loadPlans();
  if(paymentsTable) loadPayments();
  if(attendanceTable) loadAttendance();
});

/* ================= UI HELPERS ================= */
function showToast(message){
  let toast = document.getElementById("toast");
  if(!toast){
    toast = document.createElement("div");
    toast.id = "toast";
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.innerText = message;
  toast.classList.add("show");
  setTimeout(()=> toast.classList.remove("show"), 2200);
}
