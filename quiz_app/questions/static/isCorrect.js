const answerBtns = document.querySelectorAll("button.answer");
const jsForm = document.querySelector("div#js");
const htmlForm = document.querySelector("form#django");
const toggleMsg = document.getElementById("jsToggleInfo");
const switchBtn = document.querySelector("input#yes-no");
const jsFormMsg = "<strong>JS Form enabled</strong>";
const htmlFormMsg = "<strong>Django HTMLForm enabled</strong>";

window.addEventListener("DOMContentLoaded", (event) => {
  if (localStorage.getItem("jsForm") == "active" && switchBtn) {
    switchBtn.checked = true;
    switchFormToJS();
  }
});

switchBtn.addEventListener("change", toggleJS);

function toggleJS(event) {
  if (switchBtn.checked) {
    switchFormToJS();
  } else {
    switchFormToHTML();
  }
}

answerBtns.forEach((btn) => {
  btn.addEventListener("click", checkAnswer);
});

function switchFormToJS() {
  if (localStorage.getItem("jsForm") === null) {
    localStorage.setItem("jsForm", "active");
  }
  jsForm.style.display = "block";
  htmlForm.style.display = "none";
  toggleMsg.innerHTML = jsFormMsg;
}

async function switchFormToHTML() {
  if (localStorage.getItem("jsForm") == "active") {
    localStorage.removeItem("jsForm");
  }
  jsForm.style.display = "none";
  htmlForm.style.display = "block";
  toggleMsg.innerHTML = htmlFormMsg;
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
  let titleContent;
  if (correct) {
    titleContent = "Success! Correct answer";
    msg = "Your answer is correct! Let's try another question.";
    const tryAgainBtn = document.getElementById("btn-try-again");
    tryAgainBtn.remove();
  } else {
    titleContent = "Incorrect answer";
    msg = "Your answer was incorrect - try again, or skip to the next question";
  }
  const modal = document.getElementById("modal");
  const title = document.getElementById("dialog-title");
  const desc = document.getElementById("dialog-description");
  desc.innerText = msg;
  title.innerText = titleContent;
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
