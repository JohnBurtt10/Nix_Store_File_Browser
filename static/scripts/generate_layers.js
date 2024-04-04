function cancel() {
    // var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    inProgress = false;


    socket.emit('cancel');

    hideElementById("myProgress");
    hideElementById("myTask");
    hideElementById("proceedBtn");
    hideElementById("cancelBtn");
    resetLayerInfo();
    socket.disconnect();
    console.log('ghiwfkwfk');
    const generateLayersBtn = document.getElementById('generateLayersBtn');

    generateLayersBtn.disabled = false;
}

function resetLayerInfo() {
    const container = document.getElementById("accountedForFileSizeProgressBars");
    container.innerHTML = "";
    const layerInfoElem = document.getElementById("layerInfo");
    layerInfoElem.innerHTML = "";
    const newPackageInfoElem = document.getElementById("newPackageInfo");
    newPackageInfoElem.innerHTML = "";
    previousProgressDict = {};

}

function test() {
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

    socket.emit('proceed');

    hideElementById("myProgress");
    hideElementById("myTask");
    hideElementById("proceedBtn");

}
function makeElementDisplayInlineById(elementId) {
    var element = document.getElementById(elementId);
    if (element.style.display !== "inline") {
        element.style.display = "inline";
    }
}

function makeElementDisplayBlockById(elementId) {
    var element = document.getElementById(elementId);
    if (element.style.display !== "block") {
        element.style.display = "block";
    }
}

function hideElementById(elementId) {
    var element = document.getElementById(elementId);
    if (element.style.display !== "none") {
        element.style.display = "none";
    }
}

var inProgress = false;

var socket;

