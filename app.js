
// Global variables
let drugData = [];
let selectedDrugs = {};
let progress = {
    total_questions: 0,
    total_correct: 0,
    session_history: [],
    drug_performance: {}
};

// Game state
let currentScreen = 'loading-screen';
let matchingState = {
    selectedCards: [],
    matches: [],
    attempts: 0,
    matchCount: 0,
    currentData: []
};

let qaState = {
    questions: [],
    currentIndex: 0,
    sessionCorrect: 0,
    sessionTotal: 0
};

let flashcardState = {
    cards: [],
    currentIndex: 0
};

// Initialize application
async function init() {
    await loadCSVData();
    loadProgress();
    updateProgressDisplay();
    populateDropdowns();
    createDrugSelection();
    showScreen('main-menu');
}

// Screen management
function showScreen(screenId) {
    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    
    // Show target screen
    document.getElementById(screenId).classList.add('active');
    currentScreen = screenId;
    
    // Special handling for certain screens
    if (screenId === 'flashcards') {
        initFlashcards();
    } else if (screenId === 'progress-tracker') {
        updateProgressTracker();
    }
}

// Data loading
async function loadCSVData() {
    try {
        const response = await fetch('TopDrugs.csv');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const csvText = await response.text();
        
        Papa.parse(csvText, {
            header: true,
            skipEmptyLines: true,
            dynamicTyping: false,
            transformHeader: function(header) {
                return header.trim();
            },
            complete: function(results) {
                drugData = results.data.filter(row => {
                    const genericName = row['Generic Name'];
                    return genericName && !genericName.trim().startsWith('#');
                });
                
                // Initialize selected drugs (all selected by default)
                drugData.forEach((drug, index) => {
                    selectedDrugs[index] = true;
                });
                
                console.log(`Loaded ${drugData.length} drugs from CSV`);
            }
        });
    } catch (error) {
        console.error('Error loading CSV:', error);
        document.getElementById('loading-screen').innerHTML = `
            <div class="loading">
                <h2 style="color: #e53e3e;">Error Loading Data</h2>
                <p>Could not load TopDrugs.csv file: ${error.message}</p>
                <p>Please make sure the TopDrugs.csv file is in the same directory.</p>
            </div>
        `;
    }
}

// Progress management
function loadProgress() {
    const saved = localStorage.getItem('drugStudyProgress');
    if (saved) {
        progress = JSON.parse(saved);
    }
}

function saveProgress() {
    localStorage.setItem('drugStudyProgress', JSON.stringify(progress));
}

function updateProgress(sessionCorrect, sessionTotal, mode) {
    progress.total_questions += sessionTotal;
    progress.total_correct += sessionCorrect;
    
    const sessionRecord = {
        date: new Date().toISOString(),
        mode: mode,
        total: sessionTotal,
        correct: sessionCorrect,
        accuracy: (sessionCorrect / Math.max(sessionTotal, 1)) * 100
    };
    
    progress.session_history.push(sessionRecord);
    saveProgress();
    updateProgressDisplay();
}

function updateProgressDisplay() {
    const accuracy = (progress.total_correct / Math.max(progress.total_questions, 1)) * 100;
    document.getElementById('total-questions').textContent = progress.total_questions;
    document.getElementById('total-correct').textContent = progress.total_correct;
    document.getElementById('total-accuracy').textContent = accuracy.toFixed(1) + '%';
    document.getElementById('total-sessions').textContent = progress.session_history.length;
}

function clearAllProgress() {
    if (confirm('⚠️ Clear ALL progress data? This cannot be undone!')) {
        progress = {
            total_questions: 0,
            total_correct: 0,
            session_history: [],
            drug_performance: {}
        };
        saveProgress();
        updateProgressDisplay();
        alert('✅ All progress data cleared.');
        if (currentScreen === 'progress-tracker') {
            updateProgressTracker();
        }
    }
}

// Utility functions
function getSelectedData() {
    return drugData.filter((drug, index) => selectedDrugs[index]);
}

function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

function populateDropdowns() {
    if (drugData.length === 0) return;
    
    const categories = Object.keys(drugData[0]);
    const selects = ['match-category1', 'match-category2'];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Select a category...</option>';
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            select.appendChild(option);
        });
    });
}

