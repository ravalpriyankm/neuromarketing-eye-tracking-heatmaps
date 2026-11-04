// // // Create the "web view" folder if it doesn't exist
// // const folderName = 'web_view';

// // // Create a CSV file for saving screenshot details
// // const csvFile = `${folderName}/screenshot_details_web.csv`;
// // const header = ['Image', 'Scrolling Time (UTC)', 'Scroll Position', 'Scroll Percentage'];

// // // Write the header to the CSV file
// // let csvContent = header.join(',') + '\n';

// // // Calculate the scroll height
// // const scrollHeight = document.documentElement.scrollHeight;
// // const viewportHeight = window.innerHeight;

// // // Start the manual scrolling process
// // let scrollPosition = 0;
// // const screenshotImages = [];

// // function scrollAndCapture() {
// //   if (scrollPosition < scrollHeight) {
// //     // Capture a screenshot of the current view
// //     const screenshotName = `screenshot_${scrollPosition}.png`;
// //     const screenshotDataUrl = document.createElement('canvas').toDataURL();

// //     // Get the scroll percentage
// //     const scrollPercentage = (scrollPosition / scrollHeight) * 100;

// //     // Get the scrolling time in UTC format with milliseconds
// //     const scrollingTime = new Date().toISOString().slice(0, -1);

// //     // Append screenshot details to CSV content
// //     const row = [screenshotName, scrollingTime, scrollPosition, scrollPercentage];
// //     csvContent += row.join(',') + '\n';

// //     // Update the scroll position
// //     scrollPosition += viewportHeight;

// //     // Scroll the page
// //     window.scrollTo(0, scrollPosition);

// //     // Wait for the page to settle and capture the screenshot
// //     setTimeout(scrollAndCapture, 500);
// //   } else {
// //     // Save the CSV file
// //     const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
// //     const downloadLink = document.createElement('a');
// //     downloadLink.href = URL.createObjectURL(blob);
// //     downloadLink.download = 'screenshot_details_web.csv';
// //     downloadLink.click();
// //   }
// // }

// // scrollAndCapture();



// // // Function to get scroll percentage
// // function getScrollPercentage() {
// //   return ((window.scrollY + window.innerHeight) / document.body.offsetHeight) * 100;
// // }

// // // Function to get current date-time
// // function getDateTime() {
// //   return new Date().toISOString();
// // }

// // let scrollData = [];

// // // Listen to scroll event
// // let scrollTimer = null;
// // window.addEventListener('scroll', function(){
// //   let scrollPercentage = getScrollPercentage();
// //   let dateTime = getDateTime();

// //   // Save scroll data
// //   scrollData.push({
// //       time: dateTime,
// //       position: window.scrollY,
// //       percentage: scrollPercentage
// //   });

// //   // Clear the timer if it already exists
// //   if (scrollTimer !== null) {
// //       clearTimeout(scrollTimer);
// //   }

// //   // Set the timer
// //   scrollTimer = setTimeout(function() {
// //       // Create the CSV file after 3 seconds of no scrolling
// //       let csvContent = 'data:text/csv;charset=utf-8,'
// //           + 'Scrolling Time (UTC),Scroll Position,Scroll Percentage\n'
// //           + scrollData.map(e => `${e.time},${e.position},${e.percentage}`).join('\n');

// //       // Create a blob from the CSV content
// //       var blob = new Blob([csvContent], {type: 'text/csv'});

// //       // Create a blob URL
// //       var url = URL.createObjectURL(blob);

// //       // Create a download link and click it
// //       var downloadLink = document.createElement("a");
// //       downloadLink.href = url;
// //       downloadLink.download = "scroll_data.csv";
// //       document.body.appendChild(downloadLink);
// //       downloadLink.click();
// //       document.body.removeChild(downloadLink);

// //       // Clear scrollData after download
// //       scrollData = [];
// //   }, 3000);
// // });



// // Function to get scroll percentage
// function getScrollPercentage() {
//   return ((window.scrollY + window.innerHeight) / document.body.offsetHeight) * 100;
// }

// // Function to get current date-time
// function getDateTime() {
//   return new Date().toISOString();
// }

// let scrollData = [];

// // Listen to mouse wheel event
// window.addEventListener('wheel', function(event){
//   let dateTime = getDateTime();


// // Listen to scroll event
// window.addEventListener('scroll', function(){
//   let scrollPercentage = getScrollPercentage();
//   let dateTime = getDateTime();

//   // Save scroll data
//   scrollData.push({
//     time: dateTime,
//     event: 'scroll',
//     position: window.scrollY,
//     percentage: scrollPercentage
//   });
// });

// // Listen to mouse wheel event
// window.addEventListener('wheel', function(event){
//   let dateTime = getDateTime();

//   // Save wheel data
//   scrollData.push({
//     time: dateTime,
//     event: 'mouseWheel',
//     deltaY: event.deltaY
//   });
// });


// // // Listen to scroll event
// // let scrollTimer = null;

// // window.addEventListener('scroll', function(){
// //   let scrollPercentage = getScrollPercentage();
// //   let dateTime = getDateTime();