function generateLayers() {

    if (inProgress) {
        return;
    }

    inProgress = true;

    const generateLayersBtn = document.getElementById('generateLayersBtn');

    generateLayersBtn.disabled = true;


    // // Get the values from the form
    // var numberOfLayers = parseInt(document.getElementById('numberOfLayers').value);
    var quantity = parseInt(document.getElementById('valueSelector').value);

    // // Validate input values
    // if (isNaN(numberOfLayers) || isNaN(quantity)) {
    //     alert('Please enter valid numbers for the layers and quantity.');
    //     return;
    // }

    var data = { 'maxmimumLayerRecursiveFileSize': quantity, 'coverageThresholdModeEnabled': coverageThresholdModeEnabled, 'coverageThreshold': coverageThreshold, 'packageCountModeEnabled': packageCountModeEnabled, 'packageCount': packageCount };

    socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

    socket.emit('start_progress', data);

    socket.on('message', function (msg) {
        console.log(msg.data);
    });

    var previousProgress = 0;

    makeElementDisplayInlineById('cancelBtn');

    socket.on('progress', function (data) {
        makeElementDisplayBlockById("myProgress");
        makeElementDisplayBlockById("myTask");


        var progress = data.progress;
        var task = data.task;

        //TODO: there is some bug where it doesn't move after closing and reconnecting
        // console.log('progress: ', progress, previousProgress);
        if (progress < previousProgress) {
            move(0, 0, "myBar");
            previousProgress = 0;
        }

        move(progress, previousProgress, "myBar");
        previousProgress = progress;
        var myTask = document.getElementById("myTask");
        myTask.innerHTML = task;


        if (task == "Finding all store paths for packages..." || task == "Calculating Entropy...") {
            makeElementDisplayInlineById('proceedBtn');
        } else {
            hideElementById("proceedBtn");
        }


        if (task == "") {
            hideElementById("myProgress");
            hideElementById("myTask");
        }
    });

    socket.on('error', function (data) {
        var errorCode = data.error;
        if (errorCode == 1) {

        }
    });

    var previousProgressDict = {};

    // var previousData = null;
    // console.log("############### SETTING PREVIOUS DATA TO NULL");

    var stop = false;

    function createStringFromList(list) {
        if (list.length === 0) {
            return "No items to add";
        } else if (list.length === 1) {
            return "Added " + list[0];
        } else {
            var string = "Added ";
            for (var i = 0; i < list.length - 1; i++) {
                string += list[i] + ", ";
            }
            string += "and " + list[list.length - 1];
            return string;
        }
    }

    socket.on('layer_progress', function (data) {

        if (stop) {
            return;
        }
        stop = true;

        console.log('data', data);

        const accountedForFileSizeProgressBarsDiv = document.getElementById('accountedForFileSizeProgressBars');

        const jobProgressDict = data['relative_accounted_for_dict'];

        const layerInfoElem = document.getElementById('layerInfo');

        const layerCount = data['layer_count'];

        const overhead = data['overhead'];

        const isCreatingZeroEntropyLayers = data['is_creating_zero_entropy_layers'];

        const newPackages = data['new_packages'];

        const newPackageInfoElem = document.getElementById('newPackageInfo');

        const newPackageNamesString = createStringFromList(newPackages['names']);

        const jobCount = Object.keys(jobProgressDict).length;

        const megabytesAccountedFor = newPackages['accounted_for_packages_file_size'] / (1024 * 1024);

        const bytesOverhead = newPackages['overhead'];

        const newPackagesString = `${newPackageNamesString}, which accounted for ${megabytesAccountedFor.toFixed(1)}MB and introduced ${bytesOverhead}B
        of overhead across ${jobCount} images.`;

        newPackageInfoElem.innerHTML = newPackagesString;

        layerInfoElem.innerHTML = `Package Entropy: ${isCreatingZeroEntropyLayers ? 'Zero' : 'Nonzero'}, Layer Count: ${layerCount}, Overhead: ${overhead}B`;

        const layers = data['layers'];

        let packageData = {};

        for (const layer in layers) {

            const packages = layers[layer]['packages'];

            const accountedForFileSizeRelative = layers[layer]['file_size_accounted_for_relative'].toFixed(2);

            const accountedForFileSizeMagnitude = (layers[layer]['accounted_for_packages_file_size'] / (1024 * 1024)).toFixed(1);

            const average = layers[layer]['average'];

            const overhead = layers[layer]['overhead'];

            const isCreatingZeroEntropyLayers = layers[layer]['is_creating_zero_entropy_layers'];

            const recursiveFileSize = (layers[layer]['total_recursive_file_size'] / (1024 * 1024)).toFixed(1);

            packageData[layer] = { 
                
            'packages': packages,

            'overhead': overhead,

            'accountedForFileSizeMagnitude': accountedForFileSizeMagnitude,

            'accountedForFileSizeRelative': accountedForFileSizeRelative,

            'average': average,
        
            'isCreatingZeroEntropyLayers': isCreatingZeroEntropyLayers,
            
            'recursiveFileSize': recursiveFileSize,

            };
        
        }

        console.log(packageData);

        createOrUpdatePackageLayers(packageData);

        for (const key in jobProgressDict) {
            var progressBar;
            const value = parseFloat(jobProgressDict[key]);
            // Check if a div with corresponding ID already exists
            if (!document.getElementById(key)) {
                // Create a new div
                const outterDiv = document.createElement('div');
                outterDiv.id = key;
                const newDiv = document.createElement('div');
                newDiv.id = key + "ProgressBar";

                // Set the class attribute
                newDiv.classList.add('myProgress');

                // Create inner div for the title
                const title = document.createElement('div');
                title.innerText = key; // Set the title text
                // title.classList.add('title');

                // Append the title to the progress container
                outterDiv.appendChild(title);


                // Create inner div for the progress bar
                progressBar = document.createElement('div');
                // progressBar.classList.add('myBar');
                progressBar.id = key + 'Bar';
                progressBar.innerText = '0%'; // Initial value
                progressBar.classList.add('myBar', 'bg-primary'); // Adding Bootstrap class 'bg-primary'


                // Append the progress bar to the progress container
                outterDiv.appendChild(progressBar);


                // Append the new div to the document body (you can append it to a specific container if needed)
                accountedForFileSizeProgressBarsDiv.appendChild(outterDiv);

                previousProgressDict[key] = 0;
            } else {
                progressBar = document.getElementById(key + 'Bar');
            }
            move(Math.round(value * 100), previousProgressDict[key], progressBar.id);
            previousProgressDict[key] = Math.round(value * 100);
        };
        stop = false;
    });

    socket.on('error', function (data) {
        var errorCode = data.error;
        if (errorCode == 1) {

        }
    });

    var isConnected = false;
    // var socketId = null;

    // Handle the connect and disconnect events
    socket.on('connect', function () {
        if (!isConnected) {
            isConnected = true;
            // socketId = socket.id;
            hideElementById('errorMessage');
            console.log('Connected to the server');
            socket.on('disconnect', function () {

                console.log('Disconnected from the server');

                hideElementById("myProgress");
                hideElementById("myTask");
                hideElementById("errorMessage");
                hideElementById("cancelBtn");
                hideElementById("proceedBtn");
                resetLayerInfo();

                inProgress = false;
                // previousData = null;
                isConnected = false;


            });
        } else {
            console.log('ghiwfkwfk');
            socket.disconnect();
        }


    });

    socket.on('result', function (data) {
        console.log(data);
        // $('#result').text('Result: ' + JSON.stringify(data));
        handleResult(data);
    });

    socket.on('timestamp', function (data) {
        console.log(data);
        // $('#result').text('Result: ' + JSON.stringify(data));
        displayEndPoint(data);
    });



    function startProgress() {
        socket.emit('start_progress');
    }

}

