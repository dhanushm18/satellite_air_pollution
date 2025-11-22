// Enhanced JavaScript for Agentic Air Quality Monitor

// Set today's date as default
document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }

    // Update range value display
    const rangeInput = document.getElementById('dateRange');
    const rangeValue = document.getElementById('rangeValue');

    if (rangeInput && rangeValue) {
        rangeInput.addEventListener('input', (e) => {
            const days = e.target.value;
            rangeValue.textContent = days == 1 ? '1 day' : `${days} days`;
        });
    }

    // Add hover effects to agent cards
    const agentCards = document.querySelectorAll('.agent-card');
    agentCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-10px) scale(1.02)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });
});

// Handle form submission
const agentForm = document.getElementById('agentForm');
if (agentForm) {
    agentForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Get form data
        const formData = {
            city: document.getElementById('city').value,
            date: document.getElementById('date').value,
            date_range: document.getElementById('dateRange').value,
            send_pushover: document.querySelector('input[name="send_pushover"]').checked,
            send_email: document.querySelector('input[name="send_email"]').checked,
            generate_reports: document.querySelector('input[name="generate_reports"]').checked
        };

        // Disable button
        const launchBtn = document.getElementById('launchBtn');
        launchBtn.disabled = true;
        launchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Launching...';

        // Show progress section
        const progressSection = document.getElementById('progressSection');
        progressSection.style.display = 'block';
        progressSection.scrollIntoView({ behavior: 'smooth' });

        try {
            // Start agents
            const response = await fetch('/run-agents', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            const jobId = data.job_id;

            // Poll for status
            pollStatus(jobId);

        } catch (error) {
            console.error('Error:', error);
            showError('Failed to start agents. Please try again.');
            launchBtn.disabled = false;
            launchBtn.innerHTML = '<i class="fas fa-rocket"></i> Launch Agents';
        }
    });
}

// Poll job status with stage animations
function pollStatus(jobId) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    let progress = 0;
    let currentStage = 0;

    const stages = [
        { id: 'stage1', text: '<i class="fas fa-satellite fa-spin"></i> Fetching satellite data...', progress: 25 },
        { id: 'stage2', text: '<i class="fas fa-microscope fa-spin"></i> Analyzing air quality...', progress: 50 },
        { id: 'stage3', text: '<i class="fas fa-file-pdf fa-spin"></i> Generating reports...', progress: 75 },
        { id: 'stage4', text: '<i class="fas fa-bell fa-spin"></i> Sending notifications...', progress: 90 }
    ];

    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/api/status/${jobId}`);
            const status = await response.json();

            // Update stage
            if (currentStage < stages.length) {
                const stage = stages[currentStage];
                document.getElementById(stage.id).classList.add('active');
                progressText.innerHTML = stage.text;
                progress = stage.progress;
                progressFill.style.width = `${progress}%`;
                currentStage++;
            }

            // Update progress text if available
            if (status.progress) {
                progressText.innerHTML = `<i class="fas fa-cog fa-spin"></i> ${status.progress}`;
            }

            // Check if complete
            if (status.status === 'complete') {
                clearInterval(interval);

                // Complete all stages
                stages.forEach(stage => {
                    document.getElementById(stage.id).classList.add('active');
                });

                progressFill.style.width = '100%';
                progressText.innerHTML = '<i class="fas fa-check-circle"></i> ✅ Complete! Redirecting...';

                // Add success animation
                progressFill.style.boxShadow = '0 0 30px rgba(16, 185, 129, 0.8)';

                setTimeout(() => {
                    window.location.href = `/results/${jobId}`;
                }, 1500);
            } else if (status.status === 'error') {
                clearInterval(interval);
                progressFill.style.width = '100%';
                progressFill.style.background = 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)';
                progressText.innerHTML = `<i class="fas fa-exclamation-circle"></i> ❌ Error: ${status.error || 'Unknown error'}`;

                const launchBtn = document.getElementById('launchBtn');
                launchBtn.disabled = false;
                launchBtn.innerHTML = '<i class="fas fa-rocket"></i> Launch Agents';
            }

        } catch (error) {
            console.error('Status check error:', error);
        }
    }, 3000); // Poll every 3 seconds
}

// Show error message
function showError(message) {
    const progressText = document.getElementById('progressText');
    if (progressText) {
        progressText.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        progressText.style.color = '#ef4444';
    } else {
        alert(message);
    }
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// Add parallax effect to particles
window.addEventListener('scroll', () => {
    const particles = document.querySelectorAll('.particle');
    const scrolled = window.pageYOffset;

    particles.forEach((particle, index) => {
        const speed = (index + 1) * 0.1;
        particle.style.transform = `translateY(${scrolled * speed}px)`;
    });
});
