#!/usr/bin/env python3
"""
FaceAuth Simple GUI Application
A simplified graphical user interface for face-recognition-based file encryption and decryption.

This application provides an intuitive interface for:
- Basic face detection and capture
- File encryption and decryption
- Secure local authentication

Requirements:
- opencv-python
- cryptography
- tkinter (included with Python)
- pillow
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
import os
import json
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PIL import Image, ImageTk
import time
from datetime import datetime


class SimpleFaceAuthGUI:
    """Simple GUI application for face-based file encryption using OpenCV."""
    
    def __init__(self, root):
        """Initialize the Simple FaceAuth GUI application."""
        self.root = root
        self.root.title("FaceAuth - Simple Face Recognition File Protection")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Application state
        self.enrolled_face_data = None
        self.is_authenticated = False
        self.camera_active = False
        self.video_capture = None
        
        # Face detection
        self.face_cascade = None
        self.load_face_detector()
        
        # File paths
        self.data_dir = "data"
        self.faces_dir = os.path.join(self.data_dir, "faces")
        self.encrypted_dir = os.path.join(self.data_dir, "encrypted")
        self.enrollment_file = os.path.join(self.faces_dir, "enrolled_face_simple.json")
        
        # Create necessary directories
        self.create_directories()
        
        # Load existing enrollment if available
        self.load_enrollment()
        
        # Setup GUI
        self.setup_gui()
        
    def load_face_detector(self):
        """Load OpenCV face detection cascade."""
        try:
            # Try to load Haar cascade for face detection
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            if self.face_cascade.empty():
                raise Exception("Could not load face cascade")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load face detector: {str(e)}")
            self.face_cascade = None
        
    def create_directories(self):
        """Create necessary directories for data storage."""
        for directory in [self.data_dir, self.faces_dir, self.encrypted_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                
    def setup_gui(self):
        """Setup the main GUI components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="FaceAuth - Simple File Protection", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Welcome! Please enroll your face to get started.", 
                                     wraplength=700, font=('Arial', 10))
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Authentication status indicator
        self.auth_status_label = ttk.Label(status_frame, text="❌ Not Authenticated", 
                                          font=('Arial', 10, 'bold'), foreground='red')
        self.auth_status_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Face operations frame
        face_frame = ttk.LabelFrame(main_frame, text="Face Authentication", padding="10")
        face_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        face_frame.columnconfigure(0, weight=1)
        face_frame.columnconfigure(1, weight=1)
        
        self.enroll_button = ttk.Button(face_frame, text="📷 Enroll Face", 
                                       command=self.enroll_face)
        self.enroll_button.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.auth_button = ttk.Button(face_frame, text="🔐 Authenticate Face", 
                                     command=self.authenticate_face)
        self.auth_button.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # File operations frame
        file_frame = ttk.LabelFrame(main_frame, text="File Operations", padding="10")
        file_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        file_frame.columnconfigure(1, weight=1)
        
        self.encrypt_button = ttk.Button(file_frame, text="🔒 Encrypt File", 
                                        command=self.encrypt_file, state='disabled')
        self.encrypt_button.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.decrypt_button = ttk.Button(file_frame, text="🔓 Decrypt File", 
                                        command=self.decrypt_file, state='disabled')
        self.decrypt_button.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # Camera preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="Camera Preview", padding="10")
        preview_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.camera_label = ttk.Label(preview_frame, text="Camera preview will appear here", 
                                     background='black', foreground='white')
        self.camera_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        control_frame.columnconfigure(2, weight=1)
        
        self.clear_button = ttk.Button(control_frame, text="Clear Enrollment", 
                                      command=self.clear_enrollment)
        self.clear_button.grid(row=0, column=0, padx=(0, 10))
        
        self.help_button = ttk.Button(control_frame, text="Help", command=self.show_help)
        self.help_button.grid(row=0, column=1, padx=(0, 10))
        
        exit_button = ttk.Button(control_frame, text="Exit", command=self.on_closing)
        exit_button.grid(row=0, column=3)
        
        # Setup window closing protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def update_status(self, message, color='black'):
        """Update the status label with a message."""
        self.status_label.config(text=message, foreground=color)
        self.root.update_idletasks()
        
    def update_auth_status(self, authenticated=False):
        """Update authentication status indicator."""
        if authenticated:
            self.auth_status_label.config(text="✅ Authenticated", foreground='green')
            self.encrypt_button.config(state='normal')
            self.decrypt_button.config(state='normal')
        else:
            self.auth_status_label.config(text="❌ Not Authenticated", foreground='red')
            self.encrypt_button.config(state='disabled')
            self.decrypt_button.config(state='disabled')
        
        self.is_authenticated = authenticated
        
    def load_enrollment(self):
        """Load existing face enrollment from file."""
        try:
            if os.path.exists(self.enrollment_file):
                with open(self.enrollment_file, 'r') as f:
                    data = json.load(f)
                    
                self.enrolled_face_data = data
                self.update_status("Previous face enrollment loaded. You can authenticate now.", 'green')
                return True
        except Exception as e:
            print(f"Error loading enrollment: {e}")
            self.update_status("Error loading previous enrollment. Please enroll again.", 'red')
            
        return False
        
    def save_enrollment(self, face_data):
        """Save face enrollment to file."""
        try:
            enrollment_data = {
                'timestamp': datetime.now().isoformat(),
                'face_hash': face_data,
                'version': '1.0'
            }
            
            with open(self.enrollment_file, 'w') as f:
                json.dump(enrollment_data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving enrollment: {e}")
            return False
    
    def start_camera(self):
        """Start the camera for face capture."""
        if self.camera_active:
            return False
            
        try:
            self.video_capture = cv2.VideoCapture(0)
            if not self.video_capture.isOpened():
                raise Exception("Could not open camera")
                
            self.camera_active = True
            return True
        except Exception as e:
            messagebox.showerror("Camera Error", f"Failed to open camera: {str(e)}")
            return False
    
    def stop_camera(self):
        """Stop the camera."""
        self.camera_active = False
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        
        # Clear camera preview
        self.camera_label.config(image='', text="Camera preview will appear here")
        
    def detect_faces(self, frame):
        """Detect faces in the frame using OpenCV."""
        if self.face_cascade is None:
            return []
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces
    
    def create_face_signature(self, frame, face_rect):
        """Create a simple signature from face region."""
        x, y, w, h = face_rect
        face_region = frame[y:y+h, x:x+w]
        
        # Resize to standard size
        face_resized = cv2.resize(face_region, (100, 100))
        
        # Convert to grayscale and compute histogram
        gray_face = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray_face], [0], None, [256], [0, 256])
        
        # Create hash from histogram
        hist_str = str(hist.flatten().tolist())
        face_hash = hashlib.sha256(hist_str.encode()).hexdigest()
        
        return face_hash
    
    def capture_and_process_face(self, for_enrollment=True):
        """Capture face from camera and process it."""
        if not self.start_camera():
            return None
            
        self.update_status("Camera opened. Position your face in front of the camera and press SPACE to capture, ESC to cancel.", 'blue')
        
        face_data = None
        captured = False
        
        while self.camera_active and not captured:
            ret, frame = self.video_capture.read()
            if not ret:
                break
                
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect faces
            faces = self.detect_faces(frame)
            
            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Face Detected", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Add instructions
            instruction_text = "SPACE: Capture | ESC: Cancel"
            cv2.putText(frame, instruction_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Convert frame for tkinter display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            
            # Resize to fit preview area
            frame_pil = frame_pil.resize((640, 480), Image.Resampling.LANCZOS)
            frame_tk = ImageTk.PhotoImage(frame_pil)
            
            # Update GUI
            self.camera_label.config(image=frame_tk, text="")
            self.camera_label.image = frame_tk  # Keep a reference
            self.root.update()
            
            # Check for key presses
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # Space key
                if len(faces) > 0:
                    # Use the first detected face
                    face_data = self.create_face_signature(frame, faces[0])
                    captured = True
                    
                    if for_enrollment:
                        self.update_status("Face captured successfully! Saving enrollment...", 'green')
                    else:
                        self.update_status("Face captured! Comparing with enrolled face...", 'blue')
                else:
                    self.update_status("No face detected. Please position your face clearly and try again.", 'red')
                    
            elif key == 27:  # Escape key
                self.update_status("Face capture cancelled.", 'orange')
                break
        
        self.stop_camera()
        return face_data
    
    def enroll_face(self):
        """Enroll a new face."""
        if self.face_cascade is None:
            messagebox.showerror("Error", "Face detector not available. Please check OpenCV installation.")
            return
            
        self.update_status("Starting face enrollment...", 'blue')
        
        # Disable buttons during enrollment
        self.enroll_button.config(state='disabled')
        self.auth_button.config(state='disabled')
        
        try:
            face_data = self.capture_and_process_face(for_enrollment=True)
            
            if face_data is not None:
                # Save the enrollment
                if self.save_enrollment(face_data):
                    self.enrolled_face_data = {'face_hash': face_data}
                    self.update_status("Face enrolled successfully! You can now authenticate.", 'green')
                else:
                    self.update_status("Failed to save face enrollment. Please try again.", 'red')
            else:
                self.update_status("Face enrollment failed. Please try again.", 'red')
                
        except Exception as e:
            self.update_status(f"Enrollment error: {str(e)}", 'red')
            
        finally:
            # Re-enable buttons
            self.enroll_button.config(state='normal')
            self.auth_button.config(state='normal')
    
    def authenticate_face(self):
        """Authenticate user's face against enrolled face."""
        if self.enrolled_face_data is None:
            messagebox.showwarning("No Enrollment", "Please enroll your face first before authenticating.")
            return
            
        if self.face_cascade is None:
            messagebox.showerror("Error", "Face detector not available. Please check OpenCV installation.")
            return
            
        self.update_status("Starting face authentication...", 'blue')
        
        # Disable buttons during authentication
        self.enroll_button.config(state='disabled')
        self.auth_button.config(state='disabled')
        
        try:
            face_data = self.capture_and_process_face(for_enrollment=False)
            
            if face_data is not None:
                # Compare with enrolled face (simple hash comparison)
                enrolled_hash = self.enrolled_face_data.get('face_hash', '')
                
                if face_data == enrolled_hash:
                    self.update_status("Authentication successful! Face matches enrolled face.", 'green')
                    self.update_auth_status(True)
                else:
                    self.update_status("Authentication failed. Face does not match enrolled face.", 'red')
                    self.update_auth_status(False)
            else:
                self.update_status("Authentication failed. Please try again.", 'red')
                self.update_auth_status(False)
                
        except Exception as e:
            self.update_status(f"Authentication error: {str(e)}", 'red')
            self.update_auth_status(False)
            
        finally:
            # Re-enable buttons
            self.enroll_button.config(state='normal')
            self.auth_button.config(state='normal')
    
    def generate_key_from_face(self):
        """Generate encryption key from face data."""
        if self.enrolled_face_data is None:
            raise Exception("No face enrolled")
            
        # Use face hash as basis for key derivation
        face_hash = self.enrolled_face_data.get('face_hash', '')
        
        # Create a password from face hash
        password = face_hash.encode()
        
        # Use a fixed salt (in production, you might want a more sophisticated approach)
        salt = b'faceauth_salt_123'
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_file(self):
        """Encrypt a selected file."""
        if not self.is_authenticated:
            messagebox.showwarning("Authentication Required", "Please authenticate your face first.")
            return
            
        # File selection dialog
        file_path = filedialog.askopenfilename(
            title="Select File to Encrypt",
            filetypes=[("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            self.update_status("Encrypting file...", 'blue')
            
            # Generate encryption key from face
            key = self.generate_key_from_face()
            fernet = Fernet(key)
            
            # Read file content
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            # Encrypt the file
            encrypted_data = fernet.encrypt(file_data)
            
            # Save encrypted file
            base_name = os.path.basename(file_path)
            encrypted_file_path = os.path.join(self.encrypted_dir, f"{base_name}.encrypted")
            
            with open(encrypted_file_path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted_data)
            
            self.update_status(f"File encrypted successfully! Saved as: {encrypted_file_path}", 'green')
            
            # Ask if user wants to delete original file
            if messagebox.askyesno("Delete Original", "Do you want to delete the original unencrypted file?"):
                os.remove(file_path)
                self.update_status(f"Original file deleted. Encrypted file saved as: {encrypted_file_path}", 'green')
                
        except Exception as e:
            self.update_status(f"Encryption failed: {str(e)}", 'red')
            messagebox.showerror("Encryption Error", f"Failed to encrypt file: {str(e)}")
    
    def decrypt_file(self):
        """Decrypt a selected file."""
        if not self.is_authenticated:
            messagebox.showwarning("Authentication Required", "Please authenticate your face first.")
            return
            
        # File selection dialog for encrypted files
        file_path = filedialog.askopenfilename(
            title="Select File to Decrypt",
            filetypes=[("Encrypted files", "*.encrypted"), ("All files", "*.*")],
            initialdir=self.encrypted_dir
        )
        
        if not file_path:
            return
            
        try:
            self.update_status("Decrypting file...", 'blue')
            
            # Generate decryption key from face
            key = self.generate_key_from_face()
            fernet = Fernet(key)
            
            # Read encrypted file
            with open(file_path, 'rb') as encrypted_file:
                encrypted_data = encrypted_file.read()
            
            # Decrypt the file
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Save decrypted file
            base_name = os.path.basename(file_path)
            if base_name.endswith('.encrypted'):
                original_name = base_name[:-10]  # Remove .encrypted extension
            else:
                original_name = f"{base_name}.decrypted"
            
            save_path = filedialog.asksaveasfilename(
                title="Save Decrypted File As",
                initialfilename=original_name,
                filetypes=[("All files", "*.*")]
            )
            
            if save_path:
                with open(save_path, 'wb') as decrypted_file:
                    decrypted_file.write(decrypted_data)
                
                self.update_status(f"File decrypted successfully! Saved as: {save_path}", 'green')
            else:
                self.update_status("Decryption cancelled by user.", 'orange')
                
        except Exception as e:
            self.update_status(f"Decryption failed: {str(e)}", 'red')
            messagebox.showerror("Decryption Error", f"Failed to decrypt file: {str(e)}")
    
    def clear_enrollment(self):
        """Clear the current face enrollment."""
        if messagebox.askyesno("Clear Enrollment", "Are you sure you want to clear the current face enrollment? This action cannot be undone."):
            try:
                if os.path.exists(self.enrollment_file):
                    os.remove(self.enrollment_file)
                
                self.enrolled_face_data = None
                self.update_auth_status(False)
                self.update_status("Face enrollment cleared. Please enroll your face again.", 'orange')
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear enrollment: {str(e)}")
    
    def show_help(self):
        """Show help dialog."""
        help_text = """
Simple FaceAuth GUI Help

Getting Started:
1. Click "Enroll Face" to register your face with the system
2. Position your face clearly in front of the camera
3. Press SPACE to capture your face, or ESC to cancel
4. Once enrolled, click "Authenticate Face" to verify your identity
5. After successful authentication, you can encrypt and decrypt files

Face Authentication:
- This simplified version uses basic face detection and pattern matching
- Make sure you have good lighting when enrolling and authenticating
- Position your face clearly in the camera view
- Authentication is required before each session

File Operations:
- Only available after successful face authentication
- Encrypted files are saved in the 'data/encrypted' folder
- You can choose to delete the original file after encryption
- Use the same enrolled face to decrypt files

Security Notes:
- This is a simplified demonstration version
- All processing is done locally on your device
- For production use, consider more advanced face recognition methods
- Files are encrypted using your facial pattern as the key basis

Troubleshooting:
- If camera doesn't open, check if other applications are using it
- If face detection fails, ensure good lighting and clear face visibility
- If buttons are disabled, make sure you've completed the previous steps
- For file operations, make sure you have proper file permissions

For more information, see the documentation in the 'docs' folder.
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Simple FaceAuth Help")
        help_window.geometry("600x500")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(help_window, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
    
    def on_closing(self):
        """Handle application closing."""
        if self.camera_active:
            self.stop_camera()
        
        self.root.quit()
        self.root.destroy()


def main():
    """Main function to run the Simple FaceAuth GUI application."""
    # Check dependencies
    try:
        import cv2
        from cryptography.fernet import Fernet
        from PIL import Image, ImageTk
    except ImportError as e:
        print(f"Missing required dependency: {e}")
        print("Please install required packages:")
        print("pip install opencv-python cryptography pillow")
        return
    
    # Create and run the application
    root = tk.Tk()
    app = SimpleFaceAuthGUI(root)
    
    print("Simple FaceAuth GUI started successfully!")
    print("Application features:")
    print("- Basic face detection and enrollment")
    print("- Face-based authentication")
    print("- File encryption and decryption")
    print("- Local processing (no cloud dependencies)")
    print("- Simplified biometric-based encryption")
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Application Error", f"An unexpected error occurred: {str(e)}")
    finally:
        if hasattr(app, 'camera_active') and app.camera_active:
            app.stop_camera()


if __name__ == "__main__":
    main()
