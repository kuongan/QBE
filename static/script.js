document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.close-button').forEach(button => {
        button.addEventListener('click', () => {
            button.closest('.modal').style.display = 'none';
        });
    });

    document.getElementById('recordButton').addEventListener('click', async function() {
        try {
            // Send POST request to start recording or activate microphone
            const response = await fetch('/record', {
                method: 'POST',
                body: JSON.stringify({ listen: 'true' }),
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            // Use showResult to display the result
        } catch (error) {
            console.error('Error:', error);
        }
    });

    document.getElementById('upButton').addEventListener('click', function() {
        document.getElementById('fileInput').click();
    });

document.getElementById('fileInput').addEventListener('change', async function() {
    try {
        var pathfile = this.files[0].name;  // Get selected file name
        // Add code to save the path file to .\music\snippet

        // Send POST request to recognise song from audio file path
        const response = await fetch('/recognise', {
            method: 'POST',
            body: JSON.stringify({ listen: 'false', pathfile: pathfile }),
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data =response.text(); // Get response as plain text
        showResults(data);  // Update function to display results
    } catch (error) {
        console.error('Error:', error);
    }
});
function showResults(data) {
    alert(data)
    // Assuming 'data' contains the list of recognized song titles
    const resultContainer = document.getElementById('songListContainer');
    const songList = document.getElementById('songList');

    // Clear previous results
    songList.innerHTML = '';

    // Loop through each recognized song title and create list items
    data.forEach(title => {
        const listItem = document.createElement('li');
        listItem.textContent = title;
        songList.appendChild(listItem);
    });

    // Display the container with recognized songs
    resultContainer.style.display = 'block';
}

});