// MATCHING GAME FUNCTIONS
function startMatchingGame() {
    const cat1 = document.getElementById('match-category1').value;
    const cat2 = document.getElementById('match-category2').value;
    
    if (!cat1 || !cat2 || cat1 === cat2) {
        alert('Please select two different categories!');
        return;
    }
    
    const selectedData = getSelectedData();
    if (selectedData.length === 0) {
        alert('Please select some drugs to study first!');
        showScreen('drug-selection');
        return;
    }
    
    // Prepare game data
    matchingState.currentData = shuffleArray(selectedData).slice(0, Math.min(10, selectedData.length));
    matchingState.matches = matchingState.currentData.map(drug => [drug[cat1], drug[cat2]]);
    matchingState.selectedCards = [];
    matchingState.attempts = 0;
    matchingState.matchCount = 0;
    
    // Update UI
    document.getElementById('column1-title').textContent = cat1;
    document.getElementById('column2-title').textContent = cat2;
    updateMatchStatus();
    createMatchingCards(cat1, cat2);
    document.getElementById('match-completion').style.display = 'none';
    
    showScreen('matching-game');
}

function createMatchingCards(cat1, cat2) {
    const col1 = document.getElementById('column1-cards');
    const col2 = document.getElementById('column2-cards');
    
    col1.innerHTML = '';
    col2.innerHTML = '';
    
    const values1 = shuffleArray(matchingState.currentData.map(drug => drug[cat1]));
    const values2 = shuffleArray(matchingState.currentData.map(drug => drug[cat2]));
    
    values1.forEach(value => {
        const card = document.createElement('div');
        card.className = 'card';
        card.textContent = value;
        card.dataset.value = value;
        card.dataset.category = cat1;
        card.onclick = () => selectMatchingCard(card);
        col1.appendChild(card);
    });
    
    values2.forEach(value => {
        const card = document.createElement('div');
        card.className = 'card';
        card.textContent = value;
        card.dataset.value = value;
        card.dataset.category = cat2;
        card.onclick = () => selectMatchingCard(card);
        col2.appendChild(card);
    });
}

function selectMatchingCard(card) {
    if (card.classList.contains('matched') || 
        matchingState.selectedCards.includes(card) || 
        matchingState.selectedCards.length >= 2) {
        return;
    }
    
    matchingState.selectedCards.push(card);
    card.classList.add('selected');
    
    if (matchingState.selectedCards.length === 2) {
        matchingState.attempts++;
        updateMatchStatus();
        setTimeout(checkMatchingMatch, 500);
    }
}

function checkMatchingMatch() {
    const [card1, card2] = matchingState.selectedCards;
    const value1 = card1.dataset.value;
    const value2 = card2.dataset.value;
    
    const isMatch = matchingState.matches.some(match => 
        (match[0] === value1 && match[1] === value2) ||
        (match[0] === value2 && match[1] === value1)
    );
    
    if (isMatch) {
        card1.classList.remove('selected');
        card2.classList.remove('selected');
        card1.classList.add('matched');
        card2.classList.add('matched');
        matchingState.matchCount++;
        
        if (matchingState.matchCount === matchingState.matches.length) {
            setTimeout(completeMatchingGame, 500);
        }
    } else {
        card1.classList.add('error');
        card2.classList.add('error');
        
        setTimeout(() => {
            card1.classList.remove('selected', 'error');
            card2.classList.remove('selected', 'error');
        }, 1000);
    }
    
    matchingState.selectedCards = [];
    updateMatchStatus();
}

function updateMatchStatus() {
    document.getElementById('match-status').textContent = 
        `Matches: ${matchingState.matchCount} | Attempts: ${matchingState.attempts}`;
}

function completeMatchingGame() {
    const accuracy = Math.round((matchingState.matchCount / matchingState.attempts) * 100);
    document.getElementById('match-final-score').textContent = 
        `You completed the game in ${matchingState.attempts} attempts with ${accuracy}% accuracy!`;
    document.getElementById('match-completion').style.display = 'block';
    
    updateProgress(matchingState.matchCount, matchingState.attempts, 'matching_game');
}

