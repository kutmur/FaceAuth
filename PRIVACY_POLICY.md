# FaceAuth Privacy Policy

**Effective Date:** July 1, 2025  
**Last Updated:** July 1, 2025

## Privacy-First Commitment

FaceAuth is designed with **privacy by design** principles. We are committed to protecting your biometric data and ensuring complete transparency about how your information is handled.

## Data Collection and Processing

### What Data We Collect

**Biometric Templates Only:**
- Mathematical representations of facial features (512-dimensional vectors)
- Quality metrics (sharpness, brightness, contrast scores)
- Enrollment timestamps and metadata

**What We DON'T Collect:**
- ❌ Raw facial images or photographs
- ❌ Personal identifying information beyond user IDs you provide
- ❌ Usage analytics or behavioral data
- ❌ Device information or system details

### How Data Is Generated

1. **Face Detection**: Camera captures facial region using MTCNN algorithm
2. **Feature Extraction**: FaceNet generates mathematical embedding (not an image)
3. **Template Creation**: 512-dimensional vector represents facial geometry
4. **Secure Storage**: Template encrypted and stored locally

**Important:** The mathematical template cannot be used to reconstruct your face or create images.

## Data Storage and Security

### Local Storage Only

- **100% Local**: All data remains on your device
- **No Cloud**: No data transmission to external servers
- **No Network**: Zero network requests or internet dependencies
- **Offline Operation**: Complete functionality without internet connection

### Storage Location

```
Default Location: ~/.faceauth/
├── users/{user_id}/
│   ├── embedding.enc         # Your encrypted biometric template
│   └── metadata.enc          # Encrypted enrollment information
├── logs/
│   └── audit_{date}.enc      # Encrypted security logs
└── config/
    └── system.conf           # Non-sensitive configuration
```

### Security Measures

**Encryption at Rest:**
- **Algorithm**: AES-256-GCM (military-grade encryption)
- **Key Derivation**: PBKDF2 with 100,000+ iterations or Argon2
- **Salt**: Unique cryptographic salt per user
- **Authentication**: HMAC for integrity verification

**File System Security:**
- **Permissions**: Unix 600 (owner read/write only)
- **Directory Access**: Unix 700 (owner access only)
- **Secure Deletion**: Cryptographic erasure when data is removed

**Memory Protection:**
- **Secure Allocation**: Protected memory pages
- **Automatic Cleanup**: Sensitive data wiped after use
- **Anti-Forensics**: Memory overwritten to prevent recovery

## Data Retention and Deletion

### Retention Policy

- **Default**: Data stored indefinitely until manually deleted
- **Configurable**: You can set custom retention periods
- **Automatic Cleanup**: Optional automatic deletion after specified period
- **User Control**: Delete data anytime using CLI commands

### Secure Deletion

When you delete your data:
1. **Cryptographic Erasure**: Encryption keys securely destroyed
2. **File Overwriting**: Storage space overwritten multiple times
3. **Memory Clearing**: RAM wiped of sensitive information
4. **Audit Trail**: Deletion events logged (without sensitive data)

## Your Privacy Rights

### GDPR Rights (EU Users)

**Right to Access:**
```bash
python main.py privacy-settings {user_id} --export-data user_data.json
```

**Right to Rectification:**
- Re-enroll to update biometric template
- Modify user preferences through configuration

**Right to Erasure ("Right to be Forgotten"):**
```bash
python main.py privacy-settings {user_id} --delete-data
```

**Right to Data Portability:**
- Export your data in JSON format
- Transfer to other compatible systems

**Right to Object:**
```bash
python main.py privacy-settings {user_id} --revoke-consent
```

### CCPA Rights (California Users)

- **Right to Know**: This policy details all data collection
- **Right to Delete**: Use deletion commands provided
- **Right to Opt-Out**: Revoke consent anytime
- **Non-Discrimination**: No penalties for exercising rights

## Consent Management

### Explicit Consent

During enrollment, you provide explicit consent for:
- Biometric data processing for authentication
- Local storage of encrypted templates
- Security logging of authentication events

### Consent Withdrawal

```bash
# Revoke consent (stops all processing)
python main.py privacy-settings {user_id} --revoke-consent

# Check current consent status
python main.py privacy-settings {user_id}
```

### Granular Control

- **Purpose Limitation**: Data used only for authentication
- **Minimal Processing**: Only necessary operations performed
- **Consent Logging**: All consent changes securely recorded

## Data Sharing and Third Parties

### No Data Sharing

- **Zero Third Parties**: No data shared with any external entities
- **No Analytics**: No usage data collected or transmitted
- **No Advertising**: No data used for marketing or ads
- **No Partnerships**: No data sharing agreements

### Code Transparency

- **Open Source**: Complete source code available for audit
- **No Hidden Functions**: All data processing operations visible
- **Community Review**: Security practices subject to peer review

## Security Incident Response

### Our Commitments

If a security issue is discovered:

1. **Immediate Assessment**: Evaluate scope and impact
2. **User Notification**: Inform affected users within 72 hours
3. **Remediation**: Deploy fixes and security updates
4. **Documentation**: Publish incident report and lessons learned

### Your Protections

- **Local Data**: No central database to compromise
- **Encryption**: Data remains protected even if files accessed
- **Isolation**: Each user's data independently secured

## Children's Privacy

FaceAuth is not intended for children under 13. We do not knowingly collect biometric data from children. If you believe a child has used FaceAuth, please contact us immediately.

## International Users

### Data Residency

- **Local Storage**: Data never leaves your jurisdiction
- **No Transfers**: No cross-border data movement
- **Compliance**: Meets local privacy regulations

### Applicable Laws

- **EU**: GDPR compliance for European users
- **California**: CCPA compliance for California residents  
- **General**: Follows privacy best practices globally

## Privacy by Design

### Core Principles

1. **Data Minimization**: Collect only necessary biometric templates
2. **Purpose Limitation**: Use data only for stated authentication purpose
3. **Storage Minimization**: Retain data only as long as needed
4. **Access Control**: Strict limitations on data access
5. **Transparency**: Clear information about all data practices
6. **User Control**: You maintain full control over your data

## Technical Safeguards

### Cryptographic Protection

- **Encryption Standard**: FIPS 140-2 approved algorithms
- **Key Management**: Secure key derivation and storage
- **Perfect Forward Secrecy**: Past data protected even if keys compromised
- **Quantum Resistance**: Preparation for post-quantum cryptography

### System Security

- **Secure Development**: Security-first coding practices
- **Regular Audits**: Automated security scanning and manual review
- **Dependency Management**: Secure third-party library usage
- **Update Mechanism**: Secure software update process

## Contact and Questions

### Privacy Questions

For questions about this privacy policy or your data:

- **GitHub Issues**: [Repository Issues Page]
- **Security Issues**: [Security Contact] (GPG key available)
- **General Questions**: [Project Documentation]

### Data Protection Officer

While FaceAuth operates without data collection requiring a DPO, privacy questions can be directed to the project maintainers through official channels.

## Policy Updates

### Notification of Changes

- **Major Changes**: 30-day advance notice
- **Minor Updates**: Notice with next software update
- **Version Control**: All policy versions tracked in repository
- **User Rights**: Opt-out if you disagree with changes

### Effective Date

This policy is effective immediately upon installation of FaceAuth. Continued use constitutes acceptance of these terms.

---

**Remember: With FaceAuth, your biometric data never leaves your device. You maintain complete control and ownership of your privacy.**
