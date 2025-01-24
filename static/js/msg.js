function showToast(type, msg) {
    let toast = document.createElement('div');
    toast.classList.add('toastboxes', 'shadow', 'ms-3', 'me-3', 'my-2', 'rounded');

    let innerhtml = '';
    if (type === 'success') {
        toast.classList.add('success');
        innerhtml = `<i class="fa-solid fa-circle-check"></i> ${msg}`;
    } else if (type === 'warning') {
        toast.classList.add('warning');
        innerhtml = `<i class="fa-solid fa-triangle-exclamation"></i> ${msg}`;
    } else if (type === 'info') {
        toast.classList.add('info');
        innerhtml = `<i class="fa-solid fa-circle-info"></i> ${msg}`;
    } else if (type === 'error') {
        toast.classList.add('error');
        innerhtml = `<i class="fa-solid fa-circle-xmark"></i> ${msg}`;
    }

    toast.innerHTML = innerhtml;

    // Append the toast to the toastBox
    toastBox.appendChild(toast);

    // Remove the toast after 4 seconds
    setTimeout(() => {
        toast.remove();
    }, 2000);
}