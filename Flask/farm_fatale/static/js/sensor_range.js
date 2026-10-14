const saveBtn = document.getElementById("saveBtn");
const resetBtn = document.getElementById("resetBtn");

saveBtn.addEventListener("click", function(){
    const tr = document.querySelectorAll("tbody tr");

    if (confirm("현재 설정을 저장하시겠습니까?")) {
        let min = [];
        let max = [];

        for (let i = 0 ; i < tr.length ; i++) {
            const tds = tr[i].querySelectorAll("td");
            const rangeInputs = tds[2].querySelectorAll("input");       // 설정범위 (3번째 행)의 input

            if (rangeInputs[0] != null) {                               // 설정 범위/값이 존재할 경우
                min[i] = rangeInputs[0].value;
                max[i] = rangeInputs[1].value;
            }
        }
        console.log(min)
        console.log(max)

        fetch("/save-range", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                min : min,
                max : max
            })
        })
        .then(response => response.json())
        .then(data => {
            alert("설정이 저장되었습니다.");
            location.reload(true);
        })
        .catch(error => {console.error(error);});
    }
});

resetBtn.addEventListener("click", function(){
    const tr = document.querySelectorAll("tbody tr");
    
    if (confirm("설정을 기본값으로 복원하시겠습니까?")) {
        fetch("/reset-range", {
            method: "POST",
            headers: {"Content-Type": "application/json"}
        })
        .then(response => response.json())
        .then(data => {
            
            for (let i = 0 ; i < tr.length ; i++) {
                const tds = tr[i].querySelectorAll("td");
                const inputs = tds[2].querySelectorAll("input");        // 설정범위 (3번째 행)의 input

                if(inputs[0] != null){
                    let initvalue = data.init[i];
                    inputs[0].value = initvalue.min;
                    inputs[1].value = initvalue.max;
                }
            }
            alert("설정이 기본값으로 복원되었습니다.");
        })
        .catch(error => {console.error(error);});
    }
});