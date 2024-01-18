// Flash dismiss
function flashDismiss(id){
    document.getElementById(`flash-${id}`).style.display = 'none';
    document.getElementById(`flash-${id}`).setAttribute('hidden', true);
};

// Toggling required field
function fileOrLinkToggle(){
    const checkbox = document.getElementById('file-or-link');
    const link_input = document.getElementById('original-url');
    const file_input = document.getElementById('to-upload');

    if(checkbox.checked){
        link_input.removeAttribute('required');
        file_input.setAttribute('required', true);
    }
    else{
        link_input.setAttribute('required', true);
        file_input.removeAttribute('required');
    };
};

// Dialogs handling
function openDialog(route, message){
    document.getElementById('dialog').showModal();
    document.getElementById('dialog').style.display = 'flex';
    document.getElementById('dialog-message').innerText = message;
    document.getElementById('dialog-confirm').setAttribute('href', route);
};
function closeDialog(){
    document.getElementById('dialog').close();
    document.getElementById('dialog').style.display = 'none';
};