// Q&A PRACTICE FUNCTIONS
function startQAPractice() {
    const selectedData = getSelectedData();
    if (selectedData.length === 0) {
        alert('Please select some drugs to study first!');
        showScreen('drug-selection');
        return;
    }
    
    qaState.questions = generateQAQuestions(selectedData);
    qaState.currentIndex = 0;
    qaState.sessionCorrect = 0;
    qaState.sessionTotal = 0;
    
    showScreen('qa-practice');
    showQAQuestion();
}

function generateQAQuestions(data) {
    const questions = [];
    const questionTypes = [
        ['Generic Name', 'Brand Name(s)', 'What is the brand name for {}?'],
        ['Brand Name(s)', 'Generic Name', 'What is the generic name for {}?'],
        ['Generic Name', 'Drug Class', 'What drug class does {} belong to?'],
        ['Generic Name', 'Indication', 'What is {} used for?'],
        ['Generic Name', 'Side Effects', 'What are the main side effects of {}?'],
        ['Drug Class', 'Generic Name', 'Name a drug from the {} class:']
    ];
    
    data.forEach((drug, drugIndex) => {
        questionTypes.forEach(([qCol, aCol, template]) => {
            if (drug[qCol] && drug[aCol]) {
                questions.push({
                    question: template.replace('{}', drug[qCol]),
                    answer: drug[aCol],
                    drugIndex: drugIndex,
                    type: `${qCol}_to_${aCol}`
                });
            }
        });
    });
    
    return shuffleArray(questions).slice(0, Math.min(20, questions.length));
}

function showQAQuestion() {
    if (qaState.currentIndex >= qaState.questions.length) {
        endQASession();
        return;
    }
    
    const question = qaState.questions[qaState.currentIndex];
    document.getElementById('qa-question').textContent = question.question;
    document.getElementById('qa-answer').value = '';
    document.getElementById('qa-answer').focus();
    
    updateQAProgress();
}

function updateQAProgress() {
    document.getElementById('qa-progress').textContent = 
        `Question ${qaState.currentIndex + 1} of ${qaState.questions.length} | Score: ${qaState.sessionCorrect}/${qaState.sessionTotal}`;
}

function checkQAAnswer() {
    const question = qaState.questions[qaState.currentIndex];
    const userAnswer = document.getElementById('qa-answer').value.trim().toLowerCase();
    const correctAnswer = question.answer.trim().toLowerCase();
    
    qaState.sessionTotal++;
    
    let isCorrect = false;
    if (userAnswer.includes(correctAnswer) || correctAnswer.includes(userAnswer)) {
        isCorrect = true;
    } else if (userAnswer.length > 3) {
        const userWords = userAnswer.split(/\s+/);
        const correctWords = correctAnswer.split(/\s+/);
        isCorrect = userWords.some(word => 
            word.length > 3 && correctWords.some(cWord => cWord.includes(word))
        );
    }
    
    if (isCorrect) {
        qaState.sessionCorrect++;
        alert(`Correct!\n\nAnswer: ${question.answer}`);
    } else {
        alert(`Incorrect.\n\nCorrect: ${question.answer}\nYours: ${document.getElementById('qa-answer').value}`);
    }
    
    updateDrugPerformance(question.drugIndex, isCorrect);
    nextQAQuestion();
}

function showQAAnswer() {
    const question = qaState.questions[qaState.currentIndex];
    alert(`Answer: ${question.answer}`);
    nextQAQuestion();
}

function skipQAQuestion() {
    nextQAQuestion();
}

function nextQAQuestion() {
    qaState.currentIndex++;
    showQAQuestion();
}

function endQASession() {
    updateProgress(qaState.sessionCorrect, qaState.sessionTotal, 'qa_practice');
    
    const accuracy = (qaState.sessionCorrect / Math.max(qaState.sessionTotal, 1)) * 100;
    const performance = accuracy >= 90 ? 'Outstanding!' : 
                        accuracy >= 75 ? 'Great job!' : 
                        accuracy >= 60 ? 'Good progress!' : 'Keep practicing!';
    
    alert(`Session Complete!\n\nQuestions: ${qaState.sessionTotal}\nCorrect: ${qaState.sessionCorrect}\nAccuracy: ${accuracy.toFixed(1)}%\n\n${performance}`);
    
    showScreen('main-menu');
}

