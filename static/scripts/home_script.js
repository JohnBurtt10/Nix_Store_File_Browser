var selectedInfoBox;

// Function to dynamically create an info box
function createInfoBox(id, jobset, previousJobset, title, info1, info2) {
    const infoBox = document.createElement('div');
    infoBox.classList.add('info-box');
    infoBox.id = id;

    infoBox.setAttribute('jobset', jobset);
    infoBox.setAttribute('previousJobset', previousJobset);

    const titleDiv = document.createElement('div');
    titleDiv.classList.add('info-title');
    titleDiv.textContent = title;

    const infoRowDiv = document.createElement('div');
    infoRowDiv.classList.add('info-row');
    const info1Paragraph = document.createElement('p');
    info1Paragraph.textContent = `Info 1: ${info1}`;

    infoRowDiv.appendChild(info1Paragraph);

    // Convert the array to a JSON string
    const jsonString = JSON.stringify(info2);

    infoBox.setAttribute('data-custom-value', jsonString);

    infoBox.appendChild(titleDiv);
    infoBox.appendChild(infoRowDiv);

    // Add the click event to show details
    infoBox.onclick = function () {
        showDetails(this);
    };

    document.getElementById('sidebar').appendChild(infoBox);
}


function dropdownChange(projectSelect) {

    console.log("projectSelect: ", projectSelect.value);

    var project = projectSelect.value;

    var previousJobset;

    var done = false;

    $.get('/get_jobsets/' + project, function (data) {

        console.log(data);

        data.forEach(function (jobset) {
            if (previousJobset) {
                createInfoBox(jobset, jobset, previousJobset, jobset, info1 = "info1", data);
            }
            previousJobset = jobset;
        });
    });
}

function createStorePathCaret(difference) {
    // Create span element
    var listItemElement = document.createElement("li");
    var caretElement = document.createElement("span");
    var spanElement = document.createElement("span");
    caretElement.className = "caret";

    spanElement.textContent = `${difference[0]} --> ${difference[1]}, ${difference[2]}, ${difference[3]}`;

    // Create ul element
    var ulElement = document.createElement("ul");
    ulElement.className = "nested";

    caretElement.onclick = function () {
        var liElements = ulElement.querySelectorAll('li');
        var itemCount = liElements.length;

        if ((itemCount == 0) || (ulElement.innerHTML.trim() === '')) {
            // Fetch children nodes from the server using AJAX
            $.get('/compare_and_group_references/' + difference[0] + '/' + difference[1], function (data) {
                for (const key in data) {
                    const value = data[key];
                    console.log('value: ', value);
                    storePathListItemElement = createStorePathCaret(value);
                    ulElement.appendChild(storePathListItemElement);


                }
            })
        }
        // Expand the nested list
        caretElement.classList.toggle('caret-down');
        ulElement.classList.toggle('active');
    };

    // Append elements to the span element
    spanElement.appendChild(caretElement);
    spanElement.appendChild(ulElement);

    listItemElement.appendChild(spanElement);

    // Append the span element to the document or a specific container
    document.body.appendChild(listItemElement);
    return listItemElement;
}

function createJobCaret(job, value) {
    // Create span element
    var spanElement = document.createElement("span");
    var caretElement = document.createElement("span");
    var listItemElement = document.createElement("li");
    caretElement.className = "caret";
    // Create ul element
    var ulElement = document.createElement("ul");
    ulElement.className = "nested";
    var recursive_file_size_change = 0
    value.forEach(difference => {
        recursive_file_size_change += difference[3];
        storePathCaret = createStorePathCaret(difference);
        ulElement.appendChild(storePathCaret);
    })
    caretElement.onclick = function () {
        // Expand the nested list
        caretElement.classList.toggle('caret-down');
        ulElement.classList.toggle('active');
    };
    spanElement.textContent = job + ', ' + recursive_file_size_change;


    // Append elements to the span element
    spanElement.appendChild(caretElement);
    spanElement.appendChild(ulElement);
    listItemElement.appendChild(spanElement);


    // Append the span element to the document or a specific container
    document.body.appendChild(listItemElement);
    return listItemElement;

}

