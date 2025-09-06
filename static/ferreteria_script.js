// Ferretería El Martillo - JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Inicializar componentes
    initFlashMessages();
    initFormValidation();
    initSearchFunctionality();
    initTableSorting();
    initStockAlerts();
    initPriceCalculations();
    initTooltips();
    
    // Auto-cerrar mensajes flash después de 5 segundos
    function initFlashMessages() {
        const flashMessages = document.querySelectorAll('.flash');
        flashMessages.forEach((message, index) => {
            // Animación de entrada escalonada
            message.style.opacity = '0';
            message.style.transform = 'translateX(100%)';
            
            setTimeout(() => {
                message.style.transition = 'all 0.3s ease';
                message.style.opacity = '1';
                message.style.transform = 'translateX(0)';
            }, index * 200);
            
            // Auto-cerrar después de 6 segundos
            setTimeout(() => {
                if (message.parentNode) {
                    message.style.opacity = '0';
                    message.style.transform = 'translateX(100%)';
                    setTimeout(() => {
                        message.remove();
                    }, 300);
                }
            }, 6000 + (index * 200));
        });
    }
    
    // Validación específica para formularios de ferretería
    function initFormValidation() {
        const forms = document.querySelectorAll('.ferreteria-form');
        forms.forEach(form => {
            form.addEventListener('submit', validateFerreteriaForm);
            
            // Validación en tiempo real
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', validateField);
                input.addEventListener('input', clearFieldError);
            });
        });
    }
    
    function validateFerreteriaForm(event) {
        const form = event.target;
        let isValid = true;
        
        // Validaciones específicas de ferretería
        const nombreField = form.querySelector('[name="nombre"]');
        if (nombreField && nombreField.value.trim().length < 3) {
            showFieldError(nombreField, 'El nombre debe tener al menos 3 caracteres');
            isValid = false;
        }
        
        const cantidadField = form.querySelector('[name="cantidad"]');
        if (cantidadField && parseInt(cantidadField.value) < 0) {
            showFieldError(cantidadField, 'La cantidad no puede ser negativa');
            isValid = false;
        }
        
        const precioCompraField = form.querySelector('[name="precio_compra"]');
        const precioVentaField = form.querySelector('[name="precio_venta"]');
        
        if (precioCompraField && parseFloat(precioCompraField.value) < 0) {
            showFieldError(precioCompraField, 'El precio de compra no puede ser negativo');
            isValid = false;
        }
        
        if (precioVentaField && parseFloat(precioVentaField.value) < 0) {
            showFieldError(precioVentaField, 'El precio de venta no puede ser negativo');
            isValid = false;
        }
        
        // Validar que precio de venta > precio de compra
        if (precioCompraField && precioVentaField) {
            const compra = parseFloat(precioCompraField.value) || 0;
            const venta = parseFloat(precioVentaField.value) || 0;
            
            if (venta <= compra && compra > 0 && venta > 0) {
                showFieldError(precioVentaField, 'El precio de venta debe ser mayor al precio de compra');
                showNotification('Advertencia: El precio de venta debe ser mayor al precio de compra para obtener ganancia', 'warning');
                // No bloquear el envío, solo advertir
            }
        }
        
        // Validar código único (si se proporciona)
        const codigoField = form.querySelector('[name="codigo"]');
        if (codigoField && codigoField.value.trim()) {
            if (!/^[A-Z]{2,4}-\d{3,6}$/.test(codigoField.value.trim())) {
                showFieldError(codigoField, 'Formato sugerido: CAT-001 (2-4 letras, guión, 3-6 números)');
                // Solo advertencia, no bloquear
            }
        }
        
        if (!isValid) {
            event.preventDefault();
            showNotification('Por favor, corrija los errores en el formulario', 'error');
        }
    }
    
    function validateField(event) {
        const field = event.target;
        clearFieldError(event);
        
        if (field.hasAttribute('required') && !field.value.trim()) {
            showFieldError(field, 'Este campo es obligatorio');
            return false;
        }
        
        // Validaciones específicas por tipo
        if (field.name === 'precio_compra' || field.name === 'precio_venta') {
            const value = parseFloat(field.value);
            if (isNaN(value) || value < 0) {
                showFieldError(field, 'Ingrese un precio válido mayor o igual a 0');
                return false;
            }
        }
        
        if (field.name === 'cantidad' || field.name === 'stock_minimo') {
            const value = parseInt(field.value);
            if (isNaN(value) || value < 0) {
                showFieldError(field, 'Ingrese una cantidad válida mayor o igual a 0');
                return false;
            }
        }
        
        return true;
    }
    
    function clearFieldError(event) {
        const field = event.target;
        const errorElement = field.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
        field.classList.remove('error');
    }
    
    function showFieldError(field, message) {
        clearFieldError({ target: field });
        
        field.classList.add('error');
        
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error';
        errorElement.textContent = message;
        errorElement.style.cssText = `
            color: var(--danger-color);
            font-size: 0.8rem;
            margin-top: 0.25rem;
            display: block;
            animation: slideInDown 0.3s ease;
        `;
        
        field.parentNode.appendChild(errorElement);
    }
    
    // Funcionalidad de búsqueda mejorada
    function initSearchFunctionality() {
        const searchInput = document.querySelector('#q');
        const searchForm = document.querySelector('.search-form-advanced');
        
        if (searchInput) {
            searchInput.focus();
            
            // Búsqueda predictiva (simulada)
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                const query = this.value.trim();
                
                if (query.length >= 2) {
                    searchTimeout = setTimeout(() => {
                        // Mostrar sugerencias de códigos comunes
                        showSearchSuggestions(query);
                    }, 300);
                } else {
                    hideSearchSuggestions();
                }
            });
            
            // Limpiar búsqueda con doble clic
            searchInput.addEventListener('dblclick', function() {
                this.value = '';
                this.focus();
                hideSearchSuggestions();
            });
        }
        
        // Filtros rápidos por categoría
        const categoryFilters = document.querySelectorAll('.category-filter');
        categoryFilters.forEach(filter => {
            filter.addEventListener('click', function(e) {
                e.preventDefault();
                const category = this.textContent.trim();
                if (searchInput) {
                    searchInput.value = category;
                    const typeSelect = document.querySelector('[name="type"]');
                    if (typeSelect) {
                        typeSelect.value = 'categoria';
                    }
                    if (searchForm) {
                        searchForm.submit();
                    }
                }
            });
        });
    }
    
    function showSearchSuggestions(query) {
        // Códigos comunes de ferretería
        const commonCodes = [
            'HER-', 'ELE-', 'PLO-', 'PIN-', 'CON-', 'FER-', 'SEG-', 'JAR-'
        ];
        
        const suggestions = commonCodes.filter(code => 
            code.toLowerCase().includes(query.toLowerCase())
        );
        
        if (suggestions.length > 0) {
            // Crear o actualizar panel de sugerencias
            let suggestionsPanel = document.querySelector('.search-suggestions');
            if (!suggestionsPanel) {
                suggestionsPanel = document.createElement('div');
                suggestionsPanel.className = 'search-suggestions';
                suggestionsPanel.style.cssText = `
                    position: absolute;
                    top: 100%;
                    left: 0;
                    right: 0;
                    background: white;
                    border: 1px solid var(--border-color);
                    border-radius: var(--border-radius);
                    box-shadow: var(--shadow);
                    z-index: 1000;
                    max-height: 200px;
                    overflow-y: auto;
                `;
                
                const searchContainer = document.querySelector('.search-input-group');
                if (searchContainer) {
                    searchContainer.style.position = 'relative';
                    searchContainer.appendChild(suggestionsPanel);
                }
            }
            
            suggestionsPanel.innerHTML = suggestions.map(code => `
                <div class="suggestion-item" style="padding: 0.5rem; cursor: pointer; border-bottom: 1px solid #eee;">
                    <i class="fas fa-search"></i> Buscar productos con código ${code}...
                </div>
            `).join('');
            
            // Agregar click handlers
            suggestionsPanel.querySelectorAll('.suggestion-item').forEach((item, index) => {
                item.addEventListener('click', function() {
                    const searchInput = document.querySelector('#q');
                    if (searchInput) {
                        searchInput.value = suggestions[index];
                        hideSearchSuggestions();
                    }
                });
                
                item.addEventListener('mouseenter', function() {
                    this.style.backgroundColor = '#f8f9fa';
                });
                
                item.addEventListener('mouseleave', function() {
                    this.style.backgroundColor = 'white';
                });
            });
        }
    }
    
    function hideSearchSuggestions() {
        const suggestionsPanel = document.querySelector('.search-suggestions');
        if (suggestionsPanel) {
            suggestionsPanel.remove();
        }
    }
    
    // Ordenamiento avanzado de tablas
    function initTableSorting() {
        const tables = document.querySelectorAll('.products-table');
        tables.forEach(table => {
            const headers = table.querySelectorAll('th');
            headers.forEach((header, index) => {
                if (header.textContent.trim() && !header.classList.contains('no-sort')) {
                    header.style.cursor = 'pointer';
                    header.style.userSelect = 'none';
                    header.addEventListener('click', () => sortTable(table, index));
                    
                    // Icono de ordenamiento
                    const sortIcon = document.createElement('i');
                    sortIcon.className = 'fas fa-sort sort-icon';
                    sortIcon.style.cssText = 'margin-left: 0.5rem; opacity: 0.5; transition: all 0.3s;';
                    header.appendChild(sortIcon);
                }
            });
        });
    }
    
    function sortTable(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const header = table.querySelectorAll('th')[columnIndex];
        const sortIcon = header.querySelector('.sort-icon');
        
        // Determinar dirección
        const isAscending = !header.classList.contains('sorted-asc');
        
        // Limpiar estados previos
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sorted-asc', 'sorted-desc');
            const icon = th.querySelector('.sort-icon');
            if (icon) {
                icon.className = 'fas fa-sort sort-icon';
                icon.style.opacity = '0.5';
            }
        });
        
        // Ordenar
        rows.sort((a, b) => {
            const aValue = getCellValue(a, columnIndex);
            const bValue = getCellValue(b, columnIndex);
            
            // Ordenamiento inteligente
            if (!isNaN(aValue) && !isNaN(bValue)) {
                return isAscending ? aValue - bValue : bValue - aValue;
            }
            
            // Ordenamiento de códigos (alfanumérico)
            if (isProductCode(aValue) && isProductCode(bValue)) {
                return isAscending ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
            }
            
            // Ordenamiento alfabético normal
            return isAscending 
                ? aValue.localeCompare(bValue, 'es', { sensitivity: 'base' })
                : bValue.localeCompare(aValue, 'es', { sensitivity: 'base' });
        });
        
        // Aplicar ordenamiento con animación
        rows.forEach((row, index) => {
            setTimeout(() => {
                tbody.appendChild(row);
            }, index * 20);
        });
        
        // Actualizar UI
        header.classList.add(isAscending ? 'sorted-asc' : 'sorted-desc');
        sortIcon.className = `fas fa-sort-${isAscending ? 'up' : 'down'} sort-icon`;
        sortIcon.style.opacity = '1';
        sortIcon.style.color = 'var(--primary-color)';
    }
    
    function getCellValue(row, columnIndex) {
        const cell = row.cells[columnIndex];
        if (!cell) return '';
        
        const text = cell.textContent.trim();
        
        // Extraer números (precios, cantidades)
        const numberMatch = text.match(/[\d,]+\.?\d*/);
        if (numberMatch && text.includes('$')) {
            return parseFloat(numberMatch[0].replace(/,/g, ''));
        }
        
        if (numberMatch && /^\d+$/.test(text)) {
            return parseInt(text);
        }
        
        return text.toLowerCase();
    }
    
    function isProductCode(value) {
        return /^[A-Z]{2,4}-\d{3,6}$/.test(value);
    }
    
    // Alertas de stock bajo
    function initStockAlerts() {
        // Verificar stock bajo en la página actual
        const stockElements = document.querySelectorAll('.stock-badge, .current-stock');
        let lowStockCount = 0;
        
        stockElements.forEach(element => {
            const stockValue = parseInt(element.textContent);
            if (!isNaN(stockValue) && stockValue <= 5) {
                lowStockCount++;
                element.classList.add('critical-stock');
                
                // Efecto de parpadeo para stock crítico (0-2 unidades)
                if (stockValue <= 2) {
                    element.style.animation = 'blink 1.5s infinite';
                }
            }
        });
        
        // Mostrar notificación global si hay stock bajo
        if (lowStockCount > 0 && window.location.pathname === '/') {
            setTimeout(() => {
                showNotification(`¡Atención! Hay ${lowStockCount} producto${lowStockCount > 1 ? 's' : ''} con stock bajo`, 'warning', 8000);
            }, 2000);
        }
    }
    
    // Cálculos automáticos de precios y márgenes
    function initPriceCalculations() {
        const precioCompraInput = document.querySelector('#precio_compra');
        const precioVentaInput = document.querySelector('#precio_venta');
        const cantidadInput = document.querySelector('#cantidad');
        
        if (precioCompraInput && precioVentaInput) {
            [precioCompraInput, precioVentaInput, cantidadInput].forEach(input => {
                if (input) {
                    input.addEventListener('input', updatePriceCalculations);
                    input.addEventListener('blur', updatePriceCalculations);
                }
            });
            
            // Cálculo inicial
            updatePriceCalculations();
        }
    }
    
    function updatePriceCalculations() {
        const precioCompra = parseFloat(document.querySelector('#precio_compra')?.value) || 0;
        const precioVenta = parseFloat(document.querySelector('#precio_venta')?.value) || 0;
        const cantidad = parseFloat(document.querySelector('#cantidad')?.value) || 0;
        
        const margen = precioCompra > 0 ? ((precioVenta - precioCompra) / precioCompra * 100) : 0;
        const gananciaPorUnidad = precioVenta - precioCompra;
        const valorTotalStock = cantidad * precioVenta;
        const gananciaPotencialTotal = cantidad * gananciaPorUnidad;
        
        // Actualizar elementos en pantalla
        updateElement('profit-margin', `${margen.toFixed(1)}%`, getMarginColor(margen));
        updateElement('profit-per-unit', formatCurrency(gananciaPorUnidad));
        updateElement('total-stock-value', formatCurrency(valorTotalStock));
        updateElement('total-potential-profit', formatCurrency(gananciaPotencialTotal));
        
        // Sugerencias automáticas de precios
        showPricingSuggestions(precioCompra, precioVenta, margen);
    }
    
    function updateElement(id, value, color = null) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
            if (color) {
                element.style.color = color;
            }
        }
    }
    
    function getMarginColor(margin) {
        if (margin < 15) return 'var(--danger-color)';
        if (margin < 30) return 'var(--warning-color)';
        return 'var(--success-color)';
    }
    
    function showPricingSuggestions(compra, venta, margen) {
        const suggestionsContainer = document.querySelector('.pricing-suggestions');
        
        if (compra > 0) {
            let suggestion = '';
            
            if (margen < 15) {
                const sugeridoVenta = compra * 1.25; // 25% margen mínimo
                suggestion = `💡 Sugerencia: Precio mínimo recomendado $${sugeridoVenta.toFixed(2)} (25% margen)`;
            } else if (margen > 60) {
                suggestion = `⚠️ Margen muy alto: Considere ser más competitivo`;
            } else if (margen >= 25 && margen <= 40) {
                suggestion = `✅ Margen saludable para ferretería`;
            }
            
            if (suggestion && suggestionsContainer) {
                suggestionsContainer.innerHTML = `<small class="pricing-tip">${suggestion}</small>`;
            }
        }
    }
    
    // Tooltips mejorados
    function initTooltips() {
        const tooltipElements = document.querySelectorAll('[title], [data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', showTooltip);
            element.addEventListener('mouseleave', hideTooltip);
        });
    }
    
    function showTooltip(event) {
        const element = event.target;
        const title = element.getAttribute('title') || element.getAttribute('data-tooltip');
        
        if (!title) return;
        
        const tooltip = document.createElement('div');
        tooltip.className = 'ferreteria-tooltip';
        tooltip.textContent = title;
        tooltip.style.cssText = `
            position: absolute;
            background: var(--dark-color);
            color: white;
            padding: 0.5rem 0.75rem;
            border-radius: var(--border-radius);
            font-size: 0.8rem;
            z-index: 1000;
            pointer-events: none;
            white-space: nowrap;
            opacity: 0;
            transition: opacity 0.3s;
            box-shadow: var(--shadow);
        `;
        
        document.body.appendChild(tooltip);
        
        // Posicionar
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
        
        // Mostrar
        setTimeout(() => tooltip.style.opacity = '1', 100);
        
        // Guardar referencia
        element._ferreteriaTooltip = tooltip;
        
        // Limpiar title original
        if (element.getAttribute('title')) {
            element.setAttribute('data-original-title', title);
            element.removeAttribute('title');
        }
    }
    
    function hideTooltip(event) {
        const element = event.target;
        if (element._ferreteriaTooltip) {
            element._ferreteriaTooltip.remove();
            element._ferreteriaTooltip = null;
        }
        
        // Restaurar title
        const originalTitle = element.getAttribute('data-original-title');
        if (originalTitle) {
            element.setAttribute('title', originalTitle);
            element.removeAttribute('data-original-title');
        }
    }
});

