// Function to post data
function postData() {
    console.log('postData()');
    // Extract form data
    var formData = {
        sort_key_1_select_order: $("#sortKey1SelectOrder").val(),
        quantity: $("#quantity").val(),
        sort_key_1_select: $("#sortKey1Select").val(),
        minimum_entropy: $("#minimum_entropy").val(),
        minimum_file_size: $("#minimum_file_size").val(),
        sort_key_2_select: $("#sortKey2Select").val(),
        selected_project: $("#projectSelect").val(),
        recursive_mode_enabled: $(recursiveModeEnabled)
    };

    // Post data to the "/process" endpoint
    $.ajax({
        type: "POST",
        url: "/process",
        data: formData,
        success: function (response) {
            // Handle success response if needed
            console.log(response);
        },
        error: function (error) {
            // Handle error if needed
            console.error(error);
        }
    });
}