function resetTimer() {
    idleTime = 0;
}

function timerIncrement() {
    idleTime += 1;
    if (idleTime > 5) { // 5 minutes
        window.location.href = "/scada/sign-out/";
    }
}

let idleTime = 0;

// Reset idle time when user performs activity
window.onload = resetTimer;
window.onmousemove = resetTimer;
window.onkeypress = resetTimer;

setInterval(timerIncrement, 60000); // 1 minute