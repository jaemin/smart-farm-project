const view = document.getElementById('stream')
const saveBtn = document.getElementById('saveBtn')

document.addEventListener('DOMContentLoaded', function(event) {
    saveBtn.onclick = async function(){
        event.preventDefault();

        let date = new Date();
        const filename = date.getFullYear() + ("0" + (date.getMonth() + 1)).slice(-2) + ("0" + date.getDate()).slice(-2) + "_" + ("0" + date.getHours()).slice(-2) +
                                        ("0" + date.getMinutes()).slice(-2) + ("0" + date.getSeconds()).slice(-2) + ".jpg";

        const response = await fetch('/original');
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
      
        URL.revokeObjectURL(url);
    }        
}) ;