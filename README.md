# 🛡️ TrustHire - AI-Powered Job Aggregation Platform

**TrustHire** is a comprehensive job search platform that aggregates job listings from multiple sources (LinkedIn, Indeed, Naukri) and uses **Machine Learning & AI** to detect fraudulent job postings, providing users with trust scores for each listing.

---

## 🎯 Key Features

### ✅ **Problem Solved**
- **Multi-Platform Search**: Search across LinkedIn, Indeed, and Naukri simultaneously
- **Fraud Detection**: AI/ML-powered fraud detection with trust scores (0-100%)
- **Trust Scores**: Every job analyzed for authenticity
- **Community Reporting**: Users can report suspicious listings
- **Advanced Filtering**: Filter by location, experience, platform, and trust score
- **No Missed Opportunities**: See ALL job openings in one place

### 🚀 **Unique Features**
1. **AI Fraud Detection** - 6 different fraud signals analyzed:
   - Suspicious keywords detection
   - Pattern matching (fake emails, unrealistic salaries)
   - Text quality analysis
   - Company legitimacy checks
   - Salary verification
   - URL trust scoring

2. **Real-time Statistics** - Track fraud rates and trending searches
3. **Beautiful UI** - Simple, user-friendly React interface
4. **Parallel Scraping** - Fast multi-platform job aggregation

---

## 🛠️ Tech Stack

### Backend (Python)
- **Flask** - REST API
- **BeautifulSoup4 & Selenium** - Web scraping
- **Scikit-learn & NLTK** - Machine Learning & NLP
- **TextBlob** - Sentiment analysis
- **SQLAlchemy** - Database ORM
- **SQLite** - Database

### Frontend (React)
- **React 18** - UI framework
- **Axios** - API calls
- **CSS3** - Modern styling

---

## 📋 Prerequisites

Before you begin, ensure you have:
- **Python 3.8+** installed
- **Node.js 14+** and **npm** installed
- **Git** (already have it)

---

## 🚀 Installation & Setup (Step-by-Step)

### **Step 1: Navigate to Project**
```bash
cd "c:\Users\chand\Documents\GitHub\TrustHire"
```

---

### **Step 2: Backend Setup**

#### 2.1 Navigate to backend directory
```bash
cd backend
```

#### 2.2 Create Python virtual environment
```bash
python -m venv venv
```

#### 2.3 Activate virtual environment
**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

#### 2.4 Install Python dependencies
```bash
pip install -r requirements.txt
```

#### 2.5 Download NLTK data (required for NLP)
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

#### 2.6 Initialize database
```bash
python -c "from app import create_app; from database import db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized!')"
```

#### 2.7 Start the backend server
```bash
python app.py
```

**Backend will run on:** `http://localhost:5000`

✅ **Keep this terminal open!**

---

### **Step 3: Frontend Setup** (New Terminal)

#### 3.1 Open NEW terminal and navigate to frontend
```bash
cd "c:\Users\chand\Documents\GitHub\TrustHire\frontend"
```

#### 3.2 Install Node dependencies
```bash
npm install
```

#### 3.3 Start the React development server
```bash
npm start
```

**Frontend will run on:** `http://localhost:3000`

✅ **Browser will open automatically!**

---

## 🎮 Usage Guide

### **1. Search for Jobs**
- Enter job title (e.g., "Software Engineer", "Data Analyst")
- Add location (optional, e.g., "San Francisco", "Remote")
- Select experience level (Entry/Mid/Senior)
- Choose platforms to search (All, LinkedIn, Indeed, Naukri)
- Click **"Search Jobs"**

### **2. View Results**
- Jobs are sorted by **Trust Score** (highest first)
- Each job card shows:
  - ✅ **Trust Score** (0-100%) with color coding
  - 🏢 Company, Location, Salary
  - ⚠️ **Fraud Signals** if detected
  - 🔗 Link to original posting

### **3. Filter & Sort**
- **Filter**: All Jobs / Trusted (70%+) / Flagged
- **Sort**: Trust Score / Most Recent

### **4. Report Fraudulent Jobs**
- Click **"🚩 Report"** on any job card
- Provide detailed reason
- Helps improve fraud detection

### **5. View Statistics**
- Total jobs analyzed
- Fraud detection rate
- Popular searches
- Platform breakdown

---

## 🧪 Testing the Application

### **Test Search Examples:**

1. **Software Engineer Jobs:**
   ```
   Query: "Software Engineer"
   Location: "San Francisco"
   Experience: "Mid"
   ```

2. **Data Analyst Roles:**
   ```
   Query: "Data Analyst"
   Location: "Remote"
   Experience: "Entry"
   ```

3. **Test Fraud Detection:**
   - Search for common jobs
   - Look for jobs with low trust scores (<50%)
   - Check fraud signals displayed

---

## 📊 API Endpoints

