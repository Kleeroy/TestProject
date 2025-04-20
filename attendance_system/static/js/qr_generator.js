

/**
 * Helper functions for QR code display and management
 */

// Function to trigger QR code printing
function printQRCode() {
    const qrCodeContainer = document.querySelector('.qr-container');
    const studentInfo = document.querySelector('.student-info');
    
    if (!qrCodeContainer) return;
    
    // Create a new window for printing
    const printWindow = window.open('', '_blank');
    
    // Create print content
    let printContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>QR Code</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    text-align: center;
                }
                .print-container {
                    max-width: 400px;
                    margin: 0 auto;
                    border: 1px solid #ccc;
                    padding: 20px;
                    border-radius: 5px;
                }
                .qr-image {
                    max-width: 100%;
                    height: auto;
                }
                .info {
                    margin-top: 20px;
                    text-align: left;
                }
                h2 {
                    margin-top: 0;
                }
                @media print {
                    .print-container {
                        border: none;
                    }
                }
            </style>
        </head>
        <body>
            <div class="print-container">
                <h2>Attendance QR Code</h2>
                <div class="qr-image">
                    ${qrCodeContainer.innerHTML}
                </div>
                <div class="info">
                    ${studentInfo ? studentInfo.innerHTML : ''}
                </div>
            </div>
            <script>
                window.onload = function() {
                    window.print();
                    window.setTimeout(function() {
                        window.close();
                    }, 500);
                };
            </script>
        </body>
        </html>
    `;
    
    // Write to the new window and trigger print
    printWindow.document.open();
    printWindow.document.write(printContent);
    printWindow.document.close();
}

// Function to download QR code as PNG
function downloadQRCode() {
    const qrCodeImage = document.querySelector('.qr-container img');
    if (!qrCodeImage) return;
    
    // Create a link element
    const link = document.createElement('a');
    link.href = qrCodeImage.src;
    link.download = 'qr_code.png';
    
    // Append to body, trigger click, then remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Export functions
export { printQRCode, downloadQRCode };