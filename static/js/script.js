document.addEventListener('DOMContentLoaded', async () => {
    const idList = document.getElementById('id-list');
    const chatBox = document.getElementById('chat-box');
    const chatForm = document.querySelector('.chatform');
    const displayContainer = document.querySelector('.display-container');

    let jsonData = [];

    // Fetch JSON data
    try {
        const response = await fetch('/static/chat_history.json');
        jsonData = await response.json();

        // Sort jsonData based on the time property in descending order
        jsonData.sort((a, b) => new Date(b.time) - new Date(a.time));

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
    // Function to display user data
    function displayUserData(userItem) {
        chatBox.style.display = 'none';
        chatForm.style.display = 'none';
        displayContainer.style.display = 'block';
        displayContainer.innerHTML = `
            
            <img src="${userItem.url}" alt="Image from ${userItem.username}" class="display-image">
            <p><strong>Prompt:</strong> ${userItem.prompt}</p>
            <p><strong>Response:</strong> ${userItem.response}</p>
            <div id="more-content" style="display: none;">

               
                <p><strong>Username:</strong> ${userItem.username}</p>
                <p><strong>Processing_time:</strong> ${userItem.processing_time}</p>
                <p><strong>Date & Time:</strong> ${userItem.time}</p>
                <p><strong>URL:</strong> ${userItem.url}</p>
            </div>
            <button id="more-button">More</button>
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
    //chatHistory.appendChild(chatMessage);
    chatHistory.insertBefore(chatMessage, chatHistory.firstChild);
}

document.getElementById('submissionForm').addEventListener('submit', handleSubmit);

// New chat button functionality
document.getElementById('new-chat').addEventListener('click', function() {
    document.getElementById('chat-box').innerHTML = '';
    document.getElementById('submissionForm').reset();
});

// // Attach form submission handler
// document.getElementById('submissionForm').addEventListener('submit', handleSubmit);


// document.getElementById('submissionForm').addEventListener('submit', async function(event) {
//     event.preventDefault();
//     const form = event.target;
//     const formData = new FormData(form);
//     const formDataObject = Object.fromEntries(formData.entries());

//     try {
//         const response = await fetch(form.action, {
            
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/x-www-form-urlencoded',
//             },
//             body: new URLSearchParams(formDataObject),
//         });

//         if (response.ok) {
//             const result = await response.json();
//             document.getElementById('result').innerText = `Response: ${result.response}\nProcessing Time: ${result.processing_time} seconds\n Total Time Taken: ${result.total_processing_time}`;
//         } else {
//             document.getElementById('result').innerText = `Error: ${response.statusText}`;
//         }
//     } 
//     catch (error) {
//         document.getElementById('result').innerText = `Error: ${error.message}`;
//     }
// });
