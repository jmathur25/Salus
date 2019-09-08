var schoolName = "";

window.onload = function() {

    var schoolInput = document.getElementById("schoolInput");
    var goInput = document.getElementById("schoolGo");

    console.log(schoolInput)

    // Execute a function when the user releases a key on the keyboard
    schoolInput.addEventListener("keyup", function(event) {
        // Number 13 is the "Enter" key on the keyboard
        if (event.keyCode === 13) {
            event.preventDefault();
            goInput.click();
        }
    });
    
    goInput.onclick = function(event) {
        schoolName = schoolInput.value;
        fadeOutEffect();

        var mapOnboarder = document.getElementById("onboarding-div-map");

        mapOnboarder.style.display = "flex";

        // showModal();
    };

    $(function() {
        function processData(allText) {
          var record_num = 2; // or however many elements there are in each row
          var allTextLines = allText.split(/\r\n|\n/);
          var lines = [];
          var headings = allTextLines.shift().split(',');
          while (allTextLines.length > 0) {
            var tobj = {}, entry;

            entry = allTextLines.shift().split(',');
            tobj['label'] = entry[0];
            tobj['value'] = [entry[1], entry[2]];
            lines.push(tobj);
          }

          return lines;
        }
      
        // Storage for lists of CSV Data
        var lists = [];
        // Get the CSV Content
        $.get("static/university_dataset.csv", function(data) {
          lists = processData(data);
        });

        console.log(lists);
      
        $("#schoolInput").autocomplete({
          minLength: 3,
          source: lists,
          select: function(event, ui) {
            console.log(ui)
            $("#schoolInput").val(ui.item.label);
            return true;
          }
        });
      });
};

function fadeOutEffect() {
    var fadeTarget = document.getElementById("overlay");
    var fadeEffect = setInterval(function () {
        if (!fadeTarget.style.opacity) {
            fadeTarget.style.opacity = 1;
        }
        if (fadeTarget.style.opacity > 0) {
            fadeTarget.style.opacity -= 0.05;
        } else {
            clearInterval(fadeEffect);
        }
    }, 100);
};

function showModal() {
    setTimeout(function() {
        $("#exampleModal").modal()
    }, 2000);
};

function enableMap() {
    document.getElementById("overlay").style.display = "none";
};

function dismissOnboarding() {
    document.getElementById("onboarding-div").style.display = "none";
}

function dismissMapOnboarding() {
    document.getElementById("onboarding-div-map").style.display = "none";
}