// Funciones globales
function deleteProduct(productId, productName) {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.style.display = 'block';
        
        // Animación de entrada
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.transform = 'scale(0.7)';
            modalContent.style.opacity = '0';
            setTimeout(() => {
                modalContent.style.transition = 'all 0.3s ease';
                modalContent.style.transform = 'scale(1)';
                modalContent.style.opacity = '1';
            }, 10);
        }
        
        // Enfocar botón de cancelar
        setTimeout(() => {
            const cancelButton = modal.querySelector('.btn-secondary');
            if (cancelButton) {
                cancelButton.focus();
            }
        }, 300);
    }
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.transform = 'scale(0.7)';
            modalContent.style.opacity = '0';
            setTimeout(() => {
                modal.style.display = 'none';
                modalContent.style.transform = 'scale(1)';
                modalContent.style.opacity = '1';
            }, 300);
        } else {
            modal.style.display = 'none';
        }
    }
}

// Cerrar modales con Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeDeleteModal();
        hideSearchSuggestions();
    }
});

// Cerrar modales clickeando fuera
window.addEventListener('click', function(event) {
    const modal = document.getElementById('deleteModal');
    if (event.target === modal) {
        closeDeleteModal();
    }
    
    // Cerrar sugerencias de búsqueda
    if (!event.target.closest('.search-input-group')) {
        hideSearchSuggestions();
    }
});