function displayEndPoint(data) { 
    // Define custom endpoint URL
    var customEndpointPath = "/display/" + data;

    var beforeEndpointText = "Once the layers have been generated, they will be available here: ";

    // Create an anchor element for the endpoint
    var endpointAnchor = document.createElement("a");

    // Set the href attribute to the custom endpoint URL
    endpointAnchor.href = customEndpointPath;

    // Set the inner text of the anchor element to the endpoint
    endpointAnchor.textContent = customEndpointPath;

    // Create a span element for the text before the endpoint
    var beforeEndpointSpan = document.createElement("span");

    // Set the inner text of the span element to the text before the endpoint
    beforeEndpointSpan.textContent = beforeEndpointText;

    // Append the span element and the anchor element to the paragraph element
    document.getElementById("endPointInfo").appendChild(beforeEndpointSpan);
    document.getElementById("endPointInfo").appendChild(endpointAnchor);

}

i = 0;

function handleResult(response) {
    // console.log(response);
    // var i = 0;
    // for (const element of response) {
    const combination = response.combination;
    const overhead = response.overhead;
    const packages = response.packages;
    const accountedForPackagesFileSize = response.accounted_for_packages_file_size;
    const isCreatingZeroEntropyLayers = response.is_creating_zero_entropy_layers;
    // Content of the file
    const data = {
        'image_names': combination,
        'isCreatingZeroEntropyLayers': isCreatingZeroEntropyLayers,
        'overhead': overhead,
        'packages': packages,
        'accountedForPackageFileSize': accountedForPackagesFileSize,
    };

    // Convert the data to a JSON string
    const jsonData = JSON.stringify(data, null, 2);

    // Create a Blob from the JSON data
    const blob = new Blob([jsonData], { type: 'application/json' });

    // Create a download link
    const link = document.createElement('a');

    const timestamp = new Date().getTime();

    // Set the download attribute and create a data URI to trigger the download
    link.download = (timestamp + '_layer_' + i + '.txt'); // Change "subfolder" to your desired subfolder name
    link.href = window.URL.createObjectURL(blob);

    // Append the link to the document
    document.body.appendChild(link);

    // Trigger the click event to start the download
    link.click();

    // Remove the link from the document
    document.body.removeChild(link);

    i = i + 1;



    // const accountedForPackagesFileSizeGB = (accountedForPackagesFileSize / Math.pow(1024, 3)).toFixed(2);
    // var layerDownloadInfoElem = document.getElementById("layerDownloadInfo");
    // layerDownloadInfoElem.innerHTML = "Now downloading layer which accounts for " + accountedForPackagesFileSizeGB + " new gigabytes across " + combination.length + " images..."


    // }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Usage:
async function example() {
    console.log('Before sleep');
    await sleep(2000); // Sleep for 2000 milliseconds (2 seconds)
    resetLayerInfo();
    console.log('After sleep');
}

function move(targetValue, currentValue, elementId) {
    var elem = document.getElementById(elementId);
    var width = currentValue; // Set initial width to the current value
    var id;

    if (width >= targetValue) return; // If already reached or exceeded target value, do nothing

    id = setInterval(frame, 10);

    function frame() {
        if (width >= targetValue) {
            clearInterval(id);
        } else {
            width++;
            elem.style.width = width + "%";
            elem.innerHTML = width + "%";
            // console.log('elem.innerHTML:', elem.innerHTML);
        }
    }
}


function reset(elementId) {
    var elem = document.getElementById(elementId);
    // clearInterval(id);
    width = 0;
    elem.style.width = width + "%";
    elem.innerHTML = width + "%";
}


// Example usage: move to 80% and stay there
// move(80);


// Example usage:
// move(0);
