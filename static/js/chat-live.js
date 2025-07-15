const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const loadingMessage = document.getElementById('loadingMessage');
let isWelcomeShown = true;

// กำหนด URL ของ Backend API
const API_BASE_URL = 'http://localhost:5000';

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideWelcome() {
    if (isWelcomeShown) {
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
            isWelcomeShown = false;
        }
    }
}

function addMessage(content, isUser = false) {
    hideWelcome();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'message-user' : 'message-bot'}`;
    
    const avatar = isUser ? '👤' : '🤖';
    const messageHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">${content}</div>
    `;
    
    messageDiv.innerHTML = messageHTML;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function showLoading() {
    loadingMessage.style.display = 'block';
    scrollToBottom();
}

function hideLoading() {
    loadingMessage.style.display = 'none';
}

// ตรวจสอบสถานะ Backend API
async function checkBackendStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/`, {
            method: 'GET',
            mode: 'cors'
        });
        
        if (response.ok) {
            document.querySelector('.chat-header .status-indicator').innerHTML = '🟢 ONLINE';
            document.querySelector('.chat-header .status-indicator').style.background = '#10b981';
            return true;
        }
    } catch (error) {
        document.querySelector('.chat-header .status-indicator').innerHTML = '🔴 OFFLINE';
        document.querySelector('.chat-header .status-indicator').style.background = '#ef4444';
        console.warn('Backend API is not running:', error);
        return false;
    }
    return false;
}

async function sendMessage(event) {
    event.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message) return;

    // แสดงข้อความของผู้ใช้
    addMessage(message, true);
    messageInput.value = '';
    sendButton.disabled = true;
    showLoading();

    try {
        // ตรวจสอบ Backend ก่อน
        const isBackendOnline = await checkBackendStatus();
        
        if (!isBackendOnline) {
            hideLoading();
            addMessage(`
                ❌ <strong>ไม่สามารถเชื่อมต่อกับ Backend API ได้</strong><br><br>
                กรุณาทำตามขั้นตอนนี้:<br>
                1️⃣ เปิด Terminal ใหม่<br>
                2️⃣ รันคำสั่ง: <code>cd "${window.location.pathname.replace('/index-live.html', '').replace('/', '')}"</code><br>
                3️⃣ รันคำสั่ง: <code>python app.py</code><br>
                4️⃣ รอจนเห็น "🚀 ระบบพร้อมใช้งาน"<br>
                5️⃣ ลองส่งข้อความใหม่อีกครั้ง
            `);
            sendButton.disabled = false;
            messageInput.focus();
            return;
        }

        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            mode: 'cors',
            body: JSON.stringify({ prompt: message })
        });

        const data = await response.json();
        
        hideLoading();
        
        if (response.ok) {
            let formattedResponse = data.response || data.message || 'ขออภัย ไม่สามารถตอบคำถามได้';
            
            // ตรวจสอบว่าเป็น HTML หรือไม่
            if (formattedResponse.includes('<!DOCTYPE html>') || formattedResponse.includes('<html>')) {
                // เป็น HTML เต็มรูปแบบ - แยกเอาเฉพาะส่วน body
                const parser = new DOMParser();
                const doc = parser.parseFromString(formattedResponse, 'text/html');
                const bodyContent = doc.body.innerHTML;
                addMessage(bodyContent);
            } else if (formattedResponse.includes('<') && formattedResponse.includes('>')) {
                // เป็น HTML fragment
                addMessage(formattedResponse);
            } else {
                // เป็น text ธรรมดา - แปลง markdown-style formatting
                // แปลง **text** เป็น <strong>text</strong>
                formattedResponse = formattedResponse.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                
                // แปลง *text* เป็น <em>text</em>
                formattedResponse = formattedResponse.replace(/\*(.*?)\*/g, '<em>$1</em>');
                
                // แปลง newlines เป็น <br>
                formattedResponse = formattedResponse.replace(/\n/g, '<br>');
                
                addMessage(formattedResponse);
            }
        } else {
            addMessage('❌ เกิดข้อผิดพลาด: ' + (data.error || 'ไม่สามารถติดต่อเซิร์ฟเวอร์ได้'));
        }
    } catch (error) {
        hideLoading();
        addMessage(`
            ❌ <strong>เกิดข้อผิดพลาดในการเชื่อมต่อ</strong><br><br>
            สาเหตุที่เป็นไปได้:<br>
            • Backend API ไม่ได้รัน (python app.py)<br>
            • CORS Policy ปิดกั้น<br>
            • Network Error<br><br>
            <em>กรุณาตรวจสอบ Console สำหรับรายละเอียด</em>
        `);
        console.error('Error:', error);
    } finally {
        sendButton.disabled = false;
        messageInput.focus();
    }
}

function askQuestion(question) {
    messageInput.value = question;
    sendMessage({ preventDefault: () => {} });
}

// เพิ่ม event listener สำหรับ suggestion chips
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('suggestion-chip')) {
        const suggestion = e.target.textContent.replace(/^[📊⚽📰📈🔥📅]\s*/, '');
        let question = '';
        
        switch(suggestion) {
            case 'ตารางคะแนน':
                question = 'ตารางคะแนน พรีเมียร์ลีก';
                break;
            case 'ดาวซัลโว':
                question = 'ดาวซัลโว พรีเมียร์ลีก';
                break;
            case 'ข่าวล่าสุด':
                question = 'ข่าวบอลวันนี้';
                break;
            case 'ฟอร์มทีม':
                question = 'ฟอร์ม 5 นัด แมนยู';
                break;
            case 'เปรียบเทียบทีม':
                question = 'เปรียบเทียบ แมนยู vs ลิเวอร์พูล';
                break;
            case 'ผลบอล':
                question = 'ผลบอลวันนี้';
                break;
            default:
                question = suggestion;
        }
        
        askQuestion(question);
    }
});

// เมื่อหน้าเว็บโหลดเสร็จ
document.addEventListener('DOMContentLoaded', function() {
    // Focus on input
    messageInput.focus();
    
    // ตรวจสอบสถานะ Backend
    checkBackendStatus();
    
    // ตรวจสอบทุก 30 วินาที
    setInterval(checkBackendStatus, 30000);
    
    // แสดงข้อความต้อนรับพิเศษสำหรับ Live Server
    const welcomeText = document.querySelector('.welcome-message h3');
    if (welcomeText) {
        welcomeText.innerHTML = '🚀 ยินดีต้อนรับสู่ Football AI (Live Server)!';
    }
    
    // เพิ่มข้อความแนะนำ
    const welcomeDesc = document.querySelector('.welcome-message p');
    if (welcomeDesc) {
        welcomeDesc.innerHTML = `
            ฉันสามารถตอบคำถามเกี่ยวกับ:<br>
            <small style="color: #64748b;">💡 หากไม่สามารถส่งข้อความได้ กรุณารัน <code>python app.py</code> ใน Terminal</small>
        `;
    }
});

// Enter to send message
messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(e);
    }
});
