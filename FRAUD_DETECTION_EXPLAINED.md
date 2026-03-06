# 🛡️ TrustHire Fraud Detection System - Complete Explanation

## Overview
TrustHire uses an advanced AI-powered fraud detection system that analyzes every job posting across **3 critical dimensions** to calculate a **Trust Score (0-100%)**.

---

## 🔍 The 3-Step Fraud Detection Process

### **STEP 1: COMPANY VERIFICATION (40% Weight)**

#### What It Does:
The system verifies if the company is legitimate by:

1. **✅ Verified Company Database Check**
   - Checks against a database of 50+ known legitimate companies
   - Companies like: Google, Microsoft, Amazon, TCS, Infosys, Wipro, etc.
   - **Result:** If found → 95% confidence (HIGHLY TRUSTED)

2. **🔍 Company Name Analysis**
   - Checks for **FAKE indicators**:
     - Generic names: "Confidential Company", "Top MNC", "Leading Firm"
     - Placeholder names: "Name Withheld", "Not Disclosed", "HR Solutions"
   - **Result:** If fake indicator found → 0% confidence (REJECTED)

3. **🏢 Legal Structure Verification**
   - Checks for proper company suffixes:
     - Private Limited, Pvt Ltd, LLC, Inc, Corporation
     - Technologies, Solutions, Services, Systems
   - **Result:** Proper suffix → +25% confidence

4. **🌐 Online Presence Check**
   - Searches for company online presence:
     - Official website (.com, .in, .co domains)
     - LinkedIn company page
     - Wikipedia entry
     - News mentions
   - **Result:** Online presence found → +20-40% confidence

5. **⭐ Company Reviews (Simulated - Can be made real)**
   - Currently uses algorithmic simulation
   - **In production, can scrape real reviews from:**
     - **Glassdoor:** Employee reviews, company ratings (1-5 stars)
     - **Indeed:** Company ratings and reviews
     - **Google Reviews:** Public company feedback
     - **AmbitionBox:** India-specific company reviews
   - **Result:** Good reviews (>3.5 stars) → Increases confidence

#### Scoring Logic:
```
Company Confidence = 0%
+ Verified Database Match: +95%
+ Proper Legal Suffix: +25%
+ Online Presence: +20-40%
+ Website Found: +15%

Final Result:
- 95%+ = Verified Large Company ✅
- 60-80% = Legitimate Company ✅
- 40-60% = Moderate Confidence ⚠️
- 0-40% = Cannot Verify ❌
- 0% = FAKE Company ❌
```

#### Impact on Trust Score:
- Company NOT verified → **-40% from trust score**
- Company verified but low confidence → **-20% from trust score**
- Company verified with high confidence → **No penalty**

---

### **STEP 2: JOB DESCRIPTION ANALYSIS (50% Weight)**

#### What It Does:
Analyzes the job description for fraud patterns using **3 detection methods**:

#### **A. Keyword Analysis (40+ Fraud Keywords)**
Scans for suspicious phrases:
- **Financial Scams:**
  - "guaranteed income", "get rich quick", "unlimited earning"
  - "easy money", "no experience needed", "$10000/week"
- **Payment Scams:**
  - "pay upfront", "registration fee", "training fee required"
  - "advance payment", "processing fee", "joining fee"
  - "Western Union", "wire transfer", "cryptocurrency"
- **Urgency Scams:**
  - "urgent hiring", "act now", "limited spots", "hire immediately"
- **Personal Info Theft:**
  - "bank details", "social security", "personal information required"
- **MLM/Pyramid Schemes:**
  - "mlm opportunity", "pyramid scheme", "recruitment fee"

**Scoring:** Each keyword found → +5% fraud score

---

#### **B. Pattern Matching (8 Suspicious Patterns)**
Uses regex to detect:

1. **Unrealistic Salaries:**
   - `$5000+ per week`, `₹50000+ per day`
   - **Why it's suspicious:** Real jobs pay monthly/yearly, not daily
   
2. **Free Email Addresses:**
   - `contact@gmail.com`, `hr@yahoo.com`, `jobs@hotmail.com`
   - **Why it's suspicious:** Real companies use official domains (company.com)
   
3. **Shortened URLs:**
   - `bit.ly`, `tinyurl.com`, `goo.gl`
   - **Why it's suspicious:** Hides the real destination, often phishing
   
4. **Chat App Interviews:**
   - "WhatsApp interview", "Telegram contact", "Hangouts interview"
   - **Why it's suspicious:** Professional companies use Zoom/Teams/official platforms
   
5. **Excessive Urgency:**
   - "Call now!", "Apply now!", "Limited time offer!"
   - **Why it's suspicious:** Creates false urgency to make you act without thinking
   
