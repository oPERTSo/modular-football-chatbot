const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const loadingMessage = document.getElementById('loadingMessage');
let isWelcomeShown = true;

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

// จัดการโลโก้ทีมที่โหลดไม่ขึ้น
function handleTeamLogos() {
    const teamLogos = document.querySelectorAll('.team-logo');
    teamLogos.forEach(logo => {
        logo.addEventListener('error', function() {
            console.log('Logo failed to load:', this.src);
            this.style.display = 'none';
        });
        
        logo.addEventListener('load', function() {
            console.log('Logo loaded successfully:', this.src);
        });
    });
}

// เรียกใช้หลังจากเพิ่มข้อความใหม่
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
    
    // จัดการโลโก้หลังจากเพิ่ม DOM element
    setTimeout(() => {
        handleTeamLogos();
    }, 100);
    
    scrollToBottom();
}

function showLoading() {
    loadingMessage.style.display = 'block';
    scrollToBottom();
}

function hideLoading() {
    loadingMessage.style.display = 'none';
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
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
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
        addMessage('❌ เกิดข้อผิดพลาดในการเชื่อมต่อ กรุณาลองใหม่อีกครั้ง');
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
            case 'ทำนายผล':
                question = 'ทำนายผลแมตช์ที่กำลังจะมาถึง';
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

// Focus on input when page loads
messageInput.focus();

// Enter to send message
messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(e);
    }
});
