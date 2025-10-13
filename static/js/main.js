document.addEventListener('DOMContentLoaded', () => {

    const loginForm = document.querySelector('form');
    if (loginForm && window.location.pathname === '/login') {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json' 
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    window.location.href = '/dashboard';
                } else {
                    const result = await response.json();
                    alert('Error: ' + result.msg);
                }
            } catch (error) {
                console.error('Fetch error:', error);
                alert('An error occurred. Please try again.');
            }
        });
    }

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                const response = await fetch('/logout', {
                    method: 'POST',
                    credentials: 'include'
                });
                if (response.ok) {
                    window.location.href = '/'; 
                } else {
                    const result = await response.json();
                    alert('Logout failed: ' + result.msg);
                }
            } catch (error) {
                console.error('Logout error:', error);
            }
        });
    }

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

const buyButtons = document.querySelectorAll('.btn-buy');

const csrfToken = getCookie('csrf_access_token');

if (!csrfToken) {
    console.error("CSRF token cookie 'csrf_access_token' not found.");
}

buyButtons.forEach(button => {
    button.addEventListener('click', async (e) => {
        const aiId = e.target.getAttribute('data-ai-id');
        
        if (!csrfToken) {
            alert('Security error: CSRF token missing. Please log in again.');
            return;
        }

        try {
            const response = await fetch(`/buy_ai/${aiId}`, {
                method: 'POST',
                credentials: 'include', 
                headers: {
                    'X-CSRF-TOKEN': csrfToken 
                }
            });

            if (response.status === 401) {
                alert('You must be logged in to buy an AI.');
                window.location.href = "/login";
                return;
            }
            
            const result = await response.json();
            
            if (result.success) {
                alert(`Success: ${result.message}`);
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error('Fetch error:', error);
            alert('An error occurred. Please try again.');
        }
    });
});

    const dashButtons = document.querySelectorAll('.dash-btn');
    const contentPanels = document.querySelectorAll('.content-panel');

    dashButtons.forEach(button => {
        button.addEventListener('click', () => {
            dashButtons.forEach(btn => btn.classList.remove('active'));
            contentPanels.forEach(panel => panel.classList.remove('active'));
            button.classList.add('active');
            const targetId = button.id.replace('-btn', '-content');
            document.getElementById(targetId).classList.add('active');
        });
    });

    const detailsModal = document.getElementById('details-modal');
    const closeBtn = document.querySelector('.close-btn');
    const modalBody = document.querySelector('.modal-body');

    document.querySelectorAll('.btn-details').forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const card = e.target.closest('.ai-card');
            const aiName = card.querySelector('h3').textContent;
            const aiDescription = card.querySelector('p').textContent;

            const fullDescription = "This is a comprehensive description of the AI. It outlines the technology behind it, its primary use cases, and how it can significantly enhance your workflow. The more detail you provide here, the more informative the popup becomes for your users."

            modalBody.innerHTML = `
                <div class="modal-header">
                    <h3>${aiName}</h3>
                </div>
                <div class="modal-content-details">
                    <p>${aiDescription}</p>
                    <p>${fullDescription}</p>
                </div>
            `;
            detailsModal.style.display = 'block';
        });
    });

    closeBtn.addEventListener('click', () => {
        detailsModal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === detailsModal) {
            detailsModal.style.display = 'none';
        }
    });
});
