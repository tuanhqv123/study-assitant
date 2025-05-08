# StudyAssistant - AI-Enhanced Learning Platform

**Project Documentation**  
**Version:** 1.0  
**Date:** May 2025

---

## Executive Summary

StudyAssistant is an AI-powered educational platform designed to support university students with their academic journey. The system integrates cutting-edge AI technology with university data systems to provide students with instant access to academic information, study resources, and personalized learning assistance.

The platform leverages generative AI to understand and respond to student queries in natural language, while also connecting to university systems to provide real-time information about schedules, grades, and course materials. Additionally, the system includes innovative features like web search integration and document analysis to enhance the learning experience.

This document provides a comprehensive overview of the StudyAssistant platform, including system architecture, features, technologies, database design, and future development roadmap.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [User Stories](#2-user-stories)
3. [System Architecture](#3-system-architecture)
4. [Key Features](#4-key-features)
5. [Technology Stack](#5-technology-stack)
6. [Database Structure](#6-database-structure)
7. [Implementation Details](#7-implementation-details)
8. [AI Integration](#8-ai-integration)
9. [Security Measures](#9-security-measures)
10. [Future Enhancements](#10-future-enhancements)
11. [Conclusion](#11-conclusion)

---

## 1. Project Overview

### 1.1 Background

University students face numerous challenges in managing their academic workload, accessing course materials, and understanding complex subjects. Traditional educational support systems often lack immediate availability, personalization, and the ability to integrate varied information sources.

StudyAssistant addresses these challenges by providing an AI-powered platform that:

- Answers academic questions instantly
- Provides real-time access to university data (schedules, grades)
- Analyzes uploaded documents to help with studying
- Performs web searches for additional research
- Offers personalized learning assistance

### 1.2 Project Goals

1. Create a seamless integration between AI technology and university systems
2. Provide accurate, relevant responses to student queries
3. Enable document-based learning with intelligent content analysis
4. Enhance research capabilities with targeted web search
5. Deliver a user-friendly interface accessible to all students
6. Ensure data security and privacy compliance

### 1.3 Target Users

- University students (primarily PTIT students)
- Faculty members seeking to provide additional support to students
- Educational administrators monitoring student needs and questions

---

## 2. User Stories

### Student User Stories

1. **Academic Information Access**

   - As a student, I want to quickly access my class schedule so I can plan my day effectively.
   - As a student, I want to check my grades without navigating complex university portals.
   - As a student, I want to know about upcoming assignments and deadlines.

2. **AI-Assisted Learning**

   - As a student, I want to ask questions about course concepts and receive clear explanations.
   - As a student, I want to upload lecture notes and ask specific questions about the content.
   - As a student, I want to receive supplementary learning resources related to my questions.

3. **Research Assistance**

   - As a student, I want to search for academic information without leaving the platform.
   - As a student, I want to see credible sources for information provided by the system.
   - As a student, I want to save search results for future reference.

4. **User Experience**
   - As a student, I want a clean, intuitive interface that makes it easy to interact with the AI.
   - As a student, I want to access previous conversations to review information.
   - As a student, I want to use the system on both desktop and mobile devices.

---

## 3. System Architecture

StudyAssistant employs a modern, scalable architecture designed for reliability, performance, and security.

### 3.1 High-Level Architecture

```
┌─────────────┐    ┌──────────────────────────────┐    ┌─────────────────┐
│             │    │                              │    │                 │
│  Frontend   │◄───┤           Backend            │◄───┤  External APIs  │
│  (React)    │    │          (Python)            │    │                 │
│             │    │                              │    │                 │
└─────────────┘    └──────────────────────────────┘    └─────────────────┘
       ▲                        ▲                              ▲
       │                        │                              │
       │                        ▼                              │
       │            ┌──────────────────────────┐               │
       │            │                          │               │
       └───────────┤        Supabase          ├───────────────┘
                    │  (Database & Storage)    │
                    │                          │
                    └──────────────────────────┘
```

### 3.2 Component Breakdown

1. **Frontend Layer**

   - React-based web application
   - Responsive design using Tailwind CSS
   - State management with React context/hooks
   - Client-side routing

2. **Backend Layer**

   - Python Flask API server
   - Authentication and authorization services
   - Integration with AI services (OpenRouter)
   - Business logic implementation
   - Web scraping and content processing

3. **Database Layer**

   - Supabase (PostgreSQL)
   - User data management
   - Chat history storage
   - Document management
   - Vector embeddings for semantic search

4. **External Integrations**
   - OpenRouter for AI model access
   - University API for academic data
   - Brave Search API for web search functionality
   - Web content extraction services

---

## 4. Key Features

### 4.1 Conversational AI Interface

- Natural language understanding and generation
- Context-aware conversation handling
- Support for complex academic queries
- Multi-language support (Vietnamese and English)
- Intelligent query classification

### 4.2 University Data Integration

- Real-time schedule information
- Grade retrieval and analysis
- Course information and syllabi access
- Personalized academic data presentation
- Secure credential management

### 4.3 Document Analysis

- Support for multiple document formats (PDF, DOCX, TXT)
- Intelligent chunking and semantic indexing
- Relevant content extraction
- Question answering based on document content
- Document management system

### 4.4 Web Search Integration

- Intelligent query formulation
- High-quality source selection
- Web content extraction and summarization
- Source attribution and citation
- Result persistence for future reference

### 4.5 User Experience

- Clean, minimalist interface
- Responsive design for all devices
- Markdown rendering for rich text responses
- Code syntax highlighting
- Session management and history

---

## 5. Technology Stack

### 5.1 Frontend Technologies

- **Framework**: React.js
- **Styling**: Tailwind CSS
- **UI Components**: Custom components with shadcn/ui
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Code Quality**: ESLint, Prettier

### 5.2 Backend Technologies

- **Framework**: Python Flask
- **API**: RESTful endpoints
- **Authentication**: JWT with Supabase Auth
- **AI Integration**: OpenRouter API
- **Web Scraping**: BeautifulSoup, httpx
- **Text Processing**: Regular expressions, custom algorithms
- **Asynchronous Processing**: asyncio

### 5.3 Database & Storage

- **Database**: Supabase (PostgreSQL)
- **File Storage**: Supabase Storage
- **Vector Database**: PostgreSQL with pgvector extension
- **Query Engine**: SQL with specialized functions

### 5.4 External Services

- **AI Model Access**: OpenRouter API (multiple AI models)
- **Web Search**: Brave Search API
- **University Data**: PTIT API integration
- **Content Extraction**: Custom web scraper service

### 5.5 DevOps

- **Version Control**: Git/GitHub
- **Deployment**: Docker
- **Hosting**: Vercel (frontend), Railway (backend)
- **Monitoring**: Custom logging system

---

## 6. Database Structure

### 6.1 Entity Relationship Diagram

```
┌───────────────────┐         ┌────────────────────┐
│   chat_sessions   │         │      messages      │
├───────────────────┤         ├────────────────────┤
│ id (UUID)         │◄────────┤ id (BIGINT)        │
│ user_id (UUID)    │         │ chat_id (UUID)     │
│ created_at        │         │ role               │
│ agent_id          │         │ content            │
└───────────────────┘         │ created_at         │
        ▲                     │ sources (JSONB)    │
        │                     └────────────────────┘
        │
        │
┌───────────────────┐         ┌────────────────────┐         ┌────────────────────┐
│      users        │         │     user_files     │         │    file_chunks     │
├───────────────────┤         ├────────────────────┤         ├────────────────────┤
│ id (UUID)         │◄────────┤ id (UUID)          │◄────────┤ id (UUID)          │
│ email             │         │ user_id (UUID)     │         │ file_id (UUID)     │
│ created_at        │         │ filename           │         │ chunk_index        │
└───────────────────┘         │ content_type       │         │ content            │
        ▲                     │ file_size_bytes    │         │ embedding (VECTOR) │
        │                     │ status             │         │ created_at         │
        │                     │ created_at         │         └────────────────────┘
        │                     └────────────────────┘
        │
┌───────────────────┐
│  university_creds │
├───────────────────┤
│ user_id (UUID)    │
│ univ_username     │
│ univ_password     │
│ access_token      │
│ token_expiry      │
│ name              │
│ refresh_token     │
└───────────────────┘
```

### 6.2 Table Descriptions

#### 6.2.1 User Management

- **users**: Managed by Supabase Auth, contains user authentication data
- **university_credentials**: Stores encrypted credentials for accessing university systems

#### 6.2.2 Chat System

- **chat_sessions**: Represents individual chat conversations
- **messages**: Stores all messages in each chat session, including sources for web search results

#### 6.2.3 Document Management

- **user_files**: Metadata for user-uploaded documents
- **file_chunks**: Content chunks and vector embeddings for semantic search

### 6.3 Key Relationships

- Each user can have multiple chat sessions
- Each chat session contains multiple messages
- Users can upload multiple documents
- Each document is divided into multiple chunks for processing
- University credentials are linked directly to users

---

## 7. Implementation Details

### 7.1 Backend Services Architecture

The backend is organized into specialized services, each with specific responsibilities:

```
app/
├── config/            # Configuration files and constants
├── lib/               # External service integrations
├── routes/            # API endpoints
├── services/          # Business logic services
│   ├── ai_service.py           # AI integration and response generation
│   ├── file_service.py         # Document processing and management
│   ├── query_classifier.py     # Query type classification
│   ├── schedule_service.py     # University schedule integration
│   ├── ptit_auth_service.py    # University authentication
│   ├── web_search_service.py   # Web search functionality
│   └── web_scraper_service.py  # Web content extraction
└── utils/             # Utility functions and helpers
```

### 7.2 Key Processing Flows

#### 7.2.1 Web Search and Content Extraction

1. User submits a query requiring research
2. System classifies the query as needing web search
3. `web_search_service` calls Brave Search API to find relevant results
4. Top results are sent to `web_scraper_service` for content extraction
5. Content is processed, cleaned, and limited to avoid token limits
6. Combined results are sent to AI for processing
7. Response with sources is returned to the user and saved in the database

#### 7.2.2 Document Analysis

1. User uploads a document through the interface
2. `file_service` processes the document:
   - Extracts text content
   - Divides content into semantic chunks
   - Generates vector embeddings for each chunk
   - Stores chunks and embeddings in the database
3. User asks questions about the document
4. System performs vector similarity search to find relevant chunks
5. Retrieved chunks are sent to AI as context for answering
6. AI responds with information from the document

#### 7.2.3 University Data Retrieval

1. User asks about schedule, grades, or other academic data
2. System classifies the query as university data related
3. `ptit_auth_service` authenticates with university systems
4. Appropriate service retrieves requested data
5. Data is formatted and sent to AI for natural language presentation
6. AI generates a human-friendly response with the requested information

---

## 8. AI Integration

### 8.1 AI Service Implementation

The `ai_service.py` module is the core integration point for AI functionality, providing:

- Connection to OpenRouter API for accessing various AI models
- Context management for different query types
- Specialized handling for chat, file, and web search contexts
- Error handling and fallback mechanisms
- Response formatting and post-processing

### 8.2 AI Models

The system uses various models via OpenRouter:

- **Primary Model**: Mistral Small 24B (mistralai/mistral-small-3.1-24b-instruct)
- **Fallback Models**: Various OpenRouter-provided alternatives

### 8.3 Query Classification

The system intelligently classifies user queries to determine the appropriate processing path:

- **General Knowledge**: Handled directly by AI
- **University Data**: Routed to appropriate university API
- **Document Questions**: Processed with document context
- **Web Search Queries**: Sent through search and scraping pipeline
- **UML/Diagram Requests**: Processed with specialized prompting

### 8.4 Content Optimization

To maximize AI response quality while managing token usage:

- Web content is extracted and limited to 300 characters per source
- Document chunks are created with semantic boundaries
- System prompts are optimized for different query types
- Response formatting ensures readability and usefulness

---

## 9. Security Measures

### 9.1 Authentication & Authorization

- JWT-based authentication via Supabase Auth
- Role-based access control
- Session management and timeout
- Secure credential handling

### 9.2 Data Protection

- University credentials encrypted in database
- Sensitive data never exposed to frontend
- Content filtering and sanitization
- Rate limiting to prevent abuse

### 9.3 AI Safety

- Query classification to limit scope
- Content filtering for inappropriate requests
- System prompts designed to prevent prompt injection
- Error handling to prevent information leakage

---

## 10. Future Enhancements

### 10.1 Short-term Roadmap (3-6 Months)

1. **Enhanced Web Content Processing**

   - Improved content extraction algorithms
   - Better content summarization
   - Support for more complex web pages

2. **Mobile Application**

   - Native mobile applications for iOS and Android
   - Push notifications for important updates
   - Offline capabilities for document access

3. **Advanced Document Processing**
   - Support for more document formats (ePub, LaTex)
   - Image and diagram extraction from documents
   - Mathematics and formula support

### 10.2 Long-term Vision (6-12 Months)

1. **Collaborative Learning**

   - Shared document spaces
   - Group chat with AI assistance
   - Peer learning recommendations

2. **Personalized Learning Paths**

   - Analysis of student performance patterns
   - Customized study recommendations
   - Learning style adaptation

3. **Expanded University Integrations**
   - Support for additional universities
   - Integration with learning management systems
   - Faculty portal for monitoring and assistance

---

## 11. Conclusion

StudyAssistant represents a significant advancement in educational technology, bringing together AI capabilities, university data systems, and advanced content processing to create a comprehensive learning assistant.

The current implementation demonstrates the viability and value of this approach, with features that directly address student needs for academic information, learning assistance, and research support. The modular architecture ensures the system can continue to evolve with new capabilities and integrations.

As AI technology advances and educational needs evolve, StudyAssistant is positioned to grow into an increasingly valuable tool for students and educational institutions, enhancing the learning experience through intelligent, personalized support.

---

## Appendices

### Appendix A: API Endpoints

| Endpoint             | Method | Description               |
| -------------------- | ------ | ------------------------- |
| /auth/login          | POST   | User authentication       |
| /auth/signup         | POST   | User registration         |
| /chat                | POST   | Send message to AI        |
| /chat/sessions       | GET    | List user's chat sessions |
| /chat/sessions/:id   | GET    | Get specific chat session |
| /files/upload        | POST   | Upload document           |
| /files/list          | GET    | List user's documents     |
| /files/:id           | GET    | Get document details      |
| /university/schedule | GET    | Get user's schedule       |
| /university/grades   | GET    | Get user's grades         |

### Appendix B: Database Schema SQL

```sql
-- Example schema for key tables

-- Chat sessions
CREATE TABLE public.chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    agent_id TEXT
);

-- Messages
CREATE TABLE public.messages (
    id BIGINT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    role TEXT,
    content TEXT,
    chat_id UUID REFERENCES public.chat_sessions(id),
    sources JSONB
);

-- User files
CREATE TABLE public.user_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    filename TEXT NOT NULL,
    content_type TEXT,
    file_size_bytes BIGINT,
    status TEXT DEFAULT 'processing'::text,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- File chunks with vector embeddings
CREATE TABLE public.file_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES public.user_files(id),
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR,
    created_at TIMESTAMPTZ DEFAULT now()
);
```
