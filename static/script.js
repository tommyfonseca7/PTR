const categorias = [...document.querySelectorAll('.categorias-container')];
const nxtBtn = [...document.querySelectorAll('.nxt-btn')];
const preBtn = [...document.querySelectorAll('.pre-btn')];

categorias.forEach((item, i) => {
    let containerDimensions = item.getBoundingClientRect();
    let containerWidth = containerDimensions.width;

    nxtBtn[i].addEventListener('click', () => {
        item.scrollLeft += containerWidth;
    })

    preBtn[i].addEventListener('click', () => {
        item.scrollLeft -= containerWidth;
    })
})


function reduceBy0_3() {
    var resultElement = document.getElementById("compt-result");
    var result = parseFloat(resultElement.innerHTML);
    result -= 0.3;
    resultElement.innerHTML = result.toFixed(1);
}

function reduceBy0_1() {
    var resultElement = document.getElementById("compt-result");
    var result = parseFloat(resultElement.innerHTML);
    result -= 0.1;
    resultElement.innerHTML = result.toFixed(1);
}

function cancelReduceBy0_3() {
    var resultElement = document.getElementById("compt-result");
    var result = parseFloat(resultElement.innerHTML);
    result += 0.3;
    result = Math.min(result, 4.0); 
    resultElement.innerHTML = result.toFixed(1);
}

function cancelReduceBy0_1() {
    var resultElement = document.getElementById("compt-result");
    var result = parseFloat(resultElement.innerHTML);
    result += 0.1;
    result = Math.min(result, 4.0); 
    resultElement.innerHTML = result.toFixed(1);
}

function resetResult() {
    var resultElement = document.getElementById("compt-result");
    resultElement.innerHTML = "4.0";
}

document.addEventListener("DOMContentLoaded", function() {
    var h1Element = document.getElementById("sAndVValue");

    document.addEventListener("change", function(event) {
      if (event.target.matches('input[name="tabs10"]')) {
        var selectedValue = parseFloat(event.target.value);
        h1Element.innerHTML = selectedValue.toFixed(1);
      }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    var h1Element = document.getElementById("rAndCValue");

    document.addEventListener("change", function(event) {
      if (event.target.matches('input[name="tabs20"]')) {
        var selectedValue = parseFloat(event.target.value);
        h1Element.innerHTML = selectedValue.toFixed(1);
      }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    var h1Element = document.getElementById("eAndEValue");

    document.addEventListener("change", function(event) {
      if (event.target.matches('input[name="tabs30"]')) {
        var selectedValue = parseFloat(event.target.value);
        h1Element.innerHTML = selectedValue.toFixed(1);
      }
    });
});

var tabsContainer = document.querySelector('.tabs1');
var radioButtons = tabsContainer.querySelectorAll('input[type="radio"]');
var selectedValue = '';
radioButtons.forEach(function(radioButton) {
    radioButton.addEventListener('change', function() {
        if (this.checked) {
          selectedValue = this.value;
          console.log('Selected value:', selectedValue);
        }
      });
});

var tabsContainer2 = document.querySelector('.tabs2');
var radioButtons2 = tabsContainer2.querySelectorAll('input[type="radio"]');
var selectedValue2 = '';
radioButtons2.forEach(function(radioButton) {
  if (radioButton.checked) {
    selectedValue2 = radioButton.value;
  }
});

var tabsContainer3 = document.querySelector('.tabs3');
var radioButtons3 = tabsContainer3.querySelectorAll('input[type="radio"]');
var selectedValue3 = '';
radioButtons.forEach(function(radioButton) {
  if (radioButton.checked) {
    selectedValue3 = radioButton.value;
  }
});
console.log('Selected value:', selectedValue);
console.log('Selected value:', selectedValue2);
console.log('Selected value:', selectedValue3);

document.getElementById("button-submit-juri").addEventListener('click', function (event) {
  event.preventDefault();

  var athleteName = document.getElementById("athlete_name").textContent;
  var tournamentId = document.getElementById("tournament_id").value;
  var judgeId = document.getElementById("judge_id").value;
  var categoryId = document.getElementById("category_id").value;
  var athleteId = document.getElementById("athlete_id").value;
  var sAndVValue = document.getElementById("sAndVValue").textContent;
  var rAndCValue = document.getElementById("rAndCValue").textContent;
  var eAndEValue = document.getElementById("eAndEValue").textContent;
  var comptResult = document.getElementById("compt-result").textContent;

  var formData = {
      name: athleteName,
      tournament_id: tournamentId,
      category_id: categoryId,
      athlete_id: athleteId,
      strength_and_velocity: sAndVValue,
      rhythm_and_coordination: rAndCValue,
      energy_expression: eAndEValue,
      technical_component: comptResult
  };

  fetch(`/${judgeId}/juri_interface`, {
      method: "POST",
      headers: {
          "Content-Type": "application/json"
      },
      body: JSON.stringify(formData)
  })
  .then(function (response) {
      if (response.ok) {
          return response.json(); 
      } else {
          throw new Error("Failed to save results");
      }
  })
  .then(function (data) {
      if (data.next_athlete_name) {
          var athleteNameElement = document.getElementById('athlete_name');
          var tournamentNameElement = document.getElementById('tournament_name');
          var tournamentIdElement = document.getElementById("tournament_id");
          var categoryIdElement = document.getElementById("category_id");
          var athleteIdElement = document.getElementById("athlete_id");
          athleteNameElement.textContent = data.next_athlete_name;
          tournamentNameElement.textContent = data.tournament_name;
          tournamentIdElement.textContent = data.tournamentIdElement;
          categoryIdElement.textContent = data.categoryIdElement;
          athleteIdElement.textContent = data.athlete_id;
          document.getElementById("athlete_id").value = data.athlete_id;

          alert("Form submitted successfully. Moving to the next athlete.");
      }
      else {
        alert("Tournament finished. Returning to the lobby.");
        window.location.href = "/lobby"; 
    }
  })
  .catch(function (error) {
      console.error('Error:', error);
      alert("An error occurred during form submission. Please try again.");
  });
});

function show_hide(divId) {
  var click = document.getElementById(divId);
  if (click.style.display === "none") {
      click.style.display = "grid";
  } else {
      click.style.display = "none";
  }
}


function show_popup(divId) {
  var click = document.getElementById(divId);
  click.style.display = "flex";
}


function hide_popup(divId) {
  var click = document.getElementById(divId);
  click.style.display = "none";
}
