# FaceAuth - Demo Video/GIF Shooting Script

## Title: FaceAuth - End-to-End Workflow Demo

### Pre-Production Setup
**Duration**: 60-90 seconds total
**Resolution**: 1280x720 (720p) recommended
**Frame Rate**: 15-20 FPS for GIF, 30 FPS for video
**Recording Tool**: LICEcap, ScreenToGif, OBS Studio, or similar

### Screen Setup
- **Terminal**: Full-screen or large terminal window with clear, readable font (minimum 14pt)
- **File Explorer**: Side-by-side with terminal or separate shots
- **Webcam Window**: Will appear automatically during face operations
- **Background**: Clean desktop, close unnecessary applications
- **Mouse Cursor**: Make sure it's visible and easy to follow

---

## Scene 1: Project Introduction (5-8 seconds)

### Shot 1.1: Title Screen
**Action**: Show clean terminal with project information
**Type in terminal**:
```bash
clear
echo "🔐 FaceAuth Demo - Your Face is Your Key"
echo "Privacy-first face authentication for file security"
echo ""
ls -la
```

**On-Screen Text Overlay**: 
- Top: "🔐 FaceAuth Demo"
- Bottom: "Your Face is Your Key • 100% Local • Zero Cloud"

**Notes**: 
- Keep this brief but impactful
- Show the clean project directory
- Make sure FaceAuth files are visible

---

## Scene 2: Face Enrollment (15-20 seconds)

### Shot 2.1: Start Enrollment
**Action**: Initiate face enrollment process
**Type in terminal**:
```bash
python main.py enroll-face --user-id demo_user
```

**On-Screen Text Overlay**: 
- "Step 1: Enroll Your Face"
- "Registering biometric identity locally"

### Shot 2.2: Webcam Interaction
**Action**: 
- Webcam window appears automatically
- Position face in center of camera frame
- Show the real-time feedback system working
- Green rectangle should appear around face
- Instructions should be visible

**Visual Cues**:
- Face should be well-lit and clearly visible
- Show the crosshair/guidance system
- Demonstrate the quality feedback (green = good)

### Shot 2.3: Capture Moment
**Action**: 
- Press SPACE bar to capture face
- Show webcam window closing
- Return to terminal

### Shot 2.4: Password Entry
**Action**: 
- Terminal prompts: "Enter password for encryption:"
- Type a secure password (hidden/masked input)
- Press Enter

**Password Suggestion**: Use something clear but secure like "SecureDemo123!"

### Shot 2.5: Success Confirmation
**Action**: Terminal shows:
```
✅ Face enrollment successful!
📁 Face data securely stored in: face_data/a1b2c3d4_face.dat
🔒 Data encrypted with AES-256-GCM
```

**On-Screen Text Overlay**: 
- "✅ Enrollment Complete"
- "Face data encrypted and stored locally"

---

## Scene 3: Create Test File (8-10 seconds)

### Shot 3.1: Create Secret File
**Action**: Create a test file to encrypt
**Type in terminal**:
```bash
echo "This is my secret document with sensitive information!" > secret.txt
echo "Account: demo@faceauth.dev" >> secret.txt
echo "Password: MyTopSecretPassword123" >> secret.txt
cat secret.txt
```

**On-Screen Text Overlay**: 
- "Creating a secret file to protect"

### Shot 3.2: Show File in Explorer (Optional)
**Action**: 
- Briefly show file explorer with secret.txt visible
- Show file size and creation time

---

## Scene 4: File Encryption (15-20 seconds)

### Shot 4.1: Start Encryption
**Action**: Initiate file encryption
**Type in terminal**:
```bash
python main.py encrypt-file secret.txt
```

**On-Screen Text Overlay**: 
- "Step 2: Encrypt File with Face Authentication"
- "Your face becomes the key"

### Shot 4.2: Face Verification
**Action**: 
- Webcam window opens again
- Look at camera for face verification
- Show "VERIFYING..." then "ACCESS GRANTED" message
- Webcam window closes

**Visual Cues**:
- Should be faster than enrollment
- Green verification indicator
- Clear success message

### Shot 4.3: Password Confirmation
**Action**: 
- Terminal prompts: "Enter password to confirm:"
- Type the same password from enrollment
- Press Enter

### Shot 4.4: Encryption Success
**Action**: Terminal shows:
```
🔐 File encrypted successfully!
📁 Original: secret.txt (89 bytes)
🔒 Encrypted: secret.txt.faceauth (156 bytes)
✅ Original file preserved
```