// Sistema de notificaciones mejorado
function showNotification(message, type = 'info', duration = 4000) {
    const notification = document.createElement('div');
    notification.className = `ferreteria-notification notification-${type}`;
    
    const iconClass = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle', 
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    }[type] || 'fa-info-circle';
    
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${iconClass}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Estilos
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-lg);
        z-index: 1001;
        min-width: 350px;
        max-width: 500px;
        animation: slideInRight 0.4s ease-out;
        border-left: 4px solid var(--${type === 'error' ? 'danger' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'info'}-color);
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remover
    if (duration > 0) {
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.4s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 400);
        }, duration);
    }
    
    // Sonido de notificación (opcional)
    playNotificationSound(type);
}

function playNotificationSound(type) {
    // Solo reproducir en navegadores que lo soporten
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Frecuencias según tipo de notificación
        const frequencies = {
            'success': 800,
            'error': 300,
            'warning': 600,
            'info': 500
        };
        
        oscillator.frequency.setValueAtTime(frequencies[type] || 500, audioContext.currentTime);
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
    } catch (e) {
        // Ignorar errores de audio
    }
}

// Funciones utilitarias
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function hideSearchSuggestions() {
    const suggestionsPanel = document.querySelector('.search-suggestions');
    if (suggestionsPanel) {
        suggestionsPanel.remove();
    }
}

