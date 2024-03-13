function generateLayers() {

    // // // Get the values from the form
    // var numberOfLayers = parseInt(document.getElementById('numberOfLayers').value);
    // var quantity = parseInt(document.getElementById('fff').value);

    // // Validate input values
    // if (isNaN(numberOfLayers) || isNaN(quantity)) {
    //     alert('Please enter valid numbers for the layers and quantity.');
    //     return;
    // }

    // // Specify parameters
    // const params = new URLSearchParams();
    // params.append('numberOfLayers', numberOfLayers);
    // params.append('quantity', quantity);

    // // Clear previous progress
    // document.getElementById('progress').innerHTML = '';

    // // Make an asynchronous request to the Flask server
    // fetch('/generate_layers?' + params.toString(), {
    //     method: 'GET', // or 'POST' if needed
    //     headers: {
    //         'Content-Type': 'application/json',
    //         // Add other headers if necessary
    //     },
    // })
    //     .then(response => {
    //         const reader = response.body.getReader();

    //         return new ReadableStream({
    //             start(controller) {
    //                 function processChunk({ done, value }) {
    //                     if (done) {
    //                         controller.close();
    //                         return;
    //                     }


    //                     // Convert bytes to string and parse JSON
    //                     const progress = JSON.parse(new TextDecoder().decode(value));

    //                     console.log('progress: ', progress);

    //                     // Update progress on the client side
    //                     // document.getElementById('progress').innerHTML = `Progress: ${progress.progress}%<br>`;
    //                     document.getElementById('progress').innerHTML = `${progress.task} ${progress.progress}%<br>`;

    //                     // Continue reading
    //                     reader.read().then(processChunk);
    //                 }

    //                 // Start processing chunks
    //                 reader.read().then(processChunk);
    //             }
    //         });
    //     })
    //     .catch(error => console.error('Error during fetch operation:', error));

    // return

    // // Get the values from the form
    var numberOfLayers = parseInt(document.getElementById('numberOfLayers').value);
    var quantity = parseInt(document.getElementById('fff').value);

    // Validate input values
    if (isNaN(numberOfLayers) || isNaN(quantity)) {
        alert('Please enter valid numbers for the layers and quantity.');
        return;
    }

    // formData = { 
    //     numberOfLayers, 
    //     quantity
    // };

    var data = { 'param1': numberOfLayers, 'param2': quantity };

    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

    socket.emit('start_progress', data);

    socket.on('message', function (msg) {
        console.log(msg.data);
    });

    var previousProgress = 0;

    socket.on('progress', function (data) {
        var myProgress = document.getElementById("myProgress");
        var myTask = document.getElementById("myTask");
        if (myProgress.style.display !== "block") {
            myProgress.style.display = "block";
        }
        if (myTask.style.display !== "block") {
            myTask.style.display = "block";
        }


        var progress = data.progress;
        if (progress < previousProgress) {
            console.log('reseting');
            reset();
            move(0,0);
        }
        move(progress, previousProgress);
        previousProgress = progress;
        var task = data.task;
        var myTask = document.getElementById("myTask");
        myTask.innerHTML = task;
        console.log('progress: ', progress);
        // document.getElementById('myProgress').innerHTML = `Progress: ${progress}%<br>`;
        // document.getElementById('myProgress').innerHTML = `${task} ${progress}%<br>`;
        // if (progress === 100) {
        //     alert('Loading complete!');
        // }
    });

    // Handle the connect and disconnect events
    socket.on('connect', function () {
        // var myProgress = document.getElementById("myProgress");
        // var myTask = document.getElementById("myTask");
        // if (myProgress.style.display !== "block") {
        //     myProgress.style.display = "block";
        // }
        // if (myTask.style.display !== "block") {
        //     myTask.style.display = "block";
        // }


        // // var progress = data.progress;
        // // var task = data.task;
        // var myTask = document.getElementById("myTask");
        // // myTask.innerHTML = task;
        // move(100);
        console.log('Connected to the server');

    });

    socket.on('result', function (data) {
        // $('#result').text('Result: ' + JSON.stringify(data));
        handleResult(data);
    });

    socket.on('disconnect', function () {
        console.log('Disconnected from the server');
        var myProgress = document.getElementById("myProgress");
        var myTask = document.getElementById("myTask");
        if (myProgress.style.display !== "none") {
            myProgress.style.display = "none";
        }
        if (myTask.style.display !== "none") {
            myTask.style.display = "none";
        }
    });

    function startProgress() {
        socket.emit('start_progress');
    }

    // $.ajax({
    //     type: "POST",
    //     url: "/generate_layers",
    //     contentType: "application/json",
    //     data: JSON.stringify(formData),
    //     success: function (response) {
    //         console.log(response);
    //         for (const element of response) {
    //             console.log(element);
    //             // Content of the file
    //             const data = {
    //                 'image_names': element[0],
    //                 'overhead': element[1],
    //                 'packages': element[2]
    //             };

    //             // Convert the data to a JSON string
    //             const jsonData = JSON.stringify(data, null, 2);

    //             // Create a Blob from the JSON data
    //             const blob = new Blob([jsonData], { type: 'application/json' });

    //             // Create a download link
    //             const link = document.createElement('a');

    //             // Set the download attribute and create a data URI to trigger the download
    //             link.download = 'layer.txt';
    //             link.href = window.URL.createObjectURL(blob);

    //             // Append the link to the document
    //             document.body.appendChild(link);

    //             // Trigger the click event to start the download
    //             link.click();

    //             // Remove the link from the document
    //             document.body.removeChild(link);
    //         }
    //     },
    //     error: function (error) {
    //         console.error('Error:', error);
    //     }
    // });

    // alert('Hold tight, the layers are being generated!');
}

function handleResult(response) { 
    console.log(response);
    for (const element of response) {
        console.log(element[1]);
        // Content of the file
        const data = {
            'image_names': element[0],
            'overhead': element[1],
            'packages': element[2]
        };

        // Convert the data to a JSON string
        const jsonData = JSON.stringify(data, null, 2);

        // Create a Blob from the JSON data
        const blob = new Blob([jsonData], { type: 'application/json' });

        // Create a download link
        const link = document.createElement('a');

        // Set the download attribute and create a data URI to trigger the download
        link.download = 'layer.txt';
        link.href = window.URL.createObjectURL(blob);

        // Append the link to the document
        document.body.appendChild(link);

        // Trigger the click event to start the download
        link.click();

        // Remove the link from the document
        document.body.removeChild(link);
    }
}

var i = 0;
var elem = document.getElementById("myBar");
var width = 10;
var id;

function move(targetValue, currentValue) {
    if (i == 0) {
      i = 1;
      width = currentValue; // Set initial width to the current value
      id = setInterval(frame, 10);
  
      function frame() {
        if (width >= targetValue) {
          clearInterval(id);
          i = 0;
        } else {
          width++;
          elem.style.width = width + "%";
          elem.innerHTML = width + "%";
        }
      }
    }
  }

function reset() {
  clearInterval(id);
  width = 0;
  elem.style.width = width + "%";
  elem.innerHTML = width + "%";
  i = 0;
}


// Example usage: move to 80% and stay there
// move(80);


// Example usage:
// move(0);