**On-Screen Text Overlay**: 
- "🔒 File Encrypted Successfully"
- "Original file protected with face + password"

### Shot 4.5: Show Encrypted File
**Action**: 
```bash
ls -la secret.*
file secret.txt.faceauth
```

**Show**: 
- Original secret.txt still exists
- New secret.txt.faceauth encrypted file
- File types and sizes

---

## Scene 5: File Decryption (12-15 seconds)

### Shot 5.1: Remove Original (Optional)
**Action**: Demonstrate that original can be safely removed
```bash
rm secret.txt
ls secret.*
```

**On-Screen Text Overlay**: 
- "Original file removed - only encrypted version remains"

### Shot 5.2: Start Decryption
**Action**: 
```bash
python main.py decrypt-file secret.txt.faceauth
```

**On-Screen Text Overlay**: 
- "Step 3: Decrypt with Face Authentication"
- "Unlocking your protected data"

### Shot 5.3: Face Verification for Decryption
**Action**: 
- Webcam opens again
- Face verification process
- "ACCESS GRANTED" message
- Webcam closes

### Shot 5.4: Password Entry
**Action**: 
- Enter the same password
- Press Enter

### Shot 5.5: Decryption Success
**Action**: Terminal shows:
```
🔓 File decrypted successfully!
📁 Decrypted: secret.txt
✅ Original content restored
```

### Shot 5.6: Verify Content
**Action**: 
```bash
cat secret.txt
```

**Show**: Original content is perfectly restored

**On-Screen Text Overlay**: 
- "✅ File Decrypted Successfully"
- "Original content perfectly restored"

---

## Scene 6: Demo Conclusion (8-10 seconds)

### Shot 6.1: Summary
**Action**: 
```bash
clear
echo "🎉 FaceAuth Demo Complete!"
echo ""
echo "✅ Face enrolled and encrypted locally"
echo "✅ File protected with face + password"
echo "✅ Secure decryption with biometric auth"
echo "✅ Zero cloud dependencies"
echo ""
echo "Your face is your key. Your data stays yours."
```

**On-Screen Text Overlay**: 
- "🎉 Demo Complete!"
- "github.com/yourusername/FaceAuth"

### Shot 6.2: Call to Action
**Final Frame Text Overlay**:
```
🔐 FaceAuth
Your Face is Your Key

✅ 100% Local Processing
✅ Military-Grade Encryption  
✅ Zero Cloud Dependencies
✅ Open Source & Free

github.com/yourusername/FaceAuth
Star ⭐ if you believe in privacy!
```

---

## Production Notes

### Technical Requirements
- **Lighting**: Ensure face is well-lit during webcam segments
- **Audio**: Consider adding background music or keeping silent for GIF
- **Timing**: Each command should have 1-2 second pause for readability
- **Text Size**: Terminal font should be large enough to read in compressed format

### Editing Guidelines
- **Transitions**: Smooth cuts between scenes, no fancy effects needed
- **Speed**: Can be slightly sped up (1.2x-1.5x) for GIF format
- **Quality**: Balance file size vs. quality for web deployment
- **Captions**: Add clear, readable captions for key moments

### Accessibility
- **Color Contrast**: Ensure good contrast in terminal
- **Text Overlays**: Large, clear fonts for overlays
- **Visual Cues**: Clear indication when face detection succeeds/fails

### Alternative Versions
- **Short Version** (30-45 seconds): Focus only on enrollment + encryption
- **Technical Version** (2-3 minutes): Show more terminal output and technical details
- **Silent GIF**: Remove all audio, rely on visual cues and text overlays

### File Naming
- `faceauth_demo_full.gif` (complete workflow)
- `faceauth_demo_short.gif` (abbreviated version)
- `faceauth_demo.mp4` (video version with audio)

---

## Quality Checklist

Before finalizing:
- [ ] All text is readable when compressed
- [ ] Face detection clearly shows success/failure
- [ ] Terminal commands are typed at readable speed
- [ ] File operations show clear before/after states
- [ ] Webcam interactions are smooth and clear
- [ ] Final file size is appropriate for web (< 10MB for GIF)
- [ ] All security messages are visible
- [ ] Call-to-action is clear and compelling

---

**Remember**: This demo represents real users' first impression of FaceAuth. Make it count!