6. **Contact Numbers in Description:**
   - `Contact: 9876543210` directly in job post
   - **Why it's suspicious:** Professional postings use application systems
   
7. **Indian Currency Scams:**
   - "2 lakh per week", "5 crore per month"
   - **Why it's suspicious:** Unrealistic compensation for timeframe
   
8. **Data Entry/Copy-Paste Jobs:**
   - Often associated with scams that ask for registration fees

**Scoring:** Each pattern found → +8% fraud score

---

#### **C. Description Quality Analysis**

1. **Length Check:**
   - Description < 100 characters → +15% fraud score
   - **Why:** Real jobs have detailed descriptions

2. **Grammar & Professionalism:**
   - ALL CAPS text → +10% fraud score
   - Excessive exclamation marks (>5) → +10% fraud score
   - **Why:** Professional companies write properly

3. **Company Name Check:**
   - Missing company name → +20% fraud score
   - Company name < 3 characters → +20% fraud score
   - **Why:** Legitimate jobs always mention the company

4. **Salary Analysis:**
   - Compares mentioned salary with industry standards
   - Flags unrealistic amounts for experience level
   - Checks for "pay to apply" requirements

---

#### Scoring Logic:
```
Fraud Score = 0%
+ Each fraud keyword: +5%
+ Each suspicious pattern: +8%
+ Short description: +15%
+ Bad grammar: +10%
+ Missing company: +20%

Maximum Fraud Score: 100%
```

#### Impact on Trust Score:
- Fraud score multiplied by 0.5 (50% weight)
- Example: 60% fraud score → **-30% from trust score**

---

### **STEP 3: JOB AVAILABILITY CHECK (10% Weight)**

#### What It Does:
Visits the actual job URL to verify if it's still active

1. **HTTP Status Check:**
   - **200 OK:** Job page loads successfully
   - **404 Not Found:** Job has been removed
   - **403 Forbidden:** Access denied (possible expired)
   - **500 Error:** Server issues

2. **Content Analysis:**
   - Scans page for indicators:
     - ✅ Active: "Apply now", "Submit application"
     - ❌ Closed: "Job closed", "Position filled", "Expired", "No longer accepting"

3. **Redirect Check:**
   - Follows redirects to final destination
   - Checks if redirect goes to homepage (often means job removed)

#### Scoring Logic:
```
Job Availability:
- Active (200 + accepting applications) → No penalty
- Expired/Closed → -10% from trust score
- Cannot verify (errors) → -5% from trust score
```

---

## 📊 FINAL TRUST SCORE CALCULATION

### Formula:
```
Trust Score = 100%

Step 1: Company Verification (40% weight)
- Company NOT verified → -40%
- Company low confidence → -20%
- Company verified → No penalty

Step 2: Job Description Analysis (50% weight)
- Fraud Score × 0.5 → Deduct from trust score
- Example: 60% fraud → -30%

Step 3: Job Availability (10% weight)
- Job expired → -10%
- Cannot verify → -5%

FINAL = Trust Score (0% to 100%)
```

### Example Calculations:

#### **Example 1: Legitimate Job (Google)**
```
Starting Score: 100%

Company Verification:
- Found in verified database (Google)
- Confidence: 95%
- Penalty: -0%
- Score: 100%

Description Analysis:
- No fraud keywords found
- Professional description
- Fraud Score: 0%
- Penalty: -0%
- Score: 100%

Job Availability:
- Status 200 OK, active
- Penalty: -0%

FINAL TRUST SCORE: 100% ✅ HIGHLY TRUSTED
```

#### **Example 2: Suspicious Job**
```
Starting Score: 100%

Company Verification:
- Company: "Confidential HR Solutions"
- Fake indicator found
- Confidence: 0%
- Penalty: -40%
- Score: 60%

Description Analysis:
- Found: "urgent hiring", "guaranteed income", "registration fee"
- Found: Gmail contact, WhatsApp interview
- Fraud Score: 45%
- Penalty: -22.5%
- Score: 37.5%

Job Availability:
- Status 404, job removed
- Penalty: -10%

FINAL TRUST SCORE: 27.5% ❌ HIGH RISK - LIKELY FRAUD
```

---

## 🎯 Trust Score Thresholds

| Score Range | Verdict | Meaning | Action |
|-------------|---------|---------|--------|
| **85-100%** | ✅ HIGHLY TRUSTED | Verified company, no red flags, active job | **SAFE TO APPLY** |
| **70-84%** | ✅ TRUSTED | Company verified, minimal concerns | **PROCEED WITH CONFIDENCE** |
| **50-69%** | ⚠️ MODERATE | Some verification, minor red flags | **VERIFY DETAILS FIRST** |
| **30-49%** | ⚠️ HIGH CAUTION | Multiple red flags detected | **RESEARCH THOROUGHLY** |
| **0-29%** | ❌ HIGH RISK | Likely fraudulent, many red flags | **DO NOT APPLY** |

