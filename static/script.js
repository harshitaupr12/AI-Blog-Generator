function generateSingleArticle() {
    const topic = document.getElementById('singleTopic').value.trim();
    
    if (!topic) {
        alert('Please enter a topic for the comprehensive article');
        return;
    }

    // Show progress section
    document.getElementById('progressSection').classList.remove('hidden');
    document.getElementById('resultsSection').classList.add('hidden');
    
    // Disable button during generation
    const generateBtn = document.getElementById('generateBtn');
    generateBtn.disabled = true;
    generateBtn.textContent = 'Researching and Writing...';
    
    // Real-time progress animation for single topic
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 2;
        if (progress <= 90) {
            document.getElementById('progressFill').style.width = progress + '%';
            
            const stages = [
                "Researching topic...",
                "Structuring content...", 
                "Writing introduction...",
                "Developing main sections...",
                "Adding examples...",
                "Creating conclusion...",
                "Finalizing article..."
            ];
            
            const stageIndex = Math.floor(progress / 13);
            document.getElementById('progressText').textContent = stages[stageIndex] || "Finalizing...";
            document.getElementById('currentTopic').textContent = `Topic: ${topic}`;
        }
        
        if (progress >= 90) {
            clearInterval(progressInterval);
        }
    }, 500);

    // Generate single comprehensive article
    fetch('/generate_article', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic: topic })
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(progressInterval);
        
        // Complete progress bar
        let finalProgress = 90;
        const finalInterval = setInterval(() => {
            finalProgress += 2;
            document.getElementById('progressFill').style.width = finalProgress + '%';
            document.getElementById('progressText').textContent = `Finalizing... ${finalProgress}%`;
            
            if (finalProgress >= 100) {
                clearInterval(finalInterval);
                showSingleArticleResults(data);
            }
        }, 100);
    })
    .catch(error => {
        console.error('Error:', error);
        clearInterval(progressInterval);
        handleError(error);
    });
}

function showSingleArticleResults(data) {
    document.getElementById('progressText').textContent = 'Complete! ✅';
    
    if (data.error) {
        alert(data.error);
        resetUI();
        return;
    }
    
    // Show detailed results for single article
    let resultHTML = `<strong>${data.message}</strong><br><br>`;
    
    if (data.article) {
        resultHTML += `
            <div style="text-align: left; background: #f8f9fa; padding: 15px; border-radius: 8px;">
                <h4>${data.article.title}</h4>
                <p><strong>Topic:</strong> ${data.article.topic}</p>
                <p><strong>Words:</strong> ${data.article.word_count}</p>
                <p><strong>Summary:</strong> ${data.article.summary}</p>
            </div>
        `;
    }
    
    document.getElementById('resultMessage').innerHTML = resultHTML;
    document.getElementById('resultsSection').classList.remove('hidden');
    
    // Reset UI
    setTimeout(() => {
        resetUI();
    }, 2000);
}

function handleError(error) {
    document.getElementById('progressFill').style.background = '#dc3545';
    document.getElementById('progressText').textContent = 'Error! ❌';
    document.getElementById('progressText').style.color = '#dc3545';
    
    setTimeout(() => {
        resetUI();
        alert('Error generating article. Please try again.');
    }, 2000);
}

function resetUI() {
    const generateBtn = document.getElementById('generateBtn');
    generateBtn.disabled = false;
    generateBtn.textContent = 'Generate Comprehensive Article';
    
    document.getElementById('progressSection').classList.add('hidden');
    document.getElementById('progressFill').style.background = '';
    document.getElementById('progressFill').style.width = '0%';
    document.getElementById('progressText').style.color = '';
    document.getElementById('progressText').textContent = 'Preparing...';
    document.getElementById('currentTopic').textContent = '';
}

function viewBlog() {
    window.location.href = '/blog';
}

function clearArticles() {
    if (confirm('Are you sure you want to clear all articles?')) {
        fetch('/clear_articles', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                alert(`✅ ${data.message}`);
                if (window.location.pathname === '/blog') {
                    location.reload();
                }
            })
            .catch(error => {
                alert('❌ Error clearing articles');
            });
    }
}

// Add sample topics for testing
document.addEventListener('DOMContentLoaded', function() {
    const sampleTopics = [
        "Artificial Intelligence in Healthcare",
        "Python Web Development with Flask",
        "Blockchain Technology and Cryptocurrency",
        "Machine Learning for Business Applications",
        "Cloud Computing with AWS Services"
    ];
    
    // Add random topic suggestion
    const randomTopic = sampleTopics[Math.floor(Math.random() * sampleTopics.length)];
    document.getElementById('singleTopic').placeholder = `e.g., ${randomTopic}`;
    
    // Add enter key support
    document.getElementById('singleTopic').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            generateSingleArticle();
        }
    });
});