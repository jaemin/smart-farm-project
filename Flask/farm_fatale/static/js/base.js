const leftMenu = document.getElementById("leftmenu");
const leftopenBtn = document.getElementById("leftopenBtn");
const leftcloseBtn = document.getElementById("leftcloseBtn");

leftopenBtn.addEventListener("click", function(){
    leftMenu.showModal();
});

leftcloseBtn.addEventListener("click", function(){
    leftMenu.close();
});

leftMenu.addEventListener("click", function(event){
    if(event.target == leftMenu){
        leftMenu.close();
    }
});

const rightMenu = document.getElementById("rightmenu");
const rightopenBtn = document.getElementById("rightopenBtn");
const rightcloseBtn = document.getElementById("rightcloseBtn");

rightopenBtn.addEventListener("click", function(){
    rightMenu.showModal();
});

rightcloseBtn.addEventListener("click", function(){
    rightMenu.close();
});

rightMenu.addEventListener("click", function(event){
    if(event.target == rightMenu){
        rightMenu.close();
    }
});