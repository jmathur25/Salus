var schoolName = "";

window.onload = function() {

    var schoolInput = document.getElementById("schoolInput");
    var goInput = document.getElementById("schoolGo");

    var mapOverlay = document.getElementById("overlay")

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
        showModal();
    };
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
}

function showModal() {
    setTimeout(function() {
        $("#exampleModal").modal()
    }, 2000);
}

function enableMap() {
    document.getElementById("overlay").style.display = "none";
}