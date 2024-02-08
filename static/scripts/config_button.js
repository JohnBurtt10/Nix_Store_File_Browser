function toggleConfigPanel() {
    var overlay = document.getElementById('overlay');
    var configPanel = document.getElementById('configPanel');

    if (configPanel.style.display === 'block') {
        configPanel.style.display = 'none';
        overlay.style.display = 'none';
    } else {
        configPanel.style.display = 'block';
        overlay.style.display = 'block';
    }
}

var recursiveModeEnabled = false;

function saveConfig() {
    recursiveModeEnabled = document.getElementById('themeToggle').checked;

    // You can perform additional actions based on the toggle state here

    alert('Configuration saved successfully!\n\nRecursive Mode: ' + (recursiveModeEnabled ? 'Enabled' : 'Disabled'));
    toggleConfigPanel(); // Close the configuration panel after saving
}