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