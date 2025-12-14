// Enhanced JavaScript for Agentic Air Quality Monitor

document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initDateInputs();
    initHoverEffects();
});

// --- 1. Neural Network Particle System ---
function initParticles() {
    const canvas = document.getElementById('neuralCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width, height;
    let particles = [];
    const particleCount = 60;
    const connectionDistance = 150;

    // Resize handler
    function resize() {
        width = canvas.width = canvas.parentElement.offsetWidth;
        height = canvas.height = canvas.parentElement.offsetHeight;
    }

    window.addEventListener('resize', resize);
    resize();

    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.size = Math.random() * 2 + 1;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;
        }

        draw() {
            ctx.fillStyle = '#3b82f6'; // Blue-500
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // Init particles
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        // Draw connections
        ctx.strokeStyle = 'rgba(59, 130, 246, 0.15)'; // Blue with low opacity
        ctx.lineWidth = 1;

        for (let i = 0; i < particles.length; i++) {
            let p1 = particles[i];
            p1.update();
            p1.draw();

            for (let j = i + 1; j < particles.length; j++) {
                let p2 = particles[j];
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < connectionDistance) {
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animate);
    }
    animate();
}

// --- 2. Enhanced Agent Form Logic ---
function initDateInputs() {
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }

    const rangeInput = document.getElementById('dateRange');
    const rangeValue = document.getElementById('rangeValue');
    if (rangeInput && rangeValue) {
        rangeInput.addEventListener('input', (e) => {
            rangeValue.textContent = e.target.value + (e.target.value == 1 ? ' day' : ' days');
        });
    }

    // Form Submission
    const agentForm = document.getElementById('agentForm');
    if (agentForm) {
        agentForm.addEventListener('submit', handleLaunch);
    }
}

