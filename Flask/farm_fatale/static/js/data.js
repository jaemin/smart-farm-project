const start = document.getElementById("startDate");
const end = document.getElementById("endDate");
const tableBody = document.querySelector("tbody");
const searchBtn = document.getElementById("searchBtn");

start.value = new Date();
end.value = new Date();

let days = 7;

// 기간 선택 버튼 토글
function setPeriod(type, btn) {
    document.querySelectorAll(".btn-filter").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    // 7일 데이터 조회
    if (type === "7d") {
        // 조회기간이 직접 선택이 아닐 경우, input date 비활성화
        if (!start.hasAttribute("disabled")){
            start.setAttribute("disabled", true);
            end.setAttribute("disabled", true);
            start.value = "";
            end.value = "";
            searchBtn.setAttribute("disabled", true);
            days = 7;
        }
        systemsetdata(days);
    } 

    // 30일 데이터 조회
    else if (type === "30d") {
        // 조회기간이 직접 선택이 아닐 경우, input date 비활성화
        if (!start.hasAttribute("disabled")){
            start.setAttribute("disabled", true);
            end.setAttribute("disabled", true);
            start.value = "";
            end.value = "";
            searchBtn.setAttribute("disabled", true);
            days = 30;
        }
        systemsetdata(days);
    }

    // 직접 날짜를 선택하여 조회
    else {
        start.removeAttribute("disabled");
        end.removeAttribute("disabled");

        start.value = new Date().toISOString().substring(0, 10);
        end.value = new Date().toISOString().substring(0, 10);
        searchBtn.removeAttribute("disabled");
    }
}

function searchData() {
    const start = document.getElementById("startDate").value;
    const end = document.getElementById("endDate").value;    
    
    usersetdata(start, end);
}

// 테이블 데이터를 CSV 파일로 추출 및 다운로드
function downloadCSV() {
    if (confirm("CSV 파일을 다운로드하시겠습니까?")){
        const table = document.getElementById("statsTable");
        let csv = [];

        // 한글 깨짐 방지 BOM 추가
        const BOM = "\uFEFF";

        for (let row of table.rows) {
            let cols = Array.from(row.cells).map(cell => `"${cell.innerText.trim()}"`);
            csv.push(cols.join(","));
        }

        const csvContent = "data:text/csv;charset=utf-8," + BOM + encodeURIComponent(csv.join("\n"));
        const link = document.createElement("a");
        link.setAttribute("href", csvContent);

        if (start.value == ""){
            let today = new Date();
            let startDate = new Date(today);

            let endyear = today.getFullYear();
            let endmonth = (today.getMonth() + 1).toString().padStart(2, '0');
            let enddate = today.getDate().toString().padStart(2, '0');

            end.value = endyear + "-" + endmonth + "-" + enddate;       

            startDate.setDate(today.getDate() - days);

            let startyear = startDate.getFullYear();
            let startmonth = (startDate.getMonth() + 1).toString().padStart(2, '0');
            let startdate = startDate.getDate().toString().padStart(2, '0');

            start.value = startyear + "-" + startmonth + "-" + startdate;
        }

        link.setAttribute("download", `data_${start.value}_${end.value}_csv.txt`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

function systemsetdata(number){
    tableBody.innerHTML = "";

    fetch("/data-system", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            day: number
        })
    })
    .then(response => response.json())
    .then(data => {
        for (let i = 0 ; i < data.stats_data.length ; i++){
            let stat = data.stats_data[i];
            let rows = tableBody.insertRow();

            rows.insertCell().innerHTML = stat.name;
            rows.insertCell().innerHTML = stat.avg;
            rows.insertCell().innerHTML = stat.min;
            rows.insertCell().innerHTML = stat.max;
            rows.insertCell().innerHTML = stat.rate;
            rows.insertCell().innerHTML = stat.warn;
            rows.insertCell().innerHTML = stat.danger;
        }
    })
    .catch(error => {console.error(error);});
}

function usersetdata(start, end){
    tableBody.innerHTML = "";

    let startday = start.replaceAll("-", "")
    let endday = end.replaceAll("-", "")

    fetch("/data-user", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            start: startday,
            end: endday
        })
    })
    .then(response => response.json())
    .then(data => {
        for (let i = 0 ; i < data.stats_data.length ; i++){
            let stat = data.stats_data[i];
            let rows = tableBody.insertRow();

            rows.insertCell().innerHTML = stat.name;
            rows.insertCell().innerHTML = stat.avg;
            rows.insertCell().innerHTML = stat.min;
            rows.insertCell().innerHTML = stat.max;
            rows.insertCell().innerHTML = stat.rate;
            rows.insertCell().innerHTML = stat.warn;
            rows.insertCell().innerHTML = stat.danger;
        }
    })
    .catch(error => {console.error(error);});
}