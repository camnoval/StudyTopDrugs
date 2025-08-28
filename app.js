
        // Drug data structure
        let drugData = [];
        
        // Game state
        let selectedCards = [];
        let matches = [];
        let attempts = 0;
        let matchCount = 0;
        let currentData = [];
        
        // Initialize the app
        function init() {
            showLoadingMessage();
            loadCSVData();
        }
        
        function showLoadingMessage() {
            const setupPanel = document.getElementById('setup');
            setupPanel.innerHTML = '<div style="text-align: center; padding: 40px;"><h2>Loading drug data...</h2><p>Please wait while we load the TopDrugs.csv file.</p></div>';
        }
        
        function showErrorMessage(error) {
            const setupPanel = document.getElementById('setup');
            setupPanel.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #dc2626;">
                    <h2>Error Loading Data</h2>
                    <p>Could not load TopDrugs.csv file: ${error}</p>
                    <p>Please make sure the TopDrugs.csv file is in the same directory as index.html</p>
                </div>
            `;
        }
        
        function restoreSetupPanel() {
            document.getElementById('setup').innerHTML = `
                <h2 class="setup-title">Select Categories to Match</h2>
                
                <div class="category-selection">
                    <div class="category-group">
                        <label for="category1">Category 1:</label>
                        <select id="category1">
                            <option value="">Select a category...</option>
                        </select>
                    </div>
                    
                    <div class="category-group">
                        <label for="category2">Category 2:</label>
                        <select id="category2">
                            <option value="">Select a category...</option>
                        </select>
                    </div>
                </div>
                
                <div class="drug-sets">
                    <h3>Select Drug Set:</h3>
                    <div class="radio-grid">
                        <div class="radio-item">
                            <input type="radio" id="all" name="drugSet" value="all" checked>
                            <label for="all">All Drugs</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="1-10" name="drugSet" value="1-10">
                            <label for="1-10">Cardiovascular HTN (1-10)</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="11-20" name="drugSet" value="11-20">
                            <label for="11-20">Cardiovascular Other (11-20)</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="21-30" name="drugSet" value="21-30">
                            <label for="21-30">Diabetes (21-30)</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="31-41" name="drugSet" value="31-41">
                            <label for="31-41">Antibiotics (31-41)</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="21-41" name="drugSet" value="21-41">
                            <label for="21-41">Diabetes+Antibiotics (21-41)</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="42-52" name="drugSet" value="42-52">
                            <label for="42-52">Pain Management (42-52)</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="53-63" name="drugSet" value="53-63">
                            <label for="53-63">Psychiatry Dep/Anx (53-63)</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="64-84" name="drugSet" value="64-84">
                            <label for="64-84">Elderly Care (64-84)</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="85-94" name="drugSet" value="85-94">
                            <label for="85-94">Pulmonary (85-94)</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="95-106" name="drugSet" value="95-106">
                            <label for="95-106">Women's Health (95-106)</label>
                        </div>
                        <div class="radio-item">
                            <input type="radio" id="107-124" name="drugSet" value="107-124">
                            <label for="107-124">Psych/Neuro (107-124)</label>
                        </div>
                    </div>
                </div>
                
                <button class="start-button" onclick="startGame()">🚀 Start Game</button>
            `;
        }
        
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
                        return header.trim(); // Remove whitespace from headers
                    },
                    complete: function(results) {
                        if (results.errors.length > 0) {
                            console.warn('CSV parsing warnings:', results.errors);
                        }
                        
                        // Filter out rows that start with # (section headers) in Generic Name column
                        drugData = results.data.filter(row => {
                            const genericName = row['Generic Name'];
                            return genericName && !genericName.trim().startsWith('#');
                        });
                        
                        console.log(`Loaded ${drugData.length} drugs from CSV`);
                        restoreSetupPanel();
                        populateCategoryDropdowns();
                    },
                    error: function(error) {
                        throw new Error(`CSV parsing error: ${error.message}`);
                    }
                });
                
            } catch (error) {
                console.error('Error loading CSV:', error);
                showErrorMessage(error.message);
            }
        }
        
        function populateCategoryDropdowns() {
            if (drugData.length === 0) return;
            
            const categories = Object.keys(drugData[0]);
            const category1Select = document.getElementById('category1');
            const category2Select = document.getElementById('category2');
            
            categories.forEach(category => {
                const option1 = document.createElement('option');
                option1.value = category;
                option1.textContent = category;
                category1Select.appendChild(option1);
                
                const option2 = document.createElement('option');
                option2.value = category;
                option2.textContent = category;
                category2Select.appendChild(option2);
            });
        }
        
        function startGame() {
            const category1 = document.getElementById('category1').value;
            const category2 = document.getElementById('category2').value;
            const drugSet = document.querySelector('input[name="drugSet"]:checked').value;
            
            if (!category1 || !category2 || category1 === category2) {
                alert('Please select two different categories!');
                return;
            }
            
            // Get subset of data based on selection
            currentData = getDataSubset(drugSet);
            
            // Limit to 10 pairs maximum for mobile friendliness
            const numPairs = Math.min(10, currentData.length);
            currentData = currentData.slice(0, numPairs);
            
            // Create matches array
            matches = currentData.map(drug => [drug[category1], drug[category2]]);
            
            // Reset game state
            selectedCards = [];
            attempts = 0;
            matchCount = 0;
            updateStatus();
            
            // Hide setup, show game
            document.getElementById('setup').style.display = 'none';
            document.getElementById('game').style.display = 'block';
            document.getElementById('completion').style.display = 'none';
            
            // Create cards
            createCards(category1, category2);
        }
        
        function getDataSubset(drugSet) {
            // Filter data based on selected drug set (matching your Python logic)
            switch(drugSet) {
                case "1-10":
                    return drugData.slice(0, 10);
                case "11-20":
                    return drugData.slice(10, 20);
                case "21-30":
                    return drugData.slice(20, 30);
                case "31-41":
                    return drugData.slice(30, 42);
                case "21-41":
                    return drugData.slice(20, 42);
                case "42-52":
                    return drugData.slice(42, 53);
                case "53-63":
                    return drugData.slice(53, 64);
                case "64-84":
                    return drugData.slice(64, 85);
                case "85-94":
                    return drugData.slice(85, 95);
                case "95-106":
                    return drugData.slice(95, 107);
                case "107-124":
                    return drugData.slice(107, 125);
                case "all":
                default:
                    return drugData;
            }
        }
        
        function createCards(cat1, cat2) {
            const column1 = document.getElementById('column1');
            const column2 = document.getElementById('column2');
            
            // Clear existing cards
            column1.innerHTML = '';
            column2.innerHTML = '';
            
            // Get all values and shuffle them
            const values1 = currentData.map(drug => drug[cat1]);
            const values2 = currentData.map(drug => drug[cat2]);
            
            shuffleArray(values1);
            shuffleArray(values2);
            
            // Create cards for column 1
            values1.forEach(value => {
                const card = document.createElement('div');
                card.className = 'card';
                card.textContent = value;
                card.dataset.value = value;
                card.dataset.category = cat1;
                card.onclick = () => selectCard(card);
                column1.appendChild(card);
            });
            
            // Create cards for column 2
            values2.forEach(value => {
                const card = document.createElement('div');
                card.className = 'card';
                card.textContent = value;
                card.dataset.value = value;
                card.dataset.category = cat2;
                card.onclick = () => selectCard(card);
                column2.appendChild(card);
            });
        }
        
        function selectCard(card) {
            if (card.classList.contains('matched') || selectedCards.includes(card) || selectedCards.length >= 2) {
                return;
            }
            
            selectedCards.push(card);
            card.classList.add('selected');
            
            if (selectedCards.length === 2) {
                attempts++;
                updateStatus();
                setTimeout(checkMatch, 500);
            }
        }
        
        function checkMatch() {
            const [card1, card2] = selectedCards;
            const value1 = card1.dataset.value;
            const value2 = card2.dataset.value;
            
            // Check if these values form a valid match
            const isMatch = matches.some(match => 
                (match[0] === value1 && match[1] === value2) ||
                (match[0] === value2 && match[1] === value1)
            );
            
            if (isMatch) {
                // Correct match
                card1.classList.remove('selected');
                card2.classList.remove('selected');
                card1.classList.add('matched');
                card2.classList.add('matched');
                matchCount++;
                
                // Check if game is complete
                if (matchCount === matches.length) {
                    setTimeout(gameComplete, 500);
                }
            } else {
                // Wrong match
                card1.classList.remove('selected');
                card2.classList.remove('selected');
                card1.classList.add('error');
                card2.classList.add('error');
                
                setTimeout(() => {
                    card1.classList.remove('error');
                    card2.classList.remove('error');
                }, 500);
            }
            
            selectedCards = [];
            updateStatus();
        }
        
        function updateStatus() {
            document.getElementById('matches').textContent = `Matches: ${matchCount}`;
            document.getElementById('attempts').textContent = `Attempts: ${attempts}`;
        }
        
        function gameComplete() {
            const accuracy = Math.round((matchCount / attempts) * 100);
            document.getElementById('final-score').textContent = 
                `You completed the game in ${attempts} attempts with ${accuracy}% accuracy!`;
            document.getElementById('completion').style.display = 'block';
        }
        
        function backToSetup() {
            document.getElementById('setup').style.display = 'block';
            document.getElementById('game').style.display = 'none';
        }
        
        function playAgain() {
            document.getElementById('completion').style.display = 'none';
            startGame();
        }
        
        function shuffleArray(array) {
            for (let i = array.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]];
            }
        }
        
        // Initialize the app when the page loads
        window.onload = init;
