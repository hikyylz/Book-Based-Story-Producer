function selectBook(bookName) {
    // UI Update
    document.querySelectorAll('.book-card').forEach(card => card.classList.remove('selected'));

    // Find the card that was clicked (might be the event target or a parent)
    const cards = document.querySelectorAll('.book-card');
    for (const card of cards) {
        if (card.querySelector('.book-title').textContent === bookName) {
            card.classList.add('selected');
            break;
        }
    }

    // Set value
    document.getElementById('selectedBook').value = bookName;
    document.getElementById('generateBtn').disabled = false;
}

async function generateStory() {
    const bookName = document.getElementById('selectedBook').value;
    if (!bookName) return;

    // Show loading
    const resultSection = document.getElementById('resultSection');
    const loadingDiv = document.getElementById('loading');
    const contentDiv = document.getElementById('storyContent');

    resultSection.classList.remove('hidden');
    loadingDiv.classList.remove('hidden');
    contentDiv.innerHTML = ''; // Clear previous

    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth' });

    try {
        const response = await fetch('/produce-story', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ book_filename: bookName })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        // Hide loading, show content
        loadingDiv.classList.add('hidden');
        contentDiv.textContent = data.story;

    } catch (error) {
        console.error('Error:', error);
        loadingDiv.classList.add('hidden');
        contentDiv.innerHTML = `<span style="color: #ef4444;">Error generating story: ${error.message}</span>`;
    }
}

function saveStory() {
    const text = document.getElementById('storyContent').textContent;
    if (!text) return;

    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'generated_story.txt';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}
