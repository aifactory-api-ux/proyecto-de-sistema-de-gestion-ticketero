/**
 * Ticket System Frontend - Vanilla JS Implementation
 * Handles ticket creation, status consultation, and operator panel
 */

// API Configuration
const API_BASE_URL = window.API_BASE_URL || 'http://localhost:8001';

// State Management
const state = {
    tickets: [],
    currentTicket: null,
    loading: false,
    error: null
};

// ==================== API FUNCTIONS ====================

/**
 * Create a new ticket
 * @param {Object} ticketData - { user_name: string, telegram_id?: number }
 * @returns {Promise<Object>} Created ticket object
 */
async function createTicket(ticketData) {
    const response = await fetch(`${API_BASE_URL}/api/tickets`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(ticketData)
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Error ${response.status}: No se pudo crear el turno`);
    }

    return await response.json();
}

/**
 * Get all tickets
 * @returns {Promise<Array>} Array of ticket objects
 */
async function getAllTickets() {
    const response = await fetch(`${API_BASE_URL}/api/tickets`);

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Error ${response.status}: No se pudieron obtener los tickets`);
    }

    return await response.json();
}

/**
 * Get ticket status by ID
 * @param {number} ticketId - Ticket ID
 * @returns {Promise<Object>} Status response object
 */
async function getTicketStatus(ticketId) {
    const response = await fetch(`${API_BASE_URL}/api/tickets/${ticketId}/status`);

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Error ${response.status}: Ticket no encontrado`);
    }

    return await response.json();
}

/**
 * Update ticket status
 * @param {number} ticketId - Ticket ID
 * @param {string} status - New status ('attended', 'completed', 'waiting')
 * @returns {Promise<Object>} Updated ticket object
 */
async function updateTicketStatus(ticketId, status) {
    const response = await fetch(`${API_BASE_URL}/api/tickets/${ticketId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status })
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Error ${response.status}: No se pudo actualizar el ticket`);
    }

    return await response.json();
}

// ==================== UI COMPONENTS ====================

// ErrorAlert Component
function showError(message) {
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorAlert.classList.remove('d-none');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        errorAlert.classList.add('d-none');
    }, 5000);
}

function hideError() {
    const errorAlert = document.getElementById('errorAlert');
    errorAlert.classList.add('d-none');
}

// TicketForm Component
function initTicketForm() {
    const form = document.getElementById('ticketForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError();

        const userName = document.getElementById('userName').value.trim();
        const telegramIdInput = document.getElementById('telegramId').value.trim();
        const telegramId = telegramIdInput ? parseInt(telegramIdInput) : null;
        const submitBtn = document.getElementById('submitBtn');

        if (!userName) {
            showError('Por favor ingrese su nombre');
            return;
        }

        // Disable button during request
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creando...';

        try {
            const ticket = await createTicket({ user_name: userName, telegram_id: telegramId });
            
            // Show result
            document.getElementById('resultTicketNumber').textContent = `#${ticket.number}`;
            document.getElementById('resultPosition').textContent = await getPositionText(ticket.id);
            document.getElementById('resultTicketId').value = ticket.id;
            document.getElementById('ticketResult').classList.remove('d-none');
            
            // Reset form but keep result visible
            form.reset();
            
            // Refresh operator panel if visible
            loadTickets();
        } catch (error) {
            showError(error.message);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-ticket-detailed"></i> Obtener Turno';
        }
    });
}

// TicketStatus Component
function initTicketStatus() {
    const form = document.getElementById('statusForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError();

        const ticketId = parseInt(document.getElementById('ticketIdSearch').value);

        if (!ticketId || ticketId <= 0) {
            showError('Por favor ingrese un número de ticket válido');
            return;
        }

        await consultarTicket(ticketId);
    });
}

/**
 * Consultar estado de un ticket
 * @param {number} ticketId - ID del ticket a consultar
 */
