document.addEventListener('DOMContentLoaded', function() {
    // Check if element exists before adding event listener
    var playNowButton = document.getElementById('menuPlayNow');
    if (playNowButton) {
        playNowButton.addEventListener('click', function() {
            window.open('/play', '_self');
        });
    }

    var leaderboardButton = document.getElementById('menuLeaderboard');
    if (leaderboardButton) {
        leaderboardButton.addEventListener('click', function() {
            window.open('/leaderboard', '_self');
        });
    }

    var personalStatsButton = document.getElementById('menuPersonalStats');
    if (personalStatsButton) {
        personalStatsButton.addEventListener('click', function() {
            window.open('/per-stats', '_self');
        });
    }

    var playerGuideButton = document.getElementById('menuPlayerGuide');
    if (playerGuideButton) {
        playerGuideButton.addEventListener('click', function() {
            window.open('/pl-guide', '_self');
        });
    }

    var homeButton = document.getElementById('menuHome');
    if (homeButton) {
        homeButton.addEventListener('click', function() {
            window.open('/', '_self');
        });
    }

    var homeIcon = document.getElementById('homeIcon');
    if (homeIcon) {
        homeIcon.addEventListener('click', function() {
            window.open('/', '_self');
        });
    }

    var gameTitle = document.getElementById('gameTitle');
    if (gameTitle) {
        gameTitle.addEventListener('click', function() {
            window.open('/', '_self');
        });
    }

    // Chatbox functionality
    var sendButton = document.getElementById('send-btn');
    var chatInput = document.getElementById('chat-input');
    var chatBody = document.getElementById('chatbox-body');

    function appendMessage(sender, message) {
        var messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message ' + sender;
        messageDiv.innerHTML = `<strong>${sender === 'user' ? 'You' : 'Bot'}:</strong> ${message}`;
        chatBody.appendChild(messageDiv);
        chatBody.appendChild(document.createElement('br')); // Add an empty line between messages
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function sendMessage() {
        var message = chatInput.value.trim();
        if (!message) return;

        appendMessage('user', message);

        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                appendMessage('bot', data.response);
            } else if (data.error) {
                appendMessage('bot', 'Error: ' + data.error);
            }
        })
        .catch(error => {
            appendMessage('bot', 'Error: ' + error);
        });

        chatInput.value = '';
    }

    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    if (chatInput) {
        chatInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                sendMessage();
            }
        });
    }

    // Menu hover functionality
    const hamMenu = document.querySelector('.ham-menu');
    const fullPageGreen = document.querySelector('.full-page-green');
    const menuLabel = document.querySelector('label[for="ham-menu"]');

    menuLabel.addEventListener('mouseover', function() {
        hamMenu.style.transform = 'translate(0)';
        fullPageGreen.style.opacity = '1';
        fullPageGreen.style.visibility = 'visible';
        hamMenu.style.visibility = 'visible';
    });

    menuLabel.addEventListener('mouseleave', function() {
        setTimeout(() => {
            if (!hamMenu.matches(':hover') && !fullPageGreen.matches(':hover')) {
                hamMenu.style.transform = 'translate(-110%)';
                fullPageGreen.style.opacity = '0';
                fullPageGreen.style.visibility = 'hidden';
                hamMenu.style.visibility = 'hidden';
            }
        }, 300);
    });

    hamMenu.addEventListener('mouseleave', function() {
        setTimeout(() => {
            if (!hamMenu.matches(':hover') && !fullPageGreen.matches(':hover') && !menuLabel.matches(':hover')) {
                hamMenu.style.transform = 'translate(-110%)';
                fullPageGreen.style.opacity = '0';
                fullPageGreen.style.visibility = 'hidden';
                hamMenu.style.visibility = 'hidden';
            }
        }, 300);
    });

    fullPageGreen.addEventListener('mouseover', function() {
        hamMenu.style.transform = 'translate(0)';
        fullPageGreen.style.opacity = '1';
        fullPageGreen.style.visibility = 'visible';
        hamMenu.style.visibility = 'visible';
    });

    fullPageGreen.addEventListener('mouseleave', function() {
        setTimeout(() => {
            if (!hamMenu.matches(':hover') && !menuLabel.matches(':hover')) {
                hamMenu.style.transform = 'translate(-110%)';
                fullPageGreen.style.opacity = '0';
                fullPageGreen.style.visibility = 'hidden';
                hamMenu.style.visibility = 'hidden';
            }
        }, 300);
    });

    // Initial friendly bot message
    if (!document.getElementById('initial-message')) {
        appendMessage('bot', 'Hello! I am here to help you. Feel free to ask me any questions.');
    }
});