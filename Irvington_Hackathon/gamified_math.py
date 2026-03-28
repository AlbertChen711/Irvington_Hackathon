<!DOCTYPE html>
<html>
<head>
  <title>Math Battle Arena</title>
  <style>
    body {
      font-family: Arial;
      text-align: center;
      background: #0f172a;
      color: white;
    }
    .box {
      margin-top: 50px;
    }
    input {
      padding: 10px;
      font-size: 18px;
    }
    button {
      padding: 10px 20px;
      font-size: 18px;
      margin-left: 10px;
      cursor: pointer;
    }
    .bar {
      width: 300px;
      height: 20px;
      background: gray;
      margin: 10px auto;
    }
    .health {
      height: 100%;
      background: limegreen;
    }
  </style>
</head>

<body>

<h1>⚔️ Math Battle Arena</h1>

<div class="box">
  <h2 id="question">Loading...</h2>

  <input id="answer" type="number">
  <button onclick="submitAnswer()">Attack</button>

  <p id="feedback"></p>

  <h3>🧍 You</h3>
  <div class="bar"><div id="playerHealth" class="health"></div></div>

  <h3>🤖 Enemy</h3>
  <div class="bar"><div id="enemyHealth" class="health"></div></div>
</div>

<script>
let playerHP = 100;
let enemyHP = 100;
let streak = 0;
let difficulty = 1;

let correctAnswer = 0;

function generateQuestion() {
  let a, b;

  if (difficulty === 1) {
    a = Math.floor(Math.random() * 10);
    b = Math.floor(Math.random() * 10);
    correctAnswer = a + b;
    document.getElementById("question").innerText = `${a} + ${b} = ?`;
  } else if (difficulty === 2) {
    a = Math.floor(Math.random() * 20);
    b = Math.floor(Math.random() * 10);
    correctAnswer = a - b;
    document.getElementById("question").innerText = `${a} - ${b} = ?`;
  } else {
    a = Math.floor(Math.random() * 10);
    b = Math.floor(Math.random() * 10);
    correctAnswer = a * b;
    document.getElementById("question").innerText = `${a} × ${b} = ?`;
  }
}

function updateHealth() {
  document.getElementById("playerHealth").style.width = playerHP + "%";
  document.getElementById("enemyHealth").style.width = enemyHP + "%";
}

function submitAnswer() {
  let userAnswer = Number(document.getElementById("answer").value);

  if (userAnswer === correctAnswer) {
    streak++;
    let damage = 10 + (streak >= 3 ? 10 : 0);
    enemyHP -= damage;

    document.getElementById("feedback").innerText = `🔥 Correct! You dealt ${damage} damage!`;

    if (streak >= 3) difficulty = Math.min(3, difficulty + 1);

  } else {
    streak = 0;
    playerHP -= 10;

    document.getElementById("feedback").innerText = `❌ Wrong! The answer was ${correctAnswer}`;

    difficulty = Math.max(1, difficulty - 1);
  }

  document.getElementById("answer").value = "";

  updateHealth();

  if (playerHP <= 0) {
    document.getElementById("question").innerText = "💀 You Lost!";
    return;
  }

  if (enemyHP <= 0) {
    document.getElementById("question").innerText = "🏆 You Win!";
    return;
  }

  generateQuestion();
}

// Start game
generateQuestion();
updateHealth();
</script>

</body>
</html>