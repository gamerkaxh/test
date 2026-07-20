#!/usr/bin/env python3
"""
Pure Python PDF generator for Harshit Vanya's AI/ML Engineer Resume.
No external dependencies required - generates PDF using raw PDF specification.
Optimized for 2-page resume layout.
"""

class SimplePDF:
    """Minimal PDF generator using raw PDF objects - compact layout."""
    
    def __init__(self):
        self.objects = []
        self.pages = []
        self.current_page_content = []
        self.y_position = 810
        self.left_margin = 40
        self.right_margin = 555
        self.page_width = 595
        self.page_height = 842
        
    def _add_object(self, content):
        self.objects.append(content)
        return len(self.objects)
    
    def _escape_text(self, text):
        text = text.replace('\\', '\\\\')
        text = text.replace('(', '\\(')
        text = text.replace(')', '\\)')
        return text
    
    def _new_page(self):
        if self.current_page_content:
            self.pages.append('\n'.join(self.current_page_content))
        self.current_page_content = []
        self.y_position = 810
    
    def _check_page_break(self, needed=12):
        if self.y_position - needed < 30:
            self._new_page()
    
    def add_title(self, text, size=20):
        self._check_page_break()
        escaped = self._escape_text(text)
        text_width = len(text) * size * 0.48
        x = max(self.left_margin, (self.page_width - text_width) / 2)
        self.current_page_content.append(
            f'BT /F1 {size} Tf {x:.1f} {self.y_position:.1f} Td ({escaped}) Tj ET'
        )
        self.y_position -= size + 3

    def add_subtitle(self, text, size=12):
        self._check_page_break()
        escaped = self._escape_text(text)
        text_width = len(text) * size * 0.45
        x = max(self.left_margin, (self.page_width - text_width) / 2)
        self.current_page_content.append(
            f'BT /F1 {size} Tf {x:.1f} {self.y_position:.1f} Td ({escaped}) Tj ET'
        )
        self.y_position -= size + 3

    def add_contact_line(self, text, size=8.5):
        self._check_page_break()
        escaped = self._escape_text(text)
        text_width = len(text) * size * 0.43
        x = max(self.left_margin, (self.page_width - text_width) / 2)
        self.current_page_content.append(
            f'BT /F2 {size} Tf {x:.1f} {self.y_position:.1f} Td ({escaped}) Tj ET'
        )
        self.y_position -= size + 3

    def add_hr(self):
        self.current_page_content.append(
            f'0.3 0.3 0.3 RG 0.8 w {self.left_margin} {self.y_position:.1f} m {self.right_margin} {self.y_position:.1f} l S'
        )
        self.y_position -= 6

    def add_section_header(self, text, size=11):
        self._check_page_break(20)
        self.y_position -= 5
        escaped = self._escape_text(text)
        self.current_page_content.append(
            f'BT /F1 {size} Tf {self.left_margin:.1f} {self.y_position:.1f} Td ({escaped}) Tj ET'
        )
        line_y = self.y_position - 3
        self.current_page_content.append(
            f'0.3 0.3 0.3 RG 0.4 w {self.left_margin} {line_y:.1f} m {self.right_margin} {line_y:.1f} l S'
        )
        self.y_position -= size + 7

    def add_bold_text(self, text, size=8.5):
        self._check_page_break()
        escaped = self._escape_text(text)
        self.current_page_content.append(
            f'BT /F1 {size} Tf {self.left_margin:.1f} {self.y_position:.1f} Td ({escaped}) Tj ET'
        )
        self.y_position -= size + 3

    def add_text(self, text, size=8.5, indent=0):
        self._check_page_break()
        escaped = self._escape_text(text)
        x = self.left_margin + indent
        self.current_page_content.append(
            f'BT /F2 {size} Tf {x:.1f} {self.y_position:.1f} Td ({escaped}) Tj ET'
        )
        self.y_position -= size + 2.5

    def add_bullet(self, text, size=8.5):
        self._check_page_break(20)
        bullet_indent = 10
        text_indent = 18
        max_chars = int((self.right_margin - self.left_margin - text_indent) / (size * 0.43))
        
        # Add bullet
        x = self.left_margin + bullet_indent
        self.current_page_content.append(
            f'BT /F2 {size} Tf {x:.1f} {self.y_position:.1f} Td (\\267) Tj ET'
        )
        
        # Word wrap
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line += (" " + word if current_line else word)
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # First line
        if lines:
            escaped = self._escape_text(lines[0])
            x = self.left_margin + text_indent
            self.current_page_content.append(
                f'BT /F2 {size} Tf {x:.1f} {self.y_position:.1f} Td ({escaped}) Tj ET'
            )
            self.y_position -= size + 2.5
        
        # Continuation lines
        for line in lines[1:]:
            self._check_page_break()
            escaped = self._escape_text(line)
            x = self.left_margin + text_indent
            self.current_page_content.append(
                f'BT /F2 {size} Tf {x:.1f} {self.y_position:.1f} Td ({escaped}) Tj ET'
            )
            self.y_position -= size + 2.5

    def add_space(self, height=4):
        self.y_position -= height

    def add_job_header(self, title, company, dates):
        self._check_page_break(24)
        escaped_title = self._escape_text(title)
        self.current_page_content.append(
            f'BT /F1 9.5 Tf {self.left_margin:.1f} {self.y_position:.1f} Td ({escaped_title}) Tj ET'
        )
        escaped_dates = self._escape_text(dates)
        date_x = self.right_margin - len(dates) * 4.2
        self.current_page_content.append(
            f'BT /F2 8.5 Tf {date_x:.1f} {self.y_position:.1f} Td ({escaped_dates}) Tj ET'
        )
        self.y_position -= 12
        escaped_company = self._escape_text(company)
        self.current_page_content.append(
            f'BT /F2 8.5 Tf {self.left_margin:.1f} {self.y_position:.1f} Td ({escaped_company}) Tj ET'
        )
        self.y_position -= 11

    def add_project_header(self, title, duration):
        self._check_page_break(20)
        escaped_title = self._escape_text(title)
        self.current_page_content.append(
            f'BT /F1 9 Tf {self.left_margin:.1f} {self.y_position:.1f} Td ({escaped_title}) Tj ET'
        )
        escaped_dur = self._escape_text(duration)
        dur_x = self.right_margin - len(duration) * 4.2
        self.current_page_content.append(
            f'BT /F2 8.5 Tf {dur_x:.1f} {self.y_position:.1f} Td ({escaped_dur}) Tj ET'
        )
        self.y_position -= 12

    def generate(self, filename):
        if self.current_page_content:
            self.pages.append('\n'.join(self.current_page_content))
        
        pdf_objects = []
        pdf_objects.append(b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n')
        
        num_pages = len(self.pages)
        page_obj_start = 5
        page_refs = ' '.join([f'{page_obj_start + i*2} 0 R' for i in range(num_pages)])
        pdf_objects.append(f'2 0 obj\n<< /Type /Pages /Kids [{page_refs}] /Count {num_pages} >>\nendobj\n'.encode())
        
        pdf_objects.append(b'3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>\nendobj\n')
        pdf_objects.append(b'4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>\nendobj\n')
        
        for i, page_content in enumerate(self.pages):
            page_obj_num = page_obj_start + i * 2
            content_obj_num = page_obj_num + 1
            
            page_obj = (
                f'{page_obj_num} 0 obj\n'
                f'<< /Type /Page /Parent 2 0 R '
                f'/MediaBox [0 0 {self.page_width} {self.page_height}] '
                f'/Contents {content_obj_num} 0 R '
                f'/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> '
                f'>>\nendobj\n'
            )
            pdf_objects.append(page_obj.encode())
            
            stream_data = page_content.encode('latin-1', errors='replace')
            content_obj = (
                f'{content_obj_num} 0 obj\n'
                f'<< /Length {len(stream_data)} >>\n'
                f'stream\n'
            ).encode() + stream_data + b'\nendstream\nendobj\n'
            pdf_objects.append(content_obj)
        
        with open(filename, 'wb') as f:
            f.write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
            
            offsets = []
            for obj in pdf_objects:
                offsets.append(f.tell())
                f.write(obj)
            
            xref_offset = f.tell()
            f.write(b'xref\n')
            f.write(f'0 {len(pdf_objects) + 1}\n'.encode())
            f.write(b'0000000000 65535 f \n')
            for offset in offsets:
                f.write(f'{offset:010d} 00000 n \n'.encode())
            
            f.write(f'trailer\n<< /Size {len(pdf_objects) + 1} /Root 1 0 R >>\n'.encode())
            f.write(b'startxref\n')
            f.write(f'{xref_offset}\n'.encode())
            f.write(b'%%EOF\n')


def build_resume():
    """Build the complete resume PDF - optimized for 2 pages."""
    pdf = SimplePDF()
    
    # === HEADER ===
    pdf.add_title("Harshit Vanya", 20)
    pdf.add_subtitle("AI / ML Engineer", 12)
    pdf.add_space(2)
    pdf.add_contact_line("+91-9755106375 | harshitvanyagmer@gmail.com | Bhopal, India | 1+ Year Experience")
    pdf.add_hr()
    
    # === PROFESSIONAL SUMMARY ===
    pdf.add_section_header("PROFESSIONAL SUMMARY")
    pdf.add_text("AI/ML Engineer with hands-on experience designing, building, and deploying end-to-end AI-powered systems including LLM-based", 8.5)
    pdf.add_text("agentic workflows, RAG pipelines, and production-grade ML solutions across AWS, Azure, Snowflake, and Databricks. Proven track", 8.5)
    pdf.add_text("record delivering config-driven AI/ML pipelines with CI/CD automation, leveraging Python, PySpark, LangChain, LlamaIndex, and", 8.5)
    pdf.add_text("vector databases. Recognized for leadership as Data Team Lead, rapidly prototyping AI-native solutions in Agile environments.", 8.5)
    
    # === KEY SKILLS ===
    pdf.add_section_header("KEY SKILLS")
    pdf.add_bold_text("AI/ML & GenAI: LLMs | RAG Pipelines | Agent Frameworks (LangChain, LlamaIndex, LangGraph, AutoGen) | Prompt Engineering", 8)
    pdf.add_text("Transformer Models | Embeddings | Fine-Tuning | Vector DBs (Pinecone, pgvector, ChromaDB) | Hugging Face | OpenAI API | Azure OpenAI", 8)
    pdf.add_space(2)
    pdf.add_bold_text("Data & Cloud: PySpark | Python | SQL | Kafka | Airflow | Snowflake | Databricks | AWS (Lambda, SQS, S3, Bedrock) | Azure (AKS,", 8)
    pdf.add_text("DevOps, OpenAI) | Docker | CI/CD | Kubernetes | MLflow | Model Drift Detection | Hallucination Detection | Custom Eval Harnesses", 8)
    
    # === WORK EXPERIENCE ===
    pdf.add_section_header("WORK EXPERIENCE")
    
    pdf.add_job_header("Associate Data Engineer / AI-ML Engineer", "CloudNexus DigiWeb Services Pvt. Ltd.", "Mar 2026 - Jun 2026")
    pdf.add_bullet("Designed and deployed end-to-end metadata management tool with AI-powered data cataloging for GEICO enterprise client, automating pipeline governance with CI/CD on Azure Kubernetes Service (AKS), reducing manual cataloging effort by 70%.")
    pdf.add_bullet("Built RAG-based intelligent document retrieval system using LangChain, Azure OpenAI embeddings, and pgvector, achieving 92% retrieval accuracy across 50K+ enterprise documents with sub-2s query latency.")
    pdf.add_bullet("Developed LLM-powered agentic workflow for automated data quality assessment using LangGraph, reducing validation turnaround from 4 hours to 15 minutes per pipeline run.")
    pdf.add_bullet("Refactored Microsoft Fabric data pipeline for Canadian Cancer Society, improving modularity by 40% and reducing failures by 60%.")
    pdf.add_bullet("Implemented config-driven ingestion with AI-assisted anomaly detection, reducing manual intervention by 85%, scaling to 10M+ records/day.")
    pdf.add_bullet("Promoted to Data Team Lead - coordinated delivery for 5 engineers, code reviews, and mentorship in Agile sprints.")
    pdf.add_bullet("Built custom LLM evaluation frameworks including hallucination detection and factual grounding, achieving 95% alignment with human evaluators.")
    pdf.add_bullet("Researched and prototyped emerging frameworks (LangChain, LlamaIndex, AutoGen) for continuous AI engineering improvement.")
    
    pdf.add_space(3)
    pdf.add_job_header("AI/ML Intern", "Cloud Nexus", "Sep 2025 - Mar 2026")
    pdf.add_bullet("Supported LLM integration, model development, and pipeline implementation across 8+ production AI/ML projects.")
    pdf.add_bullet("Improved ML model accuracy by 18% through hyperparameter tuning and feature engineering on real-world applications.")
    pdf.add_bullet("Built transformer-based NLP models for text classification and entity extraction with 89% F1 score on production data.")
    pdf.add_bullet("Implemented vector database solutions (Pinecone, ChromaDB) for semantic search handling 100K+ document embeddings.")
    
    # === PAGE 2 ===
    pdf._new_page()
    
    # === PROJECTS ===
    pdf.add_section_header("PROJECTS")
    
    pdf.add_project_header("Enterprise RAG Pipeline with Agentic Retrieval", "4 Months")
    pdf.add_bullet("Built end-to-end RAG pipeline with multi-agent orchestration using LangChain and LangGraph for enterprise knowledge management.")
    pdf.add_bullet("Implemented hybrid retrieval (dense + sparse) with Pinecone vector DB, achieving 94% recall@10, 40% improvement over BM25 baseline.")
    pdf.add_bullet("Designed agent planning loops with tool calling, memory modules, and multi-step reasoning for complex query resolution.")
    pdf.add_bullet("Integrated Cohere Rerank and freshness pipelines, reducing hallucination rate by 65%, improving factual accuracy to 91%.")
    pdf.add_bullet("Deployed on AWS (Lambda, API Gateway, SQS) for event-driven processing, handling 5K+ queries/day with p99 latency < 3s.")
    
    pdf.add_space(3)
    pdf.add_project_header("Real-Time WiFi/Hotspot Network Monitoring Platform", "5 Months")
    pdf.add_bullet("Built real-time monitoring capturing device info and domains via TShark packet analysis, processing 1M+ packets/hour.")
    pdf.add_bullet("Streamed logs through Apache Kafka (3 partitions, 10K msgs/sec) into Databricks Delta tables for analytics.")
    pdf.add_bullet("Delivered interactive Streamlit dashboard with ML-based anomaly detection for live device activity visualization.")
    
    pdf.add_space(3)
    pdf.add_project_header("Heavy Equipment Damage Detection (AI/ML - Computer Vision)", "5 Months")
    pdf.add_bullet("Developed AI/ML pipeline using ResNet-50 and YOLOv8 for damage assessment, achieving 93% accuracy across 5 categories.")
    pdf.add_bullet("Engineered event-driven validation layer using AWS Lambda + SQS, processing 2K+ images/day from Snowflake and S3.")
    pdf.add_bullet("Implemented config-based architecture enabling reusable data ingestion across 12+ data sources.")
    
    pdf.add_space(3)
    pdf.add_project_header("LLM-Powered Salesforce Marketing Cloud Integration", "5 Months")
    pdf.add_bullet("Developed scalable integration platform using Python, AWS services, and LLM-assisted content generation for SFMC.")
    pdf.add_bullet("Implemented SOAP/REST API integrations with AI-powered campaign optimization, automating sync for 500K+ customer records.")
    pdf.add_bullet("Built monitoring with CloudWatch for error handling, retries, and model performance, achieving 99.5% uptime.")
    
    pdf.add_space(3)
    pdf.add_project_header("AI Agent for Automated Code Review & Documentation", "3 Months")
    pdf.add_bullet("Built autonomous AI agent using LangChain + GPT-4 for code review, doc generation, and tech debt identification.")
    pdf.add_bullet("Implemented tool-calling patterns for Git integration and static analysis, reviewing 200+ PRs with 88% acceptance rate.")
    pdf.add_bullet("Designed evaluation framework with custom metrics for code quality and hallucination-free documentation generation.")
    
    # === EDUCATION ===
    pdf.add_section_header("EDUCATION")
    pdf.add_job_header("B.Tech / B.E. | Computer Science and Engineering (CSE)", "Sagar Institute of Science Technology and Research, Bhopal | Grade: 6.5/10", "2026")
    pdf.add_text("12th - Madhya Pradesh | 74% (2022)    |    10th - Madhya Pradesh | 89% (2020)", 8.5)
    
    # === CERTIFICATIONS ===
    pdf.add_section_header("CERTIFICATIONS")
    pdf.add_text("LangChain & LLM Application Development  |  Azure AI Fundamentals (AI-900)  |  AWS Cloud Practitioner  |  Databricks Lakehouse", 8.5)
    
    # === ACHIEVEMENTS ===
    pdf.add_section_header("ACHIEVEMENTS")
    pdf.add_bullet("Promoted to Data Team Lead at CloudNexus within first year for strong technical delivery and AI innovation.")
    pdf.add_bullet("AI Hackathon Winner: Built LLM-powered data quality agent that reduced pipeline failures by 45%.")
    
    # === ADDITIONAL INFO ===
    pdf.add_section_header("ADDITIONAL INFORMATION")
    pdf.add_text("Hobbies: Technical Blogging, Open Source Contribution, Running, AI Research    |    Languages: English, Hindi", 8.5)
    pdf.add_text("LinkedIn: https://linkedin.com/in/harshit-vanya    |    GitHub: https://github.com/Harshit-Vanya", 8.5)
    
    # Generate
    output_path = "/projects/sandbox/test/Harshit_Vanya_AI_ML_Engineer_Resume.pdf"
    pdf.generate(output_path)
    
    import os
    size = os.path.getsize(output_path)
    print(f"PDF generated: {output_path}")
    print(f"File size: {size} bytes")
    print(f"Pages: {len(pdf.pages)}")


if __name__ == "__main__":
    build_resume()
