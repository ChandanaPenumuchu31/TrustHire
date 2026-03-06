# TrustHire UML Diagrams - Complete Documentation

This directory contains comprehensive UML diagrams for the TrustHire Job Fraud Detection System.

## 📚 Diagram Index

### 1. [Use Case Diagram](01_UseCase_Diagram.md)
**Purpose**: Shows all system use cases and actor interactions

**Key Content**:
- 14 use cases (10 for Job Seekers, 4 for Administrators)
- Primary actors: Job Seeker, Administrator
- Secondary actors: External Job APIs, ML Fraud Detector, Company Reviews DB
- Relationships: Include, Extend, Association

**View When**: Understanding system functionality and user requirements

---

### 2. [Class Diagram](02_Class_Diagram.md)
**Purpose**: Depicts system architecture and class relationships

**Key Content**:
- 15+ classes across Entity, Business Logic, Scraper, and Utility layers
- Key classes: Job, LLMFraudDetector, JobAggregator, BaseScraper
- Relationships: Inheritance, Association, Composition, Dependency
- Design patterns: Singleton, Strategy, Facade, Factory, Repository

**View When**: Understanding code structure and object relationships

---

### 3. [Sequence Diagram](03_Sequence_Diagram.md)
**Purpose**: Shows time-ordered interactions between components

**Key Content**:
- 4 detailed sequence flows:
  1. Main job search flow (with parallel scraping)
  2. View job details flow
  3. Report fraudulent job flow
  4. ML model training flow
- Timing considerations and error handling
- Message flow with parameters and return values

**View When**: Understanding component interactions and message flow

---

### 4. [Collaboration Diagram](04_Collaboration_Diagram.md)
**Purpose**: Emphasizes object relationships and message passing

**Key Content**:
- 5 collaboration scenarios:
  1. Job search collaboration
  2. Fraud detection collaboration
  3. View job details collaboration
  4. Report submission collaboration
  5. System initialization collaboration
- Numbered message flows
- Object responsibilities

**View When**: Understanding how components cooperate to accomplish tasks

---

### 5. [Activity Diagram](05_Activity_Diagram.md)
**Purpose**: Illustrates workflow and business logic flow

**Key Content**:
- 4 detailed activity flows:
  1. Complete job search process (with parallel activities)
  2. Fraud detection process (with ML analysis)
  3. Report submission process
  4. System initialization process
- Decision points and guard conditions
- Parallel activities (scrapers, ML processing)
- Error handling paths

**View When**: Understanding business processes and workflows

---

### 6. [State Chart Diagram](06_StateChart_Diagram.md)
**Purpose**: Models state transitions of system components

**Key Content**:
- 5 state machines:
  1. Job search state machine (9 states)
  2. Fraud detection state machine (20+ states)
  3. Job card component state machine (8 states)
  4. Database connection state machine (7 states)
  5. ML model state machine (10 states)
- State transitions and guard conditions
- Events triggering transitions

**View When**: Understanding component lifecycle and state management

---

### 7. [Component Diagram](07_Component_Diagram.md)
**Purpose**: Shows system's physical and logical components

**Key Content**:
- 3 layers: Frontend (React), Backend (Flask), Data (SQLite)
- 20+ components across all layers
- Component interfaces (Provided/Required)
- Technology stack details
- Deployment architecture

**View When**: Understanding system architecture and component dependencies

---

### 8. [Deployment Diagram](08_Deployment_Diagram.md)
**Purpose**: Depicts physical deployment architecture

**Key Content**:
- 4 tiers: Client, Application Server (Windows), Data, External Services
- Network topology and protocols
- Hardware/software requirements
- Resource requirements (RAM, CPU, Storage, Bandwidth)
- Startup sequence
- Production deployment recommendations

**View When**: Planning deployment or understanding infrastructure needs

---

## 🗺️ Quick Navigation by Purpose

### For Developers
1. **Start Here**: [Class Diagram](02_Class_Diagram.md) - Understand code structure
2. **Then**: [Sequence Diagram](03_Sequence_Diagram.md) - See how components interact
3. **Finally**: [Component Diagram](07_Component_Diagram.md) - Grasp overall architecture

### For Business Analysts
1. **Start Here**: [Use Case Diagram](01_UseCase_Diagram.md) - Understand features
2. **Then**: [Activity Diagram](05_Activity_Diagram.md) - See workflows
3. **Finally**: [Collaboration Diagram](04_Collaboration_Diagram.md) - Understand cooperation

### For System Administrators
1. **Start Here**: [Deployment Diagram](08_Deployment_Diagram.md) - Infrastructure setup
2. **Then**: [Component Diagram](07_Component_Diagram.md) - Component dependencies
3. **Finally**: [State Chart Diagram](06_StateChart_Diagram.md) - Component lifecycles

### For QA/Testers
1. **Start Here**: [Use Case Diagram](01_UseCase_Diagram.md) - Test scenarios
2. **Then**: [Activity Diagram](05_Activity_Diagram.md) - Test workflows
3. **Finally**: [Sequence Diagram](03_Sequence_Diagram.md) - Integration points

---

## 📊 Diagram Technologies

All diagrams use **Mermaid** syntax for rendering:
- ✅ GitHub native support
- ✅ VS Code preview (with Mermaid extension)
- ✅ Can be exported to PNG/SVG
- ✅ Easy to maintain and version control

### Viewing Diagrams

**In GitHub**: Diagrams render automatically in markdown preview

**In VS Code**: Install "Markdown Preview Mermaid Support" extension

**Export to Image**: Use [Mermaid Live Editor](https://mermaid.live/)

---

## 🎯 System Overview from Diagrams

### Key Components Identified
1. **Frontend**: React application (SearchBar, JobCard, JobList, Statistics)
2. **Backend**: Flask API (Routes, JobAggregator, LLMFraudDetector)
3. **ML Engine**: Random Forest + TF-IDF fraud detection
4. **Scrapers**: RemoteOK, Remotive (parallel execution)
5. **Database**: SQLite (Job, UserReport, SearchHistory tables)
6. **Data Files**: company_reviews.json (13 companies)

### Critical Flows
1. **Search Flow**: User → Frontend → API → Scrapers → ML Analysis → Results
2. **Fraud Detection**: Job Data → ML Model → Trust Score → Verdict
3. **Report Flow**: User Report → Validation → Database → Confirmation

### Technologies
- **Frontend**: React 18, Axios, CSS3
- **Backend**: Flask 3.0, Python 3.13
- **ML**: scikit-learn 1.8, TF-IDF, Random Forest
- **Database**: SQLite with SQLAlchemy
- **APIs**: RemoteOK, Remotive (HTTPS)

### Performance Metrics
- **Startup**: ~2 seconds (ML training)
- **Search**: 2-8 seconds (parallel scraping)
- **Per-Job Analysis**: <100ms (file-based)
- **Total Analysis (10 jobs)**: ~1 second

---

## 📝 Document Maintenance

**Last Updated**: March 5, 2026

**Version**: 1.0

**Maintained By**: Development Team

**Update Frequency**: After major system changes

**Feedback**: For corrections or additions, create an issue in the repository

---

## 🔗 Related Documentation

- [README.md](../README.md) - Project overview
- [FRAUD_DETECTION_COMPLETE.md](../FRAUD_DETECTION_COMPLETE.md) - ML implementation details
- [requirements.txt](../backend/requirements.txt) - Python dependencies
- [package.json](../frontend/package.json) - Node dependencies

---

**Note**: These diagrams represent the current state of the TrustHire system as of March 2026. They should be updated when significant architectural or functional changes are made.
