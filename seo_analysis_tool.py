#!/usr/bin/env python3
"""
Enhanced SEO Analysis Tool
--------------------------
This script performs a detailed SEO analysis of a given webpage,
providing recommendations and generating a PDF report.
"""

import logging
import os
from typing import Dict
from urllib.parse import urljoin, urlparse

# Import required third-party libraries
try:
    import requests
    from bs4 import BeautifulSoup
    import pdfkit
except ImportError as e:
    logging.basicConfig(level=logging.ERROR)
    logging.error(f"Missing required library: {e}")
    logging.error("Please install dependencies using: pip install requests beautifulsoup4 pdfkit")
    raise


class SEOAnalyzer:
    """
    SEO Analyzer Class
    ------------------
    Analyzes SEO metrics and generates recommendations for optimization.

    Attributes:
        base_url (str): The URL of the webpage to analyze.
        METRIC_DETAILS (dict): Descriptions and best practices for SEO metrics.
    """

    METRIC_DETAILS = {
        "Title": {
            "definition": "The title tag is the main clickable link shown in search results.",
            "importance": "A concise title improves click-through rates and ensures visibility on search engines.",
            "criteria": "Good: Under 60 characters. Bad: Over 60 characters or missing entirely."
        },
        "Meta Description": {
            "definition": "A meta description is a short summary of the page that appears in search results.",
            "importance": "It helps users decide whether to click and improves search engine visibility.",
            "criteria": "Good: 50-160 characters. Bad: Missing or over 160 characters."
        },
        "Word Count": {
            "definition": "The total amount of textual content on your webpage.",
            "importance": "Search engines favor detailed content with sufficient word count as it signals comprehensive value.",
            "criteria": "Good: 600+ words for main pages. Bad: Less than 300 words."
        },
        "Total Links": {
            "definition": "The total number of internal and external links present on your webpage.",
            "importance": "Links help distribute page authority and guide user navigation.",
            "criteria": "Good: 50-150 links for main pages. Bad: Less than 20 or more than 500 links."
        },
        "Alt Tags Missing": {
            "definition": "Alt tags are descriptive text alternatives for images on your webpage.",
            "importance": "Essential for accessibility and SEO image optimization.",
            "criteria": "Good: All images have descriptive alt tags. Bad: Any images missing alt tags."
        },
        "H1 Tags": {
            "definition": "H1 tags are primary headings that define the main topic of a webpage section.",
            "importance": "They provide structure for users and search engines to understand content hierarchy.",
            "criteria": "Good: One unique H1 tag. Bad: No H1 tag or multiple H1 tags."
        },
        "Mobile-Friendly": {
            "definition": "Indicates whether your website is optimized for mobile devices.",
            "importance": "Mobile optimization is crucial as most web traffic comes from mobile devices.",
            "criteria": "Good: Responsive design with viewport meta tag. Bad: No mobile optimization."
        },
        "Canonical Tag": {
            "definition": "A tag that tells search engines which version of a URL is the master copy.",
            "importance": "Prevents duplicate content issues and helps consolidate page authority.",
            "criteria": "Good: Properly implemented canonical URL. Bad: Missing canonical tag."
        },
        "Load Time": {
            "definition": "The time it takes for your webpage to fully load in a browser.",
            "importance": "Fast load times improve user experience and boost search engine rankings.",
            "criteria": "Good: Under 2 seconds. Bad: Over 2 seconds."
        }
    }

    def __init__(self, base_url: str, log_level: int = logging.INFO):
        self.base_url = self._format_url(base_url)
        self.session = self._setup_session()
        self.results = []
        self.errors = []
        self.recommendations = []
        self._setup_logging(log_level)

    @staticmethod
    def _format_url(url: str) -> str:
        """Ensure the input URL has a proper scheme (http/https)."""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        return url

    def _setup_logging(self, log_level: int) -> None:
        """Configure logging with the specified log level."""
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _setup_session(self) -> requests.Session:
        """Set up an HTTP session with a custom user-agent."""
        session = requests.Session()
        session.headers.update({'User-Agent': 'SEO Analyzer Bot'})
        return session

    def analyze_page(self, url: str) -> Dict:
        """Analyze SEO metrics for a given webpage."""
        try:
            self.logger.info(f"Analyzing URL: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract SEO metrics
            title = soup.title.string if soup.title else "No Title"
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_desc_content = meta_desc['content'] if meta_desc else "No Description"
            word_count = len(soup.get_text().split())
            links = soup.find_all('a', href=True)
            images = soup.find_all('img')
            missing_alt_tags = sum(1 for img in images if not img.get('alt'))
            h1_tags = len(soup.find_all('h1'))
            viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
            canonical_tag = soup.find('link', rel='canonical')
            load_time = response.elapsed.total_seconds()

            # Add character counts for title and meta description
            title_length = len(title) if title != "No Title" else 0
            meta_desc_length = len(meta_desc_content) if meta_desc_content != "No Description" else 0

            # Generate recommendations based on the extracted metrics
            self._generate_recommendations(
                title, title_length, meta_desc_content, meta_desc_length, word_count, len(links),
                missing_alt_tags, h1_tags, canonical_tag
            )

            # Return the analysis results as a dictionary
            return {
                "Title": f"{title} ({title_length} characters)",
                "Meta Description": f"{meta_desc_content} ({meta_desc_length} characters)",
                "Word Count": f"{word_count:,} words",
                "Total Links": f"{len(links):,} links",
                "Alt Tags Missing": f"{missing_alt_tags:,} images without alt tags",
                "H1 Tags": f"{h1_tags:,} H1 tags",
                "Mobile-Friendly": "Yes" if viewport_tag else "No",
                "Canonical Tag": canonical_tag['href'] if canonical_tag else "None",
                "Load Time": f"{load_time:.2f} seconds"
            }
        except Exception as e:
            self.logger.error(f"Error analyzing {url}: {e}")
            self.errors.append({"url": url, "error": str(e)})
            return {}

    def _generate_recommendations(self, title: str, title_length: int, meta_desc: str, meta_desc_length: int,
                                  word_count: int, link_count: int, missing_alt_tags: int, h1_count: int,
                                  canonical_tag) -> None:
        """
        Generates actionable recommendations for each analyzed metric, 
        including character counts for title and meta description.
        """
        # Title recommendations
        if not title or title_length > 60:
            self.recommendations.append(f"Title is too long ({title_length} characters). Keep it under 60.")
        elif title_length < 50:
            self.recommendations.append(f"Title is too short ({title_length} characters). Aim for 50-60 characters.")
        else:
            self.recommendations.append(f"Title is well-optimized ({title_length} characters).")

        # Meta description recommendations
        if not meta_desc or meta_desc_length > 160:
            self.recommendations.append(f"Meta description is too long ({meta_desc_length} characters). Shorten to 50-160.")
        elif meta_desc_length < 50:
            self.recommendations.append(f"Meta description is too short ({meta_desc_length} characters). Lengthen to 50-160.")
        else:
            self.recommendations.append(f"Meta description is optimal ({meta_desc_length} characters).")

        # Word count recommendations
        if word_count < 300:
            self.recommendations.append(f"Content is too short ({word_count} words). Aim for 300+ words.")
        else:
            self.recommendations.append(f"Content length is adequate ({word_count} words).")

        # Link recommendations
        if link_count < 20 or link_count > 500:
            self.recommendations.append(f"Link count should be between 50-150 (current: {link_count}).")
        else:
            self.recommendations.append("Link count is appropriate.")

        # Alt tag recommendations
        if missing_alt_tags > 0:
            self.recommendations.append(f"Add alt tags to {missing_alt_tags} images.")
        else:
            self.recommendations.append("All images have alt tags.")

        # H1 tag recommendations
        if h1_count != 1:
            self.recommendations.append("Ensure exactly one H1 tag is used.")
        else:
            self.recommendations.append("H1 tag usage is correct.")

        # Canonical tag recommendations
        if not canonical_tag:
            self.recommendations.append("Add a canonical tag to avoid duplicate content issues.")
        else:
            self.recommendations.append("Canonical tag is implemented.")

    def generate_html_report(self, analysis_results: Dict) -> str:
        """
        Generates an HTML report with analysis results and recommendations.
        """
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; color: #333; }
                h1, h2 { margin-bottom: 10px; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f4f4f4; text-align: center; }
                ul { margin-top: 20px; }
            </style>
        </head>
        <body>
        """
        html += f"<h1>SEO Analysis Report</h1>"
        html += f"<p><strong>URL Analyzed:</strong> {self.base_url}</p>"

        # Add metrics in a table
        html += "<h2>Analysis Results</h2>"
        html += "<table>"
        html += "<tr><th>Metric</th><th>Value</th><th>Best Practice</th></tr>"
        for metric, value in analysis_results.items():
            details = self.METRIC_DETAILS.get(metric, {})
            html += f"<tr><td>{metric}</td><td>{value}</td><td>{details.get('criteria', 'N/A')}</td></tr>"
        html += "</table>"

        # Add recommendations
        if self.recommendations:
            html += "<h2>Recommendations</h2><ul>"
            for recommendation in self.recommendations:
                html += f"<li>{recommendation}</li>"
            html += "</ul>"

        html += "</body></html>"
        return html

    def generate_pdf_from_html(self, html_content: str, filename: str) -> None:
        """
        Converts the HTML report to a PDF file.
        """
        try:
            options = {
                'page-size': 'Letter',
                'margin-top': '0.5in',
                'margin-right': '0.5in',
                'margin-bottom': '0.5in',
                'margin-left': '0.5in',
                'encoding': "UTF-8"
            }
            pdfkit.from_string(html_content, filename, options=options)
            self.logger.info(f"PDF report saved to: {filename}")
        except Exception as e:
            self.logger.error(f"Error generating PDF: {e}")
            raise

    def run_analysis(self) -> None:
        """
        Executes the full SEO analysis and generates a PDF report.
        """
        results = self.analyze_page(self.base_url)
        if not results:
            self.logger.error("Analysis failed.")
            return

        html_report = self.generate_html_report(results)
        output_path = os.path.join(os.path.expanduser("~"), "Downloads", "seo_analysis_report.pdf")
        self.generate_pdf_from_html(html_report, output_path)


def main():
    """
    Entry point of the script. Prompts the user for a URL and starts the analysis.
    """
    url = input("Enter the URL to analyze: ").strip()
    analyzer = SEOAnalyzer(base_url=url)
    analyzer.run_analysis()
    print("Analysis completed. Check your Downloads folder for the report.")


if __name__ == "__main__":
    main()