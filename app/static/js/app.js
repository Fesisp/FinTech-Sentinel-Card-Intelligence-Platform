// FinTech Sentinel Terminal Interactivity & API Integration

document.addEventListener('DOMContentLoaded', () => {
    const cardInput = document.getElementById('card-number-input');
    
    // Auto-format card number into 4-digit blocks & detect brand live
    cardInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        
        // Live Brand Heuristic Preview
        const badge = document.getElementById('live-brand-badge');
        if (value.startsWith('4')) badge.textContent = 'VISA';
        else if (value.startsWith('51') || value.startsWith('55') || value.startsWith('22')) badge.textContent = 'MASTERCARD';
        else if (value.startsWith('34') || value.startsWith('37')) badge.textContent = 'AMEX';
        else if (value.startsWith('6362') || value.startsWith('6363') || value.startsWith('4011')) badge.textContent = 'ELO';
        else if (value.length > 0) badge.textContent = 'CARD';
        else badge.textContent = 'DETECTING';

        // Auto format 4-4-4-4
        if (value.length > 19) value = value.substring(0, 19);
        const formatted = value.match(/.{1,4}/g)?.join(' ') || value;
        e.target.value = formatted;
    });

    // Enter key triggers validation
    cardInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            executeValidation();
        }
    });

    // Auto-run initial validation preview
    executeValidation();
});

function switchMode(mode) {
    document.getElementById('tab-single').classList.toggle('active', mode === 'single');
    document.getElementById('tab-batch').classList.toggle('active', mode === 'batch');
    
    document.getElementById('mode-single-container').style.display = mode === 'single' ? 'block' : 'none';
    document.getElementById('mode-batch-container').style.display = mode === 'batch' ? 'block' : 'none';
    
    document.getElementById('single-inspection-view').style.display = mode === 'single' ? 'block' : 'none';
    document.getElementById('batch-inspection-view').style.display = mode === 'batch' ? 'block' : 'none';
}

function loadPreset(cardNumber) {
    const input = document.getElementById('card-number-input');
    input.value = cardNumber;
    input.dispatchEvent(new Event('input'));
    executeValidation();
}

async function executeValidation() {
    const rawVal = document.getElementById('card-number-input').value;
    const cardNum = rawVal.replace(/\D/g, '') || "4111111111111111";

    const startTime = performance.now();
    try {
        const response = await fetch('/api/v1/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ card_number: cardNum, include_risk_analysis: true })
        });
        const duration = (performance.now() - startTime).toFixed(2);
        document.getElementById('request-timer').textContent = `${duration} ms`;
        document.getElementById('telemetry-latency').textContent = `${duration} ms`;

        if (!response.ok) {
            const err = await response.json();
            alert(`Error: ${err.detail || 'Validation failed'}`);
            return;
        }

        const data = await response.json();
        updateSingleView(data);
    } catch (err) {
        console.error('Validation request error:', err);
    }
}

function updateSingleView(data) {
    document.getElementById('res-masked').textContent = data.masked_card;
    document.getElementById('res-brand').textContent = `${data.brand} (${data.brand_code})`;
    
    const luhnEl = document.getElementById('res-luhn');
    if (data.is_valid_luhn) {
        luhnEl.innerHTML = `<span class="tag-valid">VALID PASSED</span>`;
    } else {
        luhnEl.innerHTML = `<span class="tag-invalid">INVALID CHECKSUM</span>`;
    }

    document.getElementById('res-bin').textContent = data.bin;
    document.getElementById('res-mii').textContent = data.mii_industry;
    document.getElementById('res-token').textContent = data.card_token;

    if (data.risk_assessment) {
        const risk = data.risk_assessment;
        const levelEl = document.getElementById('res-risk-level');
        levelEl.textContent = `${risk.level} (${risk.score}/100)`;

        const meterBar = document.getElementById('risk-meter-bar-fill');
        meterBar.style.width = `${risk.score}%`;

        if (risk.score < 30) {
            meterBar.style.background = 'var(--primary-emerald)';
            levelEl.className = 'result-value tag-risk-low';
        } else if (risk.score < 60) {
            meterBar.style.background = 'var(--warning-yellow)';
            levelEl.className = 'result-value';
        } else {
            meterBar.style.background = 'var(--danger-red)';
            levelEl.className = 'result-value tag-risk-high';
        }

        document.getElementById('res-entropy').textContent = risk.entropy;
        document.getElementById('res-flags').textContent = risk.flags.join(', ');
    }
}

async function executeBatchValidation() {
    const rawText = document.getElementById('batch-input-area').value;
    const cards = rawText.split('\n').map(s => s.trim()).filter(s => s.length > 0);

    if (cards.length === 0) {
        alert('Please enter at least one card number in the text area.');
        return;
    }

    const startTime = performance.now();
    try {
        const response = await fetch('/api/v1/validate/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cards: cards })
        });
        const duration = (performance.now() - startTime).toFixed(2);
        document.getElementById('request-timer').textContent = `${duration} ms`;

        if (!response.ok) {
            const err = await response.json();
            alert(`Batch Error: ${err.detail || 'Batch processing failed'}`);
            return;
        }

        const data = await response.json();
        renderBatchTable(data.results);
    } catch (err) {
        console.error('Batch validation error:', err);
    }
}

function renderBatchTable(results) {
    const tbody = document.getElementById('batch-results-body');
    tbody.innerHTML = '';

    results.forEach(res => {
        const tr = document.createElement('tr');
        const luhnTag = res.is_valid_luhn 
            ? `<span class="tag-valid">OK</span>` 
            : `<span class="tag-invalid">FAIL</span>`;
        
        const riskLevel = res.risk_assessment ? res.risk_assessment.level : 'UNKNOWN';
        const riskColor = riskLevel === 'LOW' ? 'var(--primary-emerald)' : (riskLevel === 'MEDIUM' ? 'var(--warning-yellow)' : 'var(--danger-red)');

        tr.innerHTML = `
            <td style="font-family: var(--mono-family); font-weight: 600;">${res.masked_card}</td>
            <td>${res.brand}</td>
            <td>${luhnTag}</td>
            <td style="color: ${riskColor}; font-weight: 700;">${riskLevel}</td>
        `;
        tbody.appendChild(tr);
    });
}
