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
window.addEventListener('click', function (e) {
    const menu = document.getElementById('profileMenu');
    const img = document.querySelector('.imgbox img');

    if (!menu.contains(e.target) && e.target !== img) {
        menu.classList.remove('show');
    }
});


//challenges
document.addEventListener("DOMContentLoaded", function () {
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

let allScenarios = [];

function slugify(title) {
    return title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

function renderScenarios(data) {
    const scenariosDiv = document.querySelector('.scenarios');
    scenariosDiv.innerHTML = '';
    if (data.length === 0) {
        const noResult = document.createElement('div');
        noResult.className = 'no-results';
        noResult.textContent = 'No results found.';
        scenariosDiv.appendChild(noResult);
        return;
    }
    data.forEach(scenario => {
        const scenarioBox = document.createElement('div');
        scenarioBox.classList.add('scenario-box');
        const slug = scenario.slug || slugify(scenario.title);
        // Create a class based on the scenario level
        const levelClass = `lvl-${scenario.lvl.toLowerCase()}`;

        scenarioBox.innerHTML = `
            <div class="scenario-img" style="background-image: url('${scenario.img}');"></div>
            <div class="Scenario-text-box">
                <h3 class="scenario-title">${scenario.title}</h3>
                <div class="scenario-badges">
                    <span class="scenario-lvl ${levelClass}">${scenario.lvl}</span>
                    <span class="scenario-points">${scenario.points} pts</span>
                </div>
                <p class="scenarios-des">${scenario.description}</p>
                <a href="/scenario/${slug}" class="scenario-btn">Start Scenario</a>
            </div>
        `;
        scenariosDiv.appendChild(scenarioBox);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    fetch('/api/scenarios')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            allScenarios = data;
            renderScenarios(allScenarios);
        })
        .catch(error => console.error('Error fetching scenarios:', error));

    // Search and filter functionality
    const form = document.getElementById('scenario-search-form');
    const searchInput = document.getElementById('search-input');
    const checkboxes = document.querySelectorAll('input[name="level"]');
    const pointsSelect = document.getElementById('points-select');
    const clearBtn = document.getElementById('clear-filters');

    function filterScenarios() {
        const searchValue = searchInput.value.toLowerCase();
        const selectedLevels = Array.from(checkboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        const pointsValue = pointsSelect.value;
        let filtered = allScenarios.filter(scenario => {
            const matchesSearch =
                scenario.title.toLowerCase().includes(searchValue) ||
                scenario.description.toLowerCase().includes(searchValue);
            const matchesLevel =
                selectedLevels.length === 0 || selectedLevels.includes(scenario.lvl);
            let matchesPoints = true;
            if (pointsValue === 'lt100') matchesPoints = scenario.points < 100;
            else if (pointsValue === '100-120') matchesPoints = scenario.points >= 100 && scenario.points <= 120;
            else if (pointsValue === 'gt120') matchesPoints = scenario.points > 120;
            return matchesSearch && matchesLevel && matchesPoints;
        });
        renderScenarios(filtered);
    }

    // Clear all filters
    clearBtn.addEventListener('click', function () {
        searchInput.value = '';
        checkboxes.forEach(cb => cb.checked = false);
        pointsSelect.value = 'all';
        filterScenarios();
    });

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        filterScenarios();
    });
    searchInput.addEventListener('input', filterScenarios);
    checkboxes.forEach(cb => cb.addEventListener('change', filterScenarios));
    pointsSelect.addEventListener('change', filterScenarios);
});