async function consultarTicket(ticketId) {
    try {
        const statusData = await getTicketStatus(ticketId);
        
        document.getElementById('statusTicketNumber').textContent = `#${statusData.number}`;
        document.getElementById('statusPosition').textContent = statusData.position;
        
        const statusBadge = document.getElementById('statusBadge');
        statusBadge.textContent = getStatusText(statusData.status);
        statusBadge.className = `status-badge ${getStatusClass(statusData.status)}`;
        
        document.getElementById('statusResult').classList.remove('d-none');
        
        // Switch to consult tab
        const consultTab = document.getElementById('consultar-tab');
        const consultPane = document.getElementById('consultar');
        const bootstrapTab = new bootstrap.Tab(consultTab);
        bootstrapTab.show();
    } catch (error) {
        showError(error.message);
        document.getElementById('statusResult').classList.add('d-none');
    }
}

// TicketList Component
function initTicketList() {
    loadTickets();
}

/**
 * Load and display all tickets in operator panel
 */
async function loadTickets() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const ticketList = document.getElementById('ticketList');
    const emptyQueue = document.getElementById('emptyQueue');
    const queueCount = document.getElementById('queueCount');
    const statWaiting = document.getElementById('statWaiting');
    const statAttended = document.getElementById('statAttended');

    loadingIndicator.classList.remove('d-none');
    ticketList.innerHTML = '';

    try {
        const tickets = await getAllTickets();
        state.tickets = tickets;

        // Filter waiting tickets
        const waitingTickets = tickets.filter(t => t.status === 'waiting');
        const attendedTickets = tickets.filter(t => t.status === 'attended');

        // Update stats
        queueCount.textContent = `${waitingTickets.length} en espera`;
        statWaiting.textContent = waitingTickets.length;
        statAttended.textContent = attendedTickets.length;

        if (tickets.length === 0) {
            emptyQueue.classList.remove('d-none');
            return;
        }

        emptyQueue.classList.add('d-none');

        // Sort tickets: waiting first, then by number
        const sortedTickets = [...tickets].sort((a, b) => {
            const statusOrder = { waiting: 0, attended: 1, completed: 2 };
            if (statusOrder[a.status] !== statusOrder[b.status]) {
                return statusOrder[a.status] - statusOrder[b.status];
            }
            return a.number - b.number;
        });

        // Render each ticket
        sortedTickets.forEach(ticket => {
            const ticketElement = createTicketCard(ticket, waitingTickets);
            ticketList.appendChild(ticketElement);
        });

    } catch (error) {
        showError(error.message);
    } finally {
        loadingIndicator.classList.add('d-none');
    }
}

/**
 * Create ticket card element
 * @param {Object} ticket - Ticket object
 * @param {Array} waitingTickets - Array of waiting tickets for position calculation
 * @returns {HTMLElement} Ticket card element
 */
function createTicketCard(ticket, waitingTickets) {
    const card = document.createElement('div');
    card.className = 'card mb-2';
    card.innerHTML = `
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h5 class="mb-0">#${ticket.number}</h5>
                    <small class="text-muted">${ticket.user_name}</small>
                    ${ticket.telegram_id ? `<br><small class="text-muted"><i class="bi bi-telegram"></i> ${ticket.telegram_id}</small>` : ''}
                </div>
                <div class="text-end">
                    <span class="status-badge ${getStatusClass(ticket.status)}">${getStatusText(ticket.status)}</span>
                    ${ticket.status === 'waiting' ? `<br><small class="text-muted">Posición: ${getPosition(waitingTickets, ticket.id)}</small>` : ''}
                </div>
            </div>
            ${ticket.status === 'waiting' ? `
                <div class="mt-2">
                    <button class="btn btn-sm btn-outline-success" onclick="updateTicketStatusAction(${ticket.id}, 'attended')">
                        <i class="bi bi-check2"></i> Atender
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="updateTicketStatusAction(${ticket.id}, 'completed')">
                        <i class="bi bi-x-lg"></i> Completar
                    </button>
                </div>
            ` : ''}
            ${ticket.status === 'attended' ? `
                <div class="mt-2">
                    <button class="btn btn-sm btn-outline-primary" onclick="updateTicketStatusAction(${ticket.id}, 'completed')">
                        <i class="bi bi-check-all"></i> Finalizar
                    </button>
                    <button class="btn btn-sm btn-outline-warning" onclick="updateTicketStatusAction(${ticket.id}, 'waiting')">
                        <i class="bi bi-arrow-counterclockwise"></i> Regresar a cola
                    </button>
                </div>
            ` : ''}
        </div>
    `;
    return card;
}

