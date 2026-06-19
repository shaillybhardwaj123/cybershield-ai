/* ==========================================================================
   CYBERSHIELD AI - INTERACTIVE CONTROLLER WITH DRIBBBLE-STYLE EFFECTS
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // ----------------------------------------------------
    // SPA Screens Router (Landing -> Login -> Dashboard)
    // ----------------------------------------------------
    const screenLanding = document.getElementById("screen-landing");
    const screenLogin = document.getElementById("screen-login");
    const screenApp = document.getElementById("screen-app");

    function navigateScreen(targetId) {
        document.querySelectorAll(".view-screen").forEach(s => {
            s.classList.remove("active");
        });
        const targetScreen = document.getElementById(targetId);
        if (targetScreen) {
            targetScreen.classList.add("active");
        }
        
        // Recalculate node map lines if entering dashboard results tab
        if (targetId === "screen-app") {
            setTimeout(updateNodeConnections, 150);
        }
    }

    // Landing screen triggers
    document.getElementById("landing-goto-login-btn").addEventListener("click", () => {
        navigateScreen("screen-login");
    });
    
    document.getElementById("landing-start-btn").addEventListener("click", () => {
        navigateScreen("screen-login");
    });

    document.getElementById("landing-learn-btn").addEventListener("click", () => {
        const featuresSec = document.getElementById("landing-features");
        if (featuresSec) {
            featuresSec.scrollIntoView({ behavior: "smooth" });
        }
    });

    // Login screen back trigger
    document.getElementById("login-brand-back").addEventListener("click", () => {
        navigateScreen("screen-landing");
    });

    // Home navigation triggers from brand logo
    const homeBrands = ["landing-brand-home", "sidebar-brand-home"];
    homeBrands.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("click", () => {
                navigateScreen("screen-landing");
            });
        }
    });

    // Login Submit flow
    const loginForm = document.getElementById("login-form-el");
    const loginSubmitBtn = document.getElementById("login-submit-btn");
    const loginBtnText = loginSubmitBtn.querySelector(".btn-text");
    const loginLoaderText = loginSubmitBtn.querySelector(".btn-loader-text");

    loginForm.addEventListener("submit", (e) => {
        e.preventDefault();
        
        loginSubmitBtn.disabled = true;
        loginBtnText.classList.add("hidden");
        loginLoaderText.classList.remove("hidden");

        // Simulate session setup and key verification
        setTimeout(() => {
            loginSubmitBtn.disabled = false;
            loginBtnText.classList.remove("hidden");
            loginLoaderText.classList.add("hidden");
            navigateScreen("screen-app");
        }, 1200);
    });

    // Guest entry trigger
    document.getElementById("login-guest-btn").addEventListener("click", () => {
        navigateScreen("screen-app");
    });

    // Logout trigger
    document.getElementById("nav-logout-btn").addEventListener("click", () => {
        navigateScreen("screen-landing");
    });

    // ----------------------------------------------------
    // Theme Toggling Logic (Dark / Light Mode)
    // ----------------------------------------------------
    function toggleTheme() {
        const isLight = document.documentElement.classList.toggle("light-mode");
        localStorage.setItem("theme", isLight ? "light" : "dark");
        
        const toggleLandingIcon = document.querySelector("#theme-toggle-landing i");
        const toggleDashboardIcon = document.querySelector("#theme-toggle-dashboard i");
        
        if (toggleLandingIcon) {
            toggleLandingIcon.className = isLight ? "fa-solid fa-sun" : "fa-solid fa-moon";
        }
        if (toggleDashboardIcon) {
            toggleDashboardIcon.className = isLight ? "fa-solid fa-sun" : "fa-solid fa-moon";
        }
        
        // Re-render agent connectors to adjust contrast lines
        setTimeout(updateNodeConnections, 120);
    }

    const btnLanding = document.getElementById("theme-toggle-landing");
    const btnDashboard = document.getElementById("theme-toggle-dashboard");
    
    if (btnLanding) btnLanding.addEventListener("click", toggleTheme);
    if (btnDashboard) btnDashboard.addEventListener("click", toggleTheme);

    // Initial theme check
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "light") {
        document.documentElement.classList.add("light-mode");
        if (btnLanding) btnLanding.querySelector("i").className = "fa-solid fa-sun";
        if (btnDashboard) btnDashboard.querySelector("i").className = "fa-solid fa-sun";
    }

    // ----------------------------------------------------
    // Citizen Incident Desk Triggers (cybercrime.gov.in style)
    // ----------------------------------------------------
    const citizenButtons = [
        "btn-sec-women",
        "btn-sec-finance",
        "btn-sec-phish",
        "btn-sec-general",
        "landing-helpline-cta-btn"
    ];

    citizenButtons.forEach(btnId => {
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.addEventListener("click", () => {
                navigateScreen("screen-login");
            });
        }
    });

    // ----------------------------------------------------
    // State Variables & Config
    // ----------------------------------------------------
    let currentUploadedFilePath = null;
    let currentUploadedFileName = null;
    let selectedCaseIdForTrace = null;
    const API_BASE = "";

    const tabHeaders = {
        "scanner": { title: "Check if something looks suspicious", desc: "Stay Safe Online" },
        "results": { title: "Safety Review Details", desc: "How we verified this content for scams" },
        "history": { title: "Safety History", desc: "Recent Safety Checks" },
        "analytics": { title: "Community Safety Trends", desc: "Scam vectors and threat indicators currently reported" },
        "education": { title: "Safety Hub", desc: "Learn to spot scam patterns and build safe habits" }
    };

    const quickDemos = [
        {
            text: "🚀 GOOGLE INTERNSHIP OFFER 🚀\nLocation: Work from Home\nStipend: ₹45,000 / Month\nDuration: 3 Months\nNo qualifications required! Students from any stream can apply.\nRegistration fee: ₹499 (Refundable)\nContact HR on Telegram: @GoogleIndiaRecruit\nClick to register: https://google-internship-registration.cc/apply",
            url: "https://google-internship-registration.cc/apply",
            fileName: "whatsapp_internship.png",
            type: "job"
        },
        {
            text: "NATIONAL MERIT SCHOLARSHIP DRIVE 2026\nApply now to get ₹1,50,000 yearly scholarship.\nSupported by Ministry of Student Welfare.\nTo claim your scholarship, deposit a processing fee of ₹1,200 immediately to account: 4433-2211-0987.\nDeadline: TODAY.\nOfficial Link: http://national-welfare-portal.net/verify",
            url: "http://national-welfare-portal.net/verify",
            fileName: "scholarship_scam.pdf",
            type: "message"
        },
        {
            text: "Dear Customer,\nYour State Bank of India account has been flagged for suspicious activity.\nPlease verify your NetBanking credentials immediately or your account will be BLOCKED within 24 hours.\nClick here to verify: https://sbi-verification-secure.com/login.html\nThank you,\nSBI Security Team",
            url: "https://sbi-verification-secure.com/login.html",
            fileName: "verification_email.png",
            type: "link"
        }
    ];

    const placeholders = {
        "message": "Paste the SMS, WhatsApp message, or chat conversation you want to check here...",
        "link": "Paste the suspicious link or web URL you want us to review here...",
        "job": "Paste the recruiting email description, job posting, or placement text here...",
        "screenshot": "Type a summary description of the image/screenshot or simply upload the file below..."
    };

    // ----------------------------------------------------
    // Dribbble Interaction: Mouse Spotlight Glow
    // ----------------------------------------------------
    const selectorCards = document.querySelectorAll(".selector-card");
    selectorCards.forEach(card => {
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty("--mouse-x", x);
            card.style.setProperty("--mouse-y", y);
        });
    });

    // ----------------------------------------------------
    // Navigation & Tab Sliding Transition
    // ----------------------------------------------------
    const navButtons = document.querySelectorAll(".nav-btn");
    const tabContents = document.querySelectorAll(".tab-content");
    const pageTitle = document.getElementById("page-title");
    const pageDesc = document.getElementById("page-desc");

    function switchTab(tabId) {
        navButtons.forEach(btn => btn.classList.remove("active"));
        
        // Tab contents transition
        tabContents.forEach(content => {
            content.classList.remove("active");
        });

        const activeBtn = document.querySelector(`.nav-btn[data-tab="${tabId}"]`);
        const activeContent = document.getElementById(`tab-${tabId}`);
        
        if (activeBtn) activeBtn.classList.add("active");
        if (activeContent) {
            activeContent.classList.add("active");
        }

        if (tabHeaders[tabId]) {
            pageTitle.textContent = tabHeaders[tabId].title;
            pageDesc.textContent = tabHeaders[tabId].desc;
        }

        if (tabId === "history") {
            loadSafetyHistory();
        } else if (tabId === "analytics") {
            loadAnalytics();
        }

        // SVG lines recalculation
        if (tabId === "results") {
            setTimeout(updateNodeConnections, 120);
        }
    }

    navButtons.forEach(button => {
        button.addEventListener("click", () => {
            const tabId = button.getAttribute("data-tab");
            switchTab(tabId);
        });
    });

    // ----------------------------------------------------
    // Input Category Selector Logic
    // ----------------------------------------------------
    const scanTextInput = document.getElementById("scan-text");
    const uploadCardWrapper = document.getElementById("upload-card-wrapper");

    selectorCards.forEach(card => {
        card.addEventListener("click", () => {
            selectorCards.forEach(c => c.classList.remove("active"));
            card.classList.add("active");

            const type = card.getAttribute("data-type");
            scanTextInput.placeholder = placeholders[type] || placeholders["message"];
            
            if (type === "screenshot") {
                uploadCardWrapper.style.border = "1px solid var(--color-secondary)";
            } else {
                uploadCardWrapper.style.border = "none";
            }
        });
    });

    // Pill actions
    const examplePills = document.querySelectorAll(".example-pill");
    examplePills.forEach(pill => {
        pill.addEventListener("click", () => {
            const idx = parseInt(pill.getAttribute("data-index"));
            loadDemoCaseData(idx);
        });
    });

    // Load Demo button in header
    let currentDemoIdx = 0;
    const loadDemoBtn = document.getElementById("load-demo-btn");
    loadDemoBtn.addEventListener("click", () => {
        loadDemoCaseData(currentDemoIdx);
        currentDemoIdx = (currentDemoIdx + 1) % quickDemos.length;
    });

    function loadDemoCaseData(index) {
        const demo = quickDemos[index];
        scanTextInput.value = demo.text;
        document.getElementById("scan-url").value = demo.url;
        
        selectorCards.forEach(c => {
            if (c.getAttribute("data-type") === demo.type) {
                c.click();
            }
        });

        selectedFileName.textContent = demo.fileName;
        selectedFileBadge.style.display = "inline-flex";
        currentUploadedFileName = demo.fileName;
        currentUploadedFilePath = demo.fileName;

        document.querySelector(".char-count").textContent = `${demo.text.length} / 5000 characters`;
    }

    scanTextInput.addEventListener("input", () => {
        document.querySelector(".char-count").textContent = `${scanTextInput.value.length} / 5000 characters`;
    });

    // ----------------------------------------------------
    // Screenshot Upload
    // ----------------------------------------------------
    const dropzone = document.getElementById("file-dropzone");
    const fileInput = document.getElementById("scan-file");
    const selectedFileBadge = document.getElementById("selected-file-badge");
    const selectedFileName = document.getElementById("selected-file-name");
    const removeFileBtn = document.getElementById("remove-file-btn");

    dropzone.addEventListener("click", (e) => {
        if (e.target !== removeFileBtn && !removeFileBtn.contains(e.target)) {
            fileInput.click();
        }
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            uploadLocalFile(fileInput.files[0]);
        }
    });

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            uploadLocalFile(e.dataTransfer.files[0]);
        }
    });

    async function uploadLocalFile(file) {
        selectedFileName.textContent = file.name;
        selectedFileBadge.style.display = "inline-flex";
        currentUploadedFileName = file.name;

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch(`${API_BASE}/api/upload`, {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            if (data.status === "success") {
                currentUploadedFilePath = data.file_path;
            }
        } catch (err) {
            console.error(err);
            alert("File upload failed.");
        }
    }

    removeFileBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        fileInput.value = "";
        selectedFileBadge.style.display = "none";
        selectedFileName.textContent = "None";
        currentUploadedFilePath = null;
        currentUploadedFileName = null;
    });

    // ----------------------------------------------------
    // Run Scan Execution
    // ----------------------------------------------------
    const startScanBtn = document.getElementById("start-scan-btn");
    const scanBtnText = startScanBtn.querySelector(".btn-text");
    const scanBtnLoader = startScanBtn.querySelector(".btn-loader");
    const scannerCard = document.querySelector(".scanner-card");

    startScanBtn.addEventListener("click", async () => {
        const text = scanTextInput.value;
        const url = document.getElementById("scan-url").value;
        const deepScan = document.getElementById("scan-mode").checked;
        
        let combinedText = text;
        if (url.trim() !== "") {
            combinedText += `\n[Reference URL]: ${url}`;
        }

        if (!combinedText.trim() && !currentUploadedFilePath) {
            alert("Please paste text, input a URL, or attach a file first.");
            return;
        }

        // Add Dribbble scanning radar beam overlay
        scannerCard.classList.add("scanning");
        startScanBtn.disabled = true;
        scanBtnText.classList.add("hidden");
        scanBtnLoader.classList.remove("hidden");

        // Set companion orb to scanning state
        const orb = document.getElementById("shield-companion-orb");
        if (orb) {
            orb.className = "shield-companion-orb scanning";
        }

        const formData = new FormData();
        formData.append("text", combinedText);
        if (currentUploadedFilePath) {
            formData.append("filePath", currentUploadedFilePath);
        }
        formData.append("mode", deepScan ? "deep" : "quick");

        try {
            const res = await fetch(`${API_BASE}/api/scan`, {
                method: "POST",
                body: formData
            });
            
            if (!res.ok) {
                throw new Error("Safety check failed.");
            }
            
            const caseData = await res.json();
            
            // Switch to results tab immediately to watch pipeline run in real-time
            document.getElementById("nav-results-btn").removeAttribute("disabled");
            switchTab("results");
            
            // Run live node pipeline simulation and then map variables
            runVisualScanAnimation(caseData.risk_score, caseData.verdict, () => {
                displayFriendlyVerdict(caseData);
                scannerCard.classList.remove("scanning");
            });

        } catch (err) {
            console.error("Scan error:", err);
            scannerCard.classList.remove("scanning");
            if (orb) {
                orb.className = "shield-companion-orb";
            }
            alert("Safety review request encountered an issue.");
        } finally {
            startScanBtn.disabled = false;
            scanBtnText.classList.remove("hidden");
            scanBtnLoader.classList.add("hidden");
        }
    });

    // ----------------------------------------------------
    // Render Friendly Verdict & Gauge Animation
    // ----------------------------------------------------
    function displayFriendlyVerdict(caseData) {
        const score = caseData.risk_score;
        const verdict = caseData.verdict;
        const scamType = caseData.scam_type;
        const explanation = caseData.explanation;
        const evidence = caseData.evidence;
        const nextSteps = caseData.next_steps;
        const safeReply = caseData.safe_reply;
        const reportSummary = caseData.report_summary;

        // 1. Gauge arc animation (circumference = 263.8)
        document.getElementById("verdict-score-value").textContent = score;
        const circle = document.getElementById("verdict-gauge");
        const offset = 263.8 - (263.8 * score) / 100;
        circle.style.strokeDashoffset = offset;

        // 2. Verdict Banner Cards Styling
        const banner = document.getElementById("verdict-card");
        banner.className = "verdict-banner-card"; // reset
        const vClass = verdict.toLowerCase().replace(" ", "_");
        banner.classList.add(vClass);

        let badgeLabel = "✅ Looks Safe";
        let friendlyTitle = "This content appears safe!";
        if (verdict === "DANGEROUS") {
            badgeLabel = "⛔ Dangerous";
            friendlyTitle = "Stay away. This looks dangerous";
        } else if (verdict === "HIGH RISK") {
            badgeLabel = "🚨 Likely Scam";
            friendlyTitle = "Be careful with this offer";
        } else if (verdict === "SUSPICIOUS") {
            badgeLabel = "⚠ Be Careful";
            friendlyTitle = "Some indicators look unusual";
        }

        document.getElementById("verdict-badge-val").textContent = badgeLabel;
        document.getElementById("scam-type-badge-val").textContent = scamType;
        document.getElementById("verdict-title-val").textContent = friendlyTitle;

        // 3. Explanation body
        document.getElementById("verdict-friendly-explanation").textContent = explanation;

        // 4. Evidence list populate
        const evidenceContainer = document.getElementById("evidence-list-container");
        evidenceContainer.innerHTML = "";
        evidence.forEach(item => {
            const div = document.createElement("div");
            div.className = "friendly-evidence-item";
            div.innerHTML = `<strong>📍 Signal:</strong> ${item}`;
            evidenceContainer.appendChild(div);
        });

        // 5. Next steps checklist populate
        const stepsContainer = document.getElementById("next-steps-container");
        stepsContainer.innerHTML = "";
        nextSteps.forEach(step => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fa-solid fa-circle-check" style="color: var(--color-safe)"></i> <span>${step}</span>`;
            stepsContainer.appendChild(li);
        });

        // 6. Safe reply templates populate
        const replySec = document.getElementById("safe-reply-section");
        if (safeReply && safeReply.trim() !== "") {
            document.getElementById("reply-template-text").textContent = safeReply;
            replySec.style.display = "block";
        } else {
            replySec.style.display = "none";
        }

        // 7. Visual checkers summary
        document.getElementById("agent-msg-summary").textContent = "Inspected urgency metrics, caps, and reward pressure patterns.";
        document.getElementById("agent-url-summary").textContent = "Checked shortened link domains and typosquatting base names.";
        document.getElementById("agent-job-summary").textContent = "Validated placement cell rules and candidate fee requests.";
        document.getElementById("agent-intel-summary").textContent = "Looked up known scam databases and verified flags.";

        // 8. Markdown report
        document.getElementById("report-md-container").textContent = reportSummary;
        
        selectedCaseIdForTrace = caseData.id;

        // Update companion orb
        const orb = document.getElementById("shield-companion-orb");
        if (orb) {
            orb.className = "shield-companion-orb";
            orb.classList.add(vClass);
        }
    }

    // Collapsible drawer toggle
    const colHeader = document.getElementById("toggle-tech-details");
    const colBody = document.getElementById("tech-details-body");
    colHeader.addEventListener("click", () => {
        colBody.classList.toggle("hidden");
        const icon = colHeader.querySelector(".toggle-icon");
        icon.classList.toggle("fa-chevron-down");
        icon.classList.toggle("fa-chevron-up");
    });

    // Copy clipboards
    document.getElementById("copy-reply-btn").addEventListener("click", () => {
        const txt = document.getElementById("reply-template-text").textContent;
        navigator.clipboard.writeText(txt);
        alert("Safe Reply copied to clipboard.");
    });

    document.getElementById("copy-report-btn").addEventListener("click", () => {
        const txt = document.getElementById("report-md-container").textContent;
        navigator.clipboard.writeText(txt);
        alert("Markdown Report copied.");
    });

    document.getElementById("print-report-btn").addEventListener("click", () => {
        window.print();
    });

    // ----------------------------------------------------
    // Load Safety History (Cases Timeline Cards)
    // ----------------------------------------------------
    async function loadSafetyHistory() {
        try {
            const res = await fetch(`${API_BASE}/api/cases`);
            const cases = await res.json();
            renderSafetyTimelineCards(cases);
        } catch (err) {
            console.error("Error loading safety history:", err);
        }
    }

    function renderSafetyTimelineCards(cases) {
        const container = document.getElementById("history-cards-container");
        container.innerHTML = "";

        if (cases.length === 0) {
            container.innerHTML = `<p class="placeholder-text">No safety checks logged yet. Perform a scan above!</p>`;
            return;
        }

        cases.forEach(c => {
            const card = document.createElement("div");
            card.className = "history-card-item";

            const dateStr = new Date(c.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const snippet = c.input_text.substring(0, 50) + (c.input_text.length > 50 ? "..." : "");
            
            const vLabel = c.verdict.toLowerCase().replace(" ", "_");
            let badgeLabel = "✅ Looks Safe";
            if (c.verdict === "DANGEROUS") badgeLabel = "⛔ Dangerous";
            else if (c.verdict === "HIGH RISK") badgeLabel = "🚨 Likely Scam";
            else if (c.verdict === "SUSPICIOUS") badgeLabel = "⚠ Be Careful";

            card.innerHTML = `
                <span class="history-card-id"><strong>${c.id}</strong></span>
                <span class="history-card-date">${dateStr}</span>
                <span class="history-card-category">${c.scam_type}</span>
                <span class="history-card-snippet" title="${c.input_text}">${snippet}</span>
                <span class="history-card-score">Score: <strong>${c.risk_score}/100</strong></span>
                <div><span class="verdict-lbl ${vLabel}">${badgeLabel}</span></div>
                <div><a class="view-case-link" data-id="${c.id}">View Review</a></div>
            `;

            card.querySelector(".view-case-link").addEventListener("click", () => {
                displayFriendlyVerdict(c);
                switchTab("results");
            });

            container.appendChild(card);
        });
    }

    const historySearch = document.getElementById("history-search");
    historySearch.addEventListener("input", async () => {
        const val = historySearch.value.toLowerCase().trim();
        try {
            const res = await fetch(`${API_BASE}/api/cases`);
            const cases = await res.json();
            const filtered = cases.filter(c => 
                c.id.toLowerCase().includes(val) ||
                c.input_text.toLowerCase().includes(val) ||
                c.scam_type.toLowerCase().includes(val) ||
                c.verdict.toLowerCase().includes(val)
            );
            renderSafetyTimelineCards(filtered);
        } catch (err) {
            console.error(err);
        }
    });

    // ----------------------------------------------------
    // Load Community Safety Trends
    // ----------------------------------------------------
    async function loadAnalytics() {
        try {
            const res = await fetch(`${API_BASE}/api/analytics`);
            const data = await res.json();

            document.getElementById("stat-total-scans").textContent = data.total_scans;
            document.getElementById("stat-avg-latency").textContent = `${data.avg_latency_ms}ms`;
            document.getElementById("stat-tool-calls").textContent = data.total_tool_calls;

            let dangerCount = 0;
            let total = data.total_scans;
            if (data.verdicts) {
                dangerCount += (data.verdicts["HIGH RISK"] || 0);
                dangerCount += (data.verdicts["DANGEROUS"] || 0);
            }
            const ratio = total > 0 ? Math.round((dangerCount / total) * 100) : 0;
            document.getElementById("stat-risk-percent").textContent = `${ratio}%`;

            const verdictChart = document.getElementById("verdict-bar-chart");
            verdictChart.innerHTML = "";
            const vKeys = ["SAFE", "SUSPICIOUS", "HIGH RISK", "DANGEROUS"];
            
            vKeys.forEach(k => {
                const count = data.verdicts[k] || 0;
                const percent = total > 0 ? (count / total) * 100 : 0;
                const vClass = k.toLowerCase().replace(" ", "_");
                
                let friendlyName = "✅ Looks Safe";
                if (k === "DANGEROUS") friendlyName = "⛔ Dangerous";
                else if (k === "HIGH RISK") friendlyName = "🚨 Likely Scam";
                else if (k === "SUSPICIOUS") friendlyName = "⚠ Be Careful";

                const row = document.createElement("div");
                row.className = "bar-row";
                row.innerHTML = `
                    <span class="bar-label">${friendlyName}</span>
                    <div class="bar-track">
                        <div class="bar-fill ${vClass}" style="width: ${percent}%"></div>
                    </div>
                    <span class="bar-count">${count}</span>
                `;
                verdictChart.appendChild(row);
            });

            const scamChart = document.getElementById("scam-type-chart");
            scamChart.innerHTML = "";
            const sCounts = Object.entries(data.scam_types);
            
            if (sCounts.length === 0) {
                scamChart.innerHTML = `<p class="placeholder-text">No logs found yet.</p>`;
            } else {
                const maxCount = Math.max(...sCounts.map(item => item[1]));
                sCounts.forEach(([type, count]) => {
                    const pct = maxCount > 0 ? (count / maxCount) * 100 : 0;
                    const row = document.createElement("div");
                    row.className = "bar-row";
                    row.innerHTML = `
                        <span class="bar-label">${type}</span>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: ${pct}%; background-color: var(--color-primary)"></div>
                        </div>
                        <span class="bar-count">${count}</span>
                    `;
                    scamChart.appendChild(row);
                });
            }

            const intelBody = document.getElementById("intel-table-body");
            intelBody.innerHTML = "";
            if (data.top_threats.length === 0) {
                intelBody.innerHTML = `<tr><td colspan="5" class="placeholder-text">No threat intelligence loaded. Database is empty.</td></tr>`;
            } else {
                data.top_threats.forEach(t => {
                    const tr = document.createElement("tr");
                    const dateStr = new Date(t.last_seen).toLocaleDateString();
                    const vClass = t.verdict.toLowerCase().replace(" ", "_");
                    
                    let badgeLabel = "✅ Safe";
                    if (t.verdict === "DANGEROUS") badgeLabel = "⛔ Dangerous";
                    else if (t.verdict === "HIGH RISK") badgeLabel = "🚨 Likely Scam";
                    else if (t.verdict === "SUSPICIOUS") badgeLabel = "⚠ Be Careful";

                    let icon = "fa-globe";
                    if (t.entity_type === "phone") icon = "fa-phone";
                    else if (t.entity_type === "email") icon = "fa-envelope";
                    else if (t.entity_type === "url") icon = "fa-link";

                    tr.innerHTML = `
                        <td><span class="intel-type-icon"><i class="fa-solid ${icon}"></i></span> ${t.entity_type.toUpperCase()}</td>
                        <td><code>${t.entity_value}</code></td>
                        <td><span class="verdict-lbl ${vClass}">${badgeLabel}</span></td>
                        <td><strong>${t.times_seen}</strong> checks</td>
                        <td>${dateStr}</td>
                    `;
                    intelBody.appendChild(tr);
                });
            }

        } catch (err) {
            console.error(err);
        }
    }

    // ----------------------------------------------------
    // Quiz Card
    // ----------------------------------------------------
    const quizButtons = document.querySelectorAll(".quiz-opt-btn");
    const quizFeedback = document.querySelector(".quiz-feedback");

    quizButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            quizButtons.forEach(b => b.classList.remove("correct-clicked", "wrong-clicked"));

            const isCorrect = btn.classList.contains("correct");
            quizFeedback.classList.remove("hidden", "success", "fail");

            if (isCorrect) {
                btn.classList.add("correct-clicked");
                quizFeedback.classList.add("success");
                quizFeedback.innerHTML = `<strong>✨ Correct!</strong> Job offers requiring advance payments for any reason are scam metrics. Amazon and other legitimate employers never charge recruitment fees.`;
            } else {
                btn.classList.add("wrong-clicked");
                quizFeedback.classList.add("fail");
                quizFeedback.innerHTML = `<strong>❌ Incorrect.</strong> Never pay money upfront to get hired. The safe choice is to ignore and block the scam contact immediately.`;
            }
        });
    });

    // ----------------------------------------------------
    // Initialize Drag & Drop, Node Maps & Evals on load
    // ----------------------------------------------------
    initDraggableCards();
    initNodeDragging();
    setTimeout(updateNodeConnections, 150);
    window.addEventListener("resize", updateNodeConnections);

    // ----------------------------------------------------
    // Custom Visual Helpers & Draggable State Functions
    // ----------------------------------------------------
    let draggedCard = null;

    function initDraggableCards() {
        const cards = document.querySelectorAll(".draggable-card");
        cards.forEach(card => {
            card.addEventListener("dragstart", (e) => {
                draggedCard = card;
                card.classList.add("dragging");
                e.dataTransfer.effectAllowed = "move";
            });
            card.addEventListener("dragend", () => {
                draggedCard = null;
                card.classList.remove("dragging");
                setTimeout(updateNodeConnections, 80);
            });
            card.addEventListener("dragover", (e) => {
                e.preventDefault();
            });
            card.addEventListener("drop", (e) => {
                e.preventDefault();
                if (draggedCard && draggedCard !== card) {
                    const parent = card.parentNode;
                    if (parent === draggedCard.parentNode) {
                        const children = Array.from(parent.children);
                        const idxCard = children.indexOf(card);
                        const idxDragged = children.indexOf(draggedCard);
                        if (idxCard > idxDragged) {
                            parent.insertBefore(draggedCard, card.nextSibling);
                        } else {
                            parent.insertBefore(draggedCard, card);
                        }
                    }
                }
            });
        });
    }

    function updateNodeConnections() {
        const container = document.getElementById("node-map-container");
        if (!container) return;
        
        const svg = document.getElementById("svg-connections-layer");
        if (!svg) return;
        
        const rect = container.getBoundingClientRect();
        
        const connections = [
            { from: "input", to: "orchestrator" },
            { from: "orchestrator", to: "message" },
            { from: "orchestrator", to: "link" },
            { from: "orchestrator", to: "job" },
            { from: "orchestrator", to: "attachment" },
            { from: "orchestrator", to: "intel" },
            { from: "message", to: "responder" },
            { from: "link", to: "responder" },
            { from: "job", to: "responder" },
            { from: "attachment", to: "responder" },
            { from: "intel", to: "responder" },
            { from: "responder", to: "archiver" }
        ];
        
        svg.innerHTML = "";
        
        connections.forEach(conn => {
            const fromEl = document.getElementById(`node-${conn.from}`);
            const toEl = document.getElementById(`node-${conn.to}`);
            
            if (fromEl && toEl) {
                const x1 = fromEl.offsetLeft + fromEl.offsetWidth / 2;
                const y1 = fromEl.offsetTop + fromEl.offsetHeight / 2;
                const x2 = toEl.offsetLeft + toEl.offsetWidth / 2;
                const y2 = toEl.offsetTop + toEl.offsetHeight / 2;
                
                const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
                const dx = Math.abs(x2 - x1) * 0.45;
                const d = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
                
                path.setAttribute("d", d);
                path.setAttribute("class", "connection-line");
                svg.appendChild(path);
            }
        });
    }

    function initNodeDragging() {
        const container = document.getElementById("node-map-container");
        if (!container) return;
        
        const nodes = container.querySelectorAll(".node-item");
        nodes.forEach(node => {
            node.addEventListener("mousedown", (e) => {
                if (e.target.closest("button") || e.target.closest("a")) return;
                
                e.preventDefault();
                const rect = container.getBoundingClientRect();
                
                function onMouseMove(moveEvent) {
                    const x = moveEvent.clientX - rect.left - 35;
                    const y = moveEvent.clientY - rect.top - 35;
                    
                    const clampedX = Math.max(5, Math.min(x, rect.width - 75));
                    const clampedY = Math.max(5, Math.min(y, rect.height - 75));
                    
                    node.style.left = `${(clampedX / rect.width) * 100}%`;
                    node.style.top = `${(clampedY / rect.height) * 100}%`;
                    
                    updateNodeConnections();
                }
                
                function onMouseUp() {
                    window.removeEventListener("mousemove", onMouseMove);
                    window.removeEventListener("mouseup", onMouseUp);
                }
                
                window.addEventListener("mousemove", onMouseMove);
                window.addEventListener("mouseup", onMouseUp);
            });
        });
    }

    function runVisualScanAnimation(score, verdict, callback) {
        const map = document.getElementById("node-map-container");
        if (!map) {
            if (callback) callback();
            return;
        }
        
        map.querySelectorAll(".node-item").forEach(n => {
            n.className = "node-item";
            if (n.id === "node-input") n.classList.add("node-center");
            else if (n.id === "node-orchestrator") n.classList.add("node-supervisor");
            else if (n.id === "node-responder" || n.id === "node-archiver") n.classList.add("node-outbound");
            else n.classList.add("node-agent");
        });
        
        document.getElementById("badge-node-msg").textContent = "-";
        document.getElementById("badge-node-url").textContent = "-";
        document.getElementById("badge-node-job").textContent = "-";
        document.getElementById("badge-node-ocr").textContent = "-";
        document.getElementById("badge-node-intel").textContent = "-";
        
        map.classList.add("animating");
        
        setTimeout(() => {
            document.getElementById("node-input").classList.add("suspicious");
            document.getElementById("node-orchestrator").classList.add("suspicious");
            
            setTimeout(() => {
                document.getElementById("node-message").classList.add("suspicious");
                document.getElementById("node-link").classList.add("suspicious");
                document.getElementById("node-job").classList.add("suspicious");
                document.getElementById("node-attachment").classList.add("suspicious");
                document.getElementById("node-intel").classList.add("suspicious");
                
                setTimeout(() => {
                    const vClass = verdict.toLowerCase().replace(" ", "_");
                    
                    document.getElementById("node-message").classList.add(vClass);
                    document.getElementById("badge-node-msg").textContent = score;
                    
                    document.getElementById("node-link").classList.add(vClass);
                    document.getElementById("badge-node-url").textContent = score > 10 ? "Scanned" : "Clean";
                    
                    document.getElementById("node-job").classList.add(vClass);
                    document.getElementById("badge-node-job").textContent = "Audited";
                    
                    document.getElementById("node-attachment").classList.add(vClass);
                    document.getElementById("badge-node-ocr").textContent = "Scanned";
                    
                    document.getElementById("node-intel").classList.add(vClass);
                    document.getElementById("badge-node-intel").textContent = "Matched";
                    
                    setTimeout(() => {
                        document.getElementById("node-responder").classList.add(vClass);
                        
                        setTimeout(() => {
                            document.getElementById("node-archiver").classList.add("safe");
                            map.classList.remove("animating");
                            if (callback) callback();
                        }, 300);
                    }, 300);
                }, 800);
            }, 400);
        }, 200);
    }

    const evalCases = [
        {
            text: "🚀 GOOGLE INTERNSHIP OFFER 🚀\nLocation: Work from Home\nStipend: ₹45,000 / Month\nDuration: 3 Months\nNo qualifications required! Students from any stream can apply.\nRegistration fee: ₹499 (Refundable)\nContact HR on Telegram: @GoogleIndiaRecruit\nClick to register: https://google-internship-registration.cc/apply",
            expected: "HIGH RISK"
        },
        {
            text: "Dear Customer,\nYour State Bank of India account has been flagged for suspicious activity.\nPlease verify your NetBanking credentials immediately or your account will be BLOCKED within 24 hours.\nClick here to verify: https://sbi-verification-secure.com/login.html\nThank you,\nSBI Security Team",
            expected: "DANGEROUS"
        },
        {
            text: "NATIONAL MERIT SCHOLARSHIP DRIVE 2026\nApply now to get ₹1,50,000 yearly scholarship.\nSupported by Ministry of Student Welfare.\nTo claim your scholarship, deposit a processing fee of ₹1,200 immediately to account: 4433-2211-0987.\nDeadline: TODAY.\nOfficial Link: http://national-welfare-portal.net/verify",
            expected: "HIGH RISK"
        },
        {
            text: "Hey, are we still meeting at the college library at 4 PM for the project discussion? I brought the reference books for the Kaggle Capstone project.",
            expected: "SAFE"
        },
        {
            text: "Earn ₹5000 daily by liking YouTube videos from home! No experience required, flexible hours. Daily payouts in crypto or UPI. Contact Telegram: @LikesRecruiterNow",
            expected: "HIGH RISK"
        },
        {
            text: "Official notice from the Dean's Office: The campus placement registration portal is open. Register with your university credentials at https://placements.university.edu/register before next Friday.",
            expected: "SAFE"
        },
        {
            text: "Your DHL parcel is held at the sorting office due to an unpaid duty of ₹180. Pay the fee to dispatch your package: http://dhl-package-fees.cc",
            expected: "HIGH RISK"
        },
        {
            text: "Get a government laptop now! All students enrolled in technical courses are eligible. Fill the form at: http://free-laptop-scheme-gov.cc",
            expected: "SUSPICIOUS"
        }
    ];
});
