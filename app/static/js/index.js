// Flash dismiss
function flashDismiss(id){
    document.getElementById(`flash-${id}`).remove();
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
    document.getElementsByTagName('dialog')[0].showModal();
    document.getElementsByTagName('dialog')[0].style.display = 'flex';
    document.getElementById('dialog-message').innerText = message;
    document.getElementById('dialog-confirm').setAttribute('href', route);
};
function closeDialog(){
    document.getElementsByTagName('dialog')[0].close();
    document.getElementsByTagName('dialog')[0].style.display = 'none';
};

// Exporting the new link to user's clipboard
function toClipboard(new_link){
    navigator.clipboard.writeText(`https://${new_link}`);
    document.getElementById('new-link').innerText = "Copié !";
};

// Responsive navbar button handling
function responsiveMenuDisplay(){
    const navbar = document.getElementsByTagName('nav')[0];
    const header = document.getElementsByTagName('header')[0];

    if(navbar.className === 'navbar'){
        navbar.className += ' responsive';
        header.style.backgroundColor = 'rgb(20, 30, 40)';
    }
    else{
        navbar.className = 'navbar';
        header.style.backgroundColor = 'rgb(30, 40, 50)';
    };
};

// Enabling user edit form
function enableUserEditForm(){
    const inputs = document.querySelectorAll('input');

    inputs.forEach(function(input){
        input.removeAttribute('disabled');
    });
    document.getElementById('cancel').removeAttribute('hidden');
    document.getElementById('submit').removeAttribute('hidden');
    document.getElementById('buttons-separator').removeAttribute('hidden');
    document.getElementById('edit').setAttribute('hidden', true);
    inputs[0].focus();
};

// Disable user edit form (cancel editing)
function disableUserEditForm(){
    const inputs = document.querySelectorAll('input');

    inputs.forEach(function(input){
        input.setAttribute('disabled', true);
    });
    document.getElementById('cancel').setAttribute('hidden', true);
    document.getElementById('submit').setAttribute('hidden', true);
    document.getElementById('buttons-separator').setAttribute('hidden', true)
    document.getElementById('edit').removeAttribute('hidden');
};

// Cards carousel
const next = document.getElementById('next-slide');
const previous = document.getElementById('previous-slide');
const slide_counter = document.getElementById('current-slide');
let cards = document.querySelectorAll('#slider .link-card');
let active = 0;

function loadShow(){
    let state = 0;
    cards[active].style.transform = 'none';
    cards[active].style.zIndex = 1;
    cards[active].style.filter = 'none';
    cards[active].style.opacity = 1;
    for(let i = active + 1; i < cards.length; i++){
        state++;
        cards[i].style.transform = `translateX(${160 * state}px) scale(${1 - 0.2 * state}) perspective(16px)`;
        cards[i].style.zIndex = -state;
        cards[i].style.filter = 'blur(5px)';
        cards[i].style.opacity = state > 2 ? 0 : 0.6;
    };
    state = 0;
    for(let i = active - 1; i >= 0; i--){
        state++;
        cards[i].style.transform = `translateX(${-160 * state}px) scale(${1 - 0.2 * state}) perspective(16px)`;
        cards[i].style.zIndex = -state;
        cards[i].style.filter = 'blur(5px)';
        cards[i].style.opacity = state > 2 ? 0 : 0.6;
    };
};

loadShow();
next.onclick = function(){
    active = active + 1 < cards.length ? active + 1 : active;
    slide_counter.innerText = (active + 1).toString();
    loadShow();
};
previous.onclick = function(){
    active = active - 1 >= 0 ? active - 1 : active;
    slide_counter.innerText = (active + 1).toString();
    loadShow();
};