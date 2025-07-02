# FaceAuth Workflow Diagrams

## 1. User Enrollment Workflow

```
┌─────────────┐
│   Start     │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ Open GUI/   │────▶│ Initialize  │
│ Run Script  │     │ Camera      │
└─────────────┘     └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Capture     │◀─┐
                    │ Face Image  │  │
                    └──────┬──────┘  │
                           │         │
                           ▼         │
                    ┌─────────────┐  │
                    │ Face        │  │
                    │ Detected?   │──┘ No
                    └──────┬──────┘
                           │ Yes
                           ▼
                    ┌─────────────┐
                    │ Extract     │
                    │ Features    │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Generate    │
                    │ Template    │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Encrypt &   │
                    │ Store       │
                    │ Template    │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Enrollment  │
                    │ Complete    │
                    └─────────────┘
```

## 2. Authentication Workflow

```
┌─────────────┐
│ Start Auth  │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ Initialize  │────▶│ Load Stored │
│ Camera      │     │ Templates   │
└─────────────┘     └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Capture     │◀─┐
                    │ Face Image  │  │
                    └──────┬──────┘  │
                           │         │
                           ▼         │
                    ┌─────────────┐  │
                    │ Face        │  │
                    │ Detected?   │──┘ No
                    └──────┬──────┘
                           │ Yes
                           ▼
                    ┌─────────────┐
                    │ Extract     │
                    │ Features    │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Compare     │
                    │ with        │
                    │ Templates   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Match       │
                    │ Found?      │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼ Yes         ▼ No
            ┌─────────────┐ ┌─────────────┐
            │ Auth        │ │ Auth        │
            │ Success     │ │ Failed      │
            └─────────────┘ └─────────────┘
```

## 3. File Encryption Workflow

```
┌─────────────┐
│ Select File │
│ for         │
│ Encryption  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Authenticate│────┐
│ User        │    │
└──────┬──────┘    │
       │ Success   │ Fail
       ▼           ▼
┌─────────────┐ ┌─────────────┐
│ Derive      │ │ Show Error  │
│ Encryption  │ │ Message     │
│ Key from    │ └─────────────┘
│ Biometric   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Generate    │
│ Random Salt │
│ & IV        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Encrypt     │
│ File with   │
│ AES-256     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Save        │
│ Encrypted   │
│ File +      │
│ Metadata    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Delete      │
│ Original    │
│ File        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Show        │
│ Success     │
│ Message     │
└─────────────┘
```

## 4. File Decryption Workflow

```
┌─────────────┐
│ Select      │
│ Encrypted   │
│ File        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Authenticate│────┐
│ User        │    │
└──────┬──────┘    │
       │ Success   │ Fail
       ▼           ▼
┌─────────────┐ ┌─────────────┐
│ Read        │ │ Show Error  │
│ Metadata &  │ │ Message     │
│ Salt        │ └─────────────┘
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Derive      │
│ Decryption  │
│ Key from    │
│ Biometric   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Decrypt     │
│ File with   │
│ AES-256     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Verify      │
│ Decryption  │
│ Success     │
└──────┬──────┘
       │
┌──────┴──────┐
│             │
▼ Success     ▼ Fail
┌─────────────┐ ┌─────────────┐
│ Save        │ │ Show Error  │
│ Decrypted   │ │ Invalid     │
│ File        │ │ Credentials │
└──────┬──────┘ └─────────────┘
       │
       ▼
┌─────────────┐
│ Delete      │
│ Encrypted   │
│ File        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Show        │
│ Success     │
│ Message     │
└─────────────┘
```

## 5. System Performance Monitoring

```
┌─────────────┐
│ Start       │
│ Monitoring  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Initialize  │
│ Metrics     │
│ Collection  │
└──────┬──────┘
       │
       ▼
┌─────────────┐ ┌─────────────┐
│ Monitor     │ │ Monitor     │
│ CPU Usage   │ │ Memory      │
└──────┬──────┘ └──────┬──────┘
       │               │
       └───────┬───────┘
               ▼
        ┌─────────────┐
        │ Monitor     │
        │ I/O & Face  │
        │ Recognition │
        │ Performance │
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐
        │ Check       │
        │ Performance │
        │ Thresholds  │
        └──────┬──────┘
               │
        ┌──────┴──────┐
        │             │
        ▼ Normal      ▼ Issues
 ┌─────────────┐ ┌─────────────┐
 │ Continue    │ │ Generate    │
 │ Monitoring  │ │ Alert &     │
 └──────┬──────┘ │ Suggestions │
        │        └─────────────┘
        │
        └◀──────────┘
```

## Key Decision Points

### Authentication Threshold
- **High Security**: 95%+ match confidence
- **Balanced**: 85-95% match confidence  
- **Convenient**: 75-85% match confidence

### Performance Optimization
- **CPU Usage**: < 70% during operation
- **Memory**: < 512MB for basic operations
- **Recognition Time**: < 2 seconds per attempt
- **File I/O**: Optimized for large files (chunked processing)

### Error Handling
- **Camera Issues**: Fallback to image upload
- **Recognition Failures**: Multiple attempt allowance
- **File Corruption**: Backup and recovery mechanisms
- **System Resources**: Graceful degradation
