document.addEventListener("DOMContentLoaded", function () {
    const scanner = new Html5Qrcode("reader");
    const startBtn = document.getElementById("start-btn");
    const stopBtn = document.getElementById("stop-btn");
    const resultDiv = document.getElementById("result");

    const config = { fps: 10, qrbox: { width: 250, height: 250 } };

    startBtn.addEventListener("click", function () {
        if (scanner._isScanning) { // Prevent multiple instances
            scanner.stop().then(() => startScanner());
        } else {
            startScanner();
        }
    });

    function startScanner() {
        Html5Qrcode.getCameras().then(cameras => {
            if (cameras.length > 0) {
                scanner.start(
                    cameras[0].id,
                    config,
                    onScanSuccess
                ).then(() => {
                    startBtn.disabled = true;
                    stopBtn.disabled = false;
                }).catch(err => {
                    resultDiv.innerHTML = `<div class="alert error">Cannot start scanner: ${err}</div>`;
                });
            }
        }).catch(err => console.error(err));
    }

    stopBtn.addEventListener("click", function () {
        scanner.stop().then(() => {
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }).catch(err => {
            console.error("Failed to stop scanner", err);
        });
    });

    async function onScanSuccess(decodedText) {
        await scanner.stop();
        stopBtn.disabled = true;

        try {
            const response = await fetch('/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ qr_data: decodedText })
            });

            const data = await response.json();

            let statusMessage = data.status === 'real' 
                ? `<p class="status-real">✅ Genuine Product</p><p>This product is verified authentic</p>`
                : `<p class="status-fake">❌ Fake Product</p><p>This product is not in our verified database</p>`;

            resultDiv.innerHTML = `
                <div class="scan-result ${data.status}">
                    <h3>${data.name || 'Unknown Product'}</h3>
                    ${data.category ? `<p>Category: ${data.category}</p>` : ''}
                    ${statusMessage}
                    <p>Verified on: ${new Date(data.created_at).toLocaleString()}</p>
                    <div class="action-buttons">
                        <button id="rescan-btn" class="btn">Scan Another</button>
                        <a href="/products/${data.status}" class="btn">
                            View ${data.status} Products
                        </a>
                    </div>
                </div>
            `;

            document.getElementById('rescan-btn').addEventListener('click', () => {
                resultDiv.innerHTML = '';
                startBtn.click();
            });

        } catch (error) {
            resultDiv.innerHTML = `
                <div class="alert error">
                    Error verifying product: ${error.message}
                    <button id="rescan-btn" class="btn">Try Again</button>
                </div>
            `;
            document.getElementById('rescan-btn').addEventListener('click', () => {
                resultDiv.innerHTML = '';
                startBtn.click();
            });
        }
    }
});