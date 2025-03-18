// Form validation and submission handling
document.addEventListener('DOMContentLoaded', function() {
    // Image preview functionality
    const imageInput = document.querySelector('input[type="file"]');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 5 * 1024 * 1024) { // 5MB limit
                    alert('File size must be less than 5MB');
                    this.value = '';
                    return;
                }
                
                if (!['image/jpeg', 'image/png'].includes(file.type)) {
                    alert('Only JPEG and PNG images are allowed');
                    this.value = '';
                    return;
                }
            }
        });
    }

    // Form submission handling
    const form = document.querySelector('#reportCaseForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = document.querySelector('#submitBtn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...';
            }
        });
    }
});

// Case management functionality
function reviewMatch(matchId) {
    if (confirm('Are you sure you want to review this match?')) {
        window.location.href = `/review_match/${matchId}`;
    }
}

// Loading state handling
function showLoading() {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(loadingOverlay);
}

function hideLoading() {
    const loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

// Error handling
function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
}
