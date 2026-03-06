# Sequence Diagram - TrustHire Job Search and Fraud Detection

## 1. Main Job Search Flow

```mermaid
sequenceDiagram
    actor User as Job Seeker
    participant Frontend as React Frontend
    participant API as Flask API
    participant JobAgg as JobAggregator
    participant Scraper1 as RemoteOK Scraper
    participant Scraper2 as Remotive Scraper
    participant FraudDet as LLMFraudDetector
    participant ML as ML Model
    participant DB as Database
    participant ReviewDB as Company Reviews
    
    User->>Frontend: Enter search query<br/>(keyword, location, experience)
    Frontend->>Frontend: Validate inputs
    Frontend->>API: POST /api/search<br/>{query, location, experience}
    
    API->>API: Validate request parameters
    API->>JobAgg: search_all_platforms(query, location, experience)
    
    par Parallel Scraping
        JobAgg->>Scraper1: scrape(query, location)
        Scraper1->>Scraper1: Make API request
        Scraper1->>Scraper1: Filter by keyword
        Scraper1-->>JobAgg: Return jobs list
        
        JobAgg->>Scraper2: scrape(query, location)
        Scraper2->>Scraper2: Make API request
        Scraper2->>Scraper2: Parse JSON data
        Scraper2-->>JobAgg: Return jobs list
    end
    
    JobAgg->>JobAgg: Deduplicate jobs
    JobAgg->>JobAgg: Validate job data
    JobAgg-->>API: Return aggregated jobs
    
    API->>API: Initiate fraud detection
    
    loop For each job
        API->>FraudDet: predict(job_data)
        
        FraudDet->>ReviewDB: _get_company_data(company_name)
        ReviewDB-->>FraudDet: Return company reviews & ratings
        
        FraudDet->>ML: _analyze_description_quality(description)
        ML->>ML: Transform with TF-IDF
        ML->>ML: Predict with Random Forest
        ML-->>FraudDet: Return fraud probability
        
        FraudDet->>FraudDet: _extract_salary_factor(job)
        FraudDet->>FraudDet: Calculate weighted trust score
        FraudDet->>FraudDet: Add randomization (±5%)
        FraudDet->>FraudDet: Generate detailed reasons
        
        FraudDet-->>API: Return fraud analysis<br/>{trust_score, verdict, reasons, reviews}
        
        API->>API: Merge fraud data into job
    end
    
    API->>JobAgg: track_search(query, location)
    JobAgg->>DB: Save to SearchHistory
    DB-->>JobAgg: Confirm saved
    
    API->>API: Sort by trust score
    API->>API: Generate statistics
    API-->>Frontend: Return JSON response<br/>{jobs, count, summary}
    
    Frontend->>Frontend: Render JobCard components
    Frontend->>Frontend: Display trust scores
    Frontend->>Frontend: Show company reviews
    Frontend->>User: Display search results
```

## 2. View Job Details Flow

```mermaid
sequenceDiagram
    actor User as Job Seeker
    participant Frontend as React Frontend
    participant JobCard as JobCard Component
    
    User->>JobCard: Click "Fraud Analysis Details"
    JobCard->>JobCard: Toggle showDetailedReasons
    JobCard->>JobCard: Render fraud reasons list
    JobCard->>JobCard: Display company verification
    JobCard->>JobCard: Show employee review samples
    JobCard-->>User: Display detailed analysis<br/>with reviews and trust score
    
    User->>JobCard: Click "Apply Now"
    JobCard->>JobCard: Open job URL in new tab
```

## 3. Report Fraudulent Job Flow

```mermaid
sequenceDiagram
    actor User as Job Seeker
    participant Frontend as React Frontend
    participant API as Flask API
    participant Validators as Validators
    participant DB as Database
    
    User->>Frontend: Click "Report Job"
    Frontend->>Frontend: Show report form modal
    User->>Frontend: Fill report form<br/>(type, reason, email)
    User->>Frontend: Submit report
    
    Frontend->>Frontend: Validate form data
    Frontend->>API: POST /api/report<br/>{job_id, type, reason, email}
    
    API->>Validators: validate_email(email)
    Validators-->>API: Valid/Invalid
    
    alt Email valid
        API->>DB: Create UserReport entry
        DB-->>API: Report saved (ID)
        API-->>Frontend: {success: true, message}
        Frontend-->>User: Show success notification
    else Email invalid
        API-->>Frontend: {success: false, error}
        Frontend-->>User: Show error message
    end
```

## 4. ML Model Training Flow (Admin)

```mermaid
sequenceDiagram
    actor Admin as Administrator
    participant System as System
    participant FraudDet as LLMFraudDetector
    participant ML as ML Components
    
    Admin->>System: Initialize/Restart System
    System->>FraudDet: __init__()
    
    FraudDet->>FraudDet: Load company_reviews.json
    FraudDet->>FraudDet: _train_advanced_ml_model()
    
    FraudDet->>FraudDet: Create training data<br/>(8 fraud + 8 legit samples)
    FraudDet->>ML: TfidfVectorizer.fit_transform(samples)
    ML-->>FraudDet: Vectorized features
    
    FraudDet->>ML: RandomForestClassifier.fit(X, y)
    ML->>ML: Train 20 trees, max depth 8
    ML-->>FraudDet: Trained model
    
    FraudDet-->>System: Detector initialized
    System-->>Admin: System ready<br/>ML model trained
```

## Timing Considerations

- **Job Search**: 2-8 seconds (depending on scrapers)
- **Fraud Analysis per Job**: <100ms (file-based, no web scraping)
- **Total Analysis for 10 jobs**: ~1 second
- **ML Model Training**: ~2 seconds (on startup)
- **Database Operations**: <50ms

## Error Handling

1. **Scraper Failure**: Continue with other scrapers
2. **Fraud Detection Error**: Return default trust score (0.5)
3. **Database Error**: Log error, continue operation
4. **API Timeout**: Return partial results
5. **Validation Error**: Return 400 Bad Request
