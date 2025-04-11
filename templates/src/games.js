window.onload = function () {
  const button_container = document.getElementById("button-container");

  var xhr = new XMLHttpRequest();

  function startGame() {
    let player_count = prompt("How many players are playing?");
    fetch(`http://${host_url}:8080/startgame/${player_count}`);
  }

  function nextGame() {
    fetch(`http://${host_url}:8080/nextgame`);
  }

  function sendCommand() {
    var inputField = document.getElementById("inputField");

    fetch(`http://${host_url}:8080/command/${inputField.value}`);

    inputField.value = "";
    loadPresets();
  }

  function loadPresets() {
    button_container.innerHTML = "";
    fetch(`http://${host_url}:8080/getgames`)
      .then((response) => response.json())
      .then((data) => {
        for (game_mode in data) {
          for (game in data[game_mode]) {
            const button = document.createElement("button");
            button.classList.add("grid-button");
            button.textContent = game;

            const GAME_MODE = game_mode;
            const GAME = game;

            button.addEventListener("click", function () {
              fetch(`http://${host_url}:8080/loadgame/${GAME_MODE}/${GAME}`);
            });

            button_container.appendChild(button);
          }
        }
      });
  }
  loadPresets();
};