---

## 🔧 How It Works in the System

### When You Search for Jobs:

1. **Job Scraping:**
   - System fetches jobs from RemoteOK and Remotive
   
2. **Fraud Analysis (for EACH job):**
   ```python
   for each job:
       # Step 1: Verify Company (40%)
       company_verification = verify_company_online(job.company)
       
       # Step 2: Analyze Description (50%)
       fraud_analysis = analyze_job_description(job.description)
       
       # Step 3: Check Availability (10%)
       availability = check_job_url(job.url)
       
       # Calculate Final Score
       trust_score = calculate_trust_score(
           company_verification,
           fraud_analysis,
           availability
       )
       
       job.trust_score = trust_score
   ```

3. **Results Displayed:**
   - Jobs sorted by trust score (highest first)
   - Each job shows:
     - Trust score percentage
     - Verification badge
     - Fraud warnings (if any)

---

## 🌐 Company Review Scraping (Future Enhancement)

### Current State:
- Uses **simulated reviews** (algorithmic)
- Provides realistic ratings for demonstration

### Future Implementation:
To scrape **real company reviews**, integrate with:

#### **1. Glassdoor Scraping**
```python
def scrape_glassdoor_reviews(company_name):
    url = f"https://www.glassdoor.com/Reviews/{company_name}"
    # Parse HTML to extract:
    # - Overall rating (1-5 stars)
    # - Number of reviews
    # - CEO approval rating
    # - Pros and cons
    return {
        'rating': 4.2,
        'review_count': 5423,
        'recommend': 85%
    }
```

#### **2. Indeed Company Reviews**
```python
def scrape_indeed_reviews(company_name):
    url = f"https://www.indeed.com/cmp/{company_name}/reviews"
    # Parse HTML to extract:
    # - Star rating
    # - Work-life balance score
    # - Job security score
    return {
        'rating': 3.9,
        'work_life_balance': 3.5
    }
```

#### **3. Google Reviews**
```python
def scrape_google_reviews(company_name):
    # Use Google Places API or scrape search results
    # Extract business rating
    return {
        'rating': 4.5,
        'total_reviews': 1234
    }
```

#### **4. AmbitionBox (India)**
```python
def scrape_ambitionbox_reviews(company_name):
    url = f"https://www.ambitionbox.com/reviews/{company_name}"
    # Parse for India-specific company data
    return {
        'rating': 3.8,
        'salary_satisfaction': 3.5
    }
```

---

## 📈 What Makes a Job Trustworthy?

### ✅ Green Flags (High Trust):
- Company in verified database
- Proper company legal structure
- Professional job description (>200 chars)
- Realistic salary for role/experience
- Company website and LinkedIn presence
- Uses official email domain
- Clear job requirements and responsibilities
- Interview through professional platforms

### 🚩 Red Flags (Low Trust):
- Generic/hidden company name
- No online presence found
- Asks for upfront payment
- Unrealistic salary promises
- Free email address for contact
- WhatsApp/Telegram interviews
- Urgent hiring pressure
- Very short job description
- Multiple fraud keywords
- Job listing expired/removed

---

## 🛠️ Technical Implementation

### Files Involved:

1. **`backend/models/fraud_detector.py`**
   - Main fraud detection logic
   - Company verification
   - Pattern matching
   - Trust score calculation

2. **`backend/api/routes.py`**
   - `/api/search` endpoint applies fraud detection to all jobs
   - Returns jobs with trust scores

3. **`frontend/src/components/JobCard.js`**
   - Displays trust score badge
   - Shows fraud warnings
   - Color-codes based on trust level

---

## 📝 Summary

**TrustHire's fraud detection is a 3-layer security system:**

1. **🏢 Company Layer (40%):** Is the company real and legitimate?
2. **📄 Description Layer (50%):** Does the job description have fraud indicators?
3. **🔗 Availability Layer (10%):** Is the job still active?

**Result:** Every job gets a **0-100% Trust Score** that tells you exactly how safe it is to apply.

---

## 🚀 Benefits

- **Protects job seekers** from scams and fraud
- **Saves time** by highlighting trustworthy jobs
- **Provides transparency** with detailed fraud reasoning
- **Real-time verification** of companies and jobs
- **Continuous learning** from fraud patterns

---

**Status:** ✅ Fully operational and analyzing every job!
