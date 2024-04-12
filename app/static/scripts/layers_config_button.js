function toggleConfigPanel() {
    var overlay = document.getElementById('overlay');
    var configPanel = document.getElementById('layersConfigPanel');

    if (configPanel.style.display === 'block') {
        configPanel.style.display = 'none';
        overlay.style.display = 'none';
    } else {
        configPanel.style.display = 'block';
        overlay.style.display = 'block';
    }
}

var recursiveModeEnabled = false;

var exponentialBackOffEnabled = false;

var advancedEntropyModeEnabled = false;

var recursiveModeEnabled = false
var exponentialBackOffEnabled = false;
var advancedEntropyModeEnabled = false;
var approximateUncalculatedJobsetsModeEnabled = false;

var coverageThresholdModeEnabled = false;
var coverageThreshold = 0;

var packageCountModeEnabled = false;
var packageCount = 0;


function saveConfig() {
    recursiveModeEnabled = document.getElementById('recursiveModeToggle').checked;
    exponentialBackOffEnabled = document.getElementById('exponentialBackOffToggle').checked;
    advancedEntropyModeEnabled = document.getElementById('advancedEntropyModeToggle').checked;
    approximateUncalculatedJobsetsModeEnabled = document.getElementById('approximateUncalculatedJobsetsToggle').checked;
    coverageThresholdModeEnabled = document.getElementById('checkCoverageToggle').checked;
    coverageThreshold = document.getElementById('coverageThresholdInput').value;
    packageCountModeEnabled = document.getElementById('checkPackageCountToggle').checked;
    packageCount = document.getElementById('packageCountInput').value;

    // You can perform additional actions based on the toggle state here

    alert('Configuration saved successfully!\n\nRecursive Mode: ' + (recursiveModeEnabled ? 'Enabled' : 'Disabled') + 
    '\nExponential Back Off Mode: ' + (exponentialBackOffEnabled ? 'Enabled' : 'Disabled') + 
    '\nAdvanced Entropy Mode: ' + (advancedEntropyModeEnabled ? 'Enabled' : 'Disabled') +
    '\nApproximate Uncalculated Jobsets Mode: ' + (approximateUncalculatedJobsetsModeEnabled ? 'Enabled' : 'Disabled') +
    '\nCoverage Threshold Mode: ' + (coverageThresholdModeEnabled ? 'Enabled' : 'Disabled')+ 
    '\nCoverage Threshold: ' + coverageThreshold +
    '\nPackage Count Mode: ' + (packageCountModeEnabled ? 'Enabled' : 'Disabled') +
    '\nPackage Count: ' + packageCount);
    toggleConfigPanel(); // Close the configuration panel after saving
    // postData();
}