// Función para exportar inventario
function exportInventory(format = 'csv') {
    const table = document.querySelector('.products-table');
    if (!table) {
        showNotification('No hay tabla para exportar', 'error');
        return;
    }
    
    const rows = Array.from(table.querySelectorAll('tr'));
    
    if (format === 'csv') {
        const csv = rows.map(row => {
            const cells = Array.from(row.querySelectorAll('th, td'));
            return cells.map(cell => {
                const text = cell.textContent.trim().replace(/"/g, '""');
                return `"${text}"`;
            }).join(',');
        }).join('\n');
        
        downloadFile(csv, 'inventario-ferreteria.csv', 'text/csv');
    }
    
    showNotification('Inventario exportado exitosamente', 'success');
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Función para imprimir
function printInventory() {
    const printContent = document.querySelector('.table-container');
    if (!printContent) {
        showNotification('No hay contenido para imprimir', 'error');
        return;
    }
    
    const printWindow = window.open('', '', 'width=800,height=600');
    printWindow.document.write(`
        <html>
        <head>
            <title>Inventario - Ferretería El Martillo</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #d35400; color: white; }
                .header { text-align: center; margin-bottom: 20px; }
                .header h1 { color: #d35400; }
                .footer { margin-top: 20px; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔨 Ferretería El Martillo</h1>
                <p>Inventario Completo - ${new Date().toLocaleDateString('es-MX')}</p>
            </div>
            ${printContent.