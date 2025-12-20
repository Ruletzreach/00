const board = document.getElementById("board");
const bombsText = document.getElementById("bombs");
const level = document.getElementById("level");
const restart = document.getElementById("restart");
const message = document.getElementById("message");

const levels = {
    easy: [9, 9, 10],
    medium: [16, 16, 40],
    hard: [16, 30, 99]
};

let cells, rows, cols, bombs, flags, firstClick, gameOver;

restart.onclick = level.onchange = start;

function start() {
    [rows, cols, bombs] = levels[level.value];
    board.innerHTML = "";
    board.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;

    flags = 0;
    firstClick = true;
    gameOver = false;
    message.className = "hidden";
    bombsText.textContent = `✹ ${bombs}`;

    cells = Array(rows * cols).fill().map((_, i) => ({
        bomb: false, open: false, flag: false, count: 0, i
    }));

    cells.forEach(c => {
        const el = document.createElement("div");
        el.className = "cell";
        el.oncontextmenu = e => (e.preventDefault(), flag(c, el));
        el.onclick = () => open(c, el);
        addTouch(el, c);
        c.el = el;
        board.appendChild(el);
    });
}

function addTouch(el, c) {
    let t;
    el.ontouchstart = () => t = setTimeout(() => flag(c, el), 500);
    el.ontouchend = () => clearTimeout(t);
}

function placeBombs(exclude) {
    let placed = 0;
    while (placed < bombs) {
        let r = Math.random() * cells.length | 0;
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
    for (let dx=-1; dx<=1; dx++)
        for (let dy=-1; dy<=1; dy++) {
            if (!dx && !dy) continue;
            let nx=x+dx, ny=y+dy;
            if (nx>=0 && ny>=0 && nx<cols && ny<rows)
                n.push(ny*cols+nx);
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

    if (c.count)
        el.textContent = c.count;
    else
        neighbors(c.i).forEach(i => open(cells[i], cells[i].el));

    checkWin();
}

function flag(c, el) {
    if (c.open || gameOver) return;
    c.flag = !c.flag;
    el.textContent = c.flag ? "✕" : "";
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
    if (cells.filter(c => c.open).length === rows*cols - bombs) {
        gameOver = true;
        message.textContent = "Вы выиграли";
        message.className = "win";
    }
}

start();
