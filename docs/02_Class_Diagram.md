# Class Diagram - TrustHire Job Fraud Detection System

```mermaid
classDiagram
    class Job {
        +int id
        +string title
        +string company
        +string description
        +string location
        +string salary
        +string url
        +string platform
        +float trust_score
        +bool is_fraudulent
        +datetime posted_date
        +datetime scraped_at
        +getFraudAnalysis()
        +calculateTrustScore()
        +toJSON()
    }
    
    class UserReport {
        +int id
        +int job_id
        +string report_type
        +string reason
        +string user_email
        +datetime created_at
        +submitReport()
        +validate()
    }
    
    class SearchHistory {
        +int id
        +string query
        +string location
        +string experience
        +int results_count
        +datetime searched_at
        +saveSearch()
        +getHistory()
    }
    
    class LLMFraudDetector {
        -TfidfVectorizer vectorizer
        -RandomForestClassifier ml_model
        -dict company_reviews
        -list FRAUD_KEYWORDS
        -list POSITIVE_KEYWORDS
        -dict REVIEW_TEMPLATES
        +__init__()
        +predict(job_data) dict
        -_train_advanced_ml_model()
        -_load_company_reviews() dict
        -_analyze_description_quality(desc) float
        -_extract_salary_factor(job) float
        -_get_company_data(company) dict
        -_generate_unknown_company_data(name) dict
        +check_job_availability(url) dict
    }
    
    class JobAggregator {
        -list scrapers
        -dict search_stats
        +__init__()
        +search_all_platforms(query, location, experience) list
        +save_jobs_to_db(jobs) int
        +track_search(query, location, experience)
        +get_search_history() list
        -_deduplicate_jobs(jobs) list
        -_validate_job_data(job) bool
    }
    
    class BaseScraper {
        <<abstract>>
        #string name
        #string base_url
        #int timeout
        +scrape(query, location) list
        #_make_request(url) Response
        #_parse_job_data(data) dict
        #_validate_response(response) bool
    }
    
    class RemoteOKScraper {
        +string api_endpoint
        +scrape(query, location) list
        -_parse_api_response(data) list
        -_filter_by_keyword(jobs, query) list
    }
    
    class RemotiveScraper {
        +string api_endpoint
        +scrape(query, location) list
        -_parse_json_data(data) list
        -_extract_job_details(job) dict
    }
    
    class Config {
        +string GEMINI_API_KEY
        +bool FAST_MODE
        +bool USE_FILE_REVIEWS
        +int MAX_RESULTS_PER_PLATFORM
        +int SCRAPE_TIMEOUT
        +string DATABASE_URI
        +dict SCRAPER_CONFIGS
        +load_config()
        +validate_config()
    }
    
    class APIRoutes {
        +search_jobs(request) Response
        +report_job(request) Response
        +get_history(request) Response
        +get_statistics(request) Response
        -_validate_search_params(data) bool
        -_format_response(data) dict
    }
    
    class Validators {
        +validate_query(query) bool
        +validate_location(location) bool
        +validate_experience(experience) bool
        +sanitize_input(text) string
        +validate_email(email) bool
    }
    
    class Database {
        +SQLAlchemy db
        +create_tables()
        +drop_tables()
        +migrate()
    }
    
    class TrustScoreCalculator {
        -dict weights
        +calculate_trust_score(factors) float
        +get_verdict(score) string
        +get_trust_color(score) string
        -_apply_randomization(score) float
    }
    
    %% Relationships
    Job "1" --> "*" UserReport : has reports
    SearchHistory "1" --> "*" Job : contains
    
    JobAggregator "1" --> "*" BaseScraper : uses
    BaseScraper <|-- RemoteOKScraper : inherits
    BaseScraper <|-- RemotiveScraper : inherits
    
    LLMFraudDetector --> Job : analyzes
    LLMFraudDetector --> TrustScoreCalculator : uses
    
    APIRoutes --> JobAggregator : calls
    APIRoutes --> LLMFraudDetector : calls
    APIRoutes --> Validators : uses
    APIRoutes --> Database : accesses
    
    JobAggregator --> Database : saves to
    Config --> JobAggregator : configures
    Config --> LLMFraudDetector : configures
    
    note for LLMFraudDetector "Core ML-based fraud detection\nusing Random Forest and TF-IDF"
    note for JobAggregator "Coordinates multiple scrapers\nand aggregates results"
    note for BaseScraper "Abstract base class for\nall job scrapers"
```

## Class Descriptions

### Entity Classes

**Job**
- Represents a job posting from external platforms
- Stores all job details including trust score and fraud analysis
- Primary entity in the system

**UserReport**
- Stores user-submitted fraud reports
- Linked to specific jobs
- Helps improve fraud detection

**SearchHistory**
- Tracks user search queries
- Used for analytics and improving search

### Business Logic Classes

**LLMFraudDetector**
- Core fraud detection engine using ML
- Uses Random Forest classifier with TF-IDF vectorization
- Analyzes description, salary, company, and reviews
- Returns trust score (0.0-1.0) and detailed analysis

**JobAggregator**
- Coordinates multiple job scrapers
- Aggregates and deduplicates results
- Manages search history and statistics

**TrustScoreCalculator**
- Calculates weighted trust scores
- Applies randomization for variety
- Generates verdicts and color codes

### Scraper Classes

**BaseScraper (Abstract)**
- Base class for all job scrapers
- Defines common interface
- Handles HTTP requests and validation

**RemoteOKScraper**
- Scrapes RemoteOK API
- Filters jobs by keyword

**RemotiveScraper**
- Scrapes Remotive API
- Extracts structured job data

### Utility Classes

**Config**
- Centralized configuration management
- Stores API keys, timeouts, database URIs

**APIRoutes**
- Flask REST API endpoints
- Handles HTTP requests/responses

**Validators**
- Input validation and sanitization
- Security checks

**Database**
- SQLAlchemy database interface
- Schema management

## Key Design Patterns

1. **Singleton**: LLMFraudDetector (via get_fraud_detector)
2. **Strategy**: BaseScraper with multiple implementations
3. **Facade**: JobAggregator simplifies scraper coordination
4. **Factory**: Scraper instantiation
5. **Repository**: Database access layer
