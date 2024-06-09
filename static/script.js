function showSection(sectionId, element) {
    // Ẩn tất cả các phần
    document.getElementById('searchSection').style.display = 'none';
    document.getElementById('addSection').style.display = 'none';
    document.getElementById('deleteSection').style.display = 'none';
    // Hiển thị phần đã chọn
    document.getElementById(sectionId + 'Section').style.display = 'block';

    // Loại bỏ lớp active khỏi tất cả các liên kết
    const links = document.querySelectorAll('.sidebar ul li a');
    links.forEach(link => {
        link.classList.remove('active');
    });

    // Thêm lớp active vào liên kết được chọn
    element.classList.add('active');

    // Thay đổi URL dựa trên phần đã chọn
    const url = '/' + sectionId;
    history.pushState({ sectionId: sectionId }, null, url);
    document.getElementById(sectionId + 'Section').style.display = 'block';
}
// Sự kiện popstate để xử lý việc điều hướng trang khi người dùng thực hiện điều hướng back hoặc forward
window.addEventListener('popstate', function(event) {
    const sectionId = event.state.sectionId;
    showSection(sectionId);
});

// Close modal functionality
document.querySelectorAll('.close-button').forEach(button => {
    button.addEventListener('click', () => {
        button.closest('.modal').style.display = 'none';
    });
});

// Example function to display the modal (you can customize it as needed)
document.getElementById('searchButton').addEventListener('click', () => {
    document.getElementById('messbox').style.display = 'block';
});

document.addEventListener('DOMContentLoaded', function() {
    let currentFilePath = null; // Đường dẫn tệp hiện tại

    // Lắng nghe sự kiện click vào nút Upload
    document.getElementById('uploadButton').addEventListener('click', function() {
        document.getElementById('fileInput').click();
    });

    // Lắng nghe sự kiện thay đổi của input type file
    document.getElementById('fileInput').addEventListener('change', function() {
        const file = this.files[0];
        currentFilePath = file;
    });

    // Lắng nghe sự kiện click vào nút Record
    document.getElementById('recordButton').addEventListener('click', function() {
        showMessage('Recording in progress...');
        fetch('/record', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Recording started successfully');
                currentFilePath = './music/snippet/query.wav';
                showMessage('Recording successful!');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Recording failed. Please try again.');
        });
    });

    document.getElementById('searchButton').addEventListener('click', function() {
        if (!currentFilePath) {
            alert('Please upload or record a file first');
            return;
        }

        const formData = new FormData();
        
        if (currentFilePath instanceof File) {
            formData.append('file', currentFilePath);
        } else {
            formData.append('filePath', currentFilePath);
        }

        fetch('/identify_snippet', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Identified snippet:', data.result);
            showMessbox(data.result); // Hiển thị modal và kết quả
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    function showMessage(message) {
        const messageBox = document.getElementById('messageBox');
        const messageText = document.getElementById('messageText');
        const closeButton = document.querySelector('.close-button');

        messageText.textContent = message;
        messageBox.style.display = 'block';

        closeButton.onclick = function() {
            messageBox.style.display = 'none';
        }

        window.onclick = function(event) {
            if (event.target === messageBox) {
                messageBox.style.display = 'none';
            }
        }
    }

    function showMessbox(results) {
        const messbox = document.getElementById('messbox');
        const songList = document.getElementById('songList');

        // Xóa các tiêu đề cũ
        songList.innerHTML = '';

        // Thêm tiêu đề mới vào danh sách
        results.forEach(result => {
            const li = document.createElement('li');
            li.textContent = result;
            songList.appendChild(li);
        });

        messbox.style.display = 'block'; // Hiển thị modal

        const closeButton = document.querySelector('.close-button');
        closeButton.addEventListener('click', function() {
            messbox.style.display = 'none'; // Ẩn modal khi click vào nút close
        });
    }



});

document.addEventListener('DOMContentLoaded', function() {
    // Lắng nghe sự kiện submit của form
    document.getElementById('addSongForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Ngăn chặn form gửi dữ liệu đi
        showMessage('Loading in progress...');
        const youtubeUrl = document.getElementById('youtubeUrl').value; // Lấy giá trị từ input

        // Gọi hàm thêm bài hát bằng AJAX
        fetch('/addsong', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'youtubeUrl': youtubeUrl })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Song added successfully!');
            } else {
                alert('Failed to add song. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again later.');
        });
    });
});
