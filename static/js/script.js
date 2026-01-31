// Global variables
let currentAnalysis = null;
let currentBookName = '';

function selectBook(bookName) {
    // Remove selection from all cards
    document.querySelectorAll('.book-card').forEach(card => {
        card.classList.remove('selected');
    });

    // Find and select the clicked card
    const cards = document.querySelectorAll('.book-card');
    for (const card of cards) {
        if (card.dataset.book === bookName) {
            card.classList.add('selected');
            break;
        }
    }

    // Set value and enable button
    document.getElementById('selectedBook').value = bookName;
    document.getElementById('generateBtn').disabled = false;
    currentBookName = bookName;
    
    // Show story options
    document.getElementById('storyOptions').classList.remove('hidden');
    
    // Smooth scroll to options
    document.getElementById('storyOptions').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

async function generateStory() {
    const bookName = document.getElementById('selectedBook').value;
    if (!bookName) return;

    // Get options
    const storyLength = document.getElementById('storyLength').value;
    const storyStyle = document.getElementById('storyStyle').value;

    // Hide other sections, show loading
    document.querySelector('.book-selection').style.opacity = '0.5';
    document.querySelector('.book-selection').style.pointerEvents = 'none';
    
    const loadingSection = document.getElementById('loadingSection');
    const analysisSection = document.getElementById('analysisSection');
    const resultSection = document.getElementById('resultSection');
    
    loadingSection.classList.remove('hidden');
    analysisSection.classList.add('hidden');
    resultSection.classList.add('hidden');

    // Scroll to loading
    loadingSection.scrollIntoView({ behavior: 'smooth' });

    // Reset all steps
    resetLoadingSteps();

    try {
        // SSE ile gerçek zamanlı ilerleme
        const url = `/produce-story-stream?book_filename=${encodeURIComponent(bookName)}&length=${storyLength}&style=${storyStyle}`;
        const eventSource = new EventSource(url);
        
        let finalData = null;
        
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.error) {
                eventSource.close();
                throw new Error(data.error);
            }
            
            // Update progress UI
            updateProgressFromServer(data);
            
            // Eğer analiz verisi geldiyse göster
            if (data.analysis && !currentAnalysis) {
                currentAnalysis = data.analysis;
                displayAnalysis(data.analysis);
                analysisSection.classList.remove('hidden');
            }
            
            // Final sonuç
            if (data.step === 7 && data.story) {
                finalData = data;
                eventSource.close();
                
                // Hide loading, show result
                loadingSection.classList.add('hidden');
                
                // Display story
                document.getElementById('storyContent').textContent = data.story;
                resultSection.classList.remove('hidden');
                
                // Scroll to result
                resultSection.scrollIntoView({ behavior: 'smooth' });
                
                // Re-enable book selection
                document.querySelector('.book-selection').style.opacity = '1';
                document.querySelector('.book-selection').style.pointerEvents = 'auto';
                
                // Show success toast
                showToast('Hikaye başarıyla oluşturuldu! ✨');
            }
        };
        
        eventSource.onerror = function(error) {
            eventSource.close();
            console.error('SSE Error:', error);
            loadingSection.classList.add('hidden');
            document.querySelector('.book-selection').style.opacity = '1';
            document.querySelector('.book-selection').style.pointerEvents = 'auto';
            showToast('Bağlantı hatası oluştu', 'error');
        };

    } catch (error) {
        console.error('Error:', error);
        loadingSection.classList.add('hidden');
        document.querySelector('.book-selection').style.opacity = '1';
        document.querySelector('.book-selection').style.pointerEvents = 'auto';
        showToast('Hata: ' + error.message, 'error');
    }
}

function resetLoadingSteps() {
    const steps = ['step1', 'step2', 'step3'];
    steps.forEach((stepId, index) => {
        const step = document.getElementById(stepId);
        const indicator = step.querySelector('.step-indicator');
        indicator.classList.remove('active', 'completed');
        // Reset icons
        const icons = ['📖', '🔍', '✍️'];
        indicator.querySelector('.step-icon').textContent = icons[index];
    });
}

function updateProgressFromServer(data) {
    const stepMapping = {
        1: { uiStep: 1, text: 'Dosya okunuyor...' },
        2: { uiStep: 1, text: data.cached ? "Cache'den yükleniyor..." : 'Metin temizleniyor...' },
        3: { uiStep: 1, text: 'Metin örnekleniyor...' },
        4: { uiStep: 2, text: 'NLP analizi yapılıyor...' },
        5: { uiStep: 2, text: 'Analiz tamamlandı!' },
        6: { uiStep: 3, text: 'Hikaye yazılıyor...' },
        7: { uiStep: 3, text: 'Tamamlandı!' }
    };
    
    const mapping = stepMapping[data.step];
    if (mapping) {
        updateLoadingStep(mapping.uiStep, mapping.text);
    }
}

function updateLoadingStep(currentStep, statusText = null) {
    const steps = ['step1', 'step2', 'step3'];
    const defaultTexts = ['Metin Temizleniyor', 'Analiz Ediliyor', 'Hikaye Yazılıyor'];
    
    steps.forEach((stepId, index) => {
        const step = document.getElementById(stepId);
        const indicator = step.querySelector('.step-indicator');
        
        if (index + 1 < currentStep) {
            indicator.classList.remove('active');
            indicator.classList.add('completed');
            indicator.querySelector('.step-icon').textContent = '✓';
        } else if (index + 1 === currentStep) {
            indicator.classList.add('active');
            indicator.classList.remove('completed');
        } else {
            indicator.classList.remove('active', 'completed');
        }
    });
    
    // Update status text
    const text = statusText || defaultTexts[currentStep - 1];
    document.getElementById('loadingText').textContent = text;
}

function displayAnalysis(analysis) {
    // Characters
    const charactersContent = document.getElementById('charactersContent');
    charactersContent.innerHTML = '';
    if (analysis.characters) {
        Object.keys(analysis.characters).slice(0, 6).forEach(char => {
            const tag = document.createElement('span');
            tag.className = 'tag tag-purple';
            tag.textContent = char;
            charactersContent.appendChild(tag);
        });
    }
    
    // Mood words
    const moodContent = document.getElementById('moodContent');
    moodContent.innerHTML = '';
    if (analysis.mood_words) {
        Object.keys(analysis.mood_words).slice(0, 8).forEach(word => {
            const tag = document.createElement('span');
            tag.className = 'tag tag-blue';
            tag.textContent = word;
            moodContent.appendChild(tag);
        });
    }
    
    // Sentiment
    const sentimentContent = document.getElementById('sentimentContent');
    sentimentContent.innerHTML = '';
    if (analysis.sentiments) {
        const polarity = analysis.sentiments.polarity;
        const subjectivity = analysis.sentiments.subjectivity;
        
        // Polarity bar
        const polarityContainer = document.createElement('div');
        polarityContainer.className = 'sentiment-bar-container';
        
        const polarityLabel = document.createElement('div');
        polarityLabel.className = 'sentiment-label';
        polarityLabel.innerHTML = `<span>Polarite</span><span>${polarity > 0 ? '+' : ''}${polarity.toFixed(2)}</span>`;
        
        const polarityBar = document.createElement('div');
        polarityBar.className = 'sentiment-bar';
        
        const polarityFill = document.createElement('div');
        polarityFill.className = `sentiment-fill ${polarity > 0.1 ? 'positive' : polarity < -0.1 ? 'negative' : 'neutral'}`;
        polarityFill.style.width = `${Math.abs(polarity) * 100}%`;
        
        polarityBar.appendChild(polarityFill);
        polarityContainer.appendChild(polarityLabel);
        polarityContainer.appendChild(polarityBar);
        
        // Subjectivity bar
        const subjectivityLabel = document.createElement('div');
        subjectivityLabel.className = 'sentiment-label';
        subjectivityLabel.innerHTML = `<span>Öznellik</span><span>${(subjectivity * 100).toFixed(0)}%</span>`;
        
        const subjectivityBar = document.createElement('div');
        subjectivityBar.className = 'sentiment-bar';
        
        const subjectivityFill = document.createElement('div');
        subjectivityFill.className = 'sentiment-fill neutral';
        subjectivityFill.style.width = `${subjectivity * 100}%`;
        
        subjectivityBar.appendChild(subjectivityFill);
        
        sentimentContent.appendChild(polarityContainer);
        sentimentContent.appendChild(subjectivityLabel);
        sentimentContent.appendChild(subjectivityBar);
    }
    
    // Keywords
    const keywordsContent = document.getElementById('keywordsContent');
    keywordsContent.innerHTML = '';
    if (analysis.keywords) {
        analysis.keywords.slice(0, 8).forEach(keyword => {
            const tag = document.createElement('span');
            tag.className = 'tag tag-orange';
            // Truncate long keywords
            tag.textContent = keyword.length > 25 ? keyword.substring(0, 25) + '...' : keyword;
            tag.title = keyword;
            keywordsContent.appendChild(tag);
        });
    }
}

function copyStory() {
    const text = document.getElementById('storyContent').textContent;
    if (!text) return;

    navigator.clipboard.writeText(text).then(() => {
        showToast('Hikaye panoya kopyalandı! 📋');
    }).catch(err => {
        console.error('Kopyalama hatası:', err);
        showToast('Kopyalama başarısız oldu', 'error');
    });
}

function saveStory() {
    const text = document.getElementById('storyContent').textContent;
    if (!text) return;

    const bookTitle = currentBookName.replace('.txt', '');
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${bookTitle}_hikaye.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    showToast('Hikaye indirildi! ⬇️');
}

function regenerateStory() {
    // Reset loading steps
    resetLoadingSteps();
    // Re-generate with same book
    generateStory();
}

function newStory() {
    // Reset everything
    document.querySelectorAll('.book-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.getElementById('selectedBook').value = '';
    document.getElementById('generateBtn').disabled = true;
    document.getElementById('storyOptions').classList.add('hidden');
    document.getElementById('loadingSection').classList.add('hidden');
    document.getElementById('analysisSection').classList.add('hidden');
    document.getElementById('resultSection').classList.add('hidden');
    document.querySelector('.book-selection').style.opacity = '1';
    document.querySelector('.book-selection').style.pointerEvents = 'auto';
    
    resetLoadingSteps();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function resetLoadingSteps() {
    ['step1', 'step2', 'step3'].forEach((stepId, index) => {
        const step = document.getElementById(stepId);
        const indicator = step.querySelector('.step-indicator');
        indicator.classList.remove('active', 'completed');
        const icons = ['📖', '🔍', '✍️'];
        indicator.querySelector('.step-icon').textContent = icons[index];
    });
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    toast.classList.remove('hidden');
    toast.classList.add('show');
    
    if (type === 'error') {
        toast.style.borderColor = '#ef4444';
    } else {
        toast.style.borderColor = '#8b5cf6';
    }
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 300);
    }, 3000);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Smooth scroll for nav links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