function updateDrugPerformance(drugIndex, isCorrect) {
    if (!progress.drug_performance[drugIndex]) {
        progress.drug_performance[drugIndex] = { correct: 0, total: 0 };
    }
    progress.drug_performance[drugIndex].total++;
    if (isCorrect) {
        progress.drug_performance[drugIndex].correct++;
    }
}

// FLASHCARD FUNCTIONS
function initFlashcards() {
    const selectedData = getSelectedData();
    if (selectedData.length === 0) {
        alert('Please select some drugs to study first!');
        showScreen('drug-selection');
        return;
    }
    
    flashcardState.cards = shuffleArray(selectedData);
    flashcardState.currentIndex = 0;
    showFlashcard();
}

function showFlashcard() {
    if (flashcardState.currentIndex >= flashcardState.cards.length) {
        alert('You have reviewed all selected drugs! Great job!');
        showScreen('main-menu');
        return;
    }
    
    const drug = flashcardState.cards[flashcardState.currentIndex];
    document.getElementById('flashcard-progress').textContent = 
        `Card ${flashcardState.currentIndex + 1} of ${flashcardState.cards.length}`;
    
    document.getElementById('flashcard-drug-name').textContent = 
        drug['Generic Name'] || 'Drug Information';
    
    const sections = [
        ['🏷️ Generic Name', drug['Generic Name']],
        ['🏪 Brand Name(s)', drug['Brand Name(s)']],
        ['🧪 Drug Class', drug['Drug Class']],
        ['💊 Dosage Forms', drug['Dosage Forms']],
        ['🎯 Indication', drug['Indication']],
        ['⚠️ Side Effects', drug['Side Effects']],
        ['💡 Clinical Pearls', drug['Clinical Pearls']]
    ];
    
    let content = '';
    sections.forEach(([label, value]) => {
        if (value && value !== 'N/A') {
            content += `
                <div class="drug-info-section">
                    <div class="drug-info-label">${label}</div>
                    <div class="drug-info-content">${value}</div>
                </div>
            `;
        }
    });
    
    document.getElementById('flashcard-content').innerHTML = content;
}

function nextFlashcard() {
    flashcardState.currentIndex++;
    showFlashcard();
}

function previousFlashcard() {
    if (flashcardState.currentIndex > 0) {
        flashcardState.currentIndex--;
        showFlashcard();
    }
}

function shuffleFlashcards() {
    flashcardState.cards = shuffleArray(flashcardState.cards);
    flashcardState.currentIndex = 0;
    alert('Cards shuffled! Starting over.');
    showFlashcard();
}

// PROGRESS TRACKER FUNCTIONS
function updateProgressTracker() {
    const container = document.getElementById('progress-content');
    
    let content = `
        <div style="background: #f7fafc; padding: 25px; border-radius: 12px; margin: 20px 0;">
            <h3>📊 Overall Statistics</h3>
            <div class="progress-stats">
                <div class="stat-item">
                    <span class="stat-value">${progress.total_questions}</span>
                    <span class="stat-label">Questions</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${progress.total_correct}</span>
                    <span class="stat-label">Correct</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${((progress.total_correct / Math.max(progress.total_questions, 1)) * 100).toFixed(1)}%</span>
                    <span class="stat-label">Accuracy</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${progress.session_history.length}</span>
                    <span class="stat-label">Sessions</span>
                </div>
            </div>
        </div>
    `;
    
    if (progress.session_history.length > 0) {
        content += `
            <div style="margin: 20px 0;">
                <h3>🕒 Recent Sessions</h3>
                <table class="progress-table">
                    <tr>
                        <th>Date</th>
                        <th>Mode</th>
                        <th>Questions</th>
                        <th>Correct</th>
                        <th>Accuracy</th>
                    </tr>
        `;
        
        const recentSessions = progress.session_history.slice(-15).reverse();
        recentSessions.forEach(session => {
            const date = new Date(session.date).toLocaleDateString();
            const mode = session.mode.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
            content += `
                <tr>
                    <td>${date}</td>
                    <td>${mode}</td>
                    <td>${session.total}</td>
                    <td>${session.correct}</td>
                    <td>${session.accuracy.toFixed(1)}%</td>
                </tr>
            `;
        });
        
        content += `
                </table>
            </div>
        `;
    }
    
    container.innerHTML = content;
}

