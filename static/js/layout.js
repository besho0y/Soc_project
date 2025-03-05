function hometabs() {
  const hometabs = document.querySelectorAll(".menu-div");
  const currentPath = window.location.pathname; 

  hometabs.forEach(tab => tab.classList.remove("active"));

  // Map routes to tab names
  const routes = {
    "/home": "Home",
    "/scenario": "Scenarios",
    "/challenges": "Challenges",
    "/achievement": "Your Achievement"
  };
  const activeTab = routes[currentPath] || "Home";

  // Highlight the correct tab
  hometabs.forEach(tab => {
    if (tab.innerText.trim() === activeTab) {
      tab.classList.add('active');
    }
  });

  hometabs.forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelector(".menu-div.active")?.classList.remove("active");
      tab.classList.add("active");
      localStorage.setItem('activeTab', tab.innerText.trim());
    });
  });
}

document.addEventListener("DOMContentLoaded", hometabs);

function toggleMenu() {
  const menu = document.getElementById('profileMenu');
  menu.classList.toggle('show');
}

// Close menu if user clicks outside
window.addEventListener('click', function(e) {
  const menu = document.getElementById('profileMenu');
  const img = document.querySelector('.imgbox img');
  
  if (!menu.contains(e.target) && e.target !== img) {
      menu.classList.remove('show');
  }
});

