// document.addEventListener('DOMContentLoaded', () => {
//     const navOpenBtn = document.getElementById('btnNavOpen');
//     const navClsBtn = document.getElementById('btnNavOpen');
//     const wrapperDiv = document.getElementById('wrapperDiv');
    
//     navOpenBtn.addEventListener('click', ()=> {
//         if(!wrapperDiv.classList.contains('show-side-nav')) {
//             wrapperDiv.classList.add('show-side-nav');
//         }
//     });
//     navClsBtn.addEventListener('click', ()=> {
//         if(wrapperDiv.classList.contains('show-side-nav')) {
//             wrapperDiv.classList.remove('show-side-nav');
//         }
//     });
// });

document.addEventListener('DOMContentLoaded', () => {
    const navOpenBtn = document.getElementById('btnNavOpen');
    const navClsBtn = document.getElementById('btnNavCls');
    const wrapperDiv = document.getElementById('wrapperDiv');

    // Event listener to open the side navigation
    navOpenBtn.addEventListener('click', () => {
        if (!wrapperDiv.classList.contains('show-side-nav')) {
            wrapperDiv.classList.add('show-side-nav');
        }
    });

    // Event listener to close the side navigation
    navClsBtn.addEventListener('click', () => {
        if (wrapperDiv.classList.contains('show-side-nav')) {
            wrapperDiv.classList.remove('show-side-nav');
        }
    });

    // dashoboard
    const dContents = document.querySelectorAll('.d-content');
    dContents.forEach(content => {
        content.addEventListener('click', () => {
            let aLinkId = content.getAttribute('data-link');
            let aLink = document.getElementById(aLinkId);
            if (aLink){
                aLink.click();
            } else {
                console.log(aLinkId)
            }
        });
    });

    // aside menu
    const btnMenusOpen = document.getElementById('btnMenusOpen');
    const divMenus = document.getElementById('divMenus');
    btnMenusOpen.addEventListener('click', () => {
        if (divMenus.classList.contains('open-menu')) {
            divMenus.classList.remove('open-menu');
        } else {
            divMenus.classList.add('open-menu');
        }
    })
    
    // requested user handeler
    const rContents = document.querySelectorAll('.r-content');
    rContents.forEach(content => {
        let uid = content.getAttribute('data');
        console.log(uid)
        content.addEventListener('click', () => {
            let currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('uid', uid);
            window.location.href = currentUrl.toString();
        });
    });
});
