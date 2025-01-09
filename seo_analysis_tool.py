#!/usr/bin/env python3
"""
Enhanced SEO Analysis Tool.
Generates a polished, user-friendly PDF report using pdfkit and includes detailed logging.
"""

import logging
import os
from typing import Dict
from urllib.parse import urljoin, urlparse
import pdfkit
import markdown2

# Import required libraries for requests and parsing HTML
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.error(f"Missing library: {e}. Please install the required libraries.")
    raise


class SEOAnalyzer:
    """
    A class to analyze a webpage's SEO performance based on various metrics.

    Attributes:
        METRIC_DETAILS (dict): Details about each SEO metric, including definitions,
                               importance, and evaluation criteria.
    """

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
        """
        Format the input URL to ensure proper structure for analysis.

        Args:
            url (str): The URL to be formatted.

        Returns:
            str: Properly formatted URL.
        """
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        if not url.endswith('/'):
            url = f"{url}/"
        return url

    def __init__(self, base_url: str, log_level: int = logging.INFO):
        """
        Initialize the SEOAnalyzer instance.

        Args:
            base_url (str): The base URL to analyze.
            log_level (int): The logging level for debugging and informational messages.
        """
        self.base_url = self.format_url(base_url)  # Format URL immediately
        self.session = self._setup_session()
        self.results = []
        self.errors = []
        self.recommendations = []
        self._setup_logging(log_level)

    def _setup_logging(self, log_level: int) -> None:
        """
        Set up the logging configuration.

        Args:
            log_level (int): The logging level (e.g., INFO, DEBUG).
        """
        logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _setup_session(self) -> requests.Session:
        """
        Set up a session for HTTP requests.

        Returns:
            requests.Session: A configured session for making HTTP requests.
        """
        session = requests.Session()
        session.headers.update({'User-Agent': 'SEO Analyzer'})
        return session

    def analyze_page(self, url: str) -> Dict:
        """
        Analyze the SEO metrics of a webpage.

        Args:
            url (str): The URL to analyze.

        Returns:
            Dict: A dictionary containing SEO metrics.
        """
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
            self._generate_recommendations(
                title, meta_desc_content, word_count, len(links),
                missing_alt_tags, h1_tags
            )

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
        """
        Generate actionable SEO recommendations based on analysis metrics.

        Args:
            title (str): The page's title tag content.
            meta_desc (str): The meta description content.
            word_count (int): Total word count on the page.
            link_count (int): Total number of links on the page.
            missing_alt_tags (int): Number of images missing alt tags.
            h1_count (int): Number of H1 tags present on the page.
        """
        if not title:
            self.recommendations.append("Add a descriptive title tag.")
        elif len(title) > 60:
            self.recommendations.append(f"Shorten your title to under 60 characters (current: {len(title)}).")

        if not meta_desc:
            self.recommendations.append("Add a meta description to improve click-through rates.")
        elif len(meta_desc) > 160:
            self.recommendations.append("Shorten your meta description to under 160 characters.")

        if word_count < 300:
            self.recommendations.append(f"Increase content to at least 300 words (current: {word_count}).")

        if link_count < 50:
            self.recommendations.append(f"Add more internal/external links. Current: {link_count}.")
        if missing_alt_tags > 0:
            self.recommendations.append(f"Add alt tags to {missing_alt_tags} images.")

        if h1_count == 0:
            self.recommendations.append("Add at least one H1 tag.")
        elif h1_count > 1:
            self.recommendations.append(f"Reduce H1 tags to one (current: {h1_count}).")

    def generate_html_report(self, analysis_results: Dict) -> str:
        """
        Generate an HTML report for the analysis.

        Args:
            analysis_results (Dict): The SEO analysis results.

        Returns:
            str: The HTML content of the report.
        """
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                h2 { color: #666; margin-top: 20px; }
                .metric { margin-bottom: 30px; }
                .recommendations { margin-top: 40px; }
            </style>
        </head>
        <body>
        """
        html += f"<h1>SEO Analysis Report</h1>"
        html += f"<p><strong>Analyzing URL:</strong> {self.base_url}</p>"

        for metric, value in analysis_results.items():
            details = self.METRIC_DETAILS.get(metric, {})
            html += f'<div class="metric">'
            html += f"<h2>{metric}</h2>"
            html += f"<p><strong>What it is:</strong> {details.get('definition', 'N/A')}</p>"
            html += f"<p><strong>Why it's important:</strong> {details.get('importance', 'N/A')}</p>"
            html += f"<p><strong>Evaluation:</strong> {value}</p>"
            html += f"<p><strong>What is good:</strong> {details.get('criteria', 'N/A')}</p>"
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
        """
        Convert the HTML report to a PDF file using pdfkit.

        Args:
            html_content (str): The HTML content to convert.
            filename (str): The path to save the PDF file.
        """
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
        """
        Run the full SEO analysis process, generate reports, and save results to a PDF file.
        """
        analysis_results = self.analyze_page(self.base_url)
        if not analysis_results:
            self.logger.error("Failed to analyze the webpage. No results available.")
            return

        html_report = self.generate_html_report(analysis_results)
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        pdf_path = os.path.join(downloads_folder, "seo_analysis_report.pdf")
        self.generate_pdf_from_html(html_report, pdf_path)


def main():
    """
    Entry point of the script. Handles user input and starts the analysis process.
    """
    url = input("Enter the URL to analyze: ").strip()
    analyzer = SEOAnalyzer(base_url=url)
    analyzer.run_analysis()


if __name__ == "__main__":
    main()