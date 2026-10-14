window.setTimeout('window.location.reload()', 60000);

document.addEventListener("DOMContentLoaded", function () {
    const canvases = document.querySelectorAll('.gauge-canvas');

    canvases.forEach(canvas => {
        const ctx = canvas.getContext('2d');
        const val = parseFloat(canvas.dataset.value);
        const min = parseFloat(canvas.dataset.min);
        const max = parseFloat(canvas.dataset.max);
        const status = canvas.dataset.status;

        canvas.width = 180;
        canvas.height = 100;

        const centerX = 90;
        const centerY = 85;
        const radius = 62;
        const lineWidth = 18;

        let ratio = (val - min) / (max - min);
        if (ratio < 0) ratio = 0;
        if (ratio > 1) ratio = 1;

        // 회색 배경 아치
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI, false);
        ctx.lineWidth = lineWidth;
        ctx.strokeStyle = '#e2e8f0';
        ctx.lineCap = 'round';
        ctx.stroke();

        // 상태별 색상
        let strokeColor = '#a4d38c';
        if (status === 'warning') strokeColor = '#f59e0b';
        if (status === 'danger') strokeColor = '#ef4444';

        // 값 채우기 아치
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, Math.PI + (Math.PI * ratio), false);
        ctx.lineWidth = lineWidth;
        ctx.strokeStyle = strokeColor;
        ctx.lineCap = 'round';
        ctx.stroke();
    });
});

function change_state(state, actuator){
    let next_state, next_state_int;
    if (state.innerHTML == "ON") {
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
            state.classList.remove('state-' + state.innerHTML);
            state.classList.add('state-' + next_state);
            state.innerHTML = next_state;
            alert(actuator + "의 상태를 " + next_state + "로 변경했습니다.");
        })
        .catch(error => {console.error(error);});
    }
}