# PDF Translation System

A sophisticated PDF translation system powered by Large Language Models (LLMs) that maintains the original document's layout and formatting while providing high-quality translations.

## Features

- **Layout Preservation**: Maintains the original PDF's formatting, including text positioning, font sizes, and colors
- **High-Quality Translation**: Leverages advanced LLMs (GPT-4, GPT-3.5) for accurate translations
- **Parallel Processing**: Uses concurrent API calls for efficient translation of individual text blocks
- **Support for Complex PDFs**: Handles academic papers, technical documents, and other complex PDF layouts
- **Font Support**: Includes built-in support for Chinese fonts and vertical text rendering
- **Version Options**: Offers both basic and advanced translation versions

## System Architecture

The system consists of two main layers:

### Interface Layer
- PDF Upload/Download Module
- PDF Analysis Module
- Text Block Module
- Translation Module
- Token Calculation Module

### Foundation Layer
- LLM Services (OpenAI, Anthropic)
- Storage System (Cloud Storage)

## Technical Requirements

- Python 3.8+
- PyMuPDF (fitz)
- OpenAI API access
- Required Python packages:
  ```
  PyMuPDF
  openai
  requests
  typing
  ```

## Key Components

### 1. PDF Processing
- Uses PyMuPDF for PDF parsing and manipulation
- Extracts text while preserving formatting information
- Handles both horizontal and vertical text layouts

### 2. Translation System
- Implements parallel processing for text block translation
- Maintains document structure through JSON intermediates
- Uses optimized prompts for academic/technical content

### 3. Document Reconstruction
- Preserves original PDF layout and formatting
- Handles font embedding and text positioning
- Supports various text orientations and layouts

## Installation

1. Clone the repository
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   export OPENAI_API_KEY="your_api_key"
   ```

## Usage

1. Upload a PDF file (max 20MB)
2. Select translation model (Basic/Advanced)
3. Wait for processing
4. Download translated PDF

## PDF Text Extraction Process

The system follows these steps:
1. Extracts text blocks from source PDF and saves to JSON
2. Removes text from PDF to create template
3. Processes JSON content for translation
4. Writes translated text back to PDF template

## Technical Details

### PyMuPDF Usage
- Used for PDF parsing and manipulation
- Supports complex PDF structures
- Handles text extraction and insertion
- Maintains formatting information

### Text Block Processing
- Calculates text block dimensions and orientation
- Handles vertical text detection (height/width ratio > 10)
- Implements adaptive font sizing

## Limitations & Future Improvements

Current limitations:
- Maximum file size: 20MB
- Source language: English only
- Target language: Simplified Chinese only
- May have issues with complex mathematical formulas or special characters

Planned improvements:
- Enhanced PDF parsing capabilities
- Support for additional languages
- Improved handling of technical content
- OCR integration for scanned documents
- Real-time translation preview
- Custom terminology management
