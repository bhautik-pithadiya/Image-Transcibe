document.getElementById('toggle-button').addEventListener('click', function() {
    var sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('hidden');
});

document.addEventListener('DOMContentLoaded', async () => {
    const idList = document.getElementById('id-list');
    const chatBox = document.getElementById('chat-box');
    const chatForm = document.querySelector('.chatform');
    const displayContainer = document.querySelector('.display-container');
    const linkRadio = document.getElementById('linkRadio');
    const fileRadio = document.getElementById('fileRadio');
    const linkInputGroup = document.getElementById('linkInputGroup');
    const fileInputGroup = document.getElementById('fileInputGroup');

    let jsonData = [];

    // Function to fetch JSON data
    async function fetchData() {
        try {
            const response = await fetch('/static/chat_history.json');
            jsonData = await response.json();

            // Sort jsonData based on the time property in descending order
            jsonData.sort((a, b) => new Date(b.time) - new Date(a.time));

            // Clear existing ID list
            idList.innerHTML = '';

            // Populate ID list
            jsonData.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item.id;
                li.addEventListener('click', () => {
                    displayUserData(item);
                });
                idList.appendChild(li);
            });
        } catch (error) {
            console.error('Error fetching JSON data:', error);
        }
    }

    // Initial fetch of JSON data
    await fetchData();

    // Refresh JSON data every 5 seconds
    setInterval(fetchData, 5000);

    // Function to display user data
    function displayUserData(userItem) {
        chatBox.style.display = 'none';
        chatForm.style.display = 'none';
        displayContainer.style.display = 'block';
        displayContainer.innerHTML = `
            <img src="${userItem.url}" alt="Image from ${userItem.username}" class="display-image" width="456" height="456">
            <p><strong>Prompt:</strong> ${userItem.prompt}</p>
            <p><strong>Response:</strong> ${userItem.response}</p>
            <div id="more-content" style="display: none;">
                <p><strong>Username:</strong> ${userItem.username}</p>
                <p><strong>Processing Time:</strong> ${userItem.processing_time}</p>
                <p><strong>Date & Time:</strong> ${userItem.time}</p>
                <p style="overflow-y:hidden;"><strong>URL:</strong> ${userItem.url}</p>
            </div>
            <div class="itt-more-btn"><button id="more-button">More</button></div>
        `;

        const moreButton = document.getElementById('more-button');
        moreButton.addEventListener('click', () => {
            const moreContent = document.getElementById('more-content');
            if (moreContent.style.display === 'none') {
                moreContent.style.display = 'block';
                moreButton.textContent = 'Less';
            } else {
                moreContent.style.display = 'none';
                moreButton.textContent = 'More';
            }
        });
    }

    // New chat button functionality
    document.getElementById('new-chat').addEventListener('click', function() {
        chatBox.style.display = 'block';
        chatForm.style.display = 'block';
        displayContainer.style.display = 'none';
        document.getElementById('submissionForm').reset();
    });

    // Handle input method change
    linkRadio.addEventListener('change', toggleInputMethod);
    fileRadio.addEventListener('change', toggleInputMethod);

    function toggleInputMethod() {
        if (linkRadio.checked) {
            linkInputGroup.style.display = 'block';
            fileInputGroup.style.display = 'none';
        } else if (fileRadio.checked) {
            linkInputGroup.style.display = 'none';
            fileInputGroup.style.display = 'block';
        }
    }
});

async function handleSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const result = await response.json();
            // Display the generated text in the chat history
            addToChatHistory(result.prompt, result.response);
        } else {
            // Handle error responses
            addToChatHistory("Error", `Error: ${response.statusText}`);
        }
    } catch (error) {
        // Handle network errors
        addToChatHistory("Error", `Error: ${error.message}`);
    }
}

// Function to add chat messages to chat history
function addToChatHistory(prompt, response) {
    const chatHistory = document.getElementById("result");
    const chatMessage = document.createElement("div");
    chatMessage.innerHTML = `<p><strong>Prompt:</strong> ${prompt}</p><p><strong>Response:</strong> ${response}</p>`;
    chatHistory.insertBefore(chatMessage, chatHistory.firstChild);
}

document.getElementById('submissionForm').addEventListener('submit', handleSubmit);

// New chat button functionality
document.getElementById('new-chat').addEventListener('click', function() {
    document.getElementById('chat-box').innerHTML = '';
    document.getElementById('submissionForm').reset();
});
