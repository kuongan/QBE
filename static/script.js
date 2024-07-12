document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.close-button').forEach(button => {
        button.addEventListener('click', () => {
            button.closest('.modal').style.display = 'none';
        });
    });

    document.getElementById('recordButton').addEventListener('click', async function() {
        try {
            const response = await fetch('/record', {
                method: 'POST',
                body: JSON.stringify({ listen: 'true' }),
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json(); // Ensure you await the response
            showResults(data);
        } catch (error) {
            console.error('Error:', error);
        }
    });

    document.getElementById('upButton').addEventListener('click', function() {
        document.getElementById('fileInput').click();
    });

    document.getElementById('fileInput').addEventListener('change', async function() {
        try {
            var pathfile = this.files[0].name;
            const response = await fetch('/recognise', {
                method: 'POST',
                body: JSON.stringify({ listen: 'false', pathfile: pathfile }),
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json(); // Ensure you await the response
            showResults(data);
        } catch (error) {
            console.error('Error:', error);
        }
    });

    function showResults(data) {
        console.log('showResults called with:', data); // Debug logging

        const resultContainer = document.getElementById('songListContainer');
        const songList = document.getElementById('songList');

        // Clear previous results
        songList.innerHTML = '';

        // Assuming 'data.results' contains the list of recognized song titles
        if (data.results && Array.isArray(data.results)) {
            data.results.forEach(title => {
                const listItem = document.createElement('li');
                listItem.textContent = title;
                songList.appendChild(listItem);
            });
        } else {
            // Handle case where results are not in expected format
            const listItem = document.createElement('li');
            listItem.textContent = 'No results found';
            songList.appendChild(listItem);
        }

        // Display the container with recognized songs
        resultContainer.style.display = 'block';

        // Show the modal
        const messbox = document.getElementById('messbox');
        messbox.style.display = 'block';
    }
});