### **Backend API** (`http://localhost:5000/api`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search` | POST | Search jobs across platforms |
| `/api/jobs` | GET | Get jobs with filters |
| `/api/jobs/<id>` | GET | Get single job details |
| `/api/jobs/<id>/report` | POST | Report fraudulent job |
| `/api/stats` | GET | Get platform statistics |
| `/api/health` | GET | Health check |

### **Example API Call:**
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python Developer",
    "location": "New York",
    "experience": "mid",
    "platforms": ["all"]
  }'
```

---

## 🤖 Fraud Detection Algorithm

### **How it Works:**

1. **Keyword Analysis (30%)** - Detects suspicious phrases:
   - "Guaranteed income", "Get rich quick"
   - "Pay upfront", "Registration fee"
   - "Investment required"

2. **Pattern Detection (20%)** - Identifies:
   - Free email domains (gmail, yahoo)
   - Unrealistic salaries
   - Personal phone numbers
   - Shortened URLs

3. **Text Quality (15%)** - Analyzes:
   - Grammar and spelling
   - Excessive capitalization
   - Description length
   - Sentence structure

4. **Company Legitimacy (20%)** - Checks:
   - Generic company names
   - Missing company details
   - Website mentions

5. **Salary Analysis (10%)** - Validates:
   - Unrealistic claims
   - Proper formatting

6. **URL Trust (5%)** - Verifies:
   - Known job platforms
   - Legitimate domains

**Trust Score Formula:**
```
Trust Score = 1.0 - (Weighted Fraud Score)
Fraudulent if: Trust Score < 60%
```

---

## 🎨 UI Features

- **Gradient Background** - Modern purple gradient
- **Responsive Design** - Works on mobile, tablet, desktop
- **Trust Score Visualization** - Circular progress indicators
- **Color-Coded Ratings**:
  - 🟢 Green (70-100%): Trusted
  - 🟠 Orange (50-69%): Moderate
  - 🔴 Red (<50%): Caution

---

## 📁 Project Structure

```
TrustHire/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration
│   ├── database.py            # Database models
│   ├── requirements.txt       # Python dependencies
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── models/
│   │   ├── fraud_detector.py  # ML fraud detection
│   │   └── job_model.py       # Job aggregation
│   ├── scrapers/
│   │   ├── base_scraper.py    # Base scraper class
│   │   ├── linkedin_scraper.py
│   │   ├── indeed_scraper.py
│   │   └── naukri_scraper.py
│   └── utils/
│       ├── validators.py      # Input validation
│       └── text_processor.py  # Text utilities
└── frontend/
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── App.js             # Main React component
    │   ├── components/
    │   │   ├── Header.js      # Header component
    │   │   ├── SearchBar.js   # Search form
    │   │   ├── JobList.js     # Job list with filters
    │   │   ├── JobCard.js     # Individual job card
    │   │   └── Statistics.js  # Stats dashboard
    │   └── services/
    │       └── api.js         # API service
    └── package.json
```

---

## 🔧 Troubleshooting

### **Backend Issues:**

1. **Port 5000 already in use:**
   ```bash
   # Change port in .env file
   API_PORT=5001
   ```

2. **Import errors:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Database errors:**
   ```bash
   # Delete database and recreate
   rm trusthire.db
   python -c "from app import create_app; from database import db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

### **Frontend Issues:**

1. **npm install fails:**
   ```bash
   npm cache clean --force
   npm install
   ```

2. **Port 3000 in use:**
   ```bash
   # React will prompt to use 3001
   # Or set PORT in environment
   set PORT=3001 && npm start
   ```

3. **API connection error:**
   - Ensure backend is running on port 5000
   - Check CORS settings in backend config.py

---

## 🌐 Web Scraping Notes

**Important:** This project demonstrates web scraping for educational purposes. When scraping:

1. **Respect robots.txt** - Check each website's scraping policy
2. **Rate Limiting** - Built-in 2-second delays between requests
3. **User-Agent** - Professional user agent headers included
4. **Legal Compliance** - Use responsibly and ethically

**Note:** Some platforms may block scraping. For production:
- Use official APIs where available
- Implement rotating proxies
- Add CAPTCHA handling

---

## 🚀 Future Enhancements

- [ ] User authentication & saved searches
- [ ] Email alerts for new jobs
- [ ] Resume parser and job matching
- [ ] Company reviews integration
- [ ] Salary analytics dashboard
- [ ] Browser extension
- [ ] Mobile app (React Native)
- [ ] Advanced ML model training with real data
- [ ] Integration with more job platforms

---

## 📝 License

This project is for **educational purposes**. Feel free to use and modify.

---

## 👨‍💻 Developer

Built with ❤️ by **Chand**

---

## 🎉 Quick Start Summary

```bash
# Terminal 1 - Backend
cd c:\Users\chand\Documents\GitHub\TrustHire\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py

# Terminal 2 - Frontend
cd c:\Users\chand\Documents\GitHub\TrustHire\frontend
npm install
npm start

# Open: http://localhost:3000
```

**That's it! Start searching for trusted jobs! 🚀**
