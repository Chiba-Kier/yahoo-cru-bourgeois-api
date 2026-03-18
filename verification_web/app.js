document.getElementById('fetchBtn').addEventListener('click', async () => {
    const baseUrl = document.getElementById('apiUrl').value.trim();
    const classification = document.getElementById('classification').value;
    const resultsGrid = document.getElementById('resultsGrid');
    const statusDiv = document.getElementById('status');
    const fetchBtn = document.getElementById('fetchBtn');

    if (!baseUrl) {
        alert('Please enter the Reader API URL (Function URL).');
        return;
    }

    // Clean up base URL (remove trailing slash if present)
    const cleanBaseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
    // Construct target URL (Reader handles /search/{classification})
    const targetUrl = `${cleanBaseUrl}/search/${classification}`;

    statusDiv.textContent = 'Fetching data from S3 via Reader Lambda...';
    resultsGrid.innerHTML = '';
    fetchBtn.disabled = true;

    try {
        const response = await fetch(targetUrl);
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        
        const data = await response.json();
        renderResults(data);
        statusDiv.textContent = `Success! Found ${data.total_chateaux} chateaux in ${classification}.`;
    } catch (err) {
        console.error(err);
        statusDiv.textContent = `Error: ${err.message}. Check browser console and CORS settings.`;
    } finally {
        fetchBtn.disabled = false;
    }
});

function renderResults(data) {
    const resultsGrid = document.getElementById('resultsGrid');
    
    if (!data.search_results || data.search_results.length === 0) {
        resultsGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center;">No results found for this classification.</div>';
        return;
    }

    data.search_results.forEach(chateauResult => {
        // Chateau Section Header
        const header = document.createElement('div');
        header.className = 'chateau-section';
        header.innerHTML = `<h3>${chateauResult.chateau} <small style="font-weight: normal; color: #888;">(${chateauResult.hit_count} hits)</small></h3>`;
        resultsGrid.appendChild(header);

        if (chateauResult.items.length === 0) {
            const noItem = document.createElement('div');
            noItem.style.padding = '20px';
            noItem.textContent = 'No items found in Yahoo! Shopping.';
            resultsGrid.appendChild(noItem);
            return;
        }

        // Wine Cards
        chateauResult.items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'card';
            
            const image = item.image || 'https://via.placeholder.com/200x200?text=No+Image';
            const price = item.price ? parseInt(item.price).toLocaleString() : 'N/A';
            const rating = item.review_rate ? '★'.repeat(Math.round(item.review_rate)) + '☆'.repeat(5 - Math.round(item.review_rate)) : '';

            card.innerHTML = `
                <img src="${image}" alt="${item.name}" class="card-image" onerror="this.src='https://via.placeholder.com/200x200?text=Error';">
                <div class="card-content">
                    <div class="item-name" title="${item.name}">${item.name}</div>
                    <div class="price">¥${price}</div>
                    <div class="store-name">${item.store || ''}</div>
                    <div class="rating">${rating} ${item.review_rate || ''}</div>
                    <a href="${item.url}" target="_blank" class="buy-button">Yahoo!ショッピングで見る</a>
                </div>
            `;
            resultsGrid.appendChild(card);
        });
    });
}
