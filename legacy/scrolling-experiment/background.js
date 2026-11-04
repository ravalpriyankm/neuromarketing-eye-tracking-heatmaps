// // Listen for the extension's popup window to open
// chrome.extension.onConnect.addListener(function (port) {
//   if (port.name === 'scrollAndCapture') {
//     // Create the "web view" folder if it doesn't exist
//     const folderName = 'web_view';

//     // Create a CSV file for saving screenshot details
//     const csvFile = `${folderName}/screenshot_details_web.csv`;
//     const header = ['Image', 'Scrolling Time (UTC)', 'Scroll Position', 'Scroll Percentage'];

//     // Write the header to the CSV file
//     let csvContent = header.join(',') + '\n';

//     // Calculate the scroll height
//     let scrollHeight = 0;
//     let viewportHeight = 0;

//     // Start the manual scrolling process
//     let scrollPosition = 0;
//     const screenshotImages = [];

//     function scrollAndCapture() {
//       if (scrollPosition < scrollHeight) {
//         // Capture a screenshot of the current view
//         const screenshotName = `screenshot_${scrollPosition}.png`;
//         const screenshotDataUrl = document.createElement('canvas').toDataURL();

//         // Get the scroll percentage
//         const scrollPercentage = (scrollPosition / scrollHeight) * 100;

//         // Get the scrolling time in UTC format with milliseconds
//         const scrollingTime = new Date().toISOString().slice(0, -1);

//         // Append screenshot details to CSV content
//         const row = [screenshotName, scrollingTime, scrollPosition, scrollPercentage];
//         csvContent += row.join(',') + '\n';

//         // Update the scroll position
//         scrollPosition += viewportHeight;

//         // Scroll the page
//         chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
//           chrome.tabs.executeScript(tabs[0].id, { code: `window.scrollTo(0, ${scrollPosition});` });
//         });

//         // Wait for the page to settle and capture the screenshot
//         console.log("here")
//         setTimeout(scrollAndCapture, 3);
//       } else {
//         // Save the CSV file
//         const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
//         const downloadLink = document.createElement('a');
//         downloadLink.href = URL.createObjectURL(blob);
//         downloadLink.download = 'screenshot_details_web.csv';
//         downloadLink.click();
//       }
//     }

//     // Listen for messages from the extension's popup window
//     port.onMessage.addListener(function (msg) {
//       if (msg.action === 'startScrolling') {
//         // Calculate the scroll height and viewport height
//         chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
//           chrome.tabs.executeScript(
//             tabs[0].id,
//             { code: 'Math.max(document.documentElement.scrollHeight, document.body.scrollHeight);' },
//             function (result) {
//               scrollHeight = result[0];

//               chrome.tabs.executeScript(
//                 tabs[0].id,
//                 { code: 'Math.max(window.innerHeight, document.documentElement.clientHeight);' },
//                 function (result) {
//                   viewportHeight = result[0];
//                   scrollAndCapture();
//                 }
//               );
//             }
//           );
//         });
//       }
//     });
//   }
// });





chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
      if( request.message === "capture_page" ) {
        chrome.tabs.captureVisibleTab(null, {}, function (image) {
          console.log(image); // Logs the data URL for the image. You can process it as needed.
        });
      }
    }
  );
  