/**
 * Get position in queue
 * @param {Array} waitingTickets - Array of waiting tickets
 * @param {number} ticketId - Ticket ID to find
 * @returns {number} Position (1-based)
 */
function getPosition(waitingTickets, ticketId) {
    const sorted = [...waitingTickets].sort((a, b) => a.number - b.number);
    const index = sorted.findIndex(t => t.id === ticketId);
    return index + 1;
}

/**
 * Get position as text (async for future API enhancement)
 * @param {number} ticketId - Ticket ID
 * @returns {Promise<string>} Position text
 */
async function getPositionText(ticketId) {
    try {
        const status = await getTicketStatus(ticketId);
        return `${status.position} en cola`;
    } catch {
        return 'Consultando...';
    }
}

// ==================== OPERATOR ACTIONS ====================

/**
 * Attend next ticket in queue
 */
async function attNextTicket() {
    hideError();
    const attNextBtn = document.getElementById('attNextBtn');
    attNextBtn.disabled = true;
    attNextBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Buscando...';

    try {
        const tickets = await getAllTickets();
        const waitingTickets = tickets.filter(t => t.status === 'waiting');
        
        if (waitingTickets.length === 0) {
            showError('No hay tickets en espera');
            return;
        }

        // Get lowest number ticket
        const nextTicket = waitingTickets.sort((a, b) => a.number - b.number)[0];
        
        await updateTicketStatus(nextTicket.id, 'attended');
        await loadTickets();
        
        // Show success message
        const operatorPanel = document.getElementById('operador');
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show';
        alertDiv.innerHTML = `
            <strong><i class="bi bi-check-circle"></i> Turno #${nextTicket.number} llamado</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        operatorPanel.insertBefore(alertDiv, operatorPanel.firstChild);
        setTimeout(() => alertDiv.remove(), 3000);

    } catch (error) {
        showError(error.message);
    } finally {
        attNextBtn.disabled = false;
        attNextBtn.innerHTML = '<i class="bi bi-check2-circle"></i> Atender Siguiente';
    }
}

/**
 * Update ticket status from operator panel
 * @param {number} ticketId - Ticket ID
 * @param {string} status - New status
 */
async function updateTicketStatusAction(ticketId, status) {
    hideError();

    try {
        await updateTicketStatus(ticketId, status);
        await loadTickets();
    } catch (error) {
        showError(error.message);
    }
}

// ==================== HELPERS ====================

/**
 * Get CSS class for status badge
 * @param {string} status - Ticket status
 * @returns {string} CSS class name
 */
function getStatusClass(status) {
    const classes = {
        waiting: 'status-waiting',
        attended: 'status-attended',
        completed: 'status-completed'
    };
    return classes[status] || 'status-waiting';
}

/**
 * Get display text for status
 * @param {string} status - Ticket status
 * @returns {string} Display text
 */
function getStatusText(status) {
    const texts = {
        waiting: 'En espera',
        attended: 'En atención',
        completed: 'Completado'
    };
    return texts[status] || status;
}

// ==================== INITIALIZATION ====================

/**
 * Initialize application
 */
document.addEventListener('DOMContentLoaded', () => {
    initTicketForm();
    initTicketStatus();
    initTicketList();
    
    // Auto-refresh ticket list every 30 seconds when on operator tab
    setInterval(() => {
        const operatorTab = document.getElementById('operador');
        if (operatorTab.classList.contains('active') || 
            document.querySelector('#operador-tab').classList.contains('active')) {
            loadTickets();
        }
    }, 30000);
    
    // Handle tab changes
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', (event) => {
            if (event.target.id === 'operador-tab') {
                loadTickets();
            }
        });
    });
});
