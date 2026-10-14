function toggleMode(checkbox) {
    const tr = checkbox.closest('tr');
    const modeText = tr.querySelector('.mode-text');

    if (checkbox.checked) {
        modeText.textContent = 'ON';
        modeText.classList.remove('manual');
        modeText.classList.add('auto');
    } else {
        modeText.textContent = 'OFF';
        modeText.classList.remove('auto');
        modeText.classList.add('manual');
    }
}

function change_state(checkbox, actuator){    
    let next_state = checkbox.checked ? "ON" : "OFF";
    let next_state_int = checkbox.checked ? 1 : 0;
    
    if (current.innerHTML == "ON") {
        next_state = "OFF";
        next_state_int = 0;
    }
    else {
        next_state = "ON";
        next_state_int = 1;
    }

    if (confirm(actuator + "의 상태를 " + next_state + "로 변경하시겠습니까?")) {
        fetch("/change-actuator", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                actuator : actuator,
                is_auto : next_state_int
            })
        })
        .then(response => response.json())
        .then(data => {
            alert(actuator + "의 상태를 " + next_state + "로 변경했습니다.");
            current.innerHTML = next_state;
        })
        .catch(error => {console.error(error);});
    }
}