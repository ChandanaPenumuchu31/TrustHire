# State Chart Diagram - TrustHire Job Fraud Detection System

## 1. Job Search State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle: Application Start
    
    Idle --> InputCapture: User Enters Query
    
    InputCapture --> Validating: Submit Search
    
    Validating --> InputCapture: Invalid Input<br/>(show error)
    Validating --> Searching: Valid Input
    
    Searching --> ScrapingInProgress: Initialize Scrapers
    
    ScrapingInProgress --> ScraperActive1: Start RemoteOK
    ScrapingInProgress --> ScraperActive2: Start Remotive
    
    ScraperActive1 --> ScraperComplete1: Jobs Retrieved
    ScraperActive2 --> ScraperComplete2: Jobs Retrieved
    
    ScraperActive1 --> ScraperFailed1: API Error
    ScraperActive2 --> ScraperFailed2: API Error
    
    ScraperComplete1 --> Aggregating: Jobs Ready
    ScraperComplete2 --> Aggregating: Jobs Ready
    ScraperFailed1 --> Aggregating: Continue Without
    ScraperFailed2 --> Aggregating: Continue Without
    
    Aggregating --> Deduplicating: Jobs Merged
    Deduplicating --> AnalyzingFraud: Duplicates Removed
    
    AnalyzingFraud --> AnalyzingFraud: Process Next Job
    AnalyzingFraud --> Sorting: All Jobs Analyzed
    
    Sorting --> CalculatingStats: Jobs Sorted by Trust
    CalculatingStats --> DisplayingResults: Stats Ready
    
    DisplayingResults --> DisplayComplete: Results Rendered
    
    DisplayComplete --> ViewingDetails: User Clicks Job
    DisplayComplete --> Idle: New Search
    DisplayComplete --> Idle: Timeout
    
    ViewingDetails --> DisplayComplete: Close Details
    ViewingDetails --> Applying: Click Apply
    ViewingDetails --> Reporting: Click Report
    
    Applying --> DisplayComplete: Application Initiated
    Reporting --> SubmittingReport: Fill Report Form
    
    SubmittingReport --> DisplayComplete: Report Submitted
    SubmittingReport --> ViewingDetails: Cancel
    
    DisplayComplete --> [*]: Exit Application
    
    note right of Validating
        Validates:
        - Query length (2-200)
        - Location format
        - Experience level
    end note
    
    note right of AnalyzingFraud
        For each job:
        1. Load company data
        2. ML analysis
        3. Calculate trust score
        4. Generate verdict
    end note
```

## 2. Fraud Detection State Machine

```mermaid
stateDiagram-v2
    [*] --> Initialized: Detector Created
    
    Initialized --> LoadingCompanyDB: Load Reviews
    
    LoadingCompanyDB --> TrainingML: Reviews Loaded
    LoadingCompanyDB --> TrainingML: File Not Found<br/>(use defaults)
    
    TrainingML --> Ready: Model Trained
    
    Ready --> ReceivingJob: predict() Called
    
    ReceivingJob --> LookingUpCompany: Extract Company Name
    
    LookingUpCompany --> CompanyFound: In Database
    LookingUpCompany --> CompanyUnknown: Not Found
    
    CompanyFound --> LoadingReviews: Get Company Data
    CompanyUnknown --> CheckingSuspicious: Analyze Name
    
    CheckingSuspicious --> SuspiciousCompany: Generic/Fake Name
    CheckingSuspicious --> GeneratingData: Normal Name
    
    SuspiciousCompany --> AnalyzingDescription: Low Trust (0.2)
    GeneratingData --> AnalyzingDescription: Neutral Trust (0.5)
    LoadingReviews --> AnalyzingDescription: High Trust (0.9)
    
    AnalyzingDescription --> VectorizingText: Transform with TF-IDF
    VectorizingText --> MLPredicting: Get Feature Vector
    
    MLPredicting --> ExtractingSalary: Fraud Probability
    ExtractingSalary --> AnalyzingPatterns: Check Patterns
    
    AnalyzingPatterns --> SuspiciousSalary: Daily/Weekly Pay
    AnalyzingPatterns --> LegitSalary: Annual/Range
    AnalyzingPatterns --> NeutralSalary: Not Specified
    
    SuspiciousSalary --> CalculatingScores: Low Score (0.2)
    LegitSalary --> CalculatingScores: High Score (0.9)
    NeutralSalary --> CalculatingScores: Neutral Score (0.5)
    
    CalculatingScores --> WeightedCalculation: Apply Weights
    
    WeightedCalculation --> ApplyingRandomization: Base Score
    ApplyingRandomization --> Clamping: Add ±5%
    Clamping --> DeterminingVerdict: Score 0.15-0.95
    
    DeterminingVerdict --> HighlyTrustworthy: Score ≥ 0.75
    DeterminingVerdict --> LikelySafe: Score 0.60-0.74
    DeterminingVerdict --> ModerateRisk: Score 0.45-0.59
    DeterminingVerdict --> HighRisk: Score 0.30-0.44
    DeterminingVerdict --> ExtremeRisk: Score < 0.30
    
    HighlyTrustworthy --> GeneratingReasons: Set Verdict
    LikelySafe --> GeneratingReasons: Set Verdict
    ModerateRisk --> GeneratingReasons: Set Verdict
    HighRisk --> GeneratingReasons: Set Verdict
    ExtremeRisk --> GeneratingReasons: Set Verdict
    
    GeneratingReasons --> BuildingResponse: Add Details
    BuildingResponse --> Ready: Return Analysis
    
    Ready --> [*]: Shutdown
    
    note right of MLPredicting
        Random Forest with:
        - 20 estimators
        - Max depth: 8
        - TF-IDF features
    end note
    
    note right of WeightedCalculation
        Weights:
        - Company: 35%
        - Description: 40%
        - Salary: 15%
        - Reviews: 10%
    end note
