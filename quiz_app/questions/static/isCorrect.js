const answerBtns = document.querySelectorAll("button.answer");
const jsForm = document.querySelector("div#js");
const htmlForm = document.querySelector("form#django");
const switchJsBtn = document.getElementById("switchJS");
const switchHtmlBtn = document.getElementById("switchHTML");
const toggleMsg = document.getElementById("jsToggleInfo");
const jsFormMsg = "JS Form enabled";
const htmlFormMsg = "Django HTMLForm enabled";

window.addEventListener("DOMContentLoaded", (event) => {
  if (localStorage.getItem("jsForm") == "active") {
    switchFormToJS(event);
  }
});

answerBtns.forEach((btn) => {
  btn.addEventListener("click", checkAnswer);
});

switchJsBtn.addEventListener("click", switchFormToJS);
switchHtmlBtn.addEventListener("click", switchFormToHTML);

function switchFormToJS(event) {
  if (localStorage.getItem("jsForm") === null) {
    localStorage.setItem("jsForm", "active");
  }
  jsForm.style.display = "block";
  htmlForm.style.display = "none";
  switchJsBtn.disabled = true;
  switchHtmlBtn.disabled = false;
  toggleMsg.innerText = jsFormMsg;
}

async function switchFormToHTML(event) {
  if (localStorage.getItem("jsForm") == "active") {
    localStorage.removeItem("jsForm");
  }
  jsForm.style.display = "none";
  htmlForm.style.display = "block";
  switchJsBtn.disabled = false;
  switchHtmlBtn.disabled = true;
  toggleMsg.innerText = htmlFormMsg;
}

async function checkAnswer(event) {
  const answerId = event.target.getAttribute("apk");
  const questionId = event.target.getAttribute("qpk");
  try {
    const csrftoken = getCookie("csrftoken");
    const response = await fetch(`/questions/${questionId}/answer/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
        mode: "same-origin",
      },
      body: JSON.stringify({ answer: answerId }),
    });
    const statusCode = response.status;
    const body = await response.json();
    isCorrectMessage(body.correct);
    disableAnswers();
  } catch (err) {
    window.alert("Something went wrong. Please try again.");
  }
}

function isCorrectMessage(correct) {
  let msg;
  if (correct) {
    msg = "Success! Your answer is correct!";
    const tryAgainBtn = document.getElementById("btn-try-again");
    tryAgainBtn.remove();
  } else {
    msg = "Try again";
  }
  const modal = document.getElementById("modal");
  modal.firstElementChild.innerText = msg;
  modal.showModal();
}

function disableAnswers() {
  answerBtns.forEach((btn) => {
    btn.disabled = true;
  });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
