// Utility for showing toast notifications
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed bottom-4 right-4 z-50 flex flex-col gap-2';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const bgColor = type === 'success' ? 'bg-green-500' : 'bg-red-500';
    toast.className = `${bgColor} text-white px-4 py-3 rounded shadow-lg flex items-center gap-2 fade-in`;
    toast.innerHTML = `
        <span class="text-sm font-medium">${message}</span>
        <button class="ml-auto text-white hover:text-gray-200 focus:outline-none" onclick="this.parentElement.remove()">
            &times;
        </button>
    `;

    document.getElementById('toast-container').appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Sidebar logic
document.addEventListener('DOMContentLoaded', () => {
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');

    // Create backdrop for mobile
    let backdrop = document.getElementById('sidebarBackdrop');
    if (!backdrop) {
        backdrop = document.createElement('div');
        backdrop.id = 'sidebarBackdrop';
        backdrop.className = 'fixed inset-0 bg-slate-900 bg-opacity-50 z-30 hidden transition-opacity lg:hidden';
        document.body.appendChild(backdrop);
    }

    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('-translate-x-full');
            if(window.innerWidth >= 1024) {
               mainContent.classList.toggle('lg:ml-64');
            } else {
               backdrop.classList.toggle('hidden');
            }
        });

        backdrop.addEventListener('click', () => {
            sidebar.classList.add('-translate-x-full');
            backdrop.classList.add('hidden');
        });
    }

    // Initialize user profile info if exists
    initUserProfile();
});

async function initUserProfile() {
    const userProfileName = document.getElementById('userProfileName');
    if (userProfileName) {
        try {
            const user = await fetchAPI('/auth/me');
            if (user) {
                userProfileName.textContent = user.full_name;
            }
        } catch (e) {
            console.error("Failed to load user profile");
        }
    }
    
    // Check for document expiry alerts only once per session
    if (!sessionStorage.getItem('expiryAlertShown')) {
        try {
            const data = await fetchAPI('/dashboard/alerts');
            if (data && data.alerts && data.alerts.length > 0) {
                showExpiryAlertModal(data.alerts);
            }
            sessionStorage.setItem('expiryAlertShown', 'true');
        } catch (e) {
            console.error("Failed to check alerts", e);
        }
    }
}

function showExpiryAlertModal(alerts) {
    if(document.getElementById('expiryAlertModal')) return; // Already showing
    
    const container = document.createElement('div');
    container.id = 'expiryAlertModal';
    container.className = 'fixed inset-0 z-50 overflow-y-auto';
    container.setAttribute('aria-labelledby', 'modal-title');
    container.setAttribute('role', 'dialog');
    container.setAttribute('aria-modal', 'true');
    
    let listItems = '';
    alerts.forEach(a => {
        const expiry = new Date(a.expiry_date).toLocaleDateString();
        listItems += `<li class="py-2 border-b border-red-100 last:border-0 text-sm">
            <span class="font-bold text-red-700">${a.employee_name}</span> - 
            <span class="text-slate-600">${a.document_type} (${a.title})</span> expires on 
            <span class="font-bold text-red-600">${expiry}</span>
        </li>`;
    });

    container.innerHTML = `
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div class="fixed inset-0 modal-backdrop transition-opacity bg-black bg-opacity-60" aria-hidden="true"></div>
            <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full fade-in border-t-4 border-red-500">
                <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                    <div class="sm:flex sm:items-start">
                        <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                            <i class="fas fa-exclamation-triangle text-red-600 text-xl"></i>
                        </div>
                        <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                            <h3 class="text-xl leading-6 font-bold text-gray-900" id="modal-title">Action Required: Expiring Documents</h3>
                            <div class="mt-4">
                                <p class="text-sm text-gray-600 mb-3">The following documents are expiring within 30 days:</p>
                                <ul class="bg-red-50 rounded p-3 max-h-60 overflow-y-auto">
                                    ${listItems}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                    <button type="button" onclick="document.getElementById('expiryAlertModal').remove()" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none sm:ml-3 sm:w-auto sm:text-sm">Acknowledge</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(container);
}
