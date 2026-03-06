# TrustHire UML Diagrams - High Resolution

This folder contains all exported UML diagrams for the TrustHire Job Search and Fraud Detection System in **HIGH QUALITY** formats.

## 🎯 Available Formats

All diagrams are available in **TWO formats** for maximum clarity:

- **PNG** - High-resolution (2400-2800px width, 3x scale, white background) for presentations and documents
- **SVG** - Scalable vector graphics for infinite zoom and perfect clarity at any size

## 📊 Diagram Files

### 1. Use Case Diagram ✅
- **PNG**: `01_UseCase_Diagram-1.png` (251 KB) - 2400x1800px
- **SVG**: `01_UseCase_Diagram-1.svg` (35 KB) - Scalable
- Shows all actors (Job Seeker, Admin) and use cases with relationships

### 2. Class Diagram ✅
- **PNG**: `02_Class_Diagram-1.png` (1.3 MB) - 2800x2400px
- **SVG**: `02_Class_Diagram-1.svg` (93 KB) - Scalable
- Full class structure with 8 core classes, attributes, methods, and relationships

### 3. Sequence Diagrams ✅
- **PNG Files** (4 variations):
  - `03_Sequence_Diagram-1.png` (755 KB) - Main user search flow
  - `03_Sequence_Diagram-2.png` (151 KB) - Alternative sequence
  - `03_Sequence_Diagram-3.png` (232 KB) - Detailed message flow
  - `03_Sequence_Diagram-4.png` (204 KB) - Component interactions
- **SVG Files**: All 4 variations available (23-42 KB each)

### 4. Collaboration Diagram ⚠️
- **Not exported** - Syntax limitations in Mermaid CLI
- Refer to `04_Collaboration_Diagram.md` for the diagram code (viewable in GitHub/VS Code)

### 5. Activity Diagrams ✅
- **PNG Files** (4 variations, 2600x3000px):
  - `05_Activity_Diagram-1.png` (938 KB) - Complete workflow
  - `05_Activity_Diagram-2.png` (850 KB) - Input validation and scraping
  - `05_Activity_Diagram-3.png` (289 KB) - Fraud detection process
  - `05_Activity_Diagram-4.png` (412 KB) - Results display and actions
- **SVG Files**: All 4 variations (120-189 KB each)

### 6. State Chart Diagrams ✅
- **PNG Files** (5 variations, 2800x2600px):
  - `06_StateChart_Diagram-1.png` (709 KB) - Main state machine
  - `06_StateChart_Diagram-2.png` (803 KB) - Search and scraping states
  - `06_StateChart_Diagram-3.png` (520 KB) - Fraud analysis states
  - `06_StateChart_Diagram-4.png` (394 KB) - User interaction states
  - `06_StateChart_Diagram-5.png` (420 KB) - Complete transitions
- **SVG Files**: All 5 variations (426-1159 KB each)

### 7. Component Diagram ✅
- **PNG**: `07_Component_Diagram-1.png` (477 KB) - 2400x2000px
- **SVG**: `07_Component_Diagram-1.svg` (75 KB) - Scalable
- 3-tier architecture with all components and dependencies

### 8. Deployment Diagram ✅
- **PNG**: `08_Deployment_Diagram-1.png` (603 KB) - 2400x2200px
- **SVG**: `08_Deployment_Diagram-1.svg` (49 KB) - Scalable
- Physical deployment topology on Windows with nodes and protocols

## 📁 File Statistics

- **Total PNG Files**: 17 high-resolution images
- **Total SVG Files**: 17 scalable vector graphics
- **Total Size**: ~11 MB (PNG: ~9.3 MB, SVG: ~1.7 MB)
- **PNG Settings**: 2400-2800px width, 3x scale factor, white background
- **SVG Settings**: Scalable vectors, perfect for zooming and printing
- **Quality**: Crystal-clear text and shapes suitable for any use

## 🔍 How to Use

### For Maximum Clarity:
1. **Use SVG files** - Perfect for presentations, documentation, and websites. Infinite zoom without quality loss
2. **Use PNG files** - High-resolution for printing, email attachments, and compatibility

### Viewing Options:
1. **View in File Explorer**: 
   - PNG: Double-click to view in any image viewer
   - SVG: Open in Chrome/Edge browser for best quality
2. **Insert in Documents**: 
   - Word/PowerPoint: Use PNG files for best compatibility
   - Web pages: Use SVG files for responsive, crisp display
   - Google Docs: Drag and drop PNG files
3. **Include in README**: Use relative paths in markdown:
   ```markdown
   ![Use Case Diagram](docs/diagrams/01_UseCase_Diagram-1.png)
   ![Use Case Diagram](docs/diagrams/01_UseCase_Diagram-1.svg)
   ```
4. **Print**: All PNG diagrams are print-ready at 300+ DPI equivalent
5. **Zoom**: For detailed inspection, use SVG files which scale infinitely without blur

## 🎨 Quality Features

- ✅ **3x Scale Factor** - Extra sharp text and lines in PNG files
- ✅ **White Background** - Maximum contrast for readability
- ✅ **Large Canvas** - 2400-2800px width ensures clarity on large displays
- ✅ **Vector SVG** - Perfect quality at any zoom level
- ✅ **Professional Grade** - Suitable for academic papers, presentations, and documentation

## 🛠️ Re-exporting Diagrams

To regenerate the high-quality diagrams:

```powershell
cd docs

# Export as SVG (scalable)
mmdc -i "01_UseCase_Diagram.md" -o "diagrams/01_UseCase_Diagram.svg" -w 2400 -H 1800

# Export as high-res PNG (3x scale, white background)
mmdc -i "01_UseCase_Diagram.md" -o "diagrams/01_UseCase_Diagram.png" -w 2400 -H 1800 -s 3 -b white

# Repeat for other diagrams...
```

**Requires**: `npm install -g @mermaid-js/mermaid-cli`

## 📝 Notes

- ✅ **Dual Format**: Every diagram available in both PNG and SVG
- ⚠️ **Collaboration Diagram**: Cannot be exported due to Mermaid CLI syntax limitations
- 📐 **Multiple Variations**: Some markdown files contain multiple diagram views
- 🎨 **Color Coding**: Red (critical), Blue (ML/AI), Green (data), Purple (external), Orange (Flask)
- 🔍 **Source Files**: All diagrams also viewable in `docs/*.md` files on GitHub and VS Code
- 💡 **Recommendation**: Use SVG for digital viewing, PNG for printing/compatibility

## 🚀 Best Practices

1. **For Presentations**: Use SVG files - they scale perfectly on any screen size
2. **For Printing**: Use PNG files - they're optimized for high-DPI printing
3. **For Documentation**: Use SVG in web docs, PNG in Word/PDF
4. **For Sharing**: PNG files work everywhere, more compatible
5. **For Archiving**: Keep both formats for maximum flexibility

---

**Generated**: March 5, 2026  
**Tool**: Mermaid CLI v11.x (with high-resolution settings)  
**Quality**: Professional-grade, presentation-ready  
**Source Files**: `docs/*.md`
