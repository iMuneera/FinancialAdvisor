document.getElementById('send-button').addEventListener('click', () => {
    const inputField = document.getElementById('user-input');
    const userInput = inputField.value.trim();
    if (!userInput) return;
    const chatMessages = document.getElementById('chat-messages');

    // Function to check if a string contains HTML tags
    const containsHTML = (str) => /<[^>]+>/g.test(str);

    // Add message function to handle both user and bot messages
    const addMessage = (text, className, alignRight = false) => {
        const message = document.createElement('div');
        message.className = `chat-message text-gray-800 mb-4 flex ${alignRight ? 'rounded-bl-3xl rounded-tl-3xl rounded-tr-xl justify-end' : 'justify-start'}`;
        
        const botImage = alignRight ? '' : '<img id="bot-icon" src="/static/images/bot.png" class="h-14 mr-2">';

        const messageContent = document.createElement('div');
        messageContent.className = `${className} p-4 max-w-xs text-xl`;
        messageContent.innerHTML = `<p>${text}</p>`;

        if (!alignRight) message.innerHTML = botImage;
        message.appendChild(messageContent);
        chatMessages.appendChild(message);

        return messageContent; // Return the message content element for text animation
    };

    inputField.value = '';

    // Pick random response for the greeting array
    const getRandomResponse = (responses) => responses[Math.floor(Math.random() * responses.length)];

    // Basic greetings 
    const greetings = {
        'hello': ['Hello! How can I help you?', 'Hi there!', 'Greetings!', 'Hello there!', 'Hi! How can I assist you today?', 'Hey! What’s up?'],
        'good morning': ['Good morning! How’s your day going?', 'Morning! What can I do for you today?', 'Good morning! Ready for a productive day?'],
        'good evening': ['Good evening! How can I assist you?', 'Evening! How’s your day been?', 'Good evening! What can I help with?'],
        'hey': ['Hey! How’s it going?', 'Hey there! What can I do for you?', 'Hey! Need any help today?'],
        'good afternoon': ['Good afternoon! How’s your day so far?', 'Afternoon! What can I assist you with?', 'Good afternoon! How can I help you today?'],
        'hi': ['Hi! How can I help you?', 'Hello! How’s it going?', 'Hi there! What can I assist you with today?']
    };
   
    
    addMessage(userInput, 'dark:bg-gray-700 p-4 rounded-bl-3xl rounded-tl-3xl rounded-tr-xl max-w-xs dark:text-white mx-4 bg-green-200 text-xl font-semibold font-sans text-gray-500', true);

    const lowerCaseInput = userInput.toLowerCase();
    let responded = false;

    // Check for greetings and respond immediately
    for (const [greeting, responses] of Object.entries(greetings)) {
        // Use a regular expression to check for an exact word match
        const regex = new RegExp(`\\b${greeting}\\b`, 'i'); // 'i' makes it case-insensitive
        if (regex.test(lowerCaseInput)) {
            const textElement = addMessage('', 'dark:bg-blue-500 p-3 rounded-br-3xl rounded-tr-3xl rounded-tl-xl dark:text-white text-gray-500 bg-blue-200');
            animateText(getRandomResponse(responses), textElement); // Pass the element for text animation
            responded = true;
            break;
        }
    }
    
    if (!responded) {
        // Send message to backend if it's not a greeting
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `message=${encodeURIComponent(userInput)}`
        })
        .then(response => response.json())
        .then(data => {
            // Clear the input field after sending the message
            inputField.value = '';

            // Check if the response contains any HTML tags
            const responseText = data.response;
            const textElement = addMessage('', 'dark:bg-blue-500 p-3 rounded-br-3xl rounded-tr-3xl rounded-tl-xl dark:text-white text-gray-500 bg-blue-200');

            if (containsHTML(responseText)) {
                // If response contains HTML, set it directly
                textElement.innerHTML = responseText; // Set the innerHTML to render HTML correctly
            } else {
                // Animate the received message letter by letter
                animateText(responseText, textElement);
            }

            // Handle budget update
            const budgetDisplay = document.getElementById('budget-display');
            if (data.updated_budget) {
                const isNegative = parseFloat(data.updated_budget) < 0;
                budgetDisplay.textContent = `${data.updated_budget} BHD`;
                budgetDisplay.className = `text-3xl font-bold p-4 rounded-lg text-center mt-4 ${isNegative ? 'bg-red-700 text-white dark:bg-red-900' : 'bg-green-100 text-green-800'}`;
            }

            // Handle graph display for weekly spending
            const graphContainer = document.getElementById('graph-container');
            const graphImage = document.getElementById('weekly-spending-graph');
            if (data.image_url) {
                graphImage.src = data.image_url;
                graphContainer.classList.remove('hidden');
            } else {
                graphContainer.classList.add('hidden');
            }

            // Handle graph display for weekly purchases
            const graphContainer2 = document.getElementById('graph-container2');
            const graphImage2 = document.getElementById('weekly-purchases-graph');
            if (data.image_url_purchases) {
                graphImage2.src = data.image_url_purchases;
                graphContainer2.classList.remove('hidden');
            } else {
                graphContainer2.classList.add('hidden');
            }
        })
        .catch(error => console.error('Error:', error));
    }
});

function animateText(text, element) {
    let i = 0;
    function displayNextLetter() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i); // Add the next letter
            i++;
            setTimeout(displayNextLetter, 20); // Delay between letters (adjust the speed here)
        }
    }
    displayNextLetter();
}

// Toggle functionality for items list
const toggleButton = document.getElementById('toggle-button');
const itemsList = document.getElementById('items-list');
const chatContainer = document.getElementById('chat-container');

toggleButton.addEventListener('click', function() {
    if (itemsList.style.display === 'none') {
        itemsList.style.display = 'block';
        chatContainer.classList.remove('w-full');
        chatContainer.classList.add('w-2/3');
    } else {
        itemsList.style.display = 'none';
        chatContainer.classList.remove('w-2/3');
        chatContainer.classList.add('w-full');
    }
});

// Initially hide the list 
itemsList.style.display = 'none';
chatContainer.classList.remove('w-2/3');
chatContainer.classList.add('w-full');


function toggleList(listId) {
    var list = document.getElementById(listId);
    if (list.classList.contains('hidden')) {
        list.classList.remove('hidden');
    } else {
        list.classList.add('hidden');
    }
}