async function handleLaunch(e) {
    e.preventDefault();

    const launchBtn = document.getElementById('launchBtn');
    launchBtn.disabled = true;
    launchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Initializing System...';
    launchBtn.classList.remove('bg-gradient-to-r');
    launchBtn.classList.add('bg-gray-600');

    document.getElementById('progressSection').style.display = 'block';
    document.getElementById('progressSection').scrollIntoView({ behavior: 'smooth' });

    // Reset logs
    document.getElementById('liveLogs').innerHTML = '';

    const formData = {
        city: document.getElementById('city').value,
        date: document.getElementById('date').value,
        date_range: document.getElementById('dateRange').value,
        send_pushover: document.querySelector('input[name="send_pushover"]').checked,
        send_email: document.querySelector('input[name="send_email"]').checked,
        generate_reports: document.querySelector('input[name="generate_reports"]').checked
    };

    try {
        const response = await fetch('/run-agents', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        const data = await response.json();

        startMissionControl(data.job_id);

    } catch (error) {
        console.error(error);
        logToTerminal("[CRITICAL ERROR] Uplink failed. Connection refused.", "error");
        launchBtn.disabled = false;
        launchBtn.innerHTML = 'Retry Launch';
    }
}

// --- 3. Mission Control Logic ---
function startMissionControl(jobId) {
    let logHistory = new Set();
    let currentStage = 0;

    // Enhanced Stage Logic
    const stages = [
        { id: 'stage1', active: true, label: "Acquisition" },
        { id: 'stage2', active: false, label: "Analysis" },
        { id: 'stage3', active: false, label: "Reporting" },
        { id: 'stage4', active: false, label: "Alerts" }
    ];

    // Countdown
    let timeLeft = 90;
    const timerEl = document.getElementById('countdownTimer');
    const timerInterval = setInterval(() => {
        timeLeft--;
        if (timerEl) timerEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span> T-MINUS ${timeLeft}s`;
        if (timeLeft <= 0) clearInterval(timerInterval);
    }, 1000);

    // Status Polling
    const pollInterval = setInterval(async () => {
        try {
            const res = await fetch(`/api/status/${jobId}`);
            const status = await res.json();

            // 1. Process Logs (Streaming Effect)
            if (status.logs) {
                status.logs.forEach(log => {
                    if (!logHistory.has(log)) {
                        logHistory.add(log);
                        typeLog(log); // Typewriter effect
                    }
                });
            }

            // 2. Update Stages based on log keywords (Simulated intelligence)
            if (status.logs) {
                const recentLogs = status.logs.slice(-3).join(" ").toLowerCase();
                if (recentLogs.includes("analysis") || recentLogs.includes("analyzing")) setStage(2);
                if (recentLogs.includes("report") || recentLogs.includes("pdf")) setStage(3);
                if (recentLogs.includes("alert") || recentLogs.includes("email")) setStage(4);
            }

            // 3. Completion
            if (status.status === 'complete') {
                clearInterval(pollInterval);
                clearInterval(timerInterval);
                setStage(4);
                // Fill progress line
                document.getElementById('progressLine').setAttribute('x2', '100%');

                logToTerminal("[SYSTEM] MISSION ACCOMPLISHED. REDIRECTING...", "success");
                setTimeout(() => window.location.href = `/results/${jobId}`, 2000);
            }

        } catch (e) {
            console.error(e);
        }
    }, 2000);

    // Stage Visualizer
    function setStage(stageNum) {
        if (stageNum <= currentStage) return; // Don't regress
        currentStage = stageNum;

        // Update Icons
        for (let i = 1; i <= 4; i++) {
            const el = document.getElementById(`stage${i}`);
            const iconBox = el.querySelector('.stage-icon');
            const text = el.querySelector('.stage-text');

            if (i <= stageNum) {
                iconBox.classList.remove('bg-gray-100', 'text-gray-400', 'border-white');
                iconBox.classList.add('bg-blue-600', 'text-white', 'border-blue-200', 'shadow-lg', 'scale-110');
                text.classList.remove('text-gray-400');
                text.classList.add('text-blue-600');
            }
        }

        // Update Line SVG
        const pct = (stageNum - 1) * 33;
        document.getElementById('progressLine').setAttribute('x2', `${pct}%`);
    }
}

// --- 4. Terminal Utilities ---
function typeLog(message) {
    const logsContainer = document.getElementById('liveLogs');
    const entry = document.createElement('div');
    entry.className = "font-mono text-green-400 leading-tight break-words";

    // Parse formatting (Simple regex for color coding)
    let formattedHTML = formatLogText(message);

    // Typewriter effect logic
    entry.innerHTML = `<span class="text-xs text-gray-600 mr-2">[${new Date().toLocaleTimeString()}]</span>`;
    logsContainer.appendChild(entry);

    // We append a span for the content
    const contentSpan = document.createElement('span');
    entry.appendChild(contentSpan);

    let charIndex = 0;
    // Strip HTML tags for typing, then plain inject (Simplified for perf)
    // Actually, for colored logs + typing, we usually type plain text then colorize.
    // To keep it robust, let's just fade it in instead of char-by-char to avoid HTML soup issues
    // OR: Fast type plain text.

    // Quick Fix: Just use fade-in for complex messages, char-type for simple ones?
    // Let's do a fast "scan" effect.
    contentSpan.innerHTML = formattedHTML;
    contentSpan.classList.add('animate-typing'); // CSS based typing or just fade in

    // Auto scroll
    const terminal = document.getElementById('terminalWindow');
    terminal.scrollTop = terminal.scrollHeight;
}

function formatLogText(text) {
    // Colorize keywords
    return text
        .replace(/\[INFO\]/g, '<span class="text-blue-400 font-bold">[INFO]</span>')
        .replace(/\[ERROR\]/g, '<span class="text-red-500 font-bold">[ERROR]</span>')
        .replace(/\[WARNING\]/g, '<span class="text-yellow-400 font-bold">[WARNING]</span>')
        .replace(/Agent/g, '<span class="text-purple-400">Agent</span>')
        .replace(/completed/g, '<span class="text-green-400">completed</span>');
}


function logToTerminal(msg, type = 'info') {
    const logsContainer = document.getElementById('liveLogs');
    const div = document.createElement('div');
    div.className = `font-bold ${type === 'error' ? 'text-red-500' : 'text-green-500'}`;
    div.innerText = `> ${msg}`;
    logsContainer.appendChild(div);
}

function initHoverEffects() {
    // Any remaining simple hover logic
}