// DRUG SELECTION FUNCTIONS
function createDrugSelection() {
    const container = document.getElementById('drug-selection-content');
    
    const sections = {
        "Cardiovascular HTN (1-10)": [0, 10],
        "Cardiovascular Other (11-20)": [10, 20],
        "Diabetes (21-30)": [20, 30],
        "Antibiotics (31-41)": [30, 41],
        "Pain Management (42-52)": [41, 52],
        "Psychiatry Dep/Anx (53-63)": [52, 63],
        "Elderly Care (64-84)": [63, 84],
        "Pulmonary (85-94)": [84, 94],
        "Women's Health (95-106)": [94, 106],
        "Psych/Neuro (107-124)": [106, 124]
    };
    
    let content = '';
    
    Object.entries(sections).forEach(([sectionName, [start, end]]) => {
        const sectionDrugs = drugData.slice(start, Math.min(end, drugData.length));
        if (sectionDrugs.length === 0) return;
        
        content += `
            <div class="drug-section">
                <div class="section-header">
                    <input type="checkbox" id="section-${start}" onchange="toggleSection(${start}, ${Math.min(end, drugData.length)})" checked>
                    <label for="section-${start}">${sectionName} (${sectionDrugs.length} drugs)</label>
                </div>
        `;
        
        sectionDrugs.forEach((drug, index) => {
            const globalIndex = start + index;
            const drugText = `${drug['Generic Name']} (${drug['Brand Name(s)'] || 'N/A'})`;
            content += `
                <div class="drug-checkbox">
                    <input type="checkbox" id="drug-${globalIndex}" ${selectedDrugs[globalIndex] ? 'checked' : ''} onchange="updateDrugSelection(${globalIndex})">
                    <label for="drug-${globalIndex}">${drugText.substring(0, 60)}${drugText.length > 60 ? '...' : ''}</label>
                </div>
            `;
        });
        
        content += `</div>`;
    });
    
    container.innerHTML = content;
    updateSectionCheckboxes();
}

function toggleSection(start, end) {
    const sectionCheckbox = document.getElementById(`section-${start}`);
    const isChecked = sectionCheckbox.checked;
    
    for (let i = start; i < end && i < drugData.length; i++) {
        selectedDrugs[i] = isChecked;
        const drugCheckbox = document.getElementById(`drug-${i}`);
        if (drugCheckbox) {
            drugCheckbox.checked = isChecked;
        }
    }
}

function updateDrugSelection(index) {
    const checkbox = document.getElementById(`drug-${index}`);
    selectedDrugs[index] = checkbox.checked;
    updateSectionCheckboxes();
}

function updateSectionCheckboxes() {
    const sections = [
        [0, 10], [10, 20], [20, 30], [30, 41], [41, 52],
        [52, 63], [63, 84], [84, 94], [94, 106], [106, 124]
    ];
    
    sections.forEach(([start, end]) => {
        const sectionCheckbox = document.getElementById(`section-${start}`);
        if (!sectionCheckbox) return;
        
        let allChecked = true;
        for (let i = start; i < end && i < drugData.length; i++) {
            if (!selectedDrugs[i]) {
                allChecked = false;
                break;
            }
        }
        sectionCheckbox.checked = allChecked;
    });
}

function selectAllDrugs() {
    drugData.forEach((_, index) => {
        selectedDrugs[index] = true;
    });
    createDrugSelection();
}

function deselectAllDrugs() {
    drugData.forEach((_, index) => {
        selectedDrugs[index] = false;
    });
    createDrugSelection();
}

function resetDrugSelection() {
    selectAllDrugs();
}

function saveDrugSelection() {
    const selectedCount = Object.values(selectedDrugs).filter(Boolean).length;
    alert(`Selection saved! ${selectedCount} drugs selected.`);
    showScreen('main-menu');
}

// Initialize app when page loads
window.onload = init;
