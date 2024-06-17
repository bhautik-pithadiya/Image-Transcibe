document.addEventListener('DOMContentLoaded', async () => {
    const idList = document.getElementById('id-list');
    const displayContainer = document.getElementById('display-container');
    const chatBox = document.getElementById('chat-box');
    const chatForm = document.getElementById('chatform');

    let jsonData = [];

    // Fetch JSON data
    try {
        const response = await fetch('static/chat_history.json');
        jsonData = await response.json();

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

    // Function to display user data
    function displayUserData(userItem) {
        chatBox.style.display = 'none';
        chatForm.style.display = 'none';
        displayContainer.style.display = 'block';
        displayContainer.innerHTML = `
            <p><bold>Username:</bold> ${userItem.username}</p>
            <img src="${userItem.url}" alt="Image from ${userItem.username}">
            <p><strong>Prompt:</strong> ${userItem.prompt}</p>
            <p><strong>Response:</strong> ${userItem.response}</p>
        `;
    }

    document.getElementById('submissionForm').addEventListener('submit', handleSubmit);

    // New chat button functionality
    document.getElementById('new-chat').addEventListener('click', function () {
        chatBox.style.display = '';
        chatForm.style.display = 'block';
        displayContainer.style.display = 'none';
        displayContainer.innerHTML = '';
        document.getElementById('submissionForm').reset();
    });
});

async function handleSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const formDataObject = Object.fromEntries(formData.entries());

    try {
        const response = await fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(formDataObject),
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
