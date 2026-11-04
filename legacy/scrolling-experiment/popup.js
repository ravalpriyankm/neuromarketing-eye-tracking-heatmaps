// Establish a connection with the background script
const port = chrome.runtime.connect({ name: 'scrollAndCapture' });

// Handle the click event of the start button
const startButton = document.getElementById('start-button');
startButton.addEventListener('click', function () {
  // Send a message to the background script to start scrolling
  port.postMessage({ action: 'startScrolling' });
});
