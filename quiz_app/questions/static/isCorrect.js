const btns = document.querySelectorAll("button");

btns.forEach((btn) => {
  btn.addEventListener("click", checkAnswer);
});

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
  } catch (err) {
    window.alert("Something went wrong. Please try again.");
  }
}

function isCorrectMessage(correct) {
  let msg;
  if (correct) {
    msg = "Success! Your answer is correct!";
  } else {
    msg = "Try again";
  }
  const newHeading = document.createElement("h3");
  newHeading.innerText = msg;
  const mainHeading = document.querySelector("h4");
  const header = document.querySelector("header");
  header.insertBefore(newHeading, mainHeading);
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
