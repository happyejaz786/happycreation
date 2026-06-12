// static/js/prompt_vault.js

document.addEventListener("DOMContentLoaded", () => {
    // 1. Vault Modal का HTML डायनामिक रूप से पेज में डालें
    const vaultHTML = `
        <div id="secretVaultModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); z-index:9999; justify-content:center; align-items:center;">
            <div style="background:#fff; width:450px; border-radius:10px; padding:20px; box-shadow:0 4px 15px rgba(0,0,0,0.2); position:relative; font-family:sans-serif;">
                <span id="closeVault" style="position:absolute; top:15px; right:20px; cursor:pointer; font-size:1.5rem; font-weight:bold; color:#333;">&times;</span>
                <h3 style="margin-top:0; color:#333; display:flex; align-items:center; gap:10px;">
                    <i class="fa-solid fa-lock" style="color:#f59e0b;"></i> Secret Prompt Vault
                </h3>
                
                <div id="vaultAuthSection">
                    <label style="font-size:0.85rem; color:#555;">Enter Master Password:</label>
                    <div style="display:flex; gap:10px; margin-top:5px; margin-bottom:15px;">
                        <input type="password" id="vaultPassword" style="flex-grow:1; padding:8px; border:1px solid #ccc; border-radius:5px;" placeholder="********">
                    </div>
                    <button id="unlockVaultBtn" style="padding:8px 15px; background:#fff; border:1px solid #ccc; border-radius:5px; cursor:pointer; font-weight:bold;">Unlock</button>
                </div>

                <div id="vaultContentSection" style="display:none; margin-top:15px;">
                    <div style="background:#d1fae5; color:#065f46; padding:10px; border-radius:5px; margin-bottom:15px; font-weight:bold; font-size:0.9rem;">
                        Access Granted!
                    </div>
                    <label style="font-size:0.85rem; color:#555;">AI Prompt (Internal Use Only):</label>
                    <textarea id="vaultPromptText" readonly style="width:100%; height:180px; margin-top:5px; padding:10px; border:none; background:#f3f4f6; border-radius:5px; color:#333; resize:none; font-family:inherit; font-size:0.9rem;"></textarea>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', vaultHTML);

    // 2. Modal के इवेंट्स और पासवर्ड लॉजिक
    const modal = document.getElementById("secretVaultModal");
    const closeBtn = document.getElementById("closeVault");
    const unlockBtn = document.getElementById("unlockVaultBtn");
    const passInput = document.getElementById("vaultPassword");
    const authSec = document.getElementById("vaultAuthSection");
    const contentSec = document.getElementById("vaultContentSection");
    const promptArea = document.getElementById("vaultPromptText");

    const MASTER_PASS = "123456"; // <-- अपना पासवर्ड यहाँ सेट करें

    closeBtn.onclick = () => { modal.style.display = "none"; };
    window.onclick = (e) => { if (e.target == modal) modal.style.display = "none"; };

    unlockBtn.onclick = () => {
        if(passInput.value === MASTER_PASS) {
            authSec.style.display = "none";
            contentSec.style.display = "block";
        } else {
            alert("Incorrect Password!");
            passInput.value = "";
        }
    };

    // 3. ग्लोबल फंक्शन जो History Manager इस्तेमाल करेगा Eye Icon लगाने के लिए
    window.attachPromptVaultIcon = function(targetContainer, promptText) {
        if(!promptText) return;

        const eyeBtnWrapper = document.createElement("div");
        eyeBtnWrapper.style.marginTop = "8px";

        const eyeBtn = document.createElement("button");
        eyeBtn.innerHTML = '<i class="fa-solid fa-eye"></i> View Prompt';
        eyeBtn.style.cssText = "background:#fff; border:1px solid #ddd; border-radius:5px; padding:5px 12px; font-size:0.8rem; cursor:pointer; color:#555; display:inline-flex; align-items:center; gap:5px;";

        eyeBtn.onclick = () => {
            passInput.value = "";
            authSec.style.display = "block";
            contentSec.style.display = "none";
            promptArea.value = promptText;
            modal.style.display = "flex";
        };

        eyeBtnWrapper.appendChild(eyeBtn);
        targetContainer.appendChild(eyeBtnWrapper);
    };
});