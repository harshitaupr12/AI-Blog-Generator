from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import random
import sqlite3

load_dotenv()
app = Flask(__name__)

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Initialize permanent database
def init_blog_db():
    """Initialize SQLite database for blog articles"""
    conn = sqlite3.connect('blog_articles.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  topic TEXT NOT NULL,
                  title TEXT NOT NULL,
                  content TEXT NOT NULL,
                  summary TEXT,
                  tags TEXT,
                  word_count INTEGER,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
    print("✅ Blog database initialized successfully")

# Initialize database on startup
init_blog_db()

def save_article_to_db(article_data):
    """Save article to SQLite database"""
    try:
        conn = sqlite3.connect('blog_articles.db')
        c = conn.cursor()
        c.execute('''INSERT INTO articles 
                     (topic, title, content, summary, tags, word_count) 
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (article_data['topic'], article_data['title'], 
                   article_data['content'], article_data['summary'],
                   ','.join(article_data['tags']), article_data['word_count']))
        conn.commit()
        conn.close()
        print(f"✅ Article saved to database: {article_data['title']}")
        return True
    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        return False

def load_articles_from_db():
    """Load all articles from SQLite database"""
    try:
        conn = sqlite3.connect('blog_articles.db')
        c = conn.cursor()
        c.execute('''SELECT * FROM articles ORDER BY created_at DESC''')
        rows = c.fetchall()
        conn.close()
        
        articles = []
        for row in rows:
            articles.append({
                'id': row[0],
                'topic': row[1],
                'title': row[2],
                'content': row[3],
                'summary': row[4],
                'tags': row[5].split(',') if row[5] else [],
                'word_count': row[6],
                'created_at': row[7]
            })
        print(f"✅ Loaded {len(articles)} articles from database")
        return articles
    except Exception as e:
        print(f"❌ Error loading from database: {e}")
        return []

def generate_article(topic):
    """Generate comprehensive article on single topic"""
    try:
        if not GEMINI_API_KEY:
            return create_comprehensive_demo_content(topic)
            
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Write a comprehensive, in-depth blog article about: {topic}
        
        Create a detailed, well-structured article with:
        
        # TITLE: Create an engaging, SEO-friendly title
        
        ## Introduction
        - Start with a compelling hook
        - Explain why this topic matters
        - Provide context and background
        
        ## Main Body (3-5 sections)
        - Break down the topic into logical sections
        - Include practical examples and use cases
        - Add data, statistics, or research findings
        - Use subheadings for better organization
        
        ## Key Features/Components
        - List and explain important aspects
        - Compare different approaches if applicable
        - Include best practices
        
        ## Real-World Applications
        - Show how this is used in industry
        - Include case studies or success stories
        - Practical implementation tips
        
        ## Future Trends
        - Discuss emerging developments
        - Predict future directions
        - Opportunities and challenges
        
        ## Conclusion
        - Summarize key takeaways
        - Provide actionable advice
        - End with thought-provoking statement
        
        Requirements:
        - Minimum 800 words
        - Professional, engaging tone
        - Include specific examples
        - Well-structured with clear sections
        - SEO-optimized content
        
        Write the complete article with proper formatting, headings, and paragraphs.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ AI Generation Error: {e}")
        return create_comprehensive_demo_content(topic)

def create_comprehensive_demo_content(topic):
    """Create detailed demo content when API fails"""
    return f"""
# The Complete Guide to {topic}: Everything You Need to Know

## Introduction
{topic} has emerged as one of the most transformative fields in recent years, revolutionizing how we approach problems and create solutions. This comprehensive guide will take you through every aspect of {topic}, from fundamental concepts to advanced applications.

## Understanding the Core Concepts

### What is {topic}?
At its essence, {topic} represents a paradigm shift in how we process information and make decisions. It combines theoretical foundations with practical implementations to solve complex challenges.

### Key Principles and Fundamentals
The foundation of {topic} rests on several core principles:
- **Principle 1**: The first fundamental concept that drives understanding
- **Principle 2**: Essential building blocks for practical application  
- **Principle 3**: Advanced concepts that enable sophisticated solutions

## Main Components and Architecture

### Core Components
1. **Component A**: The fundamental building block that handles basic operations
2. **Component B**: Advanced features that provide enhanced capabilities
3. **Component C**: Integration points that connect with other systems

### System Architecture
The typical architecture of {topic} systems includes:
- **Front-end Layer**: User-facing components and interfaces
- **Processing Layer**: Core logic and decision-making engines
- **Data Layer**: Storage and management of information
- **Integration Layer**: Connections with external systems and APIs

## Practical Applications and Use Cases

### Industry Applications
1. **Healthcare**: Revolutionizing patient care and medical research
2. **Finance**: Transforming how we manage and invest money
3. **Education**: Creating personalized learning experiences
4. **Manufacturing**: Optimizing production processes and quality control

### Real-World Examples
**Case Study 1**: How Company X implemented {topic} to increase efficiency by 45%
**Case Study 2**: Organization Y's successful adoption of {topic} for customer service

## Implementation Guide

### Getting Started
1. **Step 1**: Initial setup and configuration
2. **Step 2**: Basic implementation and testing
3. **Step 3**: Advanced features and optimization

### Best Practices
- **Practice 1**: Essential guidelines for successful implementation
- **Practice 2**: Common pitfalls to avoid
- **Practice 3**: Performance optimization techniques

## Advanced Topics and Future Directions

### Emerging Trends
1. **Trend 1**: The latest developments shaping the future
2. **Trend 2**: Innovative approaches gaining traction
3. **Trend 3**: Research directions showing promise

### Future Outlook
The future of {topic} looks promising with:
- Increased adoption across industries
- More sophisticated tools and platforms
- Greater integration with other technologies
- Enhanced accessibility for non-experts

## Conclusion

{topic} represents a significant advancement with far-reaching implications. By understanding its principles, applications, and future directions, you can leverage this technology to drive innovation and create value in your projects and organization.

This comprehensive guide has covered the essential aspects of {topic}, providing you with the knowledge needed to navigate this exciting field successfully.

*Note: This is demo content. With proper API configuration, real AI-generated content would appear here.*
"""

def parse_article_response(response_text, topic):
    """Parse the complete article response"""
    try:
        content = response_text
        word_count = len(content.split())
        
        # Extract title from content or create one
        title = f"The Complete Guide to {topic}"
        if '#' in content:
            first_line = content.split('\n')[0]
            if '#' in first_line:
                title = first_line.replace('#', '').strip()
        
        article_data = {
            "topic": topic,
            "title": title,
            "content": content,
            "summary": f"Comprehensive guide covering all aspects of {topic} from fundamentals to advanced applications",
            "tags": [topic.lower(), "guide", "tutorial", "comprehensive", "technology"],
            "word_count": word_count
        }
        
        return article_data
    except Exception as e:
        print(f"❌ Parsing Error: {e}")
        return {
            "topic": topic,
            "title": f"Complete Guide to {topic}",
            "content": response_text,
            "summary": f"Detailed exploration of {topic}",
            "tags": [topic.lower(), "guide", "knowledge"],
            "word_count": len(response_text.split())
        }

@app.route('/')
def index():
    """Main page to generate articles"""
    return render_template('generate.html')

@app.route('/generate_article', methods=['POST'])
def generate_single_article():
    """Generate one comprehensive article"""
    topic = request.json.get('topic', '').strip()
    
    if not topic:
        return jsonify({"error": "Please enter a topic"})
    
    print(f"🚀 Generating comprehensive article for: {topic}")
    
    try:
        # Generate the article
        response = generate_article(topic)
        article_data = parse_article_response(response, topic)
        
        # Add timestamp
        article_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to database
        save_success = save_article_to_db(article_data)
        
        if save_success:
            return jsonify({
                "message": f"✅ Generated comprehensive article about {topic}",
                "article": article_data,
                "saved_to_db": True
            })
        else:
            return jsonify({
                "message": f"⚠️ Generated article but failed to save to database",
                "article": article_data,
                "saved_to_db": False
            })
            
    except Exception as e:
        print(f"❌ Generation Error: {e}")
        return jsonify({"error": f"Failed to generate article: {str(e)}"})

@app.route('/blog')
def blog():
    """Display all generated articles"""
    try:
        articles = load_articles_from_db()
        return render_template('blog.html', articles=articles)
    except Exception as e:
        print(f"❌ Blog Error: {e}")
        return render_template('blog.html', articles=[])

@app.route('/clear_articles', methods=['POST'])
def clear_articles():
    """Clear all articles from database"""
    try:
        conn = sqlite3.connect('blog_articles.db')
        c = conn.cursor()
        c.execute('DELETE FROM articles')
        conn.commit()
        conn.close()
        return jsonify({"message": "✅ All articles cleared successfully from database"})
    except Exception as e:
        return jsonify({"error": f"❌ Error clearing articles: {str(e)}"})

@app.route('/stats')
def stats():
    """Get database statistics"""
    try:
        conn = sqlite3.connect('blog_articles.db')
        c = conn.cursor()
        
        # Total articles
        c.execute('SELECT COUNT(*) FROM articles')
        total_articles = c.fetchone()[0]
        
        # Total words
        c.execute('SELECT SUM(word_count) FROM articles')
        total_words = c.fetchone()[0] or 0
        
        # Latest article
        c.execute('SELECT title, created_at FROM articles ORDER BY created_at DESC LIMIT 1')
        latest = c.fetchone()
        
        conn.close()
        
        return jsonify({
            "total_articles": total_articles,
            "total_words": total_words,
            "latest_article": latest[0] if latest else "None",
            "latest_date": latest[1] if latest else "None"
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("🚀 AI Blog Generator starting on http://localhost:7000")
    print("📝 Features: Single topic deep content generation")
    print("💾 Storage: SQLite database (blog_articles.db)")
    print(f"🔑 API Status: {'✅ Connected' if GEMINI_API_KEY else '❌ Not Configured'}")
    app.run(debug=True, port=7000)