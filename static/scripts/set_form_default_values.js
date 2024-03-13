document.addEventListener('DOMContentLoaded', function () {
    var selectElement1 = document.getElementById("sortKey1Select");

    for (var i = 0; i < selectElement1.options.length; i++) {
        if (selectElement1.options[i].value === defaultSelectedValue1) {
            selectElement1.options[i].selected = true;
            break;
        }
    }
    
    // second sort key
    
    var selectElement2 = document.getElementById("sortKey2Select");
    
    // for (var i = 0; i < selectElement2.options.length; i++) {
    //     if (selectElement2.options[i].value === defaultSelectedValue2) {
    //         selectElement2.options[i].selected = true;
    //         break;
    //     }
    // }
    
    // project 
    
    var projectSelect = document.getElementById("projectSelect");
    
    for (var i = 0; i < projectSelect.options.length; i++) {
        if (projectSelect.options[i].value === defaultSelectedProject) {
            projectSelect.options[i].selected = true;
            break;
        }
    }
    
    // select
    
    var quantityInput = document.getElementById("quantity");
    
    quantityInput.value = defaultValue;
    
    // minimum entropy
    
    // var minimumEntropyInput = document.getElementById("minimum_entropy");
    
    // console.log('defaultMinimumEntropyValue: ', defaultMinimumEntropyValue);

    // minimumEntropyInput.value = defaultMinimumEntropyValue;
    
    // // minimum file size
    
    // var minimumFileSizeInput = document.getElementById("minimum_file_size");
    
    // minimumFileSizeInput.value = defaultMinimumFileSizeValue;
});

