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


//challenges
document.addEventListener("DOMContentLoaded", function() {
  fetch('/api/challenges')
      .then(response => response.json())
      .then(data => {
          const challengesSec = document.querySelector('.challenges-sec');

          // Clear existing content if needed
          challengesSec.innerHTML = '';

          // Loop through the challenges data and create divs
          data.forEach(challenge => {
              const challengeDiv = document.createElement('div');
              challengeDiv.classList.add('challenges-div');

              // Create the inner structure
              challengeDiv.innerHTML = `
                  <div class="challenges-text-box">
                      <h3>${challenge.title}</h3>
                      <p class="challenges-title">${challenge.description}</p>
                      <div class="challenge-lvl">
                          <p class="orange">${challenge.lvl}</p>
                          <p class="red">${challenge.points} pt</p>
                          <p class="green">${challenge.duration} min</p>
                      </div>
                      <button class="challenge-btn">Start Challenge</button>
                  </div>
              `;

              challengesSec.appendChild(challengeDiv);
          });
      })
      .catch(error => console.error('Error fetching challenges:', error));
});


document.addEventListener("DOMContentLoaded", function() {
  fetch('/api/scenarios')
      .then(response => {
          if (!response.ok) {
              throw new Error('Network response was not ok ' + response.statusText);
          }
          return response.json();
      })
      .then(data => {
          const scenariosDiv = document.querySelector('.scenarios');

          // Clear existing content if needed
          scenariosDiv.innerHTML = '';

          // Loop through the scenarios data and create divs
          data.forEach(scenario => {
              const scenarioBox = document.createElement('div');
              scenarioBox.classList.add('scenario-box');

              // Create the inner structure with background image
              scenarioBox.innerHTML = `
                  <div class="scenario-img" style="background-image: url('${scenario.img}');">
                      <h3 class="scenario-title">${scenario.title}</h3>
                      <h4 class="scenario-lvl">${scenario.lvl}</h4>
                      <h4 class="scenario-points">${scenario.points}</h4>
                  </div>
                  <div class="Scenario-text-box">
                      <p class="scenarios-des">${scenario.description}</p>
                      <p>Most Defenders considered this Investigation <span>${scenario.lvl}</span></p>
                      <button class="scenario-btn">Start Scenario</button>
                  </div>
              `;

              scenariosDiv.appendChild(scenarioBox);
          });
      })
      .catch(error => console.error('Error fetching scenarios:', error));
});







