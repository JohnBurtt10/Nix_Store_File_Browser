function createOrUpdatePackageLayers(packageData) {
    const modalId = 'packageListsModal'; // Assuming the modal ID is fixed
    const modal = document.getElementById(modalId);
    if (!modal) {
        console.error("Modal with ID '" + modalId + "' not found.");
        return;
    }

    // Find the modal-body element
    const modalBody = modal.querySelector('.modal-body');
    if (!modalBody) {
        console.error("Modal body not found in modal with ID '" + modalId + "'.");
        return;
    }

    modalBody.innerHTML = "";

    Object.entries(packageData).forEach(([layerName, layerInfo]) => {
        // Create layer info section
        const layerInfoSection = document.createElement('div');
        layerInfoSection.className = 'layer-info';

        // Display layer name
        const layerNameHeading = document.createElement('h6');
        layerNameHeading.textContent = layerName;
        layerInfoSection.appendChild(layerNameHeading);

        // Display overhead
        // const overheadTitle = document.createElement('p');
        // overheadTitle.textContent = 'Overhead: ' + layerInfo.overhead + ' bytes';
        // layerInfoSection.appendChild(overheadTitle);

        // Display accountedForFileSizeMagnitude
        // const accountedForFileSizeMagnitudeTitle = document.createElement('p');
        // accountedForFileSizeMagnitudeTitle.textContent = 'Accounted For File Size: ' + layerInfo.accountedForFileSizeMagnitude + ' MB';
        // layerInfoSection.appendChild(accountedForFileSizeMagnitudeTitle);

        // Display accountedForFileSizeRelative
        const accountedForFileSizeRelativeTitle = document.createElement('p');
        accountedForFileSizeRelativeTitle.textContent = 'Portion Of the World Accounted For: ' + layerInfo.accountedForFileSizeRelative;
        layerInfoSection.appendChild(accountedForFileSizeRelativeTitle);

        // Display accountedForFileSizeRelative
        const isCreatingZeroEntropyLayersTitle = document.createElement('p');
        isCreatingZeroEntropyLayersTitle.textContent = 'Packages Are Zero Entropy: ' + layerInfo.isCreatingZeroEntropyLayers;
        layerInfoSection.appendChild(isCreatingZeroEntropyLayersTitle);

          // Display accountedForFileSizeRelative
          const recursiveFileSizeTitle = document.createElement('p');
          recursiveFileSizeTitle.textContent = 'Recursive File Size: ' + layerInfo.recursiveFileSize;
          layerInfoSection.appendChild(recursiveFileSizeTitle);


        // Display package list
        const packageList = document.createElement('ul');
        packageList.className = 'list-group';
        layerInfo.packages.forEach(package => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item';
            listItem.textContent = package;
            packageList.appendChild(listItem);
        });

        // Append layer info and package list to modal body
        modalBody.appendChild(layerInfoSection);
        modalBody.appendChild(packageList);
    });
}

// // Example usage:
// const packageData = {
//     "Layer 1": {
//         packages: ["Package 1", "Package 2", "Package 3"],
//         overhead: 1024, // 1 KB
//         accountedForFileSizeMagnitude: "0.5", // 0.5 MB
//         accountedForFileSizeRelative: 0.124,
//         average: "0.5"
//     },
//     "Layer 2": {
//         packages: ["Package A", "Package B"],
//         overhead: 2048, // 2 KB
//         accountedForFileSizeMagnitude: "0.6", // 0.6 MB
//         accountedForFileSizeRelative: 0.135,
//         average: "0.6"
//     },
//     "Layer 3": {
//         packages: ["Package X", "Package Y", "Package Z"],
//         overhead: 3072, // 3 KB
//         accountedForFileSizeMagnitude: "0.7", // 0.7 MB
//         accountedForFileSizeRelative: 0.145,
//         average: "0.7"
//     }
// };

// createOrUpdatePackageLayers(packageData);
