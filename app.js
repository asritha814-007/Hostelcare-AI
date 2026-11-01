/**
 * HostelCare AI — Main Application Controller
 * Handles Navigation, Real NLP Chatbot, Complaint Lifecycle,
 * Guide Knowledge Retrieval, and Admin Operations.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Session state
    const sessionId = 'session_' + Math.random().toString(36).substring(2, 10);
    let adminToken = sessionStorage.getItem('hostelcare_admin_token') || null;

    // Doctor Avatar States
    const doctorStates = {
        normal: 'assets/doctor_normal.png',
        concerned: 'assets/doctor_concerned.png',
        urgent: 'assets/doctor_urgent.png'
    };

    // Verified Safety Tips Data (Replacing flower photo with actionable health content)
    const safetyTips = [
        {
            category: "Drinking Water Safety",
            headline: "Stay Hydrated with Clean RO Water",
            paragraph: "Drink at least 2.5–3 liters of verified filtered water daily. Inspect the dispenser maintenance tag and never consume discolored or foul-tasting water."
        },
        {
            category: "Mess Food Hygiene",
            headline: "Inspect Mess Meals & Utensil Sanitation",
            paragraph: "Always wash hands with soap before mess meals. Avoid unwashed raw foods and report any foreign matter or greasy dining plates immediately."
        },
        {
            category: "Electrical & Fire Safety",
            headline: "Inspect Sockets & Avoid Overloaded Power Strips",
            paragraph: "Never daisy-chain multiple high-wattage appliances into room adapters. Turn off the main breaker switch if you observe sparks or smell burning plastic."
        },
        {
            category: "Heat & Dehydration Prevention",
            headline: "Electrolyte Replenishment in Warm Weather",
            paragraph: "Keep an ORS packet in your room kit. Severe headaches and sudden dizziness are frequently caused by electrolyte depletion during intense study hours."
        },
        {
            category: "First Aid & Sprains",
            headline: "Remember R.I.C.E. for Physical Injuries",
            paragraph: "For sudden ankle sprains or sports injuries, follow Rest, Ice (15–20 min), Compression with crepe bandage, and Elevation above heart level."
        }
    ];
    let currentTipIndex = 0;

    // DOM Elements
    const doctorImg = document.getElementById('doctor-img');
    const chatStatusLabel = document.getElementById('chat-status-label');
    const chatOnlineDot = document.getElementById('chat-online-dot');
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const chatForm = document.getElementById('chat-form');
    const chatResetBtn = document.getElementById('chat-reset-btn');
    const suggestionsScroll = document.getElementById('suggestions-scroll');

    // Sidebar & Mobile toggles
    const sidebar = document.getElementById('sidebar');
    const menuToggleBtn = document.getElementById('menu-toggle-btn');
    const sidebarCloseBtn = document.getElementById('sidebar-close-btn');
    const mobileChatBtn = document.getElementById('mobile-chat-btn');
    const chatbotPanel = document.getElementById('chatbot-panel');
    const chatCloseMobileBtn = document.getElementById('chat-close-mobile-btn');

    // Date display
    const currentDateText = document.getElementById('current-date-text');

    // Quick Action Cards
    const actionAssistantCard = document.getElementById('action-assistant-card');
    const actionEmergencyCard = document.getElementById('action-emergency-card');
    const actionReportCard = document.getElementById('action-report-card');
    const actionGuideCard = document.getElementById('action-guide-card');

    // Tips Elements
    const tipCategoryLabel = document.getElementById('tip-category-label');
    const tipHeadline = document.getElementById('tip-headline');
    const tipParagraph = document.getElementById('tip-paragraph');
    const tipIndexLabel = document.getElementById('tip-index-label');
    const tipPrevBtn = document.getElementById('tip-prev-btn');
    const tipNextBtn = document.getElementById('tip-next-btn');
    const viewGuideBtn = document.getElementById('view-guide-btn');

    // Modals
    const reportModal = document.getElementById('report-modal');
    const trackModal = document.getElementById('track-modal');
    const guideModal = document.getElementById('guide-modal');
    const adminModal = document.getElementById('admin-modal');

    // Modal Triggers
    const openReportFormBtn = document.getElementById('open-report-form-btn');
    const bannerReportBtn = document.getElementById('banner-report-btn');
    const bannerContactsBtn = document.getElementById('banner-contacts-btn');
    const trackModalBtn = document.getElementById('track-modal-btn');
    const refreshStatsBtn = document.getElementById('refresh-stats-btn');

    // Modal Close Buttons
    const closeReportModalBtn = document.getElementById('close-report-modal-btn');
    const cancelReportBtn = document.getElementById('cancel-report-btn');
    const closeTrackModalBtn = document.getElementById('close-track-modal-btn');
    const cancelTrackBtn = document.getElementById('cancel-track-btn');
    const closeGuideModalBtn = document.getElementById('close-guide-modal-btn');
    const closeAdminModalBtn = document.getElementById('close-admin-modal-btn');

    // Forms
    const complaintForm = document.getElementById('complaint-form');
    const complaintCategory = document.getElementById('complaint-category');
    const complaintDescription = document.getElementById('complaint-description');
    const complaintLocation = document.getElementById('complaint-location');
    const complaintStudentName = document.getElementById('complaint-student-name');
    const complaintStudentContact = document.getElementById('complaint-student-contact');
    const complaintErrorBox = document.getElementById('complaint-error-box');
    const complaintSuccessScreen = document.getElementById('complaint-success-screen');
    const finishReportBtn = document.getElementById('finish-report-btn');

    const trackForm = document.getElementById('track-form');
    const trackComplaintId = document.getElementById('track-complaint-id');
    const trackPin = document.getElementById('track-pin');
    const trackErrorBox = document.getElementById('track-error-box');
    const trackResultCard = document.getElementById('track-result-card');

    // Admin Elements
    const adminLoginForm = document.getElementById('admin-login-form');
    const adminUserInput = document.getElementById('admin-user-input');
    const adminPassInput = document.getElementById('admin-pass-input');
    const adminLoginError = document.getElementById('admin-login-error');
    const adminLoginView = document.getElementById('admin-login-view');
    const adminControlView = document.getElementById('admin-control-view');
    const adminTableBody = document.getElementById('admin-table-body');
    const adminLogoutBtn = document.getElementById('admin-logout-btn');
    const adminFilterCategory = document.getElementById('admin-filter-category');
    const adminFilterStatus = document.getElementById('admin-filter-status');
    const adminSearchInput = document.getElementById('admin-search-input');
    const adminRefreshBtn = document.getElementById('admin-refresh-btn');

    // Guide Elements
    const guideSearchInput = document.getElementById('guide-search-input');
    const guideCategoryTabs = document.getElementById('guide-category-tabs');
    const guideArticlesList = document.getElementById('guide-articles-list');
    let allGuideArticles = [];
    let currentGuideCategory = 'all';

    // =========================================================================
    // 1. Initial Setup & Dynamic Date
    // =========================================================================
    function initDate() {
        const now = new Date();
        const options = { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' };
        if (currentDateText) {
            currentDateText.textContent = now.toLocaleDateString('en-US', options);
        }
    }
    initDate();

    // =========================================================================
    // 2. Health & Safety Tips Carousel Logic
    // =========================================================================
    function updateTipCard(index) {
        const tip = safetyTips[index];
        if (!tip) return;
        tipCategoryLabel.textContent = tip.category;
        tipHeadline.textContent = tip.headline;
        tipParagraph.textContent = tip.paragraph;
        tipIndexLabel.textContent = `Tip ${index + 1} of ${safetyTips.length}`;
    }

    if (tipPrevBtn && tipNextBtn) {
        tipPrevBtn.addEventListener('click', () => {
            currentTipIndex = (currentTipIndex - 1 + safetyTips.length) % safetyTips.length;
            updateTipCard(currentTipIndex);
        });
        tipNextBtn.addEventListener('click', () => {
            currentTipIndex = (currentTipIndex + 1) % safetyTips.length;
            updateTipCard(currentTipIndex);
        });
    }

    // =========================================================================
    // 3. Live Metrics & Complaints Table Data Fetching
    // =========================================================================
    async function loadStats() {
        try {
            const res = await fetch('/api/stats');
            const json = await res.json();
            if (json.success && json.data) {
                document.getElementById('stat-resources').textContent = json.data.health_resources_count || 17;
                document.getElementById('stat-pending').textContent = json.data.pending_complaints || 0;
                document.getElementById('stat-resolved').textContent = json.data.resolved_complaints || 0;
                document.getElementById('stat-safety').textContent = json.data.open_safety_reports || 0;
            }
        } catch (e) {
            console.error('Failed to load stats:', e);
        }
    }

    async function loadRecentComplaints() {
        const tbody = document.getElementById('complaints-table-body');
        try {
            const res = await fetch('/api/complaints/recent?limit=6');
            const json = await res.json();
            if (json.success && Array.isArray(json.data) && json.data.length > 0) {
                tbody.innerHTML = '';
                json.data.forEach(item => {
                    const tr = document.createElement('tr');
                    const statusClass = 'status-' + (item.status || 'submitted').toLowerCase().replace(/\s+/g, '');
                    tr.innerHTML = `
                        <td><span class="table-id-badge">${escapeHtml(item.id)}</span></td>
                        <td><strong>${escapeHtml(item.category)}</strong></td>
                        <td>${escapeHtml(item.location || 'Not specified')}</td>
                        <td><span class="status-pill ${statusClass}">${escapeHtml(item.status)}</span></td>
                        <td>${escapeHtml(item.created_at || 'Recently')}</td>
                        <td><button class="table-action-btn track-row-btn" data-id="${escapeHtml(item.id)}">Track</button></td>
                    `;
                    tbody.appendChild(tr);
                });

                // Attach track click handler to row buttons
                document.querySelectorAll('.track-row-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const id = e.target.getAttribute('data-id');
                        trackComplaintId.value = id;
                        trackPin.value = '';
                        openModal(trackModal);
                        trackComplaintStatus(id, null);
                    });
                });
            } else {
                tbody.innerHTML = `<tr><td colspan="6" class="table-loading-cell">No complaints on record. All facilities operating normally.</td></tr>`;
            }
        } catch (e) {
            console.error('Failed to load recent complaints:', e);
            tbody.innerHTML = `<tr><td colspan="6" class="table-loading-cell">Unable to load complaints preview.</td></tr>`;
        }
    }

    if (refreshStatsBtn) {
        refreshStatsBtn.addEventListener('click', () => {
            loadStats();
            loadRecentComplaints();
        });
    }

    // Initial fetch
    loadStats();
    loadRecentComplaints();

    // =========================================================================
    // 4. Modal Open & Close Utility
    // =========================================================================
    function openModal(modal) {
        if (!modal) return;
        modal.classList.add('show');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeModal(modal) {
        if (!modal) return;
        modal.classList.remove('show');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    // Modal listeners
    if (openReportFormBtn) openReportFormBtn.addEventListener('click', () => openModal(reportModal));
    if (bannerReportBtn) bannerReportBtn.addEventListener('click', () => openModal(reportModal));
    if (closeReportModalBtn) closeReportModalBtn.addEventListener('click', () => closeModal(reportModal));
    if (cancelReportBtn) cancelReportBtn.addEventListener('click', () => closeModal(reportModal));

    if (trackModalBtn) trackModalBtn.addEventListener('click', () => openModal(trackModal));
    if (closeTrackModalBtn) closeTrackModalBtn.addEventListener('click', () => closeModal(trackModal));
    if (cancelTrackBtn) cancelTrackBtn.addEventListener('click', () => closeModal(trackModal));

    if (viewGuideBtn) viewGuideBtn.addEventListener('click', () => { openModal(guideModal); loadGuideArticles(); });
    if (closeGuideModalBtn) closeGuideModalBtn.addEventListener('click', () => closeModal(guideModal));

    if (closeAdminModalBtn) closeAdminModalBtn.addEventListener('click', () => closeModal(adminModal));

    if (bannerContactsBtn) {
        bannerContactsBtn.addEventListener('click', () => {
            const section = document.getElementById('emergency-section');
            if (section) section.scrollIntoView({ behavior: 'smooth' });
        });
    }

    // Close on backdrop click
    [reportModal, trackModal, guideModal, adminModal].forEach(modal => {
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) closeModal(modal);
            });
        }
    });

    // =========================================================================
    // 5. Sidebar Navigation Handling
    // =========================================================================
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            const section = link.getAttribute('data-section');

            // Close mobile sidebar if open
            sidebar.classList.remove('open');

            if (section === 'dashboard') {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else if (section === 'assistant') {
                focusChatbot();
            } else if (section === 'emergency') {
                const el = document.getElementById('emergency-section');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
            } else if (section === 'report') {
                openModal(reportModal);
            } else if (section === 'complaints') {
                const el = document.getElementById('complaints-preview-section');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
            } else if (section === 'guide') {
                openModal(guideModal);
                loadGuideArticles();
            } else if (section === 'admin') {
                openAdminPortal();
            }
        });
    });

    // Mobile drawers
    if (menuToggleBtn) {
        menuToggleBtn.addEventListener('click', () => sidebar.classList.add('open'));
    }
    if (sidebarCloseBtn) {
        sidebarCloseBtn.addEventListener('click', () => sidebar.classList.remove('open'));
    }
    if (mobileChatBtn) {
        mobileChatBtn.addEventListener('click', () => {
            chatbotPanel.classList.add('open');
            userInput.focus();
        });
    }
    if (chatCloseMobileBtn) {
        chatCloseMobileBtn.addEventListener('click', () => chatbotPanel.classList.remove('open'));
    }

    function focusChatbot() {
        if (window.innerWidth <= 992) {
            chatbotPanel.classList.add('open');
        }
        userInput.focus();
        userInput.classList.add('pulse-focus');
        setTimeout(() => userInput.classList.remove('pulse-focus'), 1000);
    }

    // Quick Action Card handlers
    if (actionAssistantCard) actionAssistantCard.addEventListener('click', focusChatbot);
    if (actionEmergencyCard) {
        actionEmergencyCard.addEventListener('click', () => {
            document.getElementById('emergency-section').scrollIntoView({ behavior: 'smooth' });
        });
    }
    if (actionReportCard) actionReportCard.addEventListener('click', () => openModal(reportModal));
    if (actionGuideCard) {
        actionGuideCard.addEventListener('click', () => {
            openModal(guideModal);
            loadGuideArticles();
        });
    }

    // =========================================================================
    // 6. Real NLP Chatbot Workflow
    // =========================================================================
    function setDoctorAvatar(state) {
        doctorImg.style.opacity = '0.5';
        doctorImg.style.transform = 'scale(0.9)';
        setTimeout(() => {
            doctorImg.src = doctorStates[state] || doctorStates.normal;
            doctorImg.style.opacity = '1';
            doctorImg.style.transform = 'scale(1)';

            if (state === 'urgent') {
                chatOnlineDot.className = 'status-indicator-dot urgent';
                chatStatusLabel.textContent = 'Emergency Alert';
                chatStatusLabel.style.color = 'var(--critical-danger)';
            } else if (state === 'concerned') {
                chatOnlineDot.className = 'status-indicator-dot busy';
                chatStatusLabel.textContent = 'Assessment Active';
                chatStatusLabel.style.color = 'var(--warning)';
            } else {
                chatOnlineDot.className = 'status-indicator-dot online';
                chatStatusLabel.textContent = 'Online & Ready';
                chatStatusLabel.style.color = 'var(--success)';
            }
        }, 150);
    }

    function addMessage(text, isUser = false, isUrgent = false, actions = []) {
        const row = document.createElement('div');
        row.className = `message-row ${isUser ? 'user-row' : 'bot-row'}`;

        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${isUser ? 'user-bubble' : 'bot-bubble'} ${isUrgent ? 'urgent-bubble' : ''}`;

        // Simple markdown line formatting
        const formattedHtml = formatChatText(text);
        bubble.innerHTML = formattedHtml;

        // Render Action Buttons if provided
        if (Array.isArray(actions) && actions.length > 0) {
            const actionsWrap = document.createElement('div');
            actionsWrap.className = 'message-actions-wrap';

            actions.forEach(action => {
                const btn = document.createElement('button');
                btn.className = `bubble-action-btn ${action.urgent ? 'urgent-action' : ''}`;
                btn.innerHTML = `<span>${escapeHtml(action.label)}</span>`;

                btn.addEventListener('click', () => {
                    if (action.url) {
                        window.location.href = action.url;
                    } else if (action.action === 'open_complaint') {
                        if (action.category) complaintCategory.value = action.category;
                        openModal(reportModal);
                    } else if (action.action === 'open_complaints_tab') {
                        openModal(trackModal);
                    } else if (action.action === 'clinic_info') {
                        openModal(guideModal);
                        loadGuideArticles('Common Symptoms');
                    }
                });

                actionsWrap.appendChild(btn);
            });

            bubble.appendChild(actionsWrap);
        }

        row.appendChild(bubble);
        chatMessages.appendChild(row);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'chat-typing-indicator';
        typingDiv.innerHTML = `
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('chat-typing-indicator');
        if (indicator) indicator.remove();
    }

    function updateQuickReplies(replies) {
        if (!Array.isArray(replies) || replies.length === 0) return;
        suggestionsScroll.innerHTML = '';
        replies.forEach(reply => {
            const btn = document.createElement('button');
            btn.className = 'chip-btn';
            btn.textContent = reply;
            btn.setAttribute('data-query', reply);
            btn.addEventListener('click', () => {
                userInput.value = reply;
                handleChatSend();
            });
            suggestionsScroll.appendChild(btn);
        });
    }

    async function handleChatSend() {
        const text = userInput.value.trim();
        if (!text) return;

        // User message bubble
        addMessage(text, true);
        userInput.value = '';

        // Show typing indicator
        showTypingIndicator();

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, session_id: sessionId })
            });

            const json = await res.json();
            removeTypingIndicator();

            if (json.success && json.data) {
                const data = json.data;
                setDoctorAvatar(data.doctor_state || 'normal');
                addMessage(data.response, false, data.is_urgent, data.suggested_actions);
                if (data.quick_replies) {
                    updateQuickReplies(data.quick_replies);
                }
            } else {
                setDoctorAvatar('normal');
                addMessage("I apologize, but I could not process your query at this moment. For urgent help, please call 108.", false);
            }
        } catch (e) {
            removeTypingIndicator();
            setDoctorAvatar('normal');
            addMessage("Network communication error. Please check your connection or contact emergency services directly.", false);
        }
    }

    if (sendBtn) sendBtn.addEventListener('click', handleChatSend);
    if (chatForm) chatForm.addEventListener('submit', (e) => { e.preventDefault(); handleChatSend(); });

    // Suggestion chips click listeners
    document.querySelectorAll('.chip-btn').forEach(chip => {
        chip.addEventListener('click', () => {
            const q = chip.getAttribute('data-query');
            if (q) {
                userInput.value = q;
                handleChatSend();
            }
        });
    });

    // Reset Chat Button
    if (chatResetBtn) {
        chatResetBtn.addEventListener('click', async () => {
            try {
                await fetch('/api/chat/reset', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: sessionId })
                });
            } catch (e) {}

            chatMessages.innerHTML = `
                <div class="message-row bot-row">
                    <div class="message-bubble bot-bubble">
                        <p>Hello! I am your <strong>HostelCare Virtual Health & Safety Assistant</strong>. Conversation reset. How can I help you today?</p>
                        <p class="bubble-sub">You can describe your symptoms, ask about first aid, or report a facility issue.</p>
                    </div>
                </div>
            `;
            setDoctorAvatar('normal');
        });
    }

    // =========================================================================
    // 7. Complaint Management (Submission & PIN Tracking)
    // =========================================================================
    if (complaintForm) {
        complaintForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            complaintErrorBox.style.display = 'none';

            const payload = {
                category: complaintCategory.value,
                description: complaintDescription.value.trim(),
                location: complaintLocation.value.trim(),
                student_name: complaintStudentName.value.trim(),
                student_contact: complaintStudentContact.value.trim()
            };

            const submitBtn = document.getElementById('submit-complaint-btn');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span>Registering...</span>';

            try {
                const res = await fetch('/api/complaints', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const json = await res.json();
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<span>Submit Official Complaint</span>';

                if (json.success && json.data) {
                    // Show confirmation screen
                    complaintForm.style.display = 'none';
                    complaintSuccessScreen.style.display = 'block';
                    document.getElementById('success-complaint-id').textContent = json.data.id;
                    document.getElementById('success-tracking-pin').textContent = json.data.tracking_pin;

                    // Refresh stats and preview table
                    loadStats();
                    loadRecentComplaints();
                } else {
                    complaintErrorBox.textContent = json.error || 'Failed to submit complaint.';
                    complaintErrorBox.style.display = 'block';
                }
            } catch (err) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<span>Submit Official Complaint</span>';
                complaintErrorBox.textContent = 'Server connection error. Please try again.';
                complaintErrorBox.style.display = 'block';
            }
        });
    }

    if (finishReportBtn) {
        finishReportBtn.addEventListener('click', () => {
            complaintForm.reset();
            complaintForm.style.display = 'flex';
            complaintSuccessScreen.style.display = 'none';
            closeModal(reportModal);
        });
    }

    // Track Form
    if (trackForm) {
        trackForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const id = trackComplaintId.value.trim();
            const pin = trackPin.value.trim();
            trackComplaintStatus(id, pin);
        });
    }

    async function trackComplaintStatus(id, pin) {
        trackErrorBox.style.display = 'none';
        trackResultCard.style.display = 'none';

        if (!id) {
            trackErrorBox.textContent = 'Please provide a valid Complaint ID.';
            trackErrorBox.style.display = 'block';
            return;
        }

        try {
            let url = `/api/complaints/track?id=${encodeURIComponent(id)}`;
            if (pin) url += `&pin=${encodeURIComponent(pin)}`;

            const res = await fetch(url);
            const json = await res.json();

            if (json.success && json.data) {
                const d = json.data;
                document.getElementById('res-complaint-id').textContent = d.id;
                document.getElementById('res-category').textContent = d.category;
                document.getElementById('res-location').textContent = d.location || 'Not specified';
                document.getElementById('res-date').textContent = d.created_at || 'Recently';
                document.getElementById('res-description').textContent = d.description || 'Description protected with PIN.';
                document.getElementById('res-admin-notes').textContent = d.admin_notes || 'Awaiting administrator review.';

                const pill = document.getElementById('res-status-pill');
                pill.textContent = d.status;
                pill.className = 'status-pill status-' + (d.status || 'submitted').toLowerCase().replace(/\s+/g, '');

                trackResultCard.style.display = 'block';
            } else {
                trackErrorBox.textContent = json.error || 'No matching complaint found.';
                trackErrorBox.style.display = 'block';
            }
        } catch (e) {
            trackErrorBox.textContent = 'Connection error looking up status.';
            trackErrorBox.style.display = 'block';
        }
    }

    // =========================================================================
    // 8. Health & Safety Guide Knowledge Base
    // =========================================================================
    async function loadGuideArticles(initialCategory = 'all') {
        currentGuideCategory = initialCategory;
        try {
            const res = await fetch('/api/guide');
            const json = await res.json();
            if (json.success && Array.isArray(json.articles)) {
                allGuideArticles = json.articles;
                renderGuideArticles();
            }
        } catch (e) {
            guideArticlesList.innerHTML = '<p class="table-loading-cell">Failed to load safety guides.</p>';
        }
    }

    function renderGuideArticles() {
        const query = (guideSearchInput ? guideSearchInput.value : '').toLowerCase().trim();
        let filtered = allGuideArticles;

        if (currentGuideCategory !== 'all') {
            filtered = filtered.filter(a => a.category === currentGuideCategory);
        }

        if (query) {
            filtered = filtered.filter(a => 
                (a.question && a.question.toLowerCase().includes(query)) ||
                (a.answer && a.answer.toLowerCase().includes(query)) ||
                (a.keywords && a.keywords.some(k => k.toLowerCase().includes(query)))
            );
        }

        if (filtered.length === 0) {
            guideArticlesList.innerHTML = '<p class="table-loading-cell">No matching guide articles found for this search.</p>';
            return;
        }

        guideArticlesList.innerHTML = '';
        filtered.forEach(art => {
            const card = document.createElement('div');
            card.className = 'guide-article-card';
            card.innerHTML = `
                <div class="article-header-row">
                    <span class="article-category-badge">${escapeHtml(art.category)}</span>
                </div>
                <h4 class="article-question">${escapeHtml(art.question)}</h4>
                <p class="article-answer">${escapeHtml(art.answer)}</p>
            `;
            guideArticlesList.appendChild(card);
        });
    }

    if (guideSearchInput) {
        guideSearchInput.addEventListener('input', renderGuideArticles);
    }

    if (guideCategoryTabs) {
        guideCategoryTabs.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                guideCategoryTabs.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentGuideCategory = btn.getAttribute('data-cat') || 'all';
                renderGuideArticles();
            });
        });
    }

    // =========================================================================
    // 9. Administrator Dashboard Operations
    // =========================================================================
    function openAdminPortal() {
        openModal(adminModal);
        if (adminToken) {
            showAdminDashboard();
        } else {
            showAdminLogin();
        }
    }

    function showAdminLogin() {
        adminLoginView.style.display = 'block';
        adminControlView.style.display = 'none';
    }

    function showAdminDashboard() {
        adminLoginView.style.display = 'none';
        adminControlView.style.display = 'block';
        loadAdminComplaints();
    }

    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            adminLoginError.style.display = 'none';

            const username = adminUserInput.value.trim();
            const password = adminPassInput.value.trim();

            try {
                const res = await fetch('/api/admin/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const json = await res.json();
                if (json.success && json.token) {
                    adminToken = json.token;
                    sessionStorage.setItem('hostelcare_admin_token', adminToken);
                    showAdminDashboard();
                } else {
                    adminLoginError.textContent = json.error || 'Authentication failed.';
                    adminLoginError.style.display = 'block';
                }
            } catch (err) {
                adminLoginError.textContent = 'Server connection error.';
                adminLoginError.style.display = 'block';
            }
        });
    }

    if (adminLogoutBtn) {
        adminLogoutBtn.addEventListener('click', () => {
            adminToken = null;
            sessionStorage.removeItem('hostelcare_admin_token');
            showAdminLogin();
        });
    }

    async function loadAdminComplaints() {
        if (!adminToken) return;
        const category = adminFilterCategory.value;
        const status = adminFilterStatus.value;
        const search = adminSearchInput.value.trim();

        let url = `/api/admin/complaints?limit=100`;
        if (category && category !== 'all') url += `&category=${encodeURIComponent(category)}`;
        if (status && status !== 'all') url += `&status=${encodeURIComponent(status)}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;

        adminTableBody.innerHTML = '<tr><td colspan="6" class="table-loading-cell">Loading admin records...</td></tr>';

        try {
            const res = await fetch(url, {
                headers: { 'Authorization': `Bearer ${adminToken}` }
            });
            const json = await res.json();

            if (res.status === 401) {
                adminToken = null;
                sessionStorage.removeItem('hostelcare_admin_token');
                showAdminLogin();
                return;
            }

            if (json.success && Array.isArray(json.data) && json.data.length > 0) {
                adminTableBody.innerHTML = '';
                json.data.forEach(item => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${escapeHtml(item.id)}</strong></td>
                        <td>${escapeHtml(item.category)}</td>
                        <td>
                            <div>${escapeHtml(item.description)}</div>
                            <small class="form-hint">📍 ${escapeHtml(item.location || 'N/A')}</small>
                        </td>
                        <td>
                            <div>${escapeHtml(item.student_name || 'Anonymous')}</div>
                            <small class="form-hint">${escapeHtml(item.student_contact || '')}</small>
                        </td>
                        <td>
                            <select class="admin-status-select" id="select-status-${item.id}">
                                <option value="Submitted" ${item.status === 'Submitted' ? 'selected' : ''}>Submitted</option>
                                <option value="In Progress" ${item.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                                <option value="Resolved" ${item.status === 'Resolved' ? 'selected' : ''}>Resolved</option>
                                <option value="Rejected" ${item.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
                            </select>
                        </td>
                        <td>
                            <input type="text" class="admin-note-input" id="note-${item.id}" placeholder="Resolution note..." value="${escapeHtml(item.admin_notes || '')}">
                            <button class="save-status-btn" data-id="${item.id}">Save</button>
                        </td>
                    `;
                    adminTableBody.appendChild(tr);
                });

                // Attach Save button listeners
                adminTableBody.querySelectorAll('.save-status-btn').forEach(btn => {
                    btn.addEventListener('click', async (e) => {
                        const id = e.target.getAttribute('data-id');
                        const statusSelect = document.getElementById(`select-status-${id}`);
                        const noteInput = document.getElementById(`note-${id}`);
                        await updateAdminStatus(id, statusSelect.value, noteInput.value);
                    });
                });
            } else {
                adminTableBody.innerHTML = '<tr><td colspan="6" class="table-loading-cell">No matching complaints found.</td></tr>';
            }
        } catch (e) {
            adminTableBody.innerHTML = '<tr><td colspan="6" class="table-loading-cell">Error loading complaints.</td></tr>';
        }
    }

    async function updateAdminStatus(id, status, notes) {
        try {
            const res = await fetch(`/api/admin/complaints/${id}/status`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${adminToken}`
                },
                body: JSON.stringify({ status, admin_notes: notes })
            });
            const json = await res.json();
            if (json.success) {
                loadAdminComplaints();
                loadStats();
                loadRecentComplaints();
            } else {
                alert('Status update failed: ' + (json.error || 'Unknown error'));
            }
        } catch (e) {
            alert('Error updating complaint status.');
        }
    }

    if (adminFilterCategory) adminFilterCategory.addEventListener('change', loadAdminComplaints);
    if (adminFilterStatus) adminFilterStatus.addEventListener('change', loadAdminComplaints);
    if (adminSearchInput) adminSearchInput.addEventListener('input', debounce(loadAdminComplaints, 300));
    if (adminRefreshBtn) adminRefreshBtn.addEventListener('click', loadAdminComplaints);

    // =========================================================================
    // Helpers
    // =========================================================================
    function escapeHtml(text) {
        if (!text) return '';
        const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }

    function formatChatText(text) {
        if (!text) return '';
        let escaped = escapeHtml(text);
        // Replace bullet points
        escaped = escaped.replace(/• (.*?)(?=(\n|$))/g, '<li style="margin-left: 1.2rem;">$1</li>');
        // Replace bold asterisks
        escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Replace newlines with <br>
        escaped = escaped.replace(/\n/g, '<br>');
        return `<p>${escaped}</p>`;
    }

    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
});
