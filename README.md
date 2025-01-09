# seo-analysis-tool

A Python tool for comprehensive SEO analysis that generates detailed PDF reports. Features include real-time logging, metrics analysis, and recommendations for improving website SEO performance.

## Features

- **Comprehensive SEO Analysis**: 
  - Title and meta description evaluation
  - Word count analysis
  - Link structure assessment
  - Image alt tag checking
  - Mobile-friendly detection
  - Load time measurement
  - Canonical tag verification
  
- **Professional PDF Reports**:
  - Detailed metric explanations
  - Custom formatting
  - User-friendly presentation
  - Automated recommendations

- **Advanced Features**:
  - Real-time logging
  - Error handling
  - User-friendly CLI interface
  - Automated recommendations generation
  - PDF report generation in Downloads folder

## Requirements

Ensure Python 3.6+ is installed, then run the following to install required libraries:

```bash
pip install requests beautifulsoup4 pdfkit markdown2
```

Additionally, install wkhtmltopdf:
- On macOS: `brew install wkhtmltopdf`
- On Ubuntu: `sudo apt-get install wkhtmltopdf`
- On Windows: Download from [wkhtmltopdf downloads](https://wkhtmltopdf.org/downloads.html)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/seo-analysis-tool.git
cd seo-analysis-tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the script:
```bash
python seo_analyzer.py
```

## Usage

1. Run the script
2. Enter the URL when prompted
3. Wait for analysis to complete
4. Find the generated PDF report in your Downloads folder

## Technical Details

- **HTML Parsing**: Uses BeautifulSoup4 for accurate webpage analysis
- **PDF Generation**: Utilizes pdfkit with wkhtmltopdf backend
- **Logging**: Comprehensive logging system for debugging
- **Error Handling**: Robust error handling for various edge cases
- **Metrics Analysis**: Nine key SEO metrics analyzed

## Analyzed Metrics

The tool analyzes these key SEO metrics:

- Page Title
- Meta Description
- Word Count
- Total Links
- Alt Tags
- H1 Tags
- Mobile Friendliness
- Canonical Tags
- Load Time

## Acknowledgments

- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [pdfkit](https://pypi.org/project/pdfkit/) for PDF generation
- [requests](https://docs.python-requests.org/) for HTTP requests
- [markdown2](https://pypi.org/project/markdown2/) for markdown processing

---

seo-analysis-tool © 2025 by Philip Bachas-Daunert is licensed under [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International](https://creativecommons.org/licenses/by-nc-nd/4.0/)