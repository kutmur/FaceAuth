# FaceAuth Visual Assets

This directory contains visual assets for the FaceAuth project including logos, diagrams, screenshots, and demo materials.

## Directory Structure

```
assets/
├── logos/              # FaceAuth branding and logos
├── screenshots/        # Application screenshots  
├── diagrams/          # Architecture and flow diagrams
├── demos/             # Demo videos and GIFs
└── docs/              # Documentation images
```

## Logo Usage Guidelines

### Primary Logo
- Use the primary logo for official documentation
- Maintain clear space around the logo
- Do not modify colors or proportions

### Color Palette
- **Primary**: #1a237e (Deep Blue) - Security and trust
- **Secondary**: #2e7d32 (Green) - Privacy and safety  
- **Accent**: #ff6f00 (Orange) - Authentication and action
- **Text**: #212121 (Dark Gray) - Readability

### Typography
- **Headers**: Roboto Bold
- **Body**: Roboto Regular
- **Code**: Roboto Mono

## Screenshot Guidelines

### Capturing Screenshots
1. Use consistent window sizes (1200x800 minimum)
2. Include clear command outputs
3. Show successful operations
4. Blur or redact any sensitive information
5. Use high DPI displays when possible

### Naming Convention
- `enrollment_success.png` - Successful enrollment
- `authentication_demo.png` - Authentication process
- `file_encryption.png` - File encryption workflow
- `cli_help.png` - CLI help output
- `security_audit.png` - Security audit results

## Demo Content

### Demo Videos/GIFs
Create animated demonstrations showing:
1. **Complete enrollment process** (30-60 seconds)
2. **Authentication workflow** (15-30 seconds)  
3. **File encryption demo** (45-60 seconds)
4. **CLI usage examples** (30-45 seconds)

### Demo Scripts
Include commentary for demos:
- Explain each step clearly
- Highlight security features
- Show real-time performance
- Demonstrate error handling

## Architecture Diagrams

### Security Architecture
```
┌─────────────────────────────────────────────────────────┐
│                 FaceAuth Security Layers                │
├─────────────────────────────────────────────────────────┤
│ Application Layer: CLI + Core Authentication            │
├─────────────────────────────────────────────────────────┤
│ Privacy Layer: Consent Management + Data Rights         │
├─────────────────────────────────────────────────────────┤
│ Security Layer: Encryption + Access Control + Audit     │
├─────────────────────────────────────────────────────────┤
│ Storage Layer: Encrypted Files + Secure Deletion       │
├─────────────────────────────────────────────────────────┤
│ System Layer: Memory Protection + File Permissions      │
└─────────────────────────────────────────────────────────┘
```

### Data Flow Diagram
```
Face Capture → Feature Extraction → Template Generation → Encryption → Local Storage
     ↓               ↓                     ↓               ↓            ↓
  Camera Only    Mathematical Only    512-dim Vector   AES-256-GCM   Your Device Only
```

### Privacy Architecture
```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   User Consent   │    │  Data Processing │    │  Rights Management│
│                  │    │                  │    │                  │
│ • Explicit opt-in│    │ • Local only     │    │ • Data export    │
│ • Granular perms │    │ • No cloud sync  │    │ • Data deletion  │
│ • Audit trail   │    │ • Encrypted store│    │ • Access logs    │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

## File Templates

### Sample README Badge
```markdown
[![FaceAuth](assets/badges/faceauth-privacy-first.svg)](README.md)
```

### Sample Documentation Header
```markdown
![FaceAuth Logo](assets/logos/faceauth-logo-dark.png)

# FaceAuth Documentation
*Privacy-First Face Authentication*
```

## Creating Visual Assets

### Tools Recommended
- **Logos**: Adobe Illustrator, Inkscape (free)
- **Screenshots**: Built-in OS tools, LightShot
- **Diagrams**: Draw.io, Lucidchart, Mermaid
- **GIFs**: LICEcap, GIMP, ScreenToGif
- **Videos**: OBS Studio, QuickTime

### Asset Requirements
- **Logos**: SVG format preferred, PNG fallback
- **Screenshots**: PNG format, high resolution
- **Diagrams**: SVG or PNG, clean and readable
- **Videos**: MP4 format, H.264 codec
- **GIFs**: Optimized for web, <5MB preferred

## Placeholder Assets

Until custom assets are created, you can use:

### Text-based Logo
```
🔐 FaceAuth
Privacy-First Face Authentication
```

### ASCII Art Logo
```
 ______               _         _   _   _ 
|  ____|             / \       | | | | | |
| |__ __ _  ___ ___  / _ \ _   _| |_| |_| |
|  __/ _` |/ __/ _ \/ ___ \ | | | __| __| |
| | | (_| | (_|  __/ /   \ \ |_| | |_| |_|_|
|_|  \__,_|\___\___/_/     \_\__,_|\__|\__(_)

Privacy-First Face Authentication
```

### Basic Shields/Badges
```markdown
![Privacy](https://img.shields.io/badge/Privacy-Local%20Only-brightgreen)
![Security](https://img.shields.io/badge/Security-AES--256-blue)
![Platform](https://img.shields.io/badge/Platform-Cross--Platform-lightgrey)
```

## Usage Examples

### In Documentation
```markdown
![Enrollment Process](assets/screenshots/enrollment_process.png)
*Figure 1: Face enrollment process showing camera capture and quality assessment*

![Security Architecture](assets/diagrams/security_architecture.svg)  
*Figure 2: Multi-layered security architecture ensuring data protection*
```

### In README
```markdown
## 🚀 Quick Demo

![Face Authentication Demo](assets/demos/authentication_demo.gif)

See FaceAuth in action: secure, fast, and completely private face authentication.
```

## Contributing Visual Assets

### Guidelines for Contributors
1. **Follow brand guidelines** for consistency
2. **Use high-quality assets** suitable for documentation
3. **Include source files** when possible (AI, PSD, etc.)
4. **Optimize for web** (reasonable file sizes)
5. **Test on different backgrounds** (dark/light themes)

### Submission Process
1. Create assets following guidelines
2. Test in documentation context
3. Submit via pull request
4. Include description of intended usage
5. Ensure licensing compatibility (open source friendly)

---

*FaceAuth Visual Assets Guide v1.0 | Privacy-First Face Authentication*