// Function to add a new row to the table
function addTableRow(dependency, count, fileSize) {
    var table = document.getElementById('myTable').getElementsByTagName('tbody')[0];
    var newRow = table.insertRow(table.rows.length);

    var cell1 = newRow.insertCell(0);
    var cell2 = newRow.insertCell(1);
    var cell3 = newRow.insertCell(2);

    cell1.textContent = dependency;
    cell2.textContent = count;
    cell3.textContent = fileSize;
}

function getJobs(projectName, jobset, callback) {
    $.get('/get_jobs/' + projectName + '/' + jobset, function (data) {
        console.log(data);
        callback(data);
    });
}

function clearTableRows(table) {
    // Assuming your table has a tbody element to hold the rows
    var tbody = table.getElementsByTagName("tbody")[0];

    tbody.innerHTML = '';
}

function getDependenciesOfJobs(project_name, jobs, jobset1, jobset2, callback) {
    $.get('/get_dependencies_of_jobs/' + project_name + '/' + jobset1 + '/' + jobset2, { jobs: JSON.stringify(jobs) },
        function (data) {
            console.log(data);
            callback(data);

        });
}

function getSelectedJobs() {

    var selectedJobs = [];
    var selectElement = document.getElementById("jobSelect");

    for (var i = 0; i < selectElement.options.length; i++) {
        var option = selectElement.options[i];
        if (option.selected) {
            selectedJobs.push(option.value);
        }
    }

    return selectedJobs;
}

function populateTable(data) {
    for (var key in data) {
        addTableRow(key, data[key]['count'], data[key][['file_size']]);
    }
}

function emptyList(listElement) {
    // Remove all child nodes of the list
    while (listElement.firstChild) {
        listElement.removeChild(listElement.firstChild);
    }
}

function getDifferenceDependencyTree(projectName, previousJobset, jobset, callback) {
    url = '/get_whats_new/' + projectName + '/' + previousJobset + '/' + jobset;
    $.get(url, { jobs: JSON.stringify(selectedJobs) }, function (data) {
        callback(data);
    });
}

function jobSelectDropDownChange(jobSelect) {
    projectName = "v2-32-devel";
    selectedJobs = getSelectedJobs();
    var previousJobset = selectedInfoBox.getAttribute('previousJobset');
    var jobset = selectedInfoBox.getAttribute('jobset');
    var myTableElement = document.getElementById("myTable");
    clearTableRows(myTableElement);
    getDependenciesOfJobs(projectName, selectedJobs, previousJobset, jobset, function (data) {
        console.log('here');
        populateTable(data);
    })

    var listElement = document.getElementById('list');

    emptyList(listElement);

    getDifferenceDependencyTree(projectName, previousJobset, jobset, function (data) {
        for (var key in data) {
            jobListItem = createJobCaret(key, data[key]);
            listElement.appendChild(jobListItem);
        }
    })

    document.body.appendChild(listElement);

}

function showDetails(infoBox) {
    var project_name = projectSelect.value;
    const detailsDiv = document.getElementById('details');
    detailsDiv.style.display = 'block';
    selectedInfoBox = infoBox;
    console.log(infoBox);

    getJobs(project_name, infoBox.id, function (data) {
        // Process data here
        console.log('Data received:', data);
        jobs = data;
        // Get the dropdown/select element
        var jobSelectDropDown = document.getElementById("jobSelect");

        // Loop through the data and create an option element for each item
        for (var i = 0; i < jobs.length; i++) {
            var option = document.createElement("option");
            option.value = jobs[i]; // Set the value attribute
            option.text = jobs[i];  // Set the text content
            jobSelectDropDown.add(option);      // Append the option to the dropdown
        }
    });


    // You can customize the content based on the selected option and the clicked info box
    const selectedOption = document.getElementById('projectSelect').value;

}

function updateDetails() {
    // Call this function when the dropdown value changes
    // Update the details based on the selected option and the currently selected info box (if any)
    const selectedInfoBox = document.querySelector('.info-box:hover');
    if (selectedInfoBox) {
        const infoId = selectedInfoBox.getAttribute('id');
        showDetails(infoId);
    }
}
