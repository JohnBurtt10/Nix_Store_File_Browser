// script.js

function toggleDropdown(path) {
    var dropdown = document.getElementById(path);
    dropdown.classList.toggle('active');
}

// Replace 'defaultSelectedValue1' with the actual value you want to be selected by default
var defaultSelectedValue1 = '{{ selected_sort_key_1 }}';

// Get the <select> element by its ID
var selectElement1 = document.getElementById("sortKey1Select");

// Loop through each <option> and set 'selected' attribute if it matches the default value
for (var i = 0; i < selectElement1.options.length; i++) {
    if (selectElement1.options[i].value === defaultSelectedValue1) {
        selectElement1.options[i].selected = true;
        break;
    }
}

// Replace 'defaultSelectedValue2' with the actual value you want to be selected by default
var defaultSelectedValue2 = '{{ selected_sort_key_2 }}';

// Get the <select> element by its ID
var selectElement2 = document.getElementById("sortKey2Select");

// Loop through each <option> and set 'selected' attribute if it matches the default value
for (var i = 0; i < selectElement2.options.length; i++) {
    if (selectElement2.options[i].value === defaultSelectedValue2) {
        selectElement2.options[i].selected = true;
        break;
    }
}

// Replace 'defaultSelectedProject' with the actual value you want to set
var defaultSelectedProject = '{{ selected_project }}';

// Get the <select> element by its ID
var projectSelect = document.getElementById("projectSelect");

// Loop through each <option> and set 'selected' attribute if it matches the default value
for (var i = 0; i < projectSelect.options.length; i++) {
    if (projectSelect.options[i].value === defaultSelectedProject) {
        projectSelect.options[i].selected = true;
        break;
    }
}

// Replace 'defaultValue' with the actual value you want to set
var defaultValue = '{{ selected_quantity }}';

// Get the <input> element by its ID
var quantityInput = document.getElementById("quantity");

// Set the 'value' attribute to the default value
quantityInput.value = defaultValue;
