document.querySelectorAll("[data-quiz]").forEach((quiz) => {
  const feedback = quiz.querySelector(".feedback");
  quiz.addEventListener("change", (event) => {
    const choice = event.target;
    if (!choice.matches('input[type="radio"]')) return;
    const correct = choice.value === quiz.dataset.answer;
    feedback.textContent = correct
      ? quiz.dataset.correct
      : quiz.dataset.incorrect;
    feedback.className = `feedback ${correct ? "correct" : "incorrect"}`;
  });
});
