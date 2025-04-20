

/**
 * QR Code Scanner for Attendance System
 * Uses jsQR library to decode QR codes from video feed
 */

class QRScanner {
    constructor(videoElement, csrfToken, processingUrl) {
        this.video = videoElement;
        this.csrfToken = csrfToken;
        this.processingUrl = processingUrl;
        this.canvasElement = document.createElement('canvas');
        this.canvas = this.canvasElement.getContext('2d');
        this.scanning = false;
        this.videoStream = null;
    }
    
    start() {
        if (this.scanning) return;
        
        navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
            .then(stream => {
                this.videoStream = stream;
                this.video.srcObject = stream;
                this.video.setAttribute('playsinline', true);
                this.video.play();
                this.scanning = true;
                requestAnimationFrame(() => this.tick());
            })
            .catch(error => {
                console.error('Error accessing camera:', error);
                alert('Unable to access camera. Please make sure you have granted camera permissions.');
            });
    }
    
    stop() {
        this.scanning = false;
        
        if (this.videoStream) {
            this.videoStream.getTracks().forEach(track => {
                track.stop();
            });
            this.video.srcObject = null;
        }
    }
    
    tick() {
        if (!this.scanning) return;
        
        if (this.video.readyState === this.video.HAVE_ENOUGH_DATA) {
            this.canvasElement.height = this.video.videoHeight;
            this.canvasElement.width = this.video.videoWidth;
            this.canvas.drawImage(this.video, 0, 0, this.canvasElement.width, this.canvasElement.height);
            
            const imageData = this.canvas.getImageData(0, 0, this.canvasElement.width, this.canvasElement.height);
            const code = jsQR(imageData.data, imageData.width, imageData.height, {
                inversionAttempts: "dontInvert",
            });
            
            if (code) {
                // Process the QR code data
                this.processQRCode(code.data);
            }
        }
        
        requestAnimationFrame(() => this.tick());
    }
    
    processQRCode(qrData) {
        try {
            const data = JSON.parse(qrData);
            
            // Send to server
            fetch(this.processingUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    qr_data: qrData
                })
            })
            .then(response => response.json())
            .then(result => {
                // Emit an event with the result
                const event = new CustomEvent('qrScanned', { detail: result });
                document.dispatchEvent(event);
                
                // Pause scanning briefly to avoid duplicate scans
                this.scanning = false;
                setTimeout(() => {
                    this.scanning = true;
                    requestAnimationFrame(() => this.tick());
                }, 2000);
            })
            .catch(error => {
                console.error('Error processing QR code:', error);
                const event = new CustomEvent('qrError', { 
                    detail: { message: 'Error processing QR code. Please try again.' } 
                });
                document.dispatchEvent(event);
            });
        } catch (e) {
            console.error('Invalid QR code format:', e);
            const event = new CustomEvent('qrError', { 
                detail: { message: 'Invalid QR code format. Please scan a valid QR code.' } 
            });
            document.dispatchEvent(event);
        }
    }
}

// Export the class
export default QRScanner;