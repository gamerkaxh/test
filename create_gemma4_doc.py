#!/usr/bin/env python3
"""
Create a .docx file about Gemma 4 technical details using only standard library.
A .docx is a ZIP file containing XML documents following the OOXML standard.
"""
import zipfile
import os

# XML namespace constants
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
WP_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


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
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:pPr><w:spacing w:before="240" w:after="80"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="28"/><w:color w:val="1976d2"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/>
    <w:pPr><w:spacing w:before="200" w:after="60"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="333333"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:sz w:val="22"/><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/></w:rPr>
  </w:style>
</w:styles>'''



def p(text, style="Normal", bold=False):
    """Create a paragraph XML element."""
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style != "Normal" else ''
    if bold:
        return f'<w:p>{style_xml}<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'
    return f'<w:p>{style_xml}<w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'


def bullet(text):
    """Create a bullet point paragraph."""
    return f'''<w:p>
  <w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>
  <w:ind w:left="720" w:hanging="360"/></w:pPr>
  <w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'''


def escape(text):
    """Escape XML special characters."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def table_row(cells, bold=False):
    """Create a table row."""
    row = '<w:tr>'
    for cell in cells:
        rpr = '<w:rPr><w:b/></w:rPr>' if bold else ''
        row += f'''<w:tc>
  <w:tcPr><w:tcBorders>
    <w:top w:val="single" w:sz="4" w:color="999999"/>
    <w:bottom w:val="single" w:sz="4" w:color="999999"/>
    <w:left w:val="single" w:sz="4" w:color="999999"/>
    <w:right w:val="single" w:sz="4" w:color="999999"/>
  </w:tcBorders></w:tcPr>
  <w:p><w:r>{rpr}<w:t xml:space="preserve">{escape(str(cell))}</w:t></w:r></w:p></w:tc>'''
    row += '</w:tr>'
    return row



def make_document():
    body_content = []
    
    # Title
    body_content.append(p("Google Gemma 4 - Detailed Technical Summary", "Title"))
    body_content.append(p("Comprehensive Extract of Architecture, Specifications, and Capabilities", "Normal"))
    body_content.append(p("Prepared: June 2026 | Source: Google DeepMind Official Documentation", "Normal"))
    body_content.append(p("License: Apache 2.0 | Developer: Google DeepMind", "Normal"))
    body_content.append(p(""))
    
    # Section 1: Executive Overview
    body_content.append(p("1. Executive Overview", "Heading1"))
    body_content.append(p("Gemma 4 is Google DeepMind's latest family of open-weight multimodal AI models, released on April 2, 2026 (with the 12B model added June 3, 2026). The models handle text and image inputs (with audio supported on E2B, E4B, and 12B variants) and generate text output. They are released under the Apache 2.0 license, making them freely available for commercial and research use."))
    body_content.append(p("The family features both Dense and Mixture-of-Experts (MoE) architectures across five model sizes: E2B, E4B, 12B Unified, 26B A4B (MoE), and 31B Dense. Context windows range from 128K tokens (smaller models) to 256K tokens (larger models), with multilingual support for 140+ languages."))
    body_content.append(p(""))
    
    # Section 2: Model Family Overview
    body_content.append(p("2. Model Family and Size Variants", "Heading1"))
    body_content.append(p("2.1 Dense Models", "Heading2"))
    body_content.append(p("Gemma 4 E2B (Effective 2 Billion Parameters)", "Heading3"))
    body_content.append(p("Total parameters: 5.1B (including embeddings), Effective: 2.3B"))
    body_content.append(p("Layers: 35 | Sliding window: 512 tokens | Context: 128K tokens"))
    body_content.append(p("Vocabulary size: 262,144 tokens"))
    body_content.append(p("Modalities: Text, Image, Audio"))
    body_content.append(p("Vision encoder: ~150M parameters | Audio encoder: ~300M parameters"))
    body_content.append(p("Uses Per-Layer Embeddings (PLE) architecture"))
    body_content.append(p(""))


    body_content.append(p("Gemma 4 E4B (Effective 4 Billion Parameters)", "Heading3"))
    body_content.append(p("Total parameters: 8B (including embeddings), Effective: 4.5B"))
    body_content.append(p("Layers: 42 | Sliding window: 512 tokens | Context: 128K tokens"))
    body_content.append(p("Vocabulary size: 262,144 tokens"))
    body_content.append(p("Modalities: Text, Image, Audio"))
    body_content.append(p("Vision encoder: ~150M parameters | Audio encoder: ~300M parameters"))
    body_content.append(p("Uses Per-Layer Embeddings (PLE) architecture"))
    body_content.append(p("Optimized for on-device deployment (laptops, mobile)"))
    body_content.append(p(""))
    
    body_content.append(p("Gemma 4 12B Unified (Encoder-Free Architecture)", "Heading3"))
    body_content.append(p("Total parameters: 11.95B"))
    body_content.append(p("Layers: 48 | Sliding window: 1024 tokens | Context: 256K tokens"))
    body_content.append(p("Vocabulary size: 262,144 tokens"))
    body_content.append(p("Modalities: Text, Image, Audio (encoder-free)"))
    body_content.append(p("No dedicated vision or audio encoder - projects raw inputs directly into LLM embedding space"))
    body_content.append(p("Runs on laptops with 16GB VRAM; ~7GB at 4-bit quantization"))
    body_content.append(p("Includes Multi-Token Prediction (MTP) variant for faster inference"))
    body_content.append(p(""))
    
    body_content.append(p("Gemma 4 31B Dense", "Heading3"))
    body_content.append(p("Total parameters: 30.7B"))
    body_content.append(p("Layers: 60 | Sliding window: 1024 tokens | Context: 256K tokens"))
    body_content.append(p("Vocabulary size: 262,144 tokens"))
    body_content.append(p("Modalities: Text, Image (no audio support)"))
    body_content.append(p("Vision encoder: ~550M parameters"))
    body_content.append(p("Highest-performing model in the family"))
    body_content.append(p("Arena AI ELO: 1,452 (ranked 3rd among all open models at release)"))
    body_content.append(p(""))


    body_content.append(p("2.2 Mixture-of-Experts (MoE) Model", "Heading2"))
    body_content.append(p("Gemma 4 26B A4B (Active 4 Billion)", "Heading3"))
    body_content.append(p("Total parameters: 25.2B | Active parameters per token: 3.8B"))
    body_content.append(p("Layers: 30 | Sliding window: 1024 tokens | Context: 256K tokens"))
    body_content.append(p("Vocabulary size: 262,144 tokens"))
    body_content.append(p("Expert configuration: 128 total routed experts + 1 shared expert, 8 active per token"))
    body_content.append(p("Modalities: Text, Image (no audio support)"))
    body_content.append(p("Vision encoder: ~550M parameters"))
    body_content.append(p("Routing: Top-8 routing selects 8 of 128 fine-grained experts per token"))
    body_content.append(p("Runs nearly as fast as a 4B-parameter model despite 26B total size"))
    body_content.append(p("All 26B parameters must be loaded into memory; router selectively activates experts"))
    body_content.append(p(""))
    
    # Section 3: Architecture Deep Dive
    body_content.append(p("3. Architecture Technical Details", "Heading1"))
    body_content.append(p("3.1 Core Architecture: Decoder-Only Transformer", "Heading2"))
    body_content.append(p("All Gemma 4 models are decoder-only transformers with a hybrid attention mechanism that interleaves local sliding-window attention with full global attention. The final layer is always a global attention layer."))
    body_content.append(p(""))
    
    body_content.append(p("3.2 Hybrid Attention Mechanism", "Heading2"))
    body_content.append(p("Layers alternate between local sliding-window attention and global full attention in a fixed ratio (approximately 5:1 or 4:1, depending on the model size). This hybrid design delivers fast processing and low memory usage while maintaining deep contextual awareness for complex, long-context tasks."))
    body_content.append(p(""))
    body_content.append(p("Sliding window layers:", "Normal", bold=True))
    body_content.append(p("- E2B/E4B: 512-token sliding window"))
    body_content.append(p("- 12B/26B/31B: 1024-token sliding window"))
    body_content.append(p("- Head dimension: 256 with 8 KV heads (for sliding layers)"))
    body_content.append(p(""))
    body_content.append(p("Global attention layers:", "Normal", bold=True))
    body_content.append(p("- Full context attention spanning up to 128K/256K tokens"))
    body_content.append(p("- Global head dimension: 512 with unified (single) KV head"))
    body_content.append(p("- Only 25% of dimensions carry positional information in global layers"))
    body_content.append(p(""))


    body_content.append(p("3.3 Unified Keys and Values (KV Sharing)", "Heading2"))
    body_content.append(p("To optimize memory for long contexts, global attention layers feature unified Keys and Values. This means that all query heads share a single Key-Value pair in global layers, dramatically reducing KV cache memory requirements during inference. This is distinct from Grouped Query Attention (GQA) - it uses a single KV head for the entire global layer."))
    body_content.append(p(""))
    
    body_content.append(p("3.4 Proportional RoPE (p-RoPE)", "Heading2"))
    body_content.append(p("Global attention layers apply Proportional RoPE (p-RoPE), a modified version of Rotary Position Embeddings. In p-RoPE, only a proportion of the embedding dimensions carry positional information (approximately 25%), while the remaining dimensions are position-independent. This allows the model to maintain strong long-range awareness without the degradation typically seen with standard RoPE at extreme sequence lengths."))
    body_content.append(p(""))
    
    body_content.append(p("3.5 Per-Layer Embeddings (PLE)", "Heading2"))
    body_content.append(p("The E2B and E4B models use Per-Layer Embeddings (PLE) to maximize parameter efficiency for on-device deployments. Rather than adding more layers or parameters, PLE gives each decoder layer its own small embedding lookup table for every token. These embedding tables are large in total but only require quick lookups (not compute-intensive operations), which is why the 'effective' parameter count is much smaller than the total parameter count."))
    body_content.append(p(""))
    body_content.append(p("Key characteristics of PLE:"))
    body_content.append(p("- Each decoder layer has a dedicated per-layer embedding table"))
    body_content.append(p("- Embedding lookups are fast O(1) operations, not matrix multiplications"))
    body_content.append(p("- E2B: 5.1B total but only 2.3B 'effective' computation"))
    body_content.append(p("- E4B: 8B total but only 4.5B 'effective' computation"))
    body_content.append(p("- Uses double-norm architecture alongside PLE"))
    body_content.append(p("- Makes models resistant to certain fine-tuning approaches (e.g., LoRA abliteration)"))
    body_content.append(p(""))


    body_content.append(p("3.6 Encoder-Free Unified Architecture (12B)", "Heading2"))
    body_content.append(p("The 12B Unified model eliminates dedicated vision and audio encoders entirely. Instead of passing multimodal data through encoder towers before the LLM, it projects raw image patches and audio waveforms directly into the LLM's embedding space through lightweight linear projection layers."))
    body_content.append(p(""))
    body_content.append(p("Advantages of the encoder-free design:"))
    body_content.append(p("- All modalities flow into a single decoder-only transformer"))
    body_content.append(p("- Reduced multimodal latency (no encoder processing bottleneck)"))
    body_content.append(p("- Entire model can be fine-tuned in one pass"))
    body_content.append(p("- Simpler architecture for deployment"))
    body_content.append(p("- First medium-sized open model to natively ingest audio"))
    body_content.append(p(""))
    
    body_content.append(p("3.7 Mixture-of-Experts Architecture (26B A4B)", "Heading2"))
    body_content.append(p("The MoE variant uses fine-grained expert routing to achieve high performance at low per-token compute cost:"))
    body_content.append(p("- 128 routed experts per MoE layer + 1 shared expert (always active)"))
    body_content.append(p("- Top-8 routing: a router network selects 8 experts per token"))
    body_content.append(p("- Active parameters: ~3.8B per token out of 25.2B total"))
    body_content.append(p("- All 26B parameters must reside in memory; only routing is sparse"))
    body_content.append(p("- Achieves inference speed comparable to a 4B dense model"))
    body_content.append(p("- Delivers performance close to the 31B dense model"))
    body_content.append(p(""))
    
    body_content.append(p("3.8 Vision Processing", "Heading2"))
    body_content.append(p("For models with dedicated vision encoders (E2B, E4B, 26B, 31B):"))
    body_content.append(p("- Variable aspect ratio support"))
    body_content.append(p("- Variable resolution via configurable visual token budget"))
    body_content.append(p("- Supported token budgets: 70, 140, 280, 560, 1120"))
    body_content.append(p("- No standard ImageNet mean/std normalization applied"))
    body_content.append(p("- Patch embedding layer handles scaling internally (shifting to [-1, 1] range)"))
    body_content.append(p("- E2B/E4B vision encoder: ~150M parameters"))
    body_content.append(p("- 26B/31B vision encoder: ~550M parameters"))
    body_content.append(p(""))


    body_content.append(p("3.9 Audio Processing (E2B, E4B, 12B Only)", "Heading2"))
    body_content.append(p("- E2B/E4B: Dedicated audio encoder (~300M parameters)"))
    body_content.append(p("- 12B Unified: No encoder; raw audio waveforms projected via linear layers"))
    body_content.append(p("- Maximum audio length: 30 seconds"))
    body_content.append(p("- Supports ASR (Automatic Speech Recognition) and AST (Speech Translation)"))
    body_content.append(p("- Note: 26B and 31B models do NOT support audio"))
    body_content.append(p(""))
    
    # Section 4: Context Window and Tokenization
    body_content.append(p("4. Context Window and Tokenization", "Heading1"))
    body_content.append(p("4.1 Context Lengths", "Heading2"))
    body_content.append(p("- E2B, E4B: 128K tokens"))
    body_content.append(p("- 12B Unified, 26B A4B, 31B Dense: 256K tokens"))
    body_content.append(p(""))
    body_content.append(p("4.2 Vocabulary", "Heading2"))
    body_content.append(p("- Vocabulary size: 262,144 tokens (262K) across all models"))
    body_content.append(p("- Shared vocabulary across the entire Gemma 4 family"))
    body_content.append(p("- Supports 140+ languages in pre-training"))
    body_content.append(p("- 35+ languages with dedicated out-of-the-box support"))
    body_content.append(p(""))
    
    # Section 5: Inference Configuration
    body_content.append(p("5. Inference Configuration and Best Practices", "Heading1"))
    body_content.append(p("5.1 Recommended Sampling Parameters", "Heading2"))
    body_content.append(p("- Temperature: 1.0"))
    body_content.append(p("- Top-p (nucleus sampling): 0.95"))
    body_content.append(p("- Top-k: 64"))
    body_content.append(p(""))
    body_content.append(p("5.2 Thinking Mode (Chain-of-Thought Reasoning)", "Heading2"))
    body_content.append(p("Gemma 4 features built-in configurable thinking/reasoning:"))
    body_content.append(p("- Enabled by including <|think|> token at the start of system prompt"))
    body_content.append(p("- Disabled by removing the <|think|> token"))
    body_content.append(p("- When enabled, model outputs internal reasoning followed by final answer"))
    body_content.append(p("- Structure: <|channel>thought\\n[reasoning]<channel|>[final answer]"))
    body_content.append(p("- When disabled (except E2B/E4B): empty thought block still generated"))
    body_content.append(p("- Multi-turn: historical turns should only include final response, not thoughts"))
    body_content.append(p(""))


    body_content.append(p("5.3 System Prompt Support", "Heading2"))
    body_content.append(p("Gemma 4 introduces native support for the 'system' role. This is a new addition to the Gemma family, enabling more structured and controllable conversations with dedicated system-level instructions."))
    body_content.append(p(""))
    body_content.append(p("5.4 Modality Input Order", "Heading2"))
    body_content.append(p("For optimal multimodal performance:"))
    body_content.append(p("- Place image content BEFORE text in prompts"))
    body_content.append(p("- Place audio content AFTER text in prompts"))
    body_content.append(p(""))
    body_content.append(p("5.5 Visual Token Budget", "Heading2"))
    body_content.append(p("Controls how many tokens represent an image (trade-off: detail vs. speed):"))
    body_content.append(p("- Budget 70: Fast inference, suitable for classification/captioning"))
    body_content.append(p("- Budget 140: Good for general image understanding"))
    body_content.append(p("- Budget 280: Balanced detail and speed"))
    body_content.append(p("- Budget 560: Higher detail for document parsing"))
    body_content.append(p("- Budget 1120: Maximum detail for OCR, small text reading"))
    body_content.append(p(""))
    body_content.append(p("5.6 Video Processing", "Heading2"))
    body_content.append(p("- Video is processed as sequences of frames"))
    body_content.append(p("- Maximum video length: 60 seconds (at 1 frame per second)"))
    body_content.append(p("- Lower visual token budgets recommended for video (more frames, less per-frame detail)"))
    body_content.append(p(""))
    
    # Section 6: Capabilities
    body_content.append(p("6. Core Capabilities", "Heading1"))
    body_content.append(p("6.1 Function Calling and Agentic Workflows", "Heading2"))
    body_content.append(p("Gemma 4 includes native function calling support for structured tool use:"))
    body_content.append(p("- Models can generate structured function call outputs"))
    body_content.append(p("- Supports multi-step planning and autonomous action"))
    body_content.append(p("- Enables building AI agents that plan, navigate apps, and complete tasks"))
    body_content.append(p("- Works without specialized fine-tuning"))
    body_content.append(p("- tau2-bench agentic tool use: Gemma 4 31B scores 86.4% (vs. Gemma 3 27B at 6.6%)"))
    body_content.append(p(""))


    body_content.append(p("6.2 Image Understanding", "Heading2"))
    body_content.append(p("- Object detection and recognition"))
    body_content.append(p("- Document/PDF parsing"))
    body_content.append(p("- Screen and UI understanding"))
    body_content.append(p("- Chart comprehension"))
    body_content.append(p("- OCR (including multilingual OCR)"))
    body_content.append(p("- Handwriting recognition"))
    body_content.append(p("- Pointing (spatial reference)"))
    body_content.append(p("- Variable aspect ratios and resolutions"))
    body_content.append(p("- Interleaved text-image input in any order"))
    body_content.append(p(""))
    
    body_content.append(p("6.3 Audio Capabilities (E2B, E4B, 12B)", "Heading2"))
    body_content.append(p("- Automatic Speech Recognition (ASR)"))
    body_content.append(p("- Speech-to-translated-text (AST) across multiple languages"))
    body_content.append(p("- Maximum 30-second audio segments"))
    body_content.append(p(""))
    
    body_content.append(p("6.4 Coding", "Heading2"))
    body_content.append(p("- Code generation, completion, and correction"))
    body_content.append(p("- Codeforces ELO: 2150 (31B), 1718 (26B), 1659 (12B)"))
    body_content.append(p("- LiveCodeBench v6: 80.0% (31B), 77.1% (26B), 72.0% (12B)"))
    body_content.append(p("- Suitable for IDE integration and coding assistants"))
    body_content.append(p(""))
    
    body_content.append(p("6.5 Reasoning", "Heading2"))
    body_content.append(p("- All models designed as highly capable reasoners"))
    body_content.append(p("- Configurable thinking modes (can be enabled/disabled)"))
    body_content.append(p("- AIME 2026 (no tools): 89.2% (31B), 88.3% (26B), 77.5% (12B)"))
    body_content.append(p("- GPQA Diamond: 84.3% (31B), 82.3% (26B), 78.8% (12B)"))
    body_content.append(p(""))


    # Section 7: Benchmark Results
    body_content.append(p("7. Benchmark Results (Instruction-Tuned Models)", "Heading1"))
    body_content.append(p("7.1 Text and Reasoning Benchmarks", "Heading2"))
    
    # Table: Text benchmarks
    body_content.append('<w:tbl><w:tblPr><w:tblBorders>')
    body_content.append('<w:top w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:bottom w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:left w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:right w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:insideH w:val="single" w:sz="4" w:color="999999"/>')
    body_content.append('<w:insideV w:val="single" w:sz="4" w:color="999999"/>')
    body_content.append('</w:tblBorders></w:tblPr>')
    body_content.append(table_row(["Benchmark", "31B", "26B A4B", "12B", "E4B", "E2B", "Gemma 3 27B"], bold=True))
    body_content.append(table_row(["MMLU Pro", "85.2%", "82.6%", "77.2%", "69.4%", "60.0%", "67.6%"]))
    body_content.append(table_row(["AIME 2026 (no tools)", "89.2%", "88.3%", "77.5%", "42.5%", "37.5%", "20.8%"]))
    body_content.append(table_row(["LiveCodeBench v6", "80.0%", "77.1%", "72.0%", "52.0%", "44.0%", "29.1%"]))
    body_content.append(table_row(["Codeforces ELO", "2150", "1718", "1659", "940", "633", "110"]))
    body_content.append(table_row(["GPQA Diamond", "84.3%", "82.3%", "78.8%", "58.6%", "43.4%", "42.4%"]))
    body_content.append(table_row(["Tau2 (avg over 3)", "76.9%", "68.2%", "69.0%", "42.2%", "24.5%", "16.2%"]))
    body_content.append(table_row(["HLE (no tools)", "19.5%", "8.7%", "5.2%", "-", "-", "-"]))
    body_content.append(table_row(["HLE (with search)", "26.5%", "17.2%", "-", "-", "-", "-"]))
    body_content.append(table_row(["BigBench Extra Hard", "74.4%", "64.8%", "53.0%", "33.1%", "21.9%", "19.3%"]))
    body_content.append(table_row(["MMMLU", "88.4%", "86.3%", "83.4%", "76.6%", "67.4%", "70.7%"]))
    body_content.append('</w:tbl>')
    body_content.append(p(""))


    body_content.append(p("7.2 Vision Benchmarks", "Heading2"))
    body_content.append('<w:tbl><w:tblPr><w:tblBorders>')
    body_content.append('<w:top w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:bottom w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:left w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:right w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:insideH w:val="single" w:sz="4" w:color="999999"/>')
    body_content.append('<w:insideV w:val="single" w:sz="4" w:color="999999"/>')
    body_content.append('</w:tblBorders></w:tblPr>')
    body_content.append(table_row(["Benchmark", "31B", "26B A4B", "12B", "E4B", "E2B", "Gemma 3 27B"], bold=True))
    body_content.append(table_row(["MMMU Pro", "76.9%", "73.8%", "69.1%", "52.6%", "44.2%", "49.7%"]))
    body_content.append(table_row(["OmniDocBench 1.5 (lower=better)", "0.131", "0.149", "0.164", "0.181", "0.290", "0.365"]))
    body_content.append(table_row(["MATH-Vision", "85.6%", "82.4%", "79.7%", "59.5%", "52.4%", "46.0%"]))
    body_content.append(table_row(["MedXPertQA MM", "61.3%", "58.1%", "48.7%", "28.7%", "23.5%", "-"]))
    body_content.append('</w:tbl>')
    body_content.append(p(""))
    
    body_content.append(p("7.3 Audio Benchmarks", "Heading2"))
    body_content.append('<w:tbl><w:tblPr><w:tblBorders>')
    body_content.append('<w:top w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:bottom w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:left w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:right w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:insideH w:val="single" w:sz="4" w:color="999999"/>')
    body_content.append('<w:insideV w:val="single" w:sz="4" w:color="999999"/>')
    body_content.append('</w:tblBorders></w:tblPr>')
    body_content.append(table_row(["Benchmark", "12B", "E4B", "E2B"], bold=True))
    body_content.append(table_row(["CoVoST (BLEU)", "38.5", "35.54", "33.47"]))
    body_content.append(table_row(["FLEURS (WER, lower=better)", "0.069", "0.08", "0.09"]))
    body_content.append('</w:tbl>')
    body_content.append(p(""))
    
    body_content.append(p("7.4 Long Context Benchmark", "Heading2"))
    body_content.append('<w:tbl><w:tblPr><w:tblBorders>')
    body_content.append('<w:top w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:bottom w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:left w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:right w:val="single" w:sz="4" w:color="333333"/>')
    body_content.append('<w:insideH w:val="single" w:sz="4" w:color="999999"/>')
    body_content.append('<w:insideV w:val="single" w:sz="4" w:color="999999"/>')
    body_content.append('</w:tblBorders></w:tblPr>')
    body_content.append(table_row(["Benchmark", "31B", "26B A4B", "12B", "E4B", "E2B", "Gemma 3 27B"], bold=True))
    body_content.append(table_row(["MRCR v2 8-needle 128k (avg)", "66.4%", "44.1%", "43.4%", "25.4%", "19.1%", "13.5%"]))
    body_content.append('</w:tbl>')
    body_content.append(p(""))


    # Section 8: Training Data
    body_content.append(p("8. Training Data", "Heading1"))
    body_content.append(p("8.1 Dataset Composition", "Heading2"))
    body_content.append(p("Pre-training uses a large-scale, diverse collection with a cutoff date of January 2025:"))
    body_content.append(p("- Web Documents: Diverse web text in 140+ languages covering broad linguistic styles and topics"))
    body_content.append(p("- Code: Programming languages syntax, patterns, and documentation"))
    body_content.append(p("- Mathematics: Logical reasoning, symbolic representation, mathematical text"))
    body_content.append(p("- Images: Wide range of visual data for image analysis and visual extraction tasks"))
    body_content.append(p(""))
    body_content.append(p("8.2 Data Preprocessing and Safety Filtering", "Heading2"))
    body_content.append(p("- CSAM Filtering: Rigorous Child Sexual Abuse Material filtering at multiple pipeline stages"))
    body_content.append(p("- Sensitive Data Filtering: Automated removal of personal information and sensitive data"))
    body_content.append(p("- Content Quality Filtering: Quality and safety filtering aligned with Google AI policies"))
    body_content.append(p("- Training data cutoff: January 2025"))
    body_content.append(p(""))
    
    # Section 9: Model Variants
    body_content.append(p("9. Model Variants and Availability", "Heading1"))
    body_content.append(p("Each model size is available in two variants:"))
    body_content.append(p("- Pre-trained (base): Raw model weights for custom fine-tuning"))
    body_content.append(p("- Instruction-tuned (IT): Fine-tuned for conversational and instruction-following tasks"))
    body_content.append(p(""))
    body_content.append(p("Additionally available:"))
    body_content.append(p("- QAT (Quantization-Aware Training) variants for efficient deployment"))
    body_content.append(p("- Multi-Token Prediction (MTP) variant for 12B (faster local inference)"))
    body_content.append(p(""))
    body_content.append(p("Available on: Hugging Face, Kaggle, Ollama, Google AI Studio"))
    body_content.append(p(""))


    # Section 10: Deployment
    body_content.append(p("10. Deployment Targets and Hardware Requirements", "Heading1"))
    body_content.append(p("10.1 On-Device / Edge (E2B, E4B)", "Heading2"))
    body_content.append(p("- Target: Smartphones, tablets, laptops"))
    body_content.append(p("- Optimized for efficient local execution"))
    body_content.append(p("- PLE architecture minimizes active compute while maintaining capability"))
    body_content.append(p("- QAT mobile variants available for further compression"))
    body_content.append(p(""))
    body_content.append(p("10.2 Consumer Hardware (12B)", "Heading2"))
    body_content.append(p("- Target: Laptops with 16GB VRAM or unified memory"))
    body_content.append(p("- ~7GB at 4-bit quantization"))
    body_content.append(p("- Can run on dedicated GPU laptops"))
    body_content.append(p(""))
    body_content.append(p("10.3 Workstation / Server (26B A4B, 31B)", "Heading2"))
    body_content.append(p("- Target: Consumer GPUs, workstations, cloud servers"))
    body_content.append(p("- 26B MoE: All parameters must be in memory (~26B) but inference is fast (4B active)"))
    body_content.append(p("- 31B Dense: Requires more compute but delivers highest quality"))
    body_content.append(p(""))
    
    # Section 11: Key Innovations Summary
    body_content.append(p("11. Key Architectural Innovations vs. Previous Gemma Models", "Heading1"))
    body_content.append(p("- Native system prompt support (new 'system' role)"))
    body_content.append(p("- Configurable thinking mode with <|think|> control token"))
    body_content.append(p("- Per-Layer Embeddings (PLE) for parameter-efficient on-device models"))
    body_content.append(p("- Encoder-free unified architecture (12B) - no separate vision/audio encoders"))
    body_content.append(p("- Proportional RoPE (p-RoPE) for better long-context handling"))
    body_content.append(p("- Unified KV in global attention layers for memory efficiency"))
    body_content.append(p("- Fine-grained MoE with 128 experts (vs. typical 8-16 in other models)"))
    body_content.append(p("- Variable image resolution with configurable token budgets"))
    body_content.append(p("- Native audio processing without separate ASR pipeline (E2B, E4B, 12B)"))
    body_content.append(p("- Native function calling for agentic applications"))
    body_content.append(p("- Dramatically improved agentic performance (tau2: 6.6% -> 86.4%)"))
    body_content.append(p("- Extended context: up to 256K tokens (vs. 128K in Gemma 3)"))
    body_content.append(p(""))


    # Section 12: Comparison with Gemma 3
    body_content.append(p("12. Comparison: Gemma 4 vs. Gemma 3 27B", "Heading1"))
    body_content.append(p("Key improvements of Gemma 4 31B over Gemma 3 27B:"))
    body_content.append(p("- MMLU Pro: 85.2% vs 67.6% (+17.6 points)"))
    body_content.append(p("- AIME 2026: 89.2% vs 20.8% (+68.4 points)"))
    body_content.append(p("- LiveCodeBench v6: 80.0% vs 29.1% (+50.9 points)"))
    body_content.append(p("- Codeforces ELO: 2150 vs 110 (+2040 points)"))
    body_content.append(p("- GPQA Diamond: 84.3% vs 42.4% (+41.9 points)"))
    body_content.append(p("- MMMU Pro (Vision): 76.9% vs 49.7% (+27.2 points)"))
    body_content.append(p("- MRCR Long Context: 66.4% vs 13.5% (+52.9 points)"))
    body_content.append(p("- Tau2 Agentic: 76.9% vs 16.2% (+60.7 points)"))
    body_content.append(p(""))
    
    # Section 13: Safety
    body_content.append(p("13. Safety and Ethics", "Heading1"))
    body_content.append(p("- Same rigorous safety evaluations as proprietary Gemini models"))
    body_content.append(p("- Major improvements in content safety relative to previous Gemma models"))
    body_content.append(p("- Minimal policy violations across all model sizes"))
    body_content.append(p("- Low unjustified refusal rates"))
    body_content.append(p("- Testing conducted without safety filters to evaluate raw model behavior"))
    body_content.append(p("- Evaluated for: CSAM, dangerous content, sexually explicit content, hate speech, harassment"))
    body_content.append(p("- Developed in partnership with internal safety and responsible AI teams"))
    body_content.append(p("- Aligned with Google's AI Principles"))
    body_content.append(p(""))
    
    # Section 14: Limitations
    body_content.append(p("14. Known Limitations", "Heading1"))
    body_content.append(p("- Training data biases may influence outputs"))
    body_content.append(p("- May struggle with highly complex, open-ended tasks"))
    body_content.append(p("- Can generate incorrect or outdated factual statements"))
    body_content.append(p("- May not grasp subtle nuance, sarcasm, or figurative language"))
    body_content.append(p("- Common sense reasoning limitations in certain situations"))
    body_content.append(p("- 26B/31B models do NOT support audio"))
    body_content.append(p("- Audio limited to 30 seconds maximum"))
    body_content.append(p("- Video limited to 60 seconds maximum (at 1 fps)"))
    body_content.append(p(""))


    # Section 15: Sources
    body_content.append(p("15. Sources and References", "Heading1"))
    body_content.append(p("- Google AI for Developers - Gemma 4 Model Card: https://ai.google.dev/gemma/docs/core/model_card_4"))
    body_content.append(p("- Google DeepMind Gemma 4 Page: https://deepmind.google/models/gemma/gemma-4/"))
    body_content.append(p("- Hugging Face Gemma 4 Blog: https://huggingface.co/blog/gemma4"))
    body_content.append(p("- Google Developers Blog - Gemma 4 12B Guide: https://developers.googleblog.com/gemma-4-12b-the-developer-guide/"))
    body_content.append(p("- Hugging Face Model Pages: https://huggingface.co/google/gemma-4-12B"))
    body_content.append(p("- Google Launch Blog: https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/"))
    body_content.append(p(""))
    body_content.append(p("Note: Content was rephrased for compliance with licensing restrictions. All technical specifications sourced from official Google DeepMind documentation and model cards."))
    
    # Assemble the full document
    body_xml = '\n'.join(body_content)
    
    document = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    {body_xml}
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>
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
    output_file = "/projects/sandbox/Gemma_4_Technical_Summary.docx"
    create_docx(output_file)
