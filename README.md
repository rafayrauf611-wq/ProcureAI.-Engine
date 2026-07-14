# ProcureAI.-Engine

An AI-driven, highly scalable procurement ERP backend engineered with Django and Python 3.12. This system abstracts complex procurement workflows—from requisition and sourcing to three-way matching and financial settlement—while integrating seamless AI document ingestion and OCR capabilities.

Built with a Domain-Driven Design (DDD) architecture, this engine strictly separates business logic into a robust Service Layer, making it ready for enterprise deployment or as the core engine for an AI Automation Agency.

## ✨ Core Features

*   **Intelligent Document Ingestion:** Automatically process and classify PDFs, DOCX, XLSX, and images (Invoices, POs, Quotations, GRNs).
*   **AI Extraction & Abstraction:** Pluggable AI architecture supporting Odysseus, OpenAI, Azure, and local LLMs to extract highly structured JSON (items, SKUs, confidence scores) from unstructured documents.
*   **Advanced OCR:** Integrated with PaddleOCR (with Tesseract fallback) for highly accurate data extraction from scanned documents.
*   **Workflow Automation:** Zero-touch automation from Store Requisition to Goods Receipt Note (GRN) and Invoice Generation.
*   **Automated Three-Way Matching:** Cryptographically precise matching between Purchase Orders, GRNs, and Invoices to prevent financial leakage.
*   **Dynamic Rule Engine:** Database-driven approval routing based on dynamic thresholds (e.g., Manager, Director, CEO approvals).
*   **Asynchronous Processing:** Celery and Redis handle heavy OCR workloads, bulk uploads, and AI extraction tasks without blocking the main API thread.
*   **Comprehensive Audit Logging:** Immutable logs tracking user actions, IP addresses, and value mutations across all documents.

## 🏗️ Architecture

The codebase adheres strictly to SOLID principles and a Service Layer architecture, preventing "fat models" and keeping the Django views entirely logic-less.

```text
procurement_ai/
├── api/             # RESTful endpoints (DRF) and serializers
├── ai/              # AI client abstractions and prompt externalization
├── documents/       # Ingestion, OCR, classification, and validation services
├── inventory/       # Stock and SKU management bounded context
├── suppliers/       # Vendor and sourcing bounded context
├── procurement/     # Core workflow: Requisitions, Demands, POs, and matching
├── finance/         # Invoices and settlement
├── tasks/           # Celery asynchronous task definitions
└── config/          # Environment and Django core settings
