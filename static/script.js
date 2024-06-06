var searchSection = document.getElementById("searchSection");
var databaseSection = document.getElementById("databaseSection");

function showSearch() {
    searchSection.style.display = "block";
    databaseSection.style.display = "none";
}

function showDatabase() {
    searchSection.style.display = "none";
    databaseSection.style.display = "block";
}

var hamburger = document.querySelector(".hamburger");
hamburger.addEventListener("click", function(){
    document.querySelector("body").classList.toggle("active");
})

function addSong(event) {
    event.preventDefault();
    var pathfile = document.getElementById("pathfile").value;
    fetch('/add_song', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pathfile: pathfile }),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        // Update UI based on response
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function record(event) {
    event.preventDefault();
    fetch('/record', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        // Handle response
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function identifySnippet() {
  const fileInput = document.getElementById('file');
  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('file', file);

  fetch('/identify_snippet', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    console.log('Identified snippet:', data.result);
    // You can also update the UI with the result
  })
  .catch(error => {
    console.error('Error:', error);
  });
}