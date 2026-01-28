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

    // Update loading steps
    updateLoadingStep(1);

    try {
        const response = await fetch('/produce-story', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                book_filename: bookName,
                length: storyLength,
                style: storyStyle
            })
        });

        if (!response.ok) {
            throw new Error('Sunucu hatası oluştu');
        }

        const data = await response.json();

        // Update steps
        updateLoadingStep(2);
        await sleep(500);
        
        // Show analysis if available
        if (data.analysis) {
            currentAnalysis = data.analysis;
            displayAnalysis(data.analysis);
            analysisSection.classList.remove('hidden');
        }
        
        updateLoadingStep(3);
        await sleep(500);

        // Hide loading, show result
        loadingSection.classList.add('hidden');
        
        // Display story
        document.getElementById('storyContent').textContent = data.story;
        resultSection.classList.remove('hidden');
        
        // Scroll to result
        resultSection.scrollIntoView({ behavior: 'smooth' });
        
        // Show success toast
        showToast('Hikaye başarıyla oluşturuldu! ✨');

    } catch (error) {
        console.error('Error:', error);
        loadingSection.classList.add('hidden');
        document.querySelector('.book-selection').style.opacity = '1';
        document.querySelector('.book-selection').style.pointerEvents = 'auto';
        showToast('Hata: ' + error.message, 'error');
    }
}

function updateLoadingStep(currentStep) {
    const steps = ['step1', 'step2', 'step3'];
    const texts = ['Metin Temizleniyor', 'Analiz Ediliyor', 'Hikaye Yazılıyor'];
    
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
    
    document.getElementById('loadingText').textContent = texts[currentStep - 1];
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
