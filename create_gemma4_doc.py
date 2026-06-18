#!/usr/bin/env python3
"""
Create a .docx file about Gemma 4 technical details in TABULAR FORMAT.
All content is organized into tables for easy reading.
Uses only standard library (zipfile + XML).
"""
import zipfile
import os


def make_content_types():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>'''


def make_rels():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''


def make_word_rels():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''


def make_styles():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:pPr><w:jc w:val="center"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="56"/><w:color w:val="1a237e"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:pPr><w:spacing w:before="360" w:after="120"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="36"/><w:color w:val="1565c0"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:sz w:val="22"/><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/></w:rPr>
  </w:style>
</w:styles>'''



def escape(text):
    """Escape XML special characters."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def p(text, style="Normal"):
    """Create a paragraph."""
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style != "Normal" else ''
    return f'<w:p>{style_xml}<w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'


def table_start():
    """Start a table with borders."""
    return '''<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/>
<w:tblBorders>
<w:top w:val="single" w:sz="6" w:color="333333"/>
<w:bottom w:val="single" w:sz="6" w:color="333333"/>
<w:left w:val="single" w:sz="6" w:color="333333"/>
<w:right w:val="single" w:sz="6" w:color="333333"/>
<w:insideH w:val="single" w:sz="4" w:color="666666"/>
<w:insideV w:val="single" w:sz="4" w:color="666666"/>
</w:tblBorders></w:tblPr>'''


def table_end():
    return '</w:tbl>'


def row(cells, bold=False):
    """Create a table row with cells."""
    r = '<w:tr>'
    for cell in cells:
        rpr = '<w:rPr><w:b/></w:rPr>' if bold else ''
        shading = '<w:shd w:val="clear" w:color="auto" w:fill="E3F2FD"/>' if bold else ''
        r += f'''<w:tc><w:tcPr>{shading}
<w:tcBorders>
<w:top w:val="single" w:sz="4" w:color="666666"/>
<w:bottom w:val="single" w:sz="4" w:color="666666"/>
<w:left w:val="single" w:sz="4" w:color="666666"/>
<w:right w:val="single" w:sz="4" w:color="666666"/>
</w:tcBorders></w:tcPr>
<w:p><w:r>{rpr}<w:t xml:space="preserve">{escape(cell)}</w:t></w:r></w:p></w:tc>'''
    r += '</w:tr>'
    return r



def make_document():
    c = []  # content accumulator

    # Title
    c.append(p("Google Gemma 4 - Detailed Technical Summary", "Title"))
    c.append(p("All Technical Details in Tabular Format", "Normal"))
    c.append(p("Prepared: June 2026 | Developer: Google DeepMind | License: Apache 2.0", "Normal"))
    c.append(p(""))

    # ========== TABLE 1: Executive Overview ==========
    c.append(p("1. Executive Overview", "Heading1"))
    c.append(table_start())
    c.append(row(["Property", "Details"], bold=True))
    c.append(row(["Model Family", "Gemma 4 (4th generation of Google's open Gemma models)"]))
    c.append(row(["Developer", "Google DeepMind"]))
    c.append(row(["Release Date", "April 2, 2026 (E2B, E4B, 26B A4B, 31B); June 3, 2026 (12B Unified)"]))
    c.append(row(["License", "Apache 2.0 (fully open for commercial and research use)"]))
    c.append(row(["Input Modalities", "Text, Image (all models); Audio (E2B, E4B, 12B only)"]))
    c.append(row(["Output Modality", "Text only"]))
    c.append(row(["Architecture Types", "Dense and Mixture-of-Experts (MoE)"]))
    c.append(row(["Model Sizes", "E2B, E4B, 12B Unified, 26B A4B (MoE), 31B Dense"]))
    c.append(row(["Context Window", "128K tokens (E2B, E4B); 256K tokens (12B, 26B, 31B)"]))
    c.append(row(["Vocabulary Size", "262,144 tokens (262K) shared across all models"]))
    c.append(row(["Multilingual Support", "Pre-trained on 140+ languages; 35+ with dedicated support"]))
    c.append(row(["Model Variants", "Pre-trained (base) and Instruction-tuned (IT) for each size"]))
    c.append(row(["Additional Variants", "QAT (Quantization-Aware Training); MTP (Multi-Token Prediction for 12B)"]))
    c.append(row(["Availability", "Hugging Face, Kaggle, Ollama, Google AI Studio"]))
    c.append(table_end())
    c.append(p(""))


    # ========== TABLE 2: Model Specifications ==========
    c.append(p("2. Model Specifications Comparison", "Heading1"))
    c.append(table_start())
    c.append(row(["Property", "E2B", "E4B", "12B Unified", "26B A4B (MoE)", "31B Dense"], bold=True))
    c.append(row(["Total Parameters", "5.1B (2.3B effective)", "8B (4.5B effective)", "11.95B", "25.2B (3.8B active)", "30.7B"]))
    c.append(row(["Active Parameters/Token", "2.3B", "4.5B", "11.95B", "3.8B", "30.7B"]))
    c.append(row(["Layers", "35", "42", "48", "30", "60"]))
    c.append(row(["Sliding Window Size", "512 tokens", "512 tokens", "1024 tokens", "1024 tokens", "1024 tokens"]))
    c.append(row(["Context Length", "128K tokens", "128K tokens", "256K tokens", "256K tokens", "256K tokens"]))
    c.append(row(["Vocabulary Size", "262K", "262K", "262K", "262K", "262K"]))
    c.append(row(["Architecture", "Dense + PLE", "Dense + PLE", "Dense (Encoder-Free)", "MoE (128 experts)", "Dense"]))
    c.append(row(["Text Input", "Yes", "Yes", "Yes", "Yes", "Yes"]))
    c.append(row(["Image Input", "Yes", "Yes", "Yes", "Yes", "Yes"]))
    c.append(row(["Audio Input", "Yes", "Yes", "Yes", "No", "No"]))
    c.append(row(["Vision Encoder", "~150M params", "~150M params", "None (encoder-free)", "~550M params", "~550M params"]))
    c.append(row(["Audio Encoder", "~300M params", "~300M params", "None (encoder-free)", "N/A", "N/A"]))
    c.append(row(["Expert Count", "N/A", "N/A", "N/A", "128 routed + 1 shared", "N/A"]))
    c.append(row(["Active Experts/Token", "N/A", "N/A", "N/A", "8 of 128", "N/A"]))
    c.append(row(["Target Deployment", "Mobile, Edge", "Laptop, Mobile", "16GB Laptop GPU", "Consumer GPU/Server", "Workstation/Server"]))
    c.append(row(["Arena AI ELO (at release)", "-", "-", "-", "-", "1,452 (3rd open model)"]))
    c.append(table_end())
    c.append(p(""))


    # ========== TABLE 3: Architecture Details ==========
    c.append(p("3. Architecture Technical Details", "Heading1"))
    c.append(table_start())
    c.append(row(["Component", "Description"], bold=True))
    c.append(row(["Base Architecture", "Decoder-only Transformer with hybrid attention"]))
    c.append(row(["Attention Pattern", "Interleaves local sliding-window attention with full global attention (ratio ~5:1 or 4:1); final layer always global"]))
    c.append(row(["Sliding Window Layers", "Local attention limited to 512 tokens (E2B/E4B) or 1024 tokens (12B/26B/31B); head_dim=256, num_kv_heads=8"]))
    c.append(row(["Global Attention Layers", "Full context attention (128K or 256K); global_head_dim=512, num_kv_heads=1 (unified KV)"]))
    c.append(row(["Unified Keys & Values", "Global layers share a single Key-Value pair across all query heads, drastically reducing KV cache memory"]))
    c.append(row(["Proportional RoPE (p-RoPE)", "Only ~25% of embedding dimensions carry positional info in global layers; remaining are position-independent for stable long-range performance"]))
    c.append(row(["Per-Layer Embeddings (PLE)", "E2B/E4B only: Each decoder layer has its own embedding lookup table; large tables but O(1) lookups (not compute-intensive)"]))
    c.append(row(["PLE Effect", "Total params much higher than effective params; e.g., E4B is 8B total but only 4.5B effective compute"]))
    c.append(row(["Double-Norm Architecture", "E2B/E4B use double normalization alongside PLE for stability"]))
    c.append(row(["Encoder-Free (12B Unified)", "No dedicated vision/audio encoders; raw image patches and audio waveforms projected into LLM embedding space via lightweight linear layers"]))
    c.append(row(["12B Advantages", "All modalities in single decoder-only transformer; reduced latency; entire model fine-tunable in one pass"]))
    c.append(row(["MoE Architecture (26B)", "128 fine-grained routed experts + 1 shared (always active) expert per MoE layer"]))
    c.append(row(["MoE Routing", "Top-8 routing: router network selects 8 experts per token; remaining experts inactive"]))
    c.append(row(["MoE Memory", "All 26B parameters must reside in memory; only routing/activation is sparse"]))
    c.append(row(["MoE Speed", "Runs nearly as fast as a 4B dense model despite 26B total size"]))
    c.append(row(["Vision Processing", "Variable aspect ratio + variable resolution via configurable visual token budget (70/140/280/560/1120 tokens)"]))
    c.append(row(["Image Normalization", "No ImageNet mean/std normalization; patch embedding layer internally scales to [-1, 1] range"]))
    c.append(row(["Audio Processing", "E2B/E4B: dedicated ~300M encoder; 12B: raw waveform linear projection; max 30 seconds"]))
    c.append(table_end())
    c.append(p(""))


    # ========== TABLE 4: Inference Configuration ==========
    c.append(p("4. Inference Configuration and Best Practices", "Heading1"))
    c.append(table_start())
    c.append(row(["Parameter / Feature", "Value / Details"], bold=True))
    c.append(row(["Temperature", "1.0 (recommended)"]))
    c.append(row(["Top-p (nucleus sampling)", "0.95"]))
    c.append(row(["Top-k", "64"]))
    c.append(row(["Thinking Mode - Enable", "Include <|think|> token at start of system prompt"]))
    c.append(row(["Thinking Mode - Disable", "Remove <|think|> token from system prompt"]))
    c.append(row(["Thinking Output Format", "<|channel>thought\\n[internal reasoning]<channel|>[final answer]"]))
    c.append(row(["Thinking Disabled Behavior", "Empty thought block generated (except E2B/E4B which skip entirely)"]))
    c.append(row(["Multi-Turn Conversations", "Historical turns should only include final response; remove thinking content from history"]))
    c.append(row(["System Prompt", "Native support for 'system' role (new in Gemma 4)"]))
    c.append(row(["Image Placement", "Place image content BEFORE text in prompts"]))
    c.append(row(["Audio Placement", "Place audio content AFTER text in prompts"]))
    c.append(row(["Visual Token Budget: 70", "Fast inference; for classification, captioning, video frames"]))
    c.append(row(["Visual Token Budget: 140", "General image understanding"]))
    c.append(row(["Visual Token Budget: 280", "Balanced detail and speed"]))
    c.append(row(["Visual Token Budget: 560", "Higher detail; document parsing"]))
    c.append(row(["Visual Token Budget: 1120", "Maximum detail; OCR, reading small text"]))
    c.append(row(["Max Audio Length", "30 seconds"]))
    c.append(row(["Max Video Length", "60 seconds (processed at 1 frame/second)"]))
    c.append(table_end())
    c.append(p(""))


    # ========== TABLE 5: Core Capabilities ==========
    c.append(p("5. Core Capabilities", "Heading1"))
    c.append(table_start())
    c.append(row(["Capability", "Details", "Supported Models"], bold=True))
    c.append(row(["Thinking / Reasoning", "Built-in step-by-step reasoning with configurable thinking modes", "All models"]))
    c.append(row(["Long Context", "128K tokens (small) / 256K tokens (medium/large)", "All models"]))
    c.append(row(["Image Understanding", "Object detection, document/PDF parsing, UI understanding, chart comprehension, OCR (multilingual), handwriting, pointing", "All models"]))
    c.append(row(["Variable Image Resolution", "Configurable token budgets (70-1120) for quality/speed tradeoff", "All models"]))
    c.append(row(["Video Understanding", "Analyze video by processing frame sequences (max 60s at 1 fps)", "All models"]))
    c.append(row(["Interleaved Multimodal", "Mix text and images in any order within a single prompt", "All models"]))
    c.append(row(["Function Calling", "Native structured tool use for agentic workflows; multi-step planning", "All models"]))
    c.append(row(["Coding", "Code generation, completion, correction; IDE integration ready", "All models"]))
    c.append(row(["Multilingual", "35+ supported languages; pre-trained on 140+ languages", "All models"]))
    c.append(row(["Audio - ASR", "Automatic Speech Recognition in multiple languages", "E2B, E4B, 12B"]))
    c.append(row(["Audio - AST", "Speech-to-translated-text across languages", "E2B, E4B, 12B"]))
    c.append(row(["Agentic Workflows", "Plan, navigate apps, complete tasks autonomously without fine-tuning", "All models"]))
    c.append(row(["System Prompt", "Native 'system' role for structured, controllable conversations", "All models"]))
    c.append(table_end())
    c.append(p(""))


    # ========== TABLE 6: Text & Reasoning Benchmarks ==========
    c.append(p("6. Benchmark Results - Text and Reasoning", "Heading1"))
    c.append(table_start())
    c.append(row(["Benchmark", "Gemma 4 31B", "Gemma 4 26B A4B", "Gemma 4 12B", "Gemma 4 E4B", "Gemma 4 E2B", "Gemma 3 27B"], bold=True))
    c.append(row(["MMLU Pro", "85.2%", "82.6%", "77.2%", "69.4%", "60.0%", "67.6%"]))
    c.append(row(["AIME 2026 (no tools)", "89.2%", "88.3%", "77.5%", "42.5%", "37.5%", "20.8%"]))
    c.append(row(["LiveCodeBench v6", "80.0%", "77.1%", "72.0%", "52.0%", "44.0%", "29.1%"]))
    c.append(row(["Codeforces ELO", "2150", "1718", "1659", "940", "633", "110"]))
    c.append(row(["GPQA Diamond", "84.3%", "82.3%", "78.8%", "58.6%", "43.4%", "42.4%"]))
    c.append(row(["Tau2 (avg over 3)", "76.9%", "68.2%", "69.0%", "42.2%", "24.5%", "16.2%"]))
    c.append(row(["HLE (no tools)", "19.5%", "8.7%", "5.2%", "-", "-", "-"]))
    c.append(row(["HLE (with search)", "26.5%", "17.2%", "-", "-", "-", "-"]))
    c.append(row(["BigBench Extra Hard", "74.4%", "64.8%", "53.0%", "33.1%", "21.9%", "19.3%"]))
    c.append(row(["MMMLU (Multilingual)", "88.4%", "86.3%", "83.4%", "76.6%", "67.4%", "70.7%"]))
    c.append(table_end())
    c.append(p(""))

    # ========== TABLE 7: Vision Benchmarks ==========
    c.append(p("7. Benchmark Results - Vision", "Heading1"))
    c.append(table_start())
    c.append(row(["Benchmark", "Gemma 4 31B", "Gemma 4 26B A4B", "Gemma 4 12B", "Gemma 4 E4B", "Gemma 4 E2B", "Gemma 3 27B"], bold=True))
    c.append(row(["MMMU Pro", "76.9%", "73.8%", "69.1%", "52.6%", "44.2%", "49.7%"]))
    c.append(row(["OmniDocBench 1.5 (edit dist, lower=better)", "0.131", "0.149", "0.164", "0.181", "0.290", "0.365"]))
    c.append(row(["MATH-Vision", "85.6%", "82.4%", "79.7%", "59.5%", "52.4%", "46.0%"]))
    c.append(row(["MedXPertQA MM", "61.3%", "58.1%", "48.7%", "28.7%", "23.5%", "-"]))
    c.append(table_end())
    c.append(p(""))


    # ========== TABLE 8: Audio Benchmarks ==========
    c.append(p("8. Benchmark Results - Audio", "Heading1"))
    c.append(table_start())
    c.append(row(["Benchmark", "Gemma 4 12B", "Gemma 4 E4B", "Gemma 4 E2B"], bold=True))
    c.append(row(["CoVoST (BLEU score)", "38.5", "35.54", "33.47"]))
    c.append(row(["FLEURS (WER, lower=better)", "0.069", "0.08", "0.09"]))
    c.append(table_end())
    c.append(p(""))

    # ========== TABLE 9: Long Context Benchmark ==========
    c.append(p("9. Benchmark Results - Long Context", "Heading1"))
    c.append(table_start())
    c.append(row(["Benchmark", "Gemma 4 31B", "Gemma 4 26B A4B", "Gemma 4 12B", "Gemma 4 E4B", "Gemma 4 E2B", "Gemma 3 27B"], bold=True))
    c.append(row(["MRCR v2 8-needle 128K (avg)", "66.4%", "44.1%", "43.4%", "25.4%", "19.1%", "13.5%"]))
    c.append(table_end())
    c.append(p(""))

    # ========== TABLE 10: Gemma 4 vs Gemma 3 Comparison ==========
    c.append(p("10. Improvement: Gemma 4 31B vs. Gemma 3 27B", "Heading1"))
    c.append(table_start())
    c.append(row(["Benchmark", "Gemma 4 31B", "Gemma 3 27B", "Improvement"], bold=True))
    c.append(row(["MMLU Pro", "85.2%", "67.6%", "+17.6 points"]))
    c.append(row(["AIME 2026 (no tools)", "89.2%", "20.8%", "+68.4 points"]))
    c.append(row(["LiveCodeBench v6", "80.0%", "29.1%", "+50.9 points"]))
    c.append(row(["Codeforces ELO", "2150", "110", "+2040 ELO"]))
    c.append(row(["GPQA Diamond", "84.3%", "42.4%", "+41.9 points"]))
    c.append(row(["MMMU Pro (Vision)", "76.9%", "49.7%", "+27.2 points"]))
    c.append(row(["MRCR Long Context", "66.4%", "13.5%", "+52.9 points"]))
    c.append(row(["Tau2 (Agentic)", "76.9%", "16.2%", "+60.7 points"]))
    c.append(row(["BigBench Extra Hard", "74.4%", "19.3%", "+55.1 points"]))
    c.append(row(["MMMLU (Multilingual)", "88.4%", "70.7%", "+17.7 points"]))
    c.append(table_end())
    c.append(p(""))


    # ========== TABLE 11: Key Innovations ==========
    c.append(p("11. Key Architectural Innovations", "Heading1"))
    c.append(table_start())
    c.append(row(["Innovation", "Description", "Benefit"], bold=True))
    c.append(row(["Native System Prompt", "New 'system' role support", "More structured, controllable conversations"]))
    c.append(row(["Configurable Thinking", "<|think|> control token enables/disables reasoning", "Flexible reasoning for different use cases"]))
    c.append(row(["Per-Layer Embeddings (PLE)", "Each decoder layer has its own embedding table", "Maximizes parameter efficiency on-device"]))
    c.append(row(["Encoder-Free Architecture", "12B: No separate vision/audio encoders", "Lower latency, single-pass fine-tuning"]))
    c.append(row(["Proportional RoPE (p-RoPE)", "Only 25% of dims carry positional info in global layers", "Stable long-range performance at extreme lengths"]))
    c.append(row(["Unified KV Sharing", "Single Key-Value pair shared across all query heads in global layers", "Dramatically reduced KV cache memory"]))
    c.append(row(["Fine-Grained MoE", "128 experts (vs typical 8-16 in other models)", "Better specialization per token"]))
    c.append(row(["Variable Image Resolution", "Configurable token budgets (70-1120)", "Detail/speed tradeoff control"]))
    c.append(row(["Native Audio Processing", "Built-in audio without separate ASR pipeline", "End-to-end audio understanding"]))
    c.append(row(["Native Function Calling", "Structured tool use built into model", "Agentic workflows without fine-tuning"]))
    c.append(row(["Extended Context", "Up to 256K tokens (vs 128K in Gemma 3)", "Process longer documents/conversations"]))
    c.append(row(["Multi-Token Prediction", "MTP variant for 12B model", "Faster local inference speed"]))
    c.append(table_end())
    c.append(p(""))


    # ========== TABLE 12: Deployment ==========
    c.append(p("12. Deployment Targets and Hardware Requirements", "Heading1"))
    c.append(table_start())
    c.append(row(["Model", "Target Hardware", "Memory Requirement", "Notes"], bold=True))
    c.append(row(["E2B", "Smartphones, tablets, edge devices", "Minimal (2.3B effective)", "QAT mobile variants available"]))
    c.append(row(["E4B", "Laptops, mobile devices", "Moderate (4.5B effective)", "PLE architecture; QAT mobile variants"]))
    c.append(row(["12B Unified", "Laptops with 16GB VRAM/unified memory", "~7GB at 4-bit quantization", "First medium model with native audio"]))
    c.append(row(["26B A4B (MoE)", "Consumer GPUs, servers", "~26GB (all params in memory)", "Inference speed of ~4B model"]))
    c.append(row(["31B Dense", "Workstations, cloud servers", "~31GB+ full precision", "Highest quality; needs more compute"]))
    c.append(table_end())
    c.append(p(""))

    # ========== TABLE 13: Training Data ==========
    c.append(p("13. Training Data", "Heading1"))
    c.append(table_start())
    c.append(row(["Aspect", "Details"], bold=True))
    c.append(row(["Data Cutoff Date", "January 2025"]))
    c.append(row(["Web Documents", "Diverse web text in 140+ languages; broad linguistic styles and topics"]))
    c.append(row(["Code", "Programming language syntax, patterns, documentation"]))
    c.append(row(["Mathematics", "Logical reasoning, symbolic representation, mathematical text"]))
    c.append(row(["Images", "Wide range of visual data for image analysis and extraction tasks"]))
    c.append(row(["CSAM Filtering", "Rigorous multi-stage filtering for Child Sexual Abuse Material"]))
    c.append(row(["Sensitive Data Filtering", "Automated removal of personal information and sensitive data"]))
    c.append(row(["Content Quality Filtering", "Quality and safety filtering per Google AI policies"]))
    c.append(table_end())
    c.append(p(""))


    # ========== TABLE 14: Function Calling / Agentic ==========
    c.append(p("14. Function Calling and Agentic Performance", "Heading1"))
    c.append(table_start())
    c.append(row(["Feature / Metric", "Details"], bold=True))
    c.append(row(["Function Calling", "Native structured tool use; models generate structured function call outputs"]))
    c.append(row(["Multi-Step Planning", "Supports autonomous multi-step planning and action"]))
    c.append(row(["Agent Capabilities", "Plan, navigate apps, complete tasks without specialized fine-tuning"]))
    c.append(row(["Tau2-Bench (Gemma 4 31B)", "86.4% (agentic tool use benchmark)"]))
    c.append(row(["Tau2-Bench (Gemma 3 27B)", "6.6% (for comparison)"]))
    c.append(row(["Improvement", "+79.8 points absolute improvement in agentic capability"]))
    c.append(row(["Tau2 Average (31B)", "76.9% across 3 sub-benchmarks"]))
    c.append(row(["Tau2 Average (26B A4B)", "68.2%"]))
    c.append(row(["Tau2 Average (12B)", "69.0%"]))
    c.append(row(["On-Device Agentic", "E2B/E4B enable agentic workflows on mobile/laptop"]))
    c.append(table_end())
    c.append(p(""))

    # ========== TABLE 15: Safety ==========
    c.append(p("15. Safety and Ethics", "Heading1"))
    c.append(table_start())
    c.append(row(["Aspect", "Details"], bold=True))
    c.append(row(["Evaluation Standard", "Same rigorous safety evaluations as proprietary Gemini models"]))
    c.append(row(["Safety vs Gemma 3", "Major improvements in all content safety categories"]))
    c.append(row(["Policy Violations", "Minimal across all model sizes in both text-to-text and image-to-text"]))
    c.append(row(["Unjustified Refusals", "Kept low while improving safety"]))
    c.append(row(["Testing Method", "Conducted without safety filters to evaluate raw model behavior"]))
    c.append(row(["Evaluated Categories", "CSAM, dangerous content, sexually explicit content, hate speech, harassment"]))
    c.append(row(["Development Process", "Partnership with internal safety and responsible AI teams"]))
    c.append(row(["Alignment", "Google's AI Principles"]))
    c.append(row(["Content Moderation", "Guidelines provided via Responsible Generative AI Toolkit"]))
    c.append(table_end())
    c.append(p(""))


    # ========== TABLE 16: Limitations ==========
    c.append(p("16. Known Limitations", "Heading1"))
    c.append(table_start())
    c.append(row(["Limitation Category", "Details"], bold=True))
    c.append(row(["Training Data Biases", "Quality/diversity of training data may influence outputs; biases or gaps possible"]))
    c.append(row(["Task Complexity", "Open-ended or highly complex tasks may be challenging"]))
    c.append(row(["Factual Accuracy", "May generate incorrect or outdated factual statements (not a knowledge base)"]))
    c.append(row(["Language Nuance", "May struggle with sarcasm, figurative language, or subtle nuance"]))
    c.append(row(["Common Sense", "Relies on statistical patterns; may lack common sense in certain situations"]))
    c.append(row(["Audio Limitation", "26B and 31B models do NOT support audio input"]))
    c.append(row(["Audio Length", "Maximum 30 seconds per segment"]))
    c.append(row(["Video Length", "Maximum 60 seconds (at 1 frame per second)"]))
    c.append(row(["Context Dependency", "Longer context generally improves outputs, up to a point"]))
    c.append(row(["Subject Scope", "Limited to areas well-represented in training data"]))
    c.append(table_end())
    c.append(p(""))

    # ========== TABLE 17: Sources ==========
    c.append(p("17. Sources and References", "Heading1"))
    c.append(table_start())
    c.append(row(["Source", "URL"], bold=True))
    c.append(row(["Google AI Model Card", "https://ai.google.dev/gemma/docs/core/model_card_4"]))
    c.append(row(["Google DeepMind Gemma 4", "https://deepmind.google/models/gemma/gemma-4/"]))
    c.append(row(["Hugging Face Blog", "https://huggingface.co/blog/gemma4"]))
    c.append(row(["Google Developers Blog (12B)", "https://developers.googleblog.com/gemma-4-12b-the-developer-guide/"]))
    c.append(row(["HF Model: gemma-4-12B", "https://huggingface.co/google/gemma-4-12B"]))
    c.append(row(["Google Launch Blog", "https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/"]))
    c.append(row(["KerasHub Agentic Guide", "https://keras.io/keras_hub/guides/gemma4_multimodal_and_agentic_workflows/"]))
    c.append(table_end())
    c.append(p(""))
    c.append(p("Note: Content was rephrased for compliance with licensing restrictions. All technical specifications sourced from official Google DeepMind documentation and model cards."))


    # Assemble the full document
    body_xml = '\n'.join(c)

    document = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    {body_xml}
    <w:sectPr>
      <w:pgSz w:w="15840" w:h="12240" w:orient="landscape"/>
      <w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080"/>
    </w:sectPr>
  </w:body>
</w:document>'''

    return document


def create_docx(output_path):
    """Create the .docx ZIP archive."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', make_content_types())
        zf.writestr('_rels/.rels', make_rels())
        zf.writestr('word/_rels/document.xml.rels', make_word_rels())
        zf.writestr('word/styles.xml', make_styles())
        zf.writestr('word/document.xml', make_document())

    print(f"Document created successfully: {output_path}")
    print(f"File size: {os.path.getsize(output_path):,} bytes")


if __name__ == "__main__":
    output_file = "/projects/sandbox/test/Gemma_4_Technical_Summary.docx"
    create_docx(output_file)
