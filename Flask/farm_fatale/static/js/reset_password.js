const password = document.getElementById("password");
const passwordConfirm = document.getElementById("password_confirm");
const passwordMessage = document.getElementById("password-message");

passwordConfirm.addEventListener("input", function () {

    // 비밀번호 확인칸이 비어있으면 아무것도 표시하지 않음
    if (passwordConfirm.value === "") {
        passwordMessage.textContent = "";
        return;
    }

    // 두 비밀번호가 같은 경우
    if (password.value === passwordConfirm.value) {
        passwordMessage.textContent = "비밀번호가 일치합니다.";
        passwordMessage.style.color = "#2e7d32";
    }

    // 두 비밀번호가 다른 경우
    else {
        passwordMessage.textContent = "비밀번호가 일치하지 않습니다.";
        passwordMessage.style.color = "#e53935";
    }
});