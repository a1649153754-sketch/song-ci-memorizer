document.addEventListener('DOMContentLoaded', () => {
    // asteriskWorks is available from data.js
    const searchInput = document.getElementById('searchInput');
    const poemList = document.getElementById('poemList');
    const emptyState = document.getElementById('emptyState');
    const activePoem = document.getElementById('activePoem');
    const poemTitle = document.getElementById('poemTitle');
    const poemAuthor = document.getElementById('poemAuthor');
    const poemContent = document.getElementById('poemContent');
    const memoryStatus = document.getElementById('memoryStatus');
    const progressBar = document.getElementById('progressBar');
    const modeBtns = document.querySelectorAll('.mode-btn');

    let currentMode = 'normal';
    let currentIndex = -1;

    // --- Memorization tracking (localStorage) ---
    const STORAGE_KEY = 'poem_memory_records';

    function loadMemoryRecords() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
        } catch { return {}; }
    }

    function saveMemoryRecords(records) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
    }

    function toggleMemory(title) {
        const records = loadMemoryRecords();
        if (records[title]) {
            delete records[title];
        } else {
            const now = new Date();
            const m = now.getMonth() + 1;
            const d = now.getDate();
            records[title] = `${m}月${d}日`;
        }
        saveMemoryRecords(records);
        renderMemoryStatus();
        renderList(searchInput.value);
        renderProgress();
    }

    function renderMemoryStatus() {
        if (currentIndex === -1) return;
        const work = asteriskWorks[currentIndex];
        const records = loadMemoryRecords();
        const date = records[work.title];
        memoryStatus.innerHTML = '';
        if (date) {
            memoryStatus.innerHTML = `<span class="memory-done">✅ 已于 ${date} 完成背诵</span><button class="memory-btn memory-btn-undo" id="memToggleBtn">取消标记</button>`;
        } else {
            memoryStatus.innerHTML = `<span class="memory-not">尚未标记背诵</span><button class="memory-btn memory-btn-mark" id="memToggleBtn">📝 标记已背</button>`;
        }
        document.getElementById('memToggleBtn').addEventListener('click', () => toggleMemory(work.title));
    }

    function renderProgress() {
        const records = loadMemoryRecords();
        const total = asteriskWorks.length;
        const done = Object.keys(records).length;
        progressBar.textContent = `已背 ${done} / ${total}`;
    }

    // Remove punctuation helper
    const punctuationRegex = /[，。！？、；：“”‘’《》（）\s]/g;

    function renderList(query = '') {
        poemList.innerHTML = '';
        const records = loadMemoryRecords();
        asteriskWorks.forEach((work, idx) => {
            if (work.title.includes(query)) {
                const li = document.createElement('li');
                const titleSpan = document.createElement('span');
                titleSpan.textContent = work.title;
                li.appendChild(titleSpan);
                if (records[work.title]) {
                    const check = document.createElement('span');
                    check.className = 'mem-check';
                    check.textContent = '✓';
                    li.appendChild(check);
                }
                li.dataset.index = idx;
                if (idx === currentIndex) {
                    li.classList.add('active');
                }
                li.addEventListener('click', () => selectPoem(idx));
                poemList.appendChild(li);
            }
        });
    }

    function selectPoem(index) {
        currentIndex = index;
        document.querySelectorAll('.poem-list li').forEach(li => {
            li.classList.toggle('active', parseInt(li.dataset.index) === index);
        });

        const work = asteriskWorks[index];
        poemTitle.textContent = work.title;
        poemAuthor.textContent = work.author || '佚名';

        emptyState.classList.add('hidden');
        activePoem.classList.remove('hidden');

        renderContent();
        renderMemoryStatus();
    }

    function renderContent() {
        if (currentIndex === -1) return;
        const work = asteriskWorks[currentIndex];

        // Clear old content
        poemContent.innerHTML = '';
        poemContent.className = `poem-body ${currentMode}-mode`;

        work.content.forEach((line, lineIndex) => {
            const p = document.createElement('p');
            // Parse line character by character
            let charIndexInSentence = 0; // reset for each sentence

            for (let i = 0; i < line.length; i++) {
                const char = line[i];
                const span = document.createElement('span');
                const isPunctuation = punctuationRegex.test(char);
                punctuationRegex.lastIndex = 0; // reset regex state

                span.textContent = char;
                span.className = 'char';

                if (isPunctuation) {
                    span.classList.add('punct');
                    charIndexInSentence = 0; // sentence broken by punctuation
                } else {
                    span.classList.add('text-char');
                    applyModeEffects(span, charIndexInSentence, currentMode, lineIndex, i, work);
                    charIndexInSentence++;
                }

                p.appendChild(span);
            }
            poemContent.appendChild(p);
        });
    }

    function applyModeEffects(span, pos, mode, lineIndex, globalCharIndex, work) {
        if (mode === 'normal') {
            span.setAttribute('contenteditable', 'true');
            span.addEventListener('input', function () {
                // Update the memory object
                const lineContent = work.content[lineIndex];
                const newChar = this.textContent || ' ';
                // Optional: handle if user types multiple characters by only taking the first, or replacing string
                work.content[lineIndex] = lineContent.substring(0, globalCharIndex) + newChar.charAt(0) + lineContent.substring(globalCharIndex + 1);
                this.textContent = newChar.charAt(0); // force single character back to span
            });
            // Handle paste to prevent HTML injection and multiple chars
            span.addEventListener('paste', function (e) {
                e.preventDefault();
                const text = (e.originalEvent || e).clipboardData.getData('text/plain');
                if (text) {
                    this.textContent = text.charAt(0);
                    // trigger input event to save
                    const event = new Event('input', { bubbles: true });
                    this.dispatchEvent(event);
                }
            });
            return;
        } else if (mode === 'first-char') {
            if (pos !== 0) {
                span.classList.add('masked');
                span.dataset.char = span.textContent;
                // Click to reveal
                span.addEventListener('click', function () {
                    this.classList.remove('masked');
                });
            }
        } else if (mode === 'fill-blank') {
            // Randomly hide 30% of characters
            if (Math.random() < 0.3) {
                span.classList.add('masked');
                span.dataset.char = span.textContent;
                span.addEventListener('click', function () {
                    this.classList.remove('masked');
                });
            }
        } else if (mode === 'hide-all') {
            span.classList.add('masked');
            span.dataset.char = span.textContent;
            span.addEventListener('click', function () {
                this.classList.remove('masked');
            });
        }
    }

    // Event Listeners
    searchInput.addEventListener('input', (e) => {
        renderList(e.target.value);
    });

    modeBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            modeBtns.forEach(b => b.classList.remove('active'));
            const target = e.currentTarget;
            target.classList.add('active');
            currentMode = target.dataset.mode;
            renderContent();
        });
    });

    // Initialize
    renderList();
    renderProgress();
});
