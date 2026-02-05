/**
 * Agentic Honey-Pot | Dashboard Logic v2
 * Improved error handling and robust rendering
 */

document.addEventListener("DOMContentLoaded", () => {
    console.log("Honey-Pot Dashboard Initializing...");

    // --- DOM Elements ---
    const analyzeBtn = document.getElementById("analyzeBtn");
    const messageInput = document.getElementById("messageInput");
    const apiKeyInput = document.getElementById("apiKey");
    const intelligenceReport = document.getElementById("intelligenceReport");
    
    // Results DOM
    const meterFill = document.getElementById("meterFill");
    const threatScoreDisplay = document.getElementById("threatScoreDisplay");
    const threatBadge = document.getElementById("threatBadge");
    const scamTypeDisplay = document.getElementById("scamTypeDisplay");
    const confidenceDisplay = document.getElementById("confidenceDisplay");
    const intentOutput = document.getElementById("intentOutput");
    const entityCloud = document.getElementById("entityCloud");

    // Vault DOM
    const createKeyBtn = document.getElementById("createKeyBtn");
    const newKeyNameInput = document.getElementById("newKeyName");
    const newKeyDisplay = document.getElementById("newKeyDisplay");
    const generatedKeyEl = document.getElementById("generatedKey");
    const copyKeyBtn = document.getElementById("copyKeyBtn");
    const keysTableBody = document.getElementById("keysTableBody");

    // Verification
    if (!analyzeBtn || !intelligenceReport) {
        console.error("Critical DOM elements missing!");
        return;
    }

    // --- Initialization ---
    fetchKeys();

    apiKeyInput.addEventListener("input", debounce(() => {
        fetchKeys();
    }, 500));

    // --- Analysis Execution ---
    analyzeBtn.addEventListener("click", async () => {
        const message = messageInput.value.trim();
        const apiKey = apiKeyInput.value.trim();

        console.log("Analyze clicked:", { messageLength: message.length, hasApiKey: !!apiKey });

        if (!message) {
            alert("Please enter a message to analyze.");
            return;
        }

        // Toggle state
        toggleLoading(true);

        try {
            const response = await fetch("/api/honeypot", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-API-Key": apiKey
                },
                body: JSON.stringify({ message })
            });

            console.log("API Response Status:", response.status);

            const data = await response.json();

            if (!response.ok) {
                console.error("API Error Data:", data);
                throw new Error(data.detail || "Analysis failed.");
            }

            console.log("Analysis Successful, rendering...");
            renderIntelligence(data);
        } catch (error) {
            console.error("Execution Error:", error);
            alert(`Execution Failed: ${error.message}\nCheck console for details.`);
        } finally {
            toggleLoading(false);
        }
    });

    function toggleLoading(isLoading) {
        analyzeBtn.disabled = isLoading;
        const loader = analyzeBtn.querySelector(".loader");
        const icon = analyzeBtn.querySelector(".btn-icon");
        const text = analyzeBtn.querySelector(".btn-text");

        if (loader) loader.classList.toggle("hidden", !isLoading);
        if (icon) icon.classList.toggle("hidden", isLoading);
        if (text) text.textContent = isLoading ? "Deconstructing..." : "Execute Analysis";
    }

    function renderIntelligence(data) {
        // Ensure report is totally visible
        intelligenceReport.classList.remove("hidden");
        intelligenceReport.style.display = "block"; // Force display
        
        // Update basic text
        threatScoreDisplay.textContent = data.threat_score || "0";
        scamTypeDisplay.textContent = data.scam_type || "--";
        confidenceDisplay.textContent = `${((data.confidence_score || 0) * 100).toFixed(1)}%`;
        intentOutput.textContent = data.intent || "Unknown";

        // Update Meter
        const score = data.threat_score || 0;
        const offset = 282.7 - (score / 100) * 282.7;
        if (meterFill) {
            meterFill.style.strokeDashoffset = offset;
            let color = "#6366f1"; // Default
            if (score > 70) color = "#ef4444";
            else if (score > 40) color = "#f59e0b";
            else color = "#10b981";
            meterFill.style.stroke = color;
        }

        // Threat Badge
        if (threatBadge) {
            const level = (data.threat_level || "Low").toLowerCase();
            threatBadge.className = `badge-status ${level}`;
            threatBadge.textContent = `${data.threat_level || 'Low'} Priority`;
        }

        // Artifact Cloud
        if (entityCloud) {
            entityCloud.innerHTML = "";
            const ent = data.extracted_entities || {};
            const items = [...(ent.urls || []), ...(ent.emails || []), ...(ent.phones || [])];
            
            if (items.length === 0) {
                entityCloud.innerHTML = '<span style="color: grey;">No artifacts detected.</span>';
            } else {
                items.forEach(item => {
                    const span = document.createElement("span");
                    span.className = "artifact-item";
                    span.textContent = item;
                    entityCloud.appendChild(span);
                });
            }
        }

        // Trigger visual reveal
        setTimeout(() => {
            intelligenceReport.classList.add("reveal");
            intelligenceReport.scrollIntoView({ behavior: "smooth", block: "center" });
        }, 50);
    }

    // --- Vault Management ---
    async function fetchKeys() {
        const apiKey = apiKeyInput.value.trim();
        try {
            const response = await fetch("/api/keys", {
                headers: { "X-API-Key": apiKey }
            });
            if (!response.ok) return;
            const data = await response.json();
            renderKeys(data);
        } catch (e) {
            console.warn("Vault sync skipped:", e.message);
        }
    }

    function renderKeys(keys) {
        if (!keysTableBody) return;
        if (!keys || keys.length === 0) {
            keysTableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: grey; padding: 2rem;">No active keys found.</td></tr>';
            return;
        }
        keysTableBody.innerHTML = keys.map(key => `
            <tr>
                <td><strong>${key.name}</strong></td>
                <td><code style="color: #6366f1;">${key.prefix}...</code></td>
                <td style="color: grey;">${key.last_used ? new Date(key.last_used).toLocaleDateString() : 'Never'}</td>
                <td>
                    <button class="delete-action" onclick="revokeKey('${key.id}')">Revoke</button>
                </td>
            </tr>
        `).join("");
    }

    createKeyBtn.addEventListener("click", async () => {
        const name = newKeyNameInput.value.trim();
        const apiKey = apiKeyInput.value.trim();
        if (!name) return alert("Please enter a name for the key.");
        
        try {
            const response = await fetch("/api/keys", {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-API-Key": apiKey },
                body: JSON.stringify({ name })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Failed to create key.");
            
            generatedKeyEl.textContent = data.key;
            newKeyDisplay.classList.remove("hidden");
            newKeyNameInput.value = "";
            fetchKeys();
        } catch (e) {
            alert(e.message);
        }
    });

    window.revokeKey = async (id) => {
        if (!confirm("Confirm key revocation?")) return;
        const apiKey = apiKeyInput.value.trim();
        try {
            await fetch(`/api/keys/${id}`, {
                method: "DELETE",
                headers: { "X-API-Key": apiKey }
            });
            fetchKeys();
        } catch (e) { console.error(e); }
    };

    copyKeyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(generatedKeyEl.textContent);
        const original = copyKeyBtn.innerHTML;
        copyKeyBtn.textContent = "Copied!";
        setTimeout(() => copyKeyBtn.innerHTML = original, 2000);
    });

    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
});
