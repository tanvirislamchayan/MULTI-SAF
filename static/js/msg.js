function showToast(type, msg) {
    let toast = document.createElement('div');
    toast.classList.add('toastboxes', 'shadow', 'ms-3', 'me-3', 'my-2', 'rounded');

    let infoMsg = (type, msg) => {
        // Create the container for the popup
        const bg = document.createElement('div');
        bg.classList.add('info-msg', 'position-fixed', 'top-50', 'start-50', 'translate-middle', 'bg-white', 'shadow', 'p-2', 'rounded');
        bg.style.zIndex = '200000';
        bg.style.minWidth = '300px';
    
        // Add the content to the popup
        bg.innerHTML = `
            <div class="text-center">
                <i class="fa-solid fa-circle-info text-primary mb-3" style="font-size: 3rem;"></i>
                <p class="mb-3 text-dark">${msg}</p>
                <div class="text-end">
                    <button class="btn btn-warning fw-bold btn-sm">OKAY</button>
                </div>
            </div>
        `;
    
        // Append the popup to the body
        document.body.appendChild(bg);
    
        // Close the popup when the "OK" button is clicked
        bg.querySelector('button').addEventListener('click', () => {
            bg.remove();
        });
    };
    

    let innerhtml = '';
    if (type === 'success') {
        toast.classList.add('success');
        innerhtml = `<i class="fa-solid fa-circle-check"></i> ${msg}`;
    } else if (type === 'warning') {
        toast.classList.add('warning');
        innerhtml = `<i class="fa-solid fa-triangle-exclamation"></i> ${msg}`;
    } else if (type === 'info') {
        infoMsg(type, msg)
        toast.classList.add('info');
        innerhtml = `<i class="fa-solid fa-circle-info"></i> ${msg}`;
    } else if (type === 'error') {
        toast.classList.add('error');
        innerhtml = `<i class="fa-solid fa-circle-xmark"></i> ${msg}`;
    }

    toast.innerHTML = innerhtml;

    // Append the toast to the toastBox
    if(type !== 'info'){
        toastBox.appendChild(toast);
    }

    // Remove the toast after 4 seconds
    setTimeout(() => {
        toast.remove();
    }, 2000);
}