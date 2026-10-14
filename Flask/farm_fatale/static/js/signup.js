// =========================
// 아이디 중복 확인
// =========================

const userIdInput = document.getElementById("user_id");
const userIdMessage = document.getElementById("user_id_message");

userIdInput.addEventListener("input", async function () {

    const userId = this.value.trim();

    if (!userId) {
        userIdMessage.textContent = "";
        return;
    }

    const response = await fetch(
        "/check_user_id?user_id=" + encodeURIComponent(userId)
    );

    const data = await response.json();

    userIdMessage.textContent = data.message;

    if (data.available) {
        userIdMessage.className = "input-message success";
    } else {
        userIdMessage.className = "input-message error";
    }
});


// =========================
// 이메일 중복 확인
// =========================

const emailInput = document.getElementById("email");
const emailMessage = document.getElementById("email_message");

emailInput.addEventListener("input", async function () {

    const email = this.value.trim();

    if (!email) {
        emailMessage.textContent = "";
        return;
    }

    const response = await fetch(
        "/check_email?email=" + encodeURIComponent(email)
    );

    const data = await response.json();

    emailMessage.textContent = data.message;

    if (data.available) {
        emailMessage.className = "input-message success";
    } else {
        emailMessage.className = "input-message error";
    }
});


// =========================
// 비밀번호 확인
// =========================

const passwordInput = document.getElementById("password");
const passwordConfirmInput =
    document.getElementById("password_confirm");

const passwordMessage =
    document.getElementById("password_message");

const passwordConfirmMessage =
    document.getElementById("password_confirm_message");


function checkPassword() {

    const password = passwordInput.value;
    const passwordConfirm = passwordConfirmInput.value;

    // 비밀번호 길이
    if (password.length < 8) {

        passwordMessage.textContent =
            "비밀번호는 8자 이상 입력해주세요.";

        passwordMessage.className =
            "input-message error";

    } else {

        passwordMessage.textContent =
            "사용 가능한 비밀번호입니다.";

        passwordMessage.className =
            "input-message success";
    }


    // 비밀번호 확인
    if (!passwordConfirm) {

        passwordConfirmMessage.textContent = "";
        return;
    }


    if (password === passwordConfirm) {

        passwordConfirmMessage.textContent =
            "비밀번호가 일치합니다.";

        passwordConfirmMessage.className =
            "input-message success";

    } else {

        passwordConfirmMessage.textContent =
            "비밀번호가 일치하지 않습니다.";

        passwordConfirmMessage.className =
            "input-message error";
    }
}


passwordInput.addEventListener("input", checkPassword);
passwordConfirmInput.addEventListener("input", checkPassword);


// =========================
// 전화번호 중복 확인
// =========================

const phoneInput = document.getElementById("user_tel");
const phoneMessage = document.getElementById("user_tel_message");

phoneInput.addEventListener("input", async function () {

    const phone = this.value.trim();

    if (!phone) {
        phoneMessage.textContent = "";
        return;
    }

    const response = await fetch(
        "/check_phone?user_tel=" + encodeURIComponent(phone)
    );

    const data = await response.json();

    phoneMessage.textContent = data.message;

    if (data.available) {
        phoneMessage.className = "input-message success";
    } else {
        phoneMessage.className = "input-message error";
    }
});