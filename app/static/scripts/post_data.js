function cancel() {
    inProgress = false;


    socket.emit('cancel');

    socket.disconnect();
}


var inProgress = false;

var socket;

function explorePackages() {

    console.log('explorePackages');

    if (inProgress) {
        return;
    }

    inProgress = true;

    const generatePackageListBtn = document.getElementById('generatePackageListBtn');

    generatePackageListBtn.disabled = true;

    // Modify the form data
    var formValues = [];
    var forms = document.querySelectorAll('#container div');
    forms.forEach(function (form, index) {
        var inputs = form.querySelectorAll('select, input');
        var formData = {};
        inputs.forEach(function (input) {
            formData[input.name] = input.value;
        });
        formValues.push(formData);
    });
    var formData = {
        sort_key_1_select_order: $("#sortKey1SelectOrder").val(),
        quantity: $("#quantity").val(),
        sort_key_1_select: $("#sortKey1Select").val(),
        filters: formValues,
        sort_key_2_select: $("#sortKey2Select").val(),
        selected_project: $("#projectSelect").val(),
    };


    socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

    socket.emit('explore_packages', formData);

    socket.on('message', function (msg) {
        console.log(msg.data);
    });

    socket.on('progress', function (data) {
    });

    socket.on('error', function (data) {
    });

    var isConnected = false;
    // var socketId = null;

    // Handle the connect and disconnect events
    socket.on('connect', function () {
        if (!isConnected) {
            isConnected = true;
            // socketId = socket.id;
            console.log('Connected to the server');
            socket.on('disconnect', function () {

                console.log('Disconnected from the server');

                inProgress = false;
                // previousData = null;
                isConnected = false;

                generatePackageListBtn.disabled = true;


            });
        } else {
            socket.disconnect();
        }


    });

    socket.on('result', function (data) {
        console.log(data);
        // $('#result').text('Result: ' + JSON.stringify(data));
        handleResult(data);
        generatePackageListBtn.disabled = false;
    });

    socket.on('done', function () {
        generatePackageListBtn.disabled = false;
        inProgress = false;
    });

}

function createListItem(path, details, earliestJobset, latestJobset) {
    console.log(details)
    // Create li element
    var listItem = document.createElement("li");

    // Create span element with dropdown-trigger class and onclick attribute
    var spanElement = document.createElement("span");
    spanElement.className = "dropdown-trigger";
    spanElement.setAttribute("onclick", "toggleDropdown('" + path + "')");
    spanElement.textContent = path;

    // Append span element to li
    listItem.appendChild(spanElement);

    // Create and append p elements with details
    var detailsArray = [
        // ["File Size", "file_size"],
        ["Entropy", "entropy"],
        ["Dependency Weight (Nodes)", "node_dependency_weight"],
        ["Dependency Weight (File Size)", "file_size_dependency_weight"],
        ["Reverse Dependency Weight (Nodes)", "reverse_dependency_weight"],
        ["Reverse Dependency Weight (File Size)", "file_size_reverse_dependency_weight"]
    ];

    // Create dropdown div
    var dropdownDiv = document.createElement("div");
    dropdownDiv.className = "dropdown";
    dropdownDiv.id = path;
    dropdownDiv.style.border = "2px solid black"; // This creates a red solid border with 2 pixel width


    detailsArray.forEach(function (detail) {
        var title = detail[0];
        var val = details[detail[1]];
        var pElement = document.createElement("p");
        pElement.textContent = title + ": " + val;
        dropdownDiv.appendChild(pElement);
    });


    // Create inner div with store path selection and button
    var innerDiv = document.createElement("div");
    var selectLabel = document.createElement("label");
    selectLabel.textContent = "Store path:";
    var selectElement = document.createElement("select");
    selectElement.id = "storePathSelect";
    selectElement.name = "storePathSelect";
    selectElement.className = "mr-2";

    details.store_paths.forEach(function (storePath) {
        var optionElement = document.createElement("option");
        optionElement.value = storePath;
        optionElement.textContent = storePath;
        selectElement.appendChild(optionElement);
    });

    var buttonElement = document.createElement("button");
    buttonElement.setAttribute("onclick", "replacePath(this)");
    buttonElement.className = "btn-secondary";
    buttonElement.type = "submit";
    buttonElement.textContent = "Go";

    innerDiv.appendChild(selectLabel);
    innerDiv.appendChild(selectElement);
    innerDiv.appendChild(buttonElement);

    // Create span element for exploring dependency tree
    var spanInner = document.createElement("span");
    var spanOutter = document.createElement("span");
    spanInner.className = "caret";
    spanInner.setAttribute("data-path", details.last_instance_hash + "-" + path);
    spanInner.setAttribute("data-custom-value", details.last_instance_hash);
    spanInner.setAttribute("data-store-path-jobsets", details.store_path_jobsets);
    spanInner.setAttribute("data-jobset", details.latest_jobset);
    spanInner.setAttribute("onclick", "fetchAndExpand(this)");
    spanInner.textContent = details.last_instance_hash + "-" + path;

    var compareButton = document.createElement("button");
    compareButton.setAttribute("onclick", "replaceText(this.parentElement)");
    compareButton.className = "btn-secondary ml-2";
    compareButton.textContent = "Compare";

    var nestedUl = document.createElement("ul");
    nestedUl.className = "nested";

    spanOutter.appendChild(spanInner);

    spanOutter.appendChild(compareButton);

    spanOutter.appendChild(nestedUl);


    dropdownDiv.appendChild(innerDiv);

    dropdownDiv.appendChild(spanOutter);

    // Create table element
    var tableElement = document.createElement("table");

    // Create thead element with table headers
    var theadElement = document.createElement("thead");
    var trElement = document.createElement("tr");

    ["Reverse Dependency", "Earliest Occurrence", "Latest Occurrence"].forEach(function (header) {
        var thElement = document.createElement("th");
        thElement.textContent = header;
        trElement.appendChild(thElement);
    });

    theadElement.appendChild(trElement);
    tableElement.appendChild(theadElement);

    // Create tbody element with reverse dependencies
    var tbodyElement = document.createElement("tbody");

    for (var job in details.reverse_dependencies) {
        console.log(details.reverse_dependencies[job])
        if (details.reverse_dependencies.hasOwnProperty(job)) {
            var reverseDep = details.reverse_dependencies[job];
            var trReverseDep = document.createElement("tr");

            var tdJob = document.createElement("td");
            tdJob.textContent = job;

            var tdEarliest = document.createElement("td");
            // console.log("reverseDep.earliest: ", reverseDep.latest, "details.earliest_jobset: ", details.reverse_dependencies[job].latest);
            tdEarliest.className = reverseDep.earliest !== earliestJobset ? "highlight" : "";
            tdEarliest.textContent = reverseDep.earliest;

            var tdLatest = document.createElement("td");
            tdLatest.className = reverseDep.latest !== latestJobset ? "highlight" : "";
            tdLatest.textContent = reverseDep.latest;

            trReverseDep.appendChild(tdJob);
            trReverseDep.appendChild(tdEarliest);
            trReverseDep.appendChild(tdLatest);

            tbodyElement.appendChild(trReverseDep);
        }
    }

    tableElement.appendChild(tbodyElement);

    // Append dropdown div and table element to li
    dropdownDiv.appendChild(tableElement);
    listItem.appendChild(dropdownDiv);
    // listItem.appendChild(tableElement);

    return listItem;
}

i = 0;

function handleResult(response) {
    const top_n_values = response[0];
    const jobsets = response[1];
    const earliestJobset = jobsets[0];
    const latestJobset = jobsets[-1];
    const leftColumn = document.getElementById('storePathList');
    // var jobsetSelect = document.getElementById('jobsetSelect');
    // jobsetSelect.innerHTML = "";
    leftColumn.innerHTML = "";
    for (var i = 0; i < top_n_values.length; i++) {
        const path = top_n_values[i][0];
        const details = top_n_values[i][1];
        leftColumn.appendChild(createListItem(path, details, earliestJobset, latestJobset));
    }
    // for (var i = 0; i < jobsets.length; i++) {
    //     console.log(jobsets[i]);
    //     var optionElement = document.createElement("option");
    //     optionElement.value = jobsets[i];
    //     optionElement.text = jobsets[i];
    //     jobsetSelect.appendChild(optionElement);
    // }
}
