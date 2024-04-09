function toggleDropdown(path) {
    var dropdown = document.getElementById(path);
    dropdown.classList.toggle('active');
}

var earliest_jobset = '{{ earliest_jobset }}';

var latest_jobset = '{{ latest_jobset }}';

var latest_instance_hash = '{{ latest_instance_hash }}';

var category = '{{ latest_instance_hash }}';

var jobsets = '{{ jobsets }}';

// first sort key

function removeBranch(button) {
    button.parentElement.querySelector(".inline-paragraph").innerText = "";
    button.remove();
}

function replacePath(goButton) {

    var dropDownElement = goButton.parentElement.parentElement;
    var caret = dropDownElement.querySelector('.caret');
    var storePathSelectValue = goButton.parentElement.querySelector("select").value;
    var parts = storePathSelectValue.split('-');
    var hash = parts[0];
    var nested = caret.parentElement.querySelector('.nested');
    caret.setAttribute('data-path', storePathSelectValue);
    caret.setAttribute('data-custom-value', hash);
    caret.innerHTML = storePathSelectValue;
    nested.innerHTML = "";
}

function replaceText(caret) {

    var caret = caret.parentElement.querySelector('.caret');
    var hash = caret.getAttribute("data-custom-value");
    var path = caret.getAttribute("data-path");
    var base = document.getElementById("base");
    var compare = document.getElementById("compare");
    var storePathJobsets = caret.getAttribute("data-store-path-jobsets");

    console.log(storePathJobsets);

    if (base.innerText == "") {

        base.setAttribute("data-custom-value", hash);
        base.innerText = path;
        base.parentElement.innerHTML += '<button class="close-button move-up" onclick="removeBranch(this)">x</button>';

    } else if (compare.innerText == "") {
        compare.setAttribute("data-custom-value", hash);
        compare.innerText = path;
        compare.parentElement.innerHTML += '<button class="close-button move-up" onclick="removeBranch(this)">x</button>';

    } else {

        compare.setAttribute("data-custom-value", hash);
        compare.innerText = path;

    }
}

function getSelectedJobsets() {

    var selectedJobsets = [];
    var selectElement = document.getElementById("jobsetSelect");

    for (var i = 0; i < selectElement.options.length; i++) {
        var option = selectElement.options[i];
        if (option.selected) {
            selectedJobsets.push(option.value);
        }
    }

    return selectedJobsets;
}

function compare() {
    var base = document.getElementById("base");
    var compare = document.getElementById("compare");
    var baseHash = base.getAttribute('data-custom-value');
    var compareHash = compare.getAttribute('data-custom-value');
    // var jobsets = getSelectedJobsets();
    var jobsets = [];
    var serializedJobsetsArray = JSON.stringify(jobsets);
    var url = '/compare/' + projectSelect.value + '/' + baseHash + '/' + compareHash + "?jobsets=" + encodeURIComponent(serializedJobsetsArray);

    $.get(url, function (data) {
        var packageListDiv = document.getElementById("modal-content").querySelector('div');;
        packageListDiv.innerHTML = ""; // Clear previous content

        data.forEach(function (item) {
            var listItem = document.createElement('li');
            listItem.textContent = item[0];
            if (item[1] == 'overlap') {
                listItem.classList.add('green-text');
            } else {
                listItem.classList.add('red-text');
            }
            packageListDiv.appendChild(listItem);
        });

        // Display modal
        var modal = document.getElementById("modal");
        modal.style.display = "block";

        // Close modal when close button is clicked
        var closeButton = document.getElementById("close-button");
        closeButton.onclick = function () {
            modal.style.display = "none";
        };
    });
}



function fetchAndExpand(parentElement) {

    var caret = parentElement;
    var nestedList = caret.parentElement.querySelector('.nested');
    var hash = parentElement.getAttribute("data-custom-value");

    // Get all <li> elements within the <ul>
    var liElements = nestedList.querySelectorAll('li');

    var itemCount = liElements.length;

    if ((itemCount == 0) || (nestedList.innerHTML.trim() === '')) {
        // Fetch children nodes from the server using AJAX
        $.get('/get_children/' + hash, function (data) {

            // Append children nodes to the nested list
            data.forEach(function (childNode) {
                var parts = childNode.split('-');
                hash = parts[0];
                key = parts[1];

                // Set content for the li element
                nestedList.innerHTML += '<li class="mb-2">\
                <span>\
                <span\
                class="caret"\
                onclick="fetchAndExpand(this)"\
                data-path="' + childNode + '"\
                data-custom-value="'
                    + hash
                    + '">'
                    + childNode
                    + '</span><ul class="nested"></ul>\
                <button class="btn-secondary" onclick="replaceText(this.parentElement)">Compare</button>\
                <span>\
                </li>\
                ';

            });

            // Expand the nested list
            caret.classList.toggle('caret-down');
            nestedList.classList.toggle('active');
        });

    } else {

        // Toggle the caret and nested list without fetching from the server
        caret.classList.toggle('caret-down');
        nestedList.classList.toggle('active');

    }
}
