/**
 * ThinkingModels Web Application JavaScript
 * 
 * Enhanced frontend functionality including:
 * - Advanced query processing with real-time updates
 * - Comprehensive model browsing and filtering
 * - WebSocket communication with fallback to REST API
 * - Result export and sharing capabilities
 * - Responsive UI with accessibility features
 * - Error handling and user feedback
 */

class ThinkingModelsApp {
    constructor() {
        this.models = [];
        this.filteredModels = [];
        this.currentPage = 1;
        this.modelsPerPage = 12;
        this.websocket = null;
        this.isProcessing = false;
        this.currentQuery = null;
        this.queryHistory = [];
        this.connectionRetries = 0;
        this.maxRetries = 5;
        this.reconnectDelay = 3000;
        
        this.init();
    }

    async init() {
        console.log('Initializing ThinkingModels App...');
        
        this.setupEventListeners();
        await this.loadSystemStatus();
        await this.loadModels();
        this.initWebSocket();
        
        console.log('App initialization complete');
    }

    setupEventListeners() {
        // Query form submission
        const queryForm = document.getElementById('query-form');
        if (queryForm) {
            queryForm.addEventListener('submit', (e) => this.handleQuerySubmit(e));
        }

        // Clear button
        const clearBtn = document.getElementById('clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearQuery());
        }

        // Example buttons
        const exampleBtns = document.querySelectorAll('.try-example-btn');
        exampleBtns.forEach(btn => {
            btn.addEventListener('click', (e) => this.tryExample(e));
        });

        // Models search and filters
        const modelsSearch = document.getElementById('models-search');
        if (modelsSearch) {
            modelsSearch.addEventListener('input', (e) => this.filterModels());
        }

        const typeFilter = document.getElementById('type-filter');
        if (typeFilter) {
            typeFilter.addEventListener('change', (e) => this.filterModels());
        }

        const fieldFilter = document.getElementById('field-filter');
        if (fieldFilter) {
            fieldFilter.addEventListener('change', (e) => this.filterModels());
        }

        // Refresh models button
        const refreshBtn = document.getElementById('refresh-models-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadModels());
        }

        // Result actions
        const copyBtn = document.getElementById('copy-result-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copyResult());
        }

        const exportBtn = document.getElementById('export-result-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportResult());
        }

        // Navigation
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-link')) {
                const href = e.target.getAttribute('href');
                if (href && href.startsWith('#')) {
                    e.preventDefault();
                    this.scrollToSection(href.substring(1));
                }
            }
        });
    }

    async loadSystemStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            this.updateStatusIndicator(status);
            this.updateSystemStatusMessage(status);
            
        } catch (error) {
            console.error('Failed to load system status:', error);
            this.updateStatusIndicator({ status: 'error', api_configured: false });
            this.updateSystemStatusMessage({ status: 'error', message: 'Failed to connect to server' });
        }
    }

    updateStatusIndicator(status) {
        const indicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        
        if (!indicator || !statusText) return;

        // Remove existing status classes
        indicator.classList.remove('status-healthy', 'status-limited', 'status-error');
        
        // Update based on status
        if (status.status === 'healthy') {
            indicator.classList.add('status-healthy');
            statusText.innerHTML = '<i class="fas fa-check-circle me-1"></i>Ready';
        } else if (status.status === 'limited') {
            indicator.classList.add('status-limited');
            statusText.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>Limited';
        } else {
            indicator.classList.add('status-error');
            statusText.innerHTML = '<i class="fas fa-times-circle me-1"></i>Error';
        }

        // Remove spinner
        const spinner = indicator.querySelector('.spinner-border');
        if (spinner) spinner.remove();
    }

    updateSystemStatusMessage(status) {
        const statusDiv = document.getElementById('system-status');
        const messageSpan = document.getElementById('status-message');
        
        if (!statusDiv || !messageSpan) return;

        // Remove existing alert classes
        statusDiv.classList.remove('alert-info', 'alert-success', 'alert-warning', 'alert-danger');

        if (status.status === 'healthy') {
            statusDiv.classList.add('alert-success');
            messageSpan.textContent = `System ready with ${status.total_models} thinking models loaded.`;
        } else if (status.status === 'limited') {
            statusDiv.classList.add('alert-warning');
            messageSpan.textContent = `${status.total_models} models loaded, but API is not configured for query processing.`;
        } else {
            statusDiv.classList.add('alert-danger');
            messageSpan.textContent = status.message || 'System error. Please check configuration.';
        }
    }

    async loadModels() {
        try {
            console.log('Loading thinking models...');
            
            const [modelsResponse, summaryResponse] = await Promise.all([
                fetch('/api/models'),
                fetch('/api/models/summary')
            ]);

            this.models = await modelsResponse.json();
            const summary = await summaryResponse.json();

            console.log(`Loaded ${this.models.length} models`);
            
            this.updateModelsSummary(summary);
            this.populateFieldFilter();
            this.filterModels(); // Initial render
            
        } catch (error) {
            console.error('Failed to load models:', error);
            this.showError('Failed to load thinking models');
        }
    }

    updateModelsSummary(summary) {
        const totalElement = document.getElementById('total-models');
        const solveElement = document.getElementById('solve-models');
        const explainElement = document.getElementById('explain-models');
        const fieldElement = document.getElementById('field-count');

        if (totalElement) totalElement.textContent = summary.total_models;
        if (solveElement) solveElement.textContent = summary.type_distribution?.solve || 0;
        if (explainElement) explainElement.textContent = summary.type_distribution?.explain || 0;
        if (fieldElement) fieldElement.textContent = summary.fields?.length || 0;
    }

    populateFieldFilter() {
        const fieldFilter = document.getElementById('field-filter');
        if (!fieldFilter) return;

        // Get unique fields
        const fields = [...new Set(this.models.map(m => m.field).filter(f => f))];
        fields.sort();

        // Clear existing options (except "All Fields")
        const firstOption = fieldFilter.firstElementChild;
        fieldFilter.innerHTML = '';
        fieldFilter.appendChild(firstOption);

        // Add field options
        fields.forEach(field => {
            const option = document.createElement('option');
            option.value = field;
            option.textContent = field.charAt(0).toUpperCase() + field.slice(1);
            fieldFilter.appendChild(option);
        });
    }

    filterModels() {
        const searchTerm = document.getElementById('models-search')?.value.toLowerCase() || '';
        const typeFilter = document.getElementById('type-filter')?.value || '';
        const fieldFilter = document.getElementById('field-filter')?.value || '';

        this.filteredModels = this.models.filter(model => {
            const matchesSearch = !searchTerm || 
                model.id.toLowerCase().includes(searchTerm) ||
                model.definition.toLowerCase().includes(searchTerm);
            
            const matchesType = !typeFilter || model.type === typeFilter;
            const matchesField = !fieldFilter || model.field === fieldFilter;

            return matchesSearch && matchesType && matchesField;
        });

        this.currentPage = 1;
        this.renderModels();
        this.renderPagination();
    }

    renderModels() {
        const modelsList = document.getElementById('models-list');
        if (!modelsList) return;

        const startIndex = (this.currentPage - 1) * this.modelsPerPage;
        const endIndex = startIndex + this.modelsPerPage;
        const pageModels = this.filteredModels.slice(startIndex, endIndex);

        if (pageModels.length === 0) {
            modelsList.innerHTML = `
                <div class="col-12 text-center py-4">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No models found</h5>
                    <p class="text-muted">Try adjusting your search criteria</p>
                </div>
            `;
            return;
        }

        modelsList.innerHTML = pageModels.map(model => `
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="model-card" data-model-id="${model.id}">
                    <div class="model-id">${model.id}</div>
                    <span class="model-type ${model.type}">${model.type}</span>
                    <div class="model-definition">
                        ${model.definition.length > 150 ? 
                            model.definition.substring(0, 150) + '...' : 
                            model.definition}
                    </div>
                    ${model.field ? `<div class="model-field">Field: ${model.field}</div>` : ''}
                </div>
            </div>
        `).join('');

        // Add click listeners to model cards
        modelsList.querySelectorAll('.model-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const modelId = e.currentTarget.getAttribute('data-model-id');
                this.showModelDetail(modelId);
            });
        });
    }

    renderPagination() {
        const pagination = document.getElementById('models-pagination');
        const paginationList = document.getElementById('pagination-list');
        
        if (!pagination || !paginationList) return;

        const totalPages = Math.ceil(this.filteredModels.length / this.modelsPerPage);

        if (totalPages <= 1) {
            pagination.style.display = 'none';
            return;
        }

        pagination.style.display = 'block';

        let paginationHTML = '';

        // Previous button
        paginationHTML += `
            <li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${this.currentPage - 1}">Previous</a>
            </li>
        `;

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= this.currentPage - 2 && i <= this.currentPage + 2)) {
                paginationHTML += `
                    <li class="page-item ${i === this.currentPage ? 'active' : ''}">
                        <a class="page-link" href="#" data-page="${i}">${i}</a>
                    </li>
                `;
            } else if (i === this.currentPage - 3 || i === this.currentPage + 3) {
                paginationHTML += `
                    <li class="page-item disabled">
                        <span class="page-link">...</span>
                    </li>
                `;
            }
        }

        // Next button
        paginationHTML += `
            <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${this.currentPage + 1}">Next</a>
            </li>
        `;

        paginationList.innerHTML = paginationHTML;

        // Add click listeners
        paginationList.querySelectorAll('a.page-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = parseInt(e.target.getAttribute('data-page'));
                if (page && page !== this.currentPage) {
                    this.currentPage = page;
                    this.renderModels();
                    this.renderPagination();
                    this.scrollToSection('models-section');
                }
            });
        });
    }

    async showModelDetail(modelId) {
        try {
            const response = await fetch(`/api/models/${modelId}`);
            const model = await response.json();

            const modal = document.getElementById('modelModal');
            const title = document.getElementById('modal-model-title');
            const content = document.getElementById('modal-model-content');

            title.textContent = model.id;
            
            content.innerHTML = `
                <div class="mb-3">
                    <span class="badge bg-${model.type === 'solve' ? 'success' : 'info'} mb-2">${model.type}</span>
                    ${model.field ? `<span class="badge bg-warning ms-2">${model.field}</span>` : ''}
                </div>
                <div class="mb-4">
                    <h6>Definition:</h6>
                    <p>${model.definition}</p>
                </div>
                ${model.examples && model.examples.length > 0 ? `
                    <div>
                        <h6>Examples:</h6>
                        <ul class="list-group list-group-flush">
                            ${model.examples.map(example => `
                                <li class="list-group-item px-0">${example}</li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
            `;

            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();

        } catch (error) {
            console.error('Failed to load model details:', error);
            this.showError('Failed to load model details');
        }
    }

    initWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                // Attempt to reconnect after 3 seconds
                setTimeout(() => this.initWebSocket(), 3000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'status':
                this.updateProcessingMessage(data.message);
                break;
            case 'result':
                this.displayResult(data);
                break;
            case 'error':
                this.hideProcessing();
                this.showError(data.error);
                break;
            case 'pong':
                // Connection health check response
                break;
        }
    }

    async handleQuerySubmit(e) {
        e.preventDefault();
        
        const queryInput = document.getElementById('query-input');
        const query = queryInput.value.trim();
        
        if (!query) {
            this.showError('Please enter a query');
            return;
        }

        if (this.isProcessing) {
            console.log('Query already in progress');
            return;
        }

        this.currentQuery = query;
        this.showProcessing();

        try {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                // Use WebSocket for real-time updates
                this.websocket.send(JSON.stringify({
                    type: 'query',
                    query: query
                }));
            } else {
                // Fall back to REST API
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ query: query })
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Query processing failed');
                }

                const result = await response.json();
                this.displayResult(result);
            }

        } catch (error) {
            console.error('Query processing error:', error);
            this.hideProcessing();
            this.showError(error.message);
        }
    }

    showProcessing() {
        this.isProcessing = true;
        
        const submitBtn = document.getElementById('submit-btn');
        const processingStatus = document.getElementById('processing-status');
        const resultsSection = document.getElementById('results-section');

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        }

        if (processingStatus) {
            processingStatus.style.display = 'block';
            processingStatus.classList.add('fade-in');
        }

        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
    }

    hideProcessing() {
        this.isProcessing = false;
        
        const submitBtn = document.getElementById('submit-btn');
        const processingStatus = document.getElementById('processing-status');

        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-rocket me-2"></i>Solve Problem';
        }

        if (processingStatus) {
            processingStatus.style.display = 'none';
        }
    }

    updateProcessingMessage(message) {
        const processingMessage = document.getElementById('processing-message');
        if (processingMessage) {
            processingMessage.textContent = message;
        }
    }

    displayResult(result) {
        this.hideProcessing();
        
        // Update result elements
        const resultQuery = document.getElementById('result-query');
        const selectedModels = document.getElementById('selected-models');
        const processingTime = document.getElementById('processing-time');
        const solutionText = document.getElementById('solution-text');
        const resultsSection = document.getElementById('results-section');

        if (resultQuery) resultQuery.textContent = result.query;
        if (processingTime) processingTime.textContent = `${result.processing_time?.toFixed(2)}s`;

        // Display selected models
        if (selectedModels) {
            selectedModels.innerHTML = result.selected_models && result.selected_models.length > 0
                ? result.selected_models.map(model => `<span class="selected-model">${model}</span>`).join('')
                : '<span class="text-muted">None selected</span>';
        }

        // Display solution with markdown rendering
        if (solutionText) {
            if (typeof marked !== 'undefined') {
                solutionText.innerHTML = marked.parse(result.solution);
            } else {
                solutionText.innerHTML = this.formatTextSolution(result.solution);
            }
        }

        // Show results section
        if (resultsSection) {
            resultsSection.style.display = 'block';
            resultsSection.classList.add('fade-in');
            
            // Scroll to results
            setTimeout(() => {
                this.scrollToSection('results-section');
            }, 100);
        }
    }

    formatTextSolution(text) {
        // Simple text formatting if markdown is not available
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^(.*)$/, '<p>$1</p>');
    }

    tryExample(e) {
        const exampleCard = e.target.closest('.example-card');
        if (exampleCard) {
            const exampleText = exampleCard.querySelector('p').textContent.replace(/"/g, '');
            const queryInput = document.getElementById('query-input');
            
            if (queryInput) {
                queryInput.value = exampleText;
                this.scrollToSection('query-section');
                queryInput.focus();
            }
        }
    }

    clearQuery() {
        const queryInput = document.getElementById('query-input');
        const resultsSection = document.getElementById('results-section');
        
        if (queryInput) {
            queryInput.value = '';
            queryInput.focus();
        }

        if (resultsSection) {
            resultsSection.style.display = 'none';
        }

        this.currentQuery = null;
    }

    async copyResult() {
        const solutionText = document.getElementById('solution-text');
        if (!solutionText) return;

        try {
            const textContent = solutionText.innerText || solutionText.textContent;
            await navigator.clipboard.writeText(textContent);
            
            // Show success feedback
            const copyBtn = document.getElementById('copy-result-btn');
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
            copyBtn.classList.add('btn-success');
            copyBtn.classList.remove('btn-light');
            
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.classList.remove('btn-success');
                copyBtn.classList.add('btn-light');
            }, 2000);

        } catch (error) {
            console.error('Failed to copy text:', error);
            this.showError('Failed to copy result');
        }
    }

    exportResult() {
        const resultQuery = document.getElementById('result-query');
        const selectedModels = document.getElementById('selected-models');
        const solutionText = document.getElementById('solution-text');
        const processingTime = document.getElementById('processing-time');

        if (!resultQuery || !solutionText) return;

        const exportData = {
            query: resultQuery.textContent,
            selected_models: Array.from(selectedModels.querySelectorAll('.selected-model')).map(el => el.textContent),
            processing_time: processingTime?.textContent,
            solution: solutionText.innerText || solutionText.textContent,
            timestamp: new Date().toISOString()
        };

        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `thinkingmodels-result-${Date.now()}.json`;
        link.click();
    }

    scrollToSection(sectionId) {
        const element = document.getElementById(sectionId);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    showError(message) {
        const modal = document.getElementById('errorModal');
        const errorMessage = document.getElementById('error-message');
        
        if (modal && errorMessage) {
            errorMessage.textContent = message;
            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();
        } else {
            alert(message); // Fallback
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.thinkingModelsApp = new ThinkingModelsApp();
});

// Handle page visibility changes to maintain WebSocket connection
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.thinkingModelsApp) {
        // Send ping to check connection health
        if (window.thinkingModelsApp.websocket?.readyState === WebSocket.OPEN) {
            window.thinkingModelsApp.websocket.send(JSON.stringify({ type: 'ping' }));
        }
    }
});