// //   // Save scroll data
// //   scrollData.push({
// //       time: dateTime,
// //       position: window.scrollY,
// //       percentage: scrollPercentage

// //   });

//   // Clear the timer if it already exists
//   if (scrollTimer !== null) {
//       clearTimeout(scrollTimer);
//   }

//   // Set the timer
//   scrollTimer = setTimeout(function() {
//       // Create the CSV file after 3 seconds of no scrolling
//       // let csvContent = 'data:text/csv;charset=utf-8,'
//       //     + 'Scrolling Time (UTC),Scroll Position,Scroll Percentage\n'
//       //     + scrollData.map(e => `${e.time},${e.position},${e.percentage}`).join('\n');

//       // Create the CSV file after 3 seconds of no scrolling
//       // let csvContent = 'data:text/csv;charset=utf-8,'
//       //     + 'Event Time (UTC),Event,Scroll Position,Scroll Percentage,Mouse Scroll DeltaY\n'
//       //     + scrollData.map(e => `${e.time},${e.event || 'scroll'},${e.position || ''},${e.percentage || ''},${e.deltaY || ''}`).join('\n');
          

//       let csvContent = 'data:text/csv;charset=utf-8,'
//           + 'Event Time (UTC),Event,Scroll Position,Scroll Percentage,Mouse Scroll DeltaY\n'
//           + scrollData.map(e => `${e.time},${e.event || ''},${e.position || ''},${e.percentage || ''},${e.deltaY || ''}`).join('\n');
      
//       // Create a blob from the CSV content
//       var blob = new Blob([csvContent], {type: 'text/csv'});

//       // Create a blob URL
//       var url = URL.createObjectURL(blob);

//       // Create a download link and click it
//       var downloadLink = document.createElement("a");
//       downloadLink.href = url;
//       downloadLink.download = "scroll_data.csv";
//       document.body.appendChild(downloadLink);
//       downloadLink.click();
//       document.body.removeChild(downloadLink);

//       // Clear scrollData after download
//       scrollData = [];
//   }, 3000);
// });

// // // Listen to mouse wheel event
// // window.addEventListener('wheel', function(event){
// //   console.log(event.deltaY); // Logs the distance scrolled in pixels. Positive value if scrolling down, negative value if scrolling up.
// // });

// // // Listen to mouse wheel event
// // window.addEventListener('wheel', function(event){
// //   let dateTime = getDateTime();

// //   // Save scroll data
// //   scrollData.push({
// //       time: dateTime,
// //       event: 'mouseScroll',
// //       deltaY: event.deltaY
// //   });
// // });

// // Capture screenshot of visible area
// chrome.runtime.sendMessage({"message": "capture_page"});





// Function to get scroll percentage
function getScrollPercentage() {
  return ((window.scrollY + window.innerHeight) / document.body.offsetHeight) * 100;
}

// Function to get current date-time
function getDateTime() {
  return new Date().toISOString();
}

let scrollData = [];
let previousScrollPosition = window.scrollY;

// Listen to scroll event
window.addEventListener('scroll', function(){
  let currentScrollPosition = window.scrollY;

  // We only want to record a scroll event if the position has changed.
  if (currentScrollPosition !== previousScrollPosition) {
    let scrollPercentage = getScrollPercentage();
    let dateTime = getDateTime();

    // Save scroll data
    scrollData.push({
      time: dateTime,
      event: 'scroll',
      position: currentScrollPosition,
      percentage: scrollPercentage
    });

    previousScrollPosition = currentScrollPosition;
  }
});

// Listen to mousemove event
window.addEventListener('mousemove', function(event){
  let dateTime = getDateTime();

  // Save mouse position data
  scrollData.push({
    time: dateTime,
    event: 'mousemove',
    mouseX: event.clientX,
    mouseY: event.clientY
  });
});

let scrollTimer = null;
window.addEventListener('scroll', function(){
  // Clear the timer if it already exists
  if (scrollTimer !== null) {
      clearTimeout(scrollTimer);
  }

  // Set the timer
  scrollTimer = setTimeout(function() {
      // Create the CSV file after 3 seconds of no scrolling
      let csvContent = 'data:text/csv;charset=utf-8,'
          + 'Time (UTC),Event,Scroll Position,Scroll Percentage,Mouse X,Mouse Y\n'
          + scrollData.map(e => {
              // Get the values in the correct order
              let values = [
                  e.time,
                  e.event,
                  e.position || '', // Use an empty string if the position is not defined
                  e.percentage || '', // Use an empty string if the percentage is not defined
                  e.mouseX || '', // Use an empty string if the mouseX is not defined
                  e.mouseY || ''  // Use an empty string if the mouseY is not defined
              ];

              // Join the values into a string and return it
              return values.join(',');
          }).join('\n');

      // Create a blob from the CSV content
      var blob = new Blob([csvContent], {type: 'text/csv'});

      // Create a blob URL
      var url = URL.createObjectURL(blob);

      // Create a download link and click it
      var downloadLink = document.createElement("a");
      downloadLink.href = url;
      downloadLink.download = "scroll_data.csv";
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);

      // Clear scrollData after download
      scrollData = [];
  }, 3000);
});
