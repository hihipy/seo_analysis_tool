#!/usr/bin/env python3
"""
Enhanced SEO Analysis Tool.
Generates a polished, user-friendly PDF report using pdfkit and includes detailed logging.
"""

import logging
import os
from urllib.parse import urljoin, urlparse
from typing import Dict
import pdfkit
import markdown2

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.error(f"Missing library: {e}. Please install the required libraries.")
    raise


class SEOAnalyzer:
    """SEO analysis tailored for non-technical audiences."""

    METRIC_DETAILS = {
        "Title": {
            "definition": "The title tag is the main clickable link shown in search results. It summarizes the page content.",
            "importance": "A concise title improves click-through rates and ensures visibility on search engines.",
            "criteria": "Good: Under 60 characters. Bad: Over 60 characters or missing entirely."
        },
        "Meta Description": {
            "definition": "A meta description is a short summary of the page that appears in search results under the title.",
            "importance": "It helps users decide whether to click and improves search engine visibility.",
            "criteria": "Good: 50-160 characters. Bad: Missing or over 160 characters."
        },
        "Word Count": {
            "definition": "Word count measures the amount of text content on a page.",
            "importance": "Search engines favor detailed content (300+ words) as it signals value to users.",
            "criteria": "Good: 300+ words. Bad: Fewer than 300 words."
        },
        "Total Links": {
            "definition": "Links refer to clickable text or images that connect to other pages, either internally or externally.",
            "importance": "Links improve navigation and boost SEO by distributing link equity.",
            "criteria": "Good: 50+ links. Bad: Fewer than 50 links."
        },
        "Alt Tags Missing": {
            "definition": "Alt tags describe images, improving accessibility and helping search engines understand the content.",
            "importance": "They are essential for visually impaired users and improve image search rankings.",
            "criteria": "Good: No missing alt tags. Bad: Missing alt tags for some or all images."
        },
        "H1 Tags": {
            "definition": "The H1 tag is the main heading of a page and describes its primary topic.",
            "importance": "It helps users and search engines quickly understand the page's focus.",
            "criteria": "Good: At least one H1 tag. Bad: No H1 tags."
        },
        "Mobile-Friendly": {
            "definition": "A mobile-friendly site is optimized for viewing on phones and tablets.",
            "importance": "Most users browse on mobile devices, and search engines prioritize mobile-friendly websites.",
            "criteria": "Good: Viewport meta tag present. Bad: Viewport meta tag missing."
        },
        "Canonical Tag": {
            "definition": "Canonical tags prevent duplicate content by indicating the preferred URL for search engines.",
            "importance": "They ensure proper indexing and avoid ranking penalties for duplicate content.",
            "criteria": "Good: Canonical tag present. Bad: Canonical tag missing."
        },
        "Load Time": {
            "definition": "Load time measures how quickly a page fully loads in a browser.",
            "importance": "Fast load times improve user experience and boost search engine rankings.",
            "criteria": "Good: Under 2 seconds. Bad: Over 2 seconds."
        }
    }

    @staticmethod
    def format_url(url: str) -> str:
        """Format URL to ensure proper structure."""
        url = url.strip()
        
        if not url.startswith(('http://', 'https://')):
            print(f"URL '{url}' needs 'https://' prefix for proper analysis.")
            url = f"https://{url.rstrip('/')}/"
            print(f"Using: {url}")
        elif not url.endswith('/'):
            url = f"{url}/"
            print(f"Added trailing slash. Using: {url}")
            
        return url

    def __init__(self, base_url: str, log_level: int = logging.INFO):
        """Initialize the SEOAnalyzer."""
        self.base_url = self.format_url(base_url)  # Format URL immediately
        self.session = self._setup_session()
        self.results = []
        self.errors = []
        self.recommendations = []
        self._setup_logging(log_level)

    def _setup_logging(self, log_level: int) -> None:
        """Set up logging configuration."""
        logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _setup_session(self) -> requests.Session:
        """Set up requests session."""
        session = requests.Session()
        session.headers.update({'User-Agent': 'SEO Analyzer'})
        return session

    def analyze_page(self, url: str) -> Dict:
        """Analyze the SEO metrics of a webpage."""
        try:
            self.logger.info(f"Analyzing: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
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

            # Generate recommendations
            self._generate_recommendations(title, meta_desc_content, word_count, len(links), 
                                       missing_alt_tags, h1_tags)

            # Format values for better readability
            load_time_formatted = f"{load_time:.2f} seconds"
            mobile_friendly_status = "Yes" if viewport_tag else "No"

            return {
                "Title": title,
                "Meta Description": meta_desc_content,
                "Word Count": f"{word_count:,} words",
                "Total Links": f"{len(links):,} links",
                "Alt Tags Missing": f"{missing_alt_tags:,} images without alt tags",
                "H1 Tags": f"{h1_tags:,} H1 tags",
                "Mobile-Friendly": mobile_friendly_status,
                "Canonical Tag": canonical_tag['href'] if canonical_tag else "None",
                "Load Time": load_time_formatted
            }
        except Exception as e:
            self.logger.error(f"Error analyzing {url}: {e}")
            self.errors.append({"url": url, "error": str(e)})
            return {}

    def _generate_recommendations(self, title: str, meta_desc: str, word_count: int,
                               link_count: int, missing_alt_tags: int, h1_count: int) -> None:
        """Generate recommendations based on analysis."""
        # Title recommendations
        if not title or title == "No Title":
            self.recommendations.append("Add a title tag to your page.")
        elif len(title) > 60:
            self.recommendations.append(f"Shorten your title from {len(title)} to under 60 characters.")

        # Meta description recommendations
        if meta_desc == "No Description":
            self.recommendations.append("Add a meta description to improve click-through rates.")
        elif len(meta_desc) > 160:
            self.recommendations.append("Shorten your meta description to under 160 characters.")
        elif len(meta_desc) < 50:
            self.recommendations.append("Expand your meta description to at least 50 characters.")

        # Content recommendations
        if word_count < 300:
            self.recommendations.append(f"Increase content length from {word_count} to at least 300 words.")

        # Link recommendations
        if link_count < 50:
            self.recommendations.append(f"Add more internal/external links. Current: {link_count}, recommended: 50+")

        # Image recommendations
        if missing_alt_tags > 0:
            self.recommendations.append(f"Add alt tags to {missing_alt_tags} images.")

        # H1 recommendations
        if h1_count == 0:
            self.recommendations.append("Add an H1 tag to clearly indicate your page's main topic.")
        elif h1_count > 1:
            self.recommendations.append(f"Consolidate your {h1_count} H1 tags into a single H1 tag.")

    def generate_html_report(self, analysis_results: Dict) -> str:
        """Generate an HTML report for the analysis."""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                h2 { color: #666; margin-top: 20px; }
                .metric { margin-bottom: 30px; }
                .recommendations { margin-top: 40px; }
                .alert { color: #d32f2f; }
                .success { color: #388e3c; }
            </style>
        </head>
        <body>
        """
        
        html += f"<h1>SEO Analysis Report</h1>"
        html += f"<p><strong>Analyzing URL:</strong> {self.base_url}</p>"

        if not analysis_results:
            html += '<p class="alert">Error: Unable to analyze the URL. Please verify the URL is accessible.</p>'
            return html

        for metric, value in analysis_results.items():
            details = self.METRIC_DETAILS[metric]  # We know the metric exists in our dictionary
            html += f'<div class="metric">'
            html += f"<h2>{metric}</h2>"
            html += f"<p><strong>What it is:</strong> {details['definition']}</p>"
            html += f"<p><strong>Why it's important:</strong> {details['importance']}</p>"
            html += f"<p><strong>Evaluation:</strong> {value}</p>"
            html += f"<p><strong>What is good:</strong> {details['criteria']}</p>"
            html += "</div>"

        if self.recommendations:
            html += '<div class="recommendations">'
            html += "<h2>Recommendations</h2>"
            html += "<ul>"
            for rec in self.recommendations:
                html += f"<li>{rec}</li>"
            html += "</ul>"
            html += "</div>"

        html += "</body></html>"
        return html

    def generate_pdf_from_html(self, html_content: str, filename: str) -> None:
        """Convert HTML to PDF using pdfkit."""
        try:
            options = {
                'page-size': 'Letter',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None
            }
            pdfkit.from_string(html_content, filename, options=options)
            self.logger.info(f"PDF successfully saved to: {filename}")
        except Exception as e:
            self.logger.error(f"Error generating PDF: {e}")
            raise

    def run_analysis(self) -> None:
        """Run the analysis and generate reports."""
        analysis_results = self.analyze_page(self.base_url)
        html_report = self.generate_html_report(analysis_results)
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        pdf_path = os.path.join(downloads_folder, "seo_analysis_report.pdf")
        self.generate_pdf_from_html(html_report, pdf_path)


def main():
    """Entry point of the script."""
    while True:
        try:
            url = input("Enter the URL to analyze: ").strip()
            analyzer = SEOAnalyzer(base_url=url)
            analyzer.run_analysis()
            break
        except requests.exceptions.RequestException as e:
            print(f"\nError accessing URL: {e}")
            print("Please try again with a valid URL.")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please try again with a different URL.")


if __name__ == "__main__":
    main()