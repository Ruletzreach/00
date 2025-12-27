const board = document.getElementById("board");
const bombsText = document.getElementById("bombs");
const level = document.getElementById("level");
const restart = document.getElementById("restart");
const message = document.getElementById("message");
const modeBtn = document.getElementById("mode");

const levels = {
    easy:   [9, 9, 10],
    medium: [16, 16, 40],
    hard:   [30, 16, 99]
};

let cells, rows, cols, bombs, flags, firstClick, gameOver;
let cellSize = 32;
let mode = "open";

restart.onclick = level.onchange = start;

modeBtn.onclick = () => {
    mode = mode === "open" ? "flag" : "open";
    modeBtn.textContent = mode === "open" ? "✹" : "✕";
};

function start() {
    [rows, cols, bombs] = levels[level.value];

    board.innerHTML = "";
    flags = 0;
    firstClick = true;
    gameOver = false;

    message.className = "hidden";
    bombsText.textContent = `✹ ${bombs}`;

    resizeCells();
    board.style.gridTemplateColumns = `repeat(${cols}, ${cellSize}px)`;

    cells = Array(rows * cols).fill().map((_, i) => ({
        i, bomb: false, open: false, flag: false, count: 0
    }));

    cells.forEach(c => {
        const el = document.createElement("div");
        el.className = "cell";
        el.style.width = el.style.height = cellSize + "px";

        el.onclick = () => {
            if (gameOver) return;

            if (mode === "flag") {
                toggleFlag(c, el);
            } else {
                open(c, el);
            }
        };

        el.oncontextmenu = e => {
            e.preventDefault();
            toggleFlag(c, el);
        };

        c.el = el;
        board.appendChild(el);
    });
}

function resizeCells() {
    const maxW = window.innerWidth - 30;
    const maxH = window.innerHeight - 160;
    cellSize = Math.floor(Math.min(maxW / cols, maxH / rows, 32));
}

function placeBombs(exclude) {
    let placed = 0;
    while (placed < bombs) {
        const r = Math.random() * cells.length | 0;
        if (!cells[r].bomb && r !== exclude) {
            cells[r].bomb = true;
            placed++;
        }
    }
    cells.forEach(c =>
        c.count = neighbors(c.i).filter(n => cells[n].bomb).length
    );
}

function neighbors(i) {
    let x = i % cols, y = i / cols | 0, n = [];
    for (let dx = -1; dx <= 1; dx++)
        for (let dy = -1; dy <= 1; dy++) {
            if (!dx && !dy) continue;
            let nx = x + dx, ny = y + dy;
            if (nx >= 0 && ny >= 0 && nx < cols && ny < rows)
                n.push(ny * cols + nx);
        }
    return n;
}

function open(c, el) {
    if (c.open || c.flag || gameOver) return;

    if (firstClick) {
        placeBombs(c.i);
        firstClick = false;
    }

    c.open = true;
    el.classList.add("open");

    if (c.bomb) return lose(el);

    if (c.count) el.textContent = c.count;
    else neighbors(c.i).forEach(i => open(cells[i], cells[i].el));

    checkWin();
}

function toggleFlag(c, el) {
    if (c.open || gameOver) return;
    c.flag = !c.flag;
    el.textContent = c.flag ? "✹" : "";
    flags += c.flag ? 1 : -1;
    bombsText.textContent = `✹ ${bombs - flags}`;
}

function lose(el) {
    gameOver = true;
    el.classList.add("bomb");
    cells.forEach(c => c.bomb && (c.el.textContent = "✹"));
    message.textContent = "Вы проиграли";
    message.className = "lose";
}

function checkWin() {
    if (cells.filter(c => c.open).length === rows * cols - bombs) {
        gameOver = true;
        message.textContent = "Вы выиграли";
        message.className = "win";
    }
}

start();
window.onresize = start;