```

## 3. Job Card Component State Machine

```mermaid
stateDiagram-v2
    [*] --> Collapsed: Initial Render
    
    Collapsed --> ExpandedDesc: Click "Read More"
    ExpandedDesc --> Collapsed: Click "Show Less"
    
    Collapsed --> ShowingAnalysis: Click "Fraud Analysis"
    ExpandedDesc --> ShowingAnalysis: Click "Fraud Analysis"
    
    ShowingAnalysis --> Collapsed: Click Again
    ShowingAnalysis --> ExpandedDesc: Click Again<br/>(if desc expanded)
    
    ShowingAnalysis --> DisplayingReviews: Reviews Available
    DisplayingReviews --> ShowingAnalysis: No More Reviews
    
    Collapsed --> ReportFormOpen: Click "Report Job"
    ShowingAnalysis --> ReportFormOpen: Click "Report Job"
    
    ReportFormOpen --> FillingForm: User Types
    FillingForm --> ValidatingForm: Click Submit
    
    ValidatingForm --> FillingForm: Validation Error
    ValidatingForm --> SubmittingReport: Valid Data
    
    SubmittingReport --> ReportSuccess: 200 OK
    SubmittingReport --> ReportError: Error Response
    
    ReportSuccess --> Collapsed: Close Notification
    ReportError --> FillingForm: Show Error
    
    ReportFormOpen --> Collapsed: Click Cancel
    
    Collapsed --> ApplyingJob: Click "Apply Now"
    ShowingAnalysis --> ApplyingJob: Click "Apply Now"
    
    ApplyingJob --> Collapsed: New Tab Opened
    
    Collapsed --> [*]: Component Unmount
    
    note right of ShowingAnalysis
        Displays:
        - Trust score details
        - Fraud reasons
        - Company verification
        - Employee reviews
    end note
```

## 4. Database Connection State Machine

```mermaid
stateDiagram-v2
    [*] --> Disconnected: Application Start
    
    Disconnected --> Connecting: Initialize Database
    
    Connecting --> Connected: Connection Success
    Connecting --> ConnectionError: Connection Failed
    
    ConnectionError --> Connecting: Retry
    ConnectionError --> [*]: Max Retries Exceeded
    
    Connected --> Idle: Ready for Queries
    
    Idle --> ExecutingQuery: Query Received
    
    ExecutingQuery --> WritingData: INSERT/UPDATE/DELETE
    ExecutingQuery --> ReadingData: SELECT
    
    WritingData --> Committing: Data Modified
    ReadingData --> ReturningResults: Data Retrieved
    
    Committing --> CommitSuccess: Changes Saved
    Committing --> CommitError: Conflict/Error
    
    CommitSuccess --> Idle: Transaction Complete
    CommitError --> RollingBack: Undo Changes
    
    RollingBack --> Idle: Rollback Complete
    ReturningResults --> Idle: Results Sent
    
    Idle --> Disconnected: Close Connection
    Connected --> Disconnected: Timeout
    
    Disconnected --> [*]: Shutdown
    
    note right of Committing
        Ensures ACID properties:
        - Atomicity
        - Consistency
        - Isolation
        - Durability
    end note
```

## 5. ML Model State Machine

```mermaid
stateDiagram-v2
    [*] --> Untrained: Model Created
    
    Untrained --> LoadingData: Load Training Samples
    
    LoadingData --> DataLoaded: 16 Samples Ready<br/>(8 fraud + 8 legit)
    LoadingData --> DataError: Load Failed
    
    DataError --> [*]: Initialization Failed
    
    DataLoaded --> Vectorizing: Fit TF-IDF
    
    Vectorizing --> VectorizerReady: 50 Features
    VectorizerReady --> Training: Fit Random Forest
    
    Training --> Trained: Model Ready
    Training --> TrainingError: Training Failed
    
    TrainingError --> LoadingData: Retry
    
    Trained --> Idle: Ready for Predictions
    
    Idle --> Predicting: predict() Called
    
    Predicting --> Transforming: Vectorize Input
    Transforming --> Classifying: Transform Complete
    
    Classifying --> ReturningProbability: Probability Calculated
    ReturningProbability --> Idle: Prediction Complete
    
    Idle --> Retraining: Retrain Requested
    Retraining --> LoadingData: Load New Data
    
    Idle --> [*]: System Shutdown
    
    note right of Training
        Random Forest Parameters:
        - Trees: 20
        - Max Depth: 8
        - Features: 50 (TF-IDF)
        - Random State: 42
    end note
```

## State Descriptions

### Job Search States
- **Idle**: Waiting for user input
- **Searching**: Active scraping in progress
- **AnalyzingFraud**: ML processing each job
- **DisplayingResults**: Showing jobs with trust scores

### Fraud Detection States
- **Ready**: Detector initialized and waiting
- **AnalyzingDescription**: ML text analysis
- **CalculatingScores**: Weighted scoring
- **GeneratingReasons**: Building detailed analysis

### Job Card States
- **Collapsed**: Minimal view
- **ShowingAnalysis**: Fraud details visible
- **ReportFormOpen**: Report modal active

### Transitions
- User actions trigger state changes
- Automatic transitions after processing
- Error states with retry capability
- Timeout transitions to idle states

### Guard Conditions
- Input validation gates
- Trust score thresholds
- Data availability checks
- Error state conditions
