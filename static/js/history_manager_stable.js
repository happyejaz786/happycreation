// static/js/history_manager.js

// =========================================================================
// GLOBAL CODE ACTIONS (COPY & DOWNLOAD)
// =========================================================================
window.copyCode = function(button) {
    const wrapper = button.closest('.code-block-wrapper');
    const codeContent = wrapper.querySelector('.code-content').textContent;
    
    navigator.clipboard.writeText(codeContent).then(() => {
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="fa-solid fa-check" style="color:#10b981;"></i>';
        setTimeout(() => { button.innerHTML = originalHTML; }, 2000);
    }).catch(err => console.error("Copy failed:", err));
};

window.downloadCode = function(button, extension) {
    const wrapper = button.closest('.code-block-wrapper');
    const codeContent = wrapper.querySelector('.code-content').textContent;
    
    const blob = new Blob([codeContent], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    
    const extMap = { 'python': 'py', 'javascript': 'js', 'html': 'html', 'css': 'css', 'json': 'json', 'bash': 'sh', 'shell': 'sh' };
    const finalExt = extMap[extension] || extension || 'txt';
    
    a.href = url;
    a.download = `Happy_Code_${Math.floor(Math.random() * 10000)}.${finalExt}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};

// =========================================================================
// MESSAGE FORMATTING ENGINE (TEXT & CODE BLOCKS)
// =========================================================================
function formatMessage(text) {
    let blocks = [];
    let placeholder = "___CODE_BLOCK_PLACEHOLDER___";
    
    // 1. Extract and protect code blocks
    let extractedText = text.replace(/```(\w*)\n([\s\S]*?)```/g, function(match, lang, code) {
        blocks.push({lang: lang, code: code});
        return placeholder;
    });

    // 2. Convert standard newlines to <br> for plain text
    extractedText = extractedText.replace(/\n/g, "<br>");

    // 3. Restore code blocks with advanced UI
    let finalHtml = extractedText.replace(new RegExp(placeholder, 'g'), function() {
        let block = blocks.shift();
        let safeCode = block.code.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        let extension = block.lang.toLowerCase() || 'txt';
        let langDisplay = block.lang ? block.lang.toUpperCase() : 'CODE';
        
        return `<div class="code-block-wrapper" style="background:#1e1e1e; border-radius:8px; margin:15px 0; overflow:hidden; border: 1px solid #333; text-align:left; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div class="code-header" style="background:#2d2d2d; padding:8px 15px; display:flex; justify-content:space-between; align-items:center; color:#e0e0e0; font-size:0.85rem; font-family:'Segoe UI', Tahoma, sans-serif; border-bottom: 1px solid #444;">
                <span class="code-lang" style="font-weight:bold; letter-spacing:0.5px;">${langDisplay}</span>
                <div class="code-actions" style="display:flex; gap:15px;">
                    <button onclick="downloadCode(this, '${extension}')" style="background:none; border:none; color:#e0e0e0; cursor:pointer; font-size:1.1rem; padding:0; transition:color 0.2s;" title="Download" onmouseover="this.style.color='#10b981'" onmouseout="this.style.color='#e0e0e0'"><i class="fa-solid fa-circle-down"></i></button>
                    <button onclick="copyCode(this)" style="background:none; border:none; color:#e0e0e0; cursor:pointer; font-size:1.1rem; padding:0; transition:color 0.2s;" title="Copy" onmouseover="this.style.color='#2563eb'" onmouseout="this.style.color='#e0e0e0'"><i class="fa-regular fa-copy"></i></button>
                </div>
            </div>
            <div style="padding:15px; overflow-x:auto; background:#1e1e1e;">
                <code class="code-content" style="color:#d4d4d4; font-family:Consolas, Monaco, monospace; font-size:0.95rem; white-space: pre;">${safeCode}</code>
            </div>
        </div>`;
    });
    
    return finalHtml;
}
document.addEventListener("DOMContentLoaded", function () {
    const chatForm = document.getElementById("chatForm");
    const userInput = document.getElementById("userInput");
    const chatContainer = document.getElementById("chat-container");
    const historyList = document.getElementById("history-list");
    const btnNewChat = document.getElementById("btn-new-chat");
    const chatWrapper = document.getElementById("chat-wrapper");
    const moduleContainer = document.getElementById("module-container");

    // Global App States
    let activeChatId = "";
    let currentChatHistory = [];

    // --- URL Se Chat ID nikalne ka logic (For Iframe Mode) ---
    const urlParams = new URLSearchParams(window.location.search);
    const urlChatId = urlParams.get("chat_id");
    if (urlChatId) {
        activeChatId = urlChatId;
    }

    // =========================================================================
    // 1. FETCH AND RENDER SIDEBAR RECENT CHATS LIST PANEL
    // =========================================================================
    window.loadHistoryList = async function() {
        try {
            const response = await fetch("/api/history");
            const data = await response.json();

            if (!historyList) return;
            historyList.innerHTML = "";

            if (data.length === 0) {
                historyList.innerHTML = '<div class="history-item text-muted justify-content-center" style="font-size: 0.9rem; padding: 10px 24px;">No recent chats</div>';
                return;
            }

            data.forEach(item => {
                const historyItem = document.createElement("div");
                historyItem.className = `history-item ${item.id === activeChatId ? 'active' : ''}`;
                historyItem.setAttribute("data-id", item.id);
                
                historyItem.innerHTML = `
                    <span class="chat-title-text text-truncate me-2" style="flex-grow: 1; cursor: pointer; font-size: 1rem; font-weight: bold;">
                        <i class="fa-regular fa-message me-2" style="font-size: 0.9rem; color: #444746;"></i>${item.title}
                    </span>
                    <div class="history-actions d-flex gap-2">
                        <button class="btn-pin-chat border-0 bg-transparent p-0" title="${item.pinned ? 'Unpin' : 'Pin'}" style="color: ${item.pinned ? '#1a73e8' : '#747775'}; font-size: 0.85rem;">
                            <i class="fa-solid fa-thumbtack" style="${item.pinned ? '' : 'opacity: 0.4;'}"></i>
                        </button>
                        <button class="btn-rename-chat border-0 bg-transparent p-0" title="Rename" style="color: #747775; font-size: 0.85rem;">
                            <i class="fa-regular fa-pen-to-square"></i>
                        </button>
                        <button class="btn-delete-chat border-0 bg-transparent p-0" title="Delete" style="color: #ff4b4b; font-size: 0.85rem;">
                            <i class="fa-regular fa-trash-can"></i>
                        </button>
                    </div>
                `;

                historyItem.querySelector(".chat-title-text").addEventListener("click", () => {
                    if (moduleContainer) {
                        moduleContainer.src = "/assistant?chat_id=" + item.id;
                        moduleContainer.style.display = "block";
                        document.querySelectorAll(".history-item").forEach(el => el.classList.remove("active"));
                        historyItem.classList.add("active");
                    } else {
                        loadChatSessionDetails(item.id);
                    }
                });

                historyItem.querySelector(".btn-pin-chat").addEventListener("click", async (e) => {
                    e.stopPropagation();
                    await fetch("/api/history/pin", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: item.id }) });
                    window.loadHistoryList();
                });

                historyItem.querySelector(".btn-rename-chat").addEventListener("click", async (e) => {
                    e.stopPropagation();
                    const newTitle = prompt("Naya chat title enter karein:", item.title);
                    if (newTitle && newTitle.trim() !== "") {
                        await fetch("/api/history/rename", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: item.id, title: newTitle.trim() }) });
                        window.loadHistoryList();
                    }
                });

                historyItem.querySelector(".btn-delete-chat").addEventListener("click", async (e) => {
                    e.stopPropagation();
                    if (confirm("Kya aap is conversation ko delete karna chahte hain?")) {
                        await fetch("/api/history/delete", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: item.id }) });
                        if (item.id === activeChatId) {
                            if(moduleContainer) moduleContainer.src = "/assistant";
                            else resetToNewChatState();
                        }
                        window.loadHistoryList();
                    }
                });

                historyList.appendChild(historyItem);
            });
        } catch (error) {
            console.error("History data sync fault:", error);
        }
    }

    if (historyList) window.loadHistoryList();

    // =========================================================================
    // 2. LOAD RECONSTRUCTED CONVERSATION LOGS INTO MAIN VIEWPORT
    // =========================================================================
    async function loadChatSessionDetails(chatId) {
        try {
            const response = await fetch(`/api/get_chat_details/${chatId}`);
            const data = await response.json();

            if (data.status === "success") {
                activeChatId = chatId;
                currentChatHistory = []; 
                
                if (chatContainer) {
                    chatContainer.innerHTML = "";
                    
					data.history.forEach(msg => {
                        console.log("HISTORY ITEM:", msg);
						const msgDiv = document.createElement("div");
                        msgDiv.className = `message ${msg.role === 'user' ? 'msg-user' : 'msg-ai'}`;
                        
                        // Using the new robust formatMessage function
                        //msgDiv.innerHTML = formatMessage(msg.text);
                        msgDiv.innerHTML = 
						formatMessage(
							msg.text ||
							msg.content ||
							msg.message ||
							""
						)
						
                        chatContainer.appendChild(msgDiv);
                        //currentChatHistory.push({ role: msg.role, text: msg.text });
						currentChatHistory.push({
							role: msg.role ||
							msg.content ||
							msg.message ||
							""
						});
                    });
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
                if (chatWrapper) chatWrapper.style.display = "flex";
            }
        } catch (error) {
            console.error("Context synchronization parsing mismatch trace:", error);
        }
    }

    if (urlChatId && chatContainer) loadChatSessionDetails(urlChatId);

    // =========================================================================
    // 3. SLATE TO NEW UNINITIALIZED SLATE VIEW WORKSPACE
    // =========================================================================
    function resetToNewChatState() {
        activeChatId = "";
        currentChatHistory = [];
        if (chatContainer) {
            chatContainer.innerHTML = `
                <div class="message msg-ai">
                    Assalamu Alaikum! I am here to help you. How can I assist you today?
                </div>
            `;
        }
        if (chatWrapper) chatWrapper.style.display = "flex";
        if (moduleContainer) {
            moduleContainer.src = "/assistant";
            moduleContainer.style.display = "block";
            document.querySelectorAll(".history-item").forEach(el => el.classList.remove("active"));
        }
    }

    // =========================================================================
    // 4. CHAT MESSAGE CORE PIPELINE INTERACTION GATEWAY SYSTEM
    // =========================================================================
    async function submitConversationalPayload() {
        const rawMessage = userInput.value.trim();
        
        let filesToSend = [];
        if (window.selectedFiles && window.selectedFiles.length > 0) {
            filesToSend = window.selectedFiles;
        } else {
            const fileInputIDs = ["file-upload", "fileInput", "file_upload"];
            for (let id of fileInputIDs) {
                const el = document.getElementById(id);
                if (el && el.files && el.files.length > 0) {
                    filesToSend = Array.from(el.files);
                    break;
                }
            }
        }

        const hasFiles = filesToSend.length > 0;
        if (!rawMessage && !hasFiles) return;

        const userMsgDiv = document.createElement("div");
        userMsgDiv.className = "message msg-user";
        
        let msgHTML = "";
        if (rawMessage) {
            msgHTML += `<div>${rawMessage.replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\n/g, "<br>")}</div>`;
        }
        if (hasFiles) {
            msgHTML += `<div class="mt-2" style="font-size: 0.85em; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 8px; color: rgba(255,255,255,0.85);">`;
            msgHTML += `<i class="fa-solid fa-paperclip me-1"></i> <strong>Attached Files:</strong><br>`;
            filesToSend.forEach(f => {
                let size = (f.size / 1024).toFixed(1);
                msgHTML += `<span style="display: block; margin-top: 3px;">📄 ${f.name} (${size} KB)</span>`;
            });
            msgHTML += `</div>`;
        }
        userMsgDiv.innerHTML = msgHTML;
        chatContainer.appendChild(userMsgDiv);
        
        userInput.value = ""; 
        userInput.style.height = "auto"; 
        chatContainer.scrollTop = chatContainer.scrollHeight;

        const typingIndicator = document.createElement("div");
        typingIndicator.className = "typing-indicator";
        typingIndicator.id = "system-typing-indicator";
        typingIndicator.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
        chatContainer.appendChild(typingIndicator);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        const payloadFormData = new FormData();

		payloadFormData.append("message", rawMessage);
		payloadFormData.append("chat_id", activeChatId);
		payloadFormData.append(
			"history",
			JSON.stringify(currentChatHistory)
		);

		const currentMode =
			document.getElementById("mode-search").checked
				? "web"
				: "ai";

		payloadFormData.append("mode", currentMode);

		console.log("MODE SENT:", currentMode);

		filesToSend.forEach((file) => {
			payloadFormData.append("files", file);
		});

        if (window.selectedFiles) window.selectedFiles = [];
        if (typeof window.clearFilePreview === "function") window.clearFilePreview();
        const previewContainer = document.getElementById("file-preview-container");
        if (previewContainer) previewContainer.innerHTML = "";
        ["file-upload", "fileInput"].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = "";
        });

        try {
            const response = await fetch("/api/smart_chat", {
                method: "POST",
                body: payloadFormData
            });
            const responseData = await response.json();

            const indicatorNode = document.getElementById("system-typing-indicator");
            if (indicatorNode) indicatorNode.remove();

            if (responseData.status === "success") {
                activeChatId = responseData.chat_id;
				// --- Eye Icon यहाँ लगेगा ------------------------------------------------------------------------
                if (window.attachPromptVaultIcon) {
                    // ध्यान दें: अगर आपने response का नाम responseData रखा है, तो responseData.prompt_used लिखें
                    window.attachPromptVaultIcon(userMsgDiv, responseData.prompt_used); 
                }
                // ---------------------------------------------------------------------------------------------
                const aiMsgDiv = document.createElement("div");
                aiMsgDiv.className = "message msg-ai";
                
                // Using the new robust formatMessage function
                // aiMsgDiv.innerHTML = formatMessage(responseData.reply);
                // (जहाँ लाइन लिखी है: aiMsgDiv.innerHTML = formatMessage(responseData.reply);)
                // इसके ठीक नीचे पेस्ट करें:
                
                aiMsgDiv.innerHTML = formatMessage(responseData.reply);

                if (responseData.source_indicator) {
                    const sourceDiv = document.createElement("div");
                    sourceDiv.style.fontSize = "0.75rem";
                    sourceDiv.style.color = "#666";
                    sourceDiv.style.marginTop = "4px";
                    sourceDiv.style.marginLeft = "18px";
                    sourceDiv.style.fontStyle = "italic";
                    sourceDiv.textContent = responseData.source_indicator;
                    chatContainer.appendChild(sourceDiv);
                }
				
                chatContainer.appendChild(aiMsgDiv);

				currentChatHistory.push({ role: "user", content: rawMessage });
				currentChatHistory.push({ role: "assistant", content: responseData.reply });
				//currentChatHistory.push({ role: "model", text: responseData.reply });
                chatContainer.scrollTop = chatContainer.scrollHeight;

                if (window.parent && typeof window.parent.loadHistoryList === "function") {
                    window.parent.loadHistoryList();
                } else {
                    window.loadHistoryList();
                }
            } else {
                throw new Error(responseData.message || "Pipeline error");
            }
        } catch (error) {
            const indicatorNode = document.getElementById("system-typing-indicator");
            if (indicatorNode) indicatorNode.remove();
            
            const errDiv = document.createElement("div");
            errDiv.className = "message msg-ai text-danger";
            errDiv.textContent = `Error Exception: ${error.message}`;
            chatContainer.appendChild(errDiv);
        }
    }

    // =========================================================================
    // 5. EVENT HANDLERS REGISTRATIONS MATCHING LAYOUT DOM NODES
    // =========================================================================
    if (chatForm) {
        chatForm.addEventListener("submit", function (e) {
            e.preventDefault();
            submitConversationalPayload();
        });
    }

    if (userInput) {
        userInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submitConversationalPayload();
            }
        });
        userInput.addEventListener("input", function () {
            this.style.height = "auto";
            this.style.height = (this.scrollHeight) + "px";
        });
    }

    if (btnNewChat) {
        btnNewChat.addEventListener("click", function (e) {
            e.preventDefault();
            resetToNewChatState();
        });
    }
});