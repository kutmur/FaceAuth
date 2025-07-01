"""
Face Enrollment Module for FaceAuth
====================================

This module handles the enrollment of new users by capturing their face via webcam,
generating face embeddings using DeepFace, and securely storing the data locally.

Key Features:
- Real-time face detection and feedback
- Robust error handling for edge cases
- Secure local storage of face embeddings
- Privacy-first approach with no cloud dependencies
"""

import cv2
import numpy as np
import os
import time
from typing import Optional, Tuple, Dict, Any
from deepface import DeepFace
from pathlib import Path
import getpass
from .crypto import encrypt_embedding_with_password


class FaceEnrollmentError(Exception):
    """Custom exception for face enrollment errors"""
    pass


class FaceEnroller:
    """
    Face enrollment class that handles webcam capture, face detection,
    and secure storage of face embeddings.
    """
    
    def __init__(self, model_name: str = "Facenet", data_dir: str = "face_data"):
        """
        Initialize the Face Enroller.
        
        Args:
            model_name: Deep learning model for face embedding ("Facenet", "ArcFace", "VGG-Face")
            data_dir: Directory to store encrypted face data
        """
        self.model_name = model_name
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Face detection parameters
        self.min_confidence = 0.7
        self.min_face_size = (100, 100)  # Minimum face dimensions
        self.max_faces_allowed = 1
        
        # Capture parameters
        self.capture_delay = 3  # seconds to wait before capture
        self.frame_skip = 5  # Process every nth frame for performance
        
        print(f"🔥 FaceAuth Enrollment initialized with {model_name} model")
    
    def _initialize_camera(self) -> cv2.VideoCapture:
        """Initialize and configure the camera."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise FaceEnrollmentError("❌ Cannot access webcam. Please check your camera connection.")
        
        # Set camera properties for better quality
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        return cap
    
    def _detect_faces(self, frame: np.ndarray) -> Tuple[bool, str, list]:
        """
        Detect faces in the frame using DeepFace.
        
        Args:
            frame: Input frame from webcam
            
        Returns:
            Tuple of (is_valid, message, face_regions)
        """
        try:
            # Use DeepFace for face detection
            faces = DeepFace.extract_faces(
                img_path=frame,
                target_size=(224, 224),
                detector_backend='opencv',
                enforce_detection=False
            )
            
            if len(faces) == 0:
                return False, "❌ No face detected", []
            elif len(faces) > 1:
                return False, "❌ Multiple faces detected - please ensure only one person is visible", []
            else:
                # Check face quality/size
                face = faces[0]
                if face.shape[0] < self.min_face_size[0] or face.shape[1] < self.min_face_size[1]:
                    return False, "❌ Face too small - please move closer to the camera", []
                
                return True, "✅ Face detected - good quality", faces
                
        except Exception as e:
            return False, f"❌ Face detection error: {str(e)}", []
    
    def _draw_feedback(self, frame: np.ndarray, message: str, is_valid: bool) -> np.ndarray:
        """
        Draw real-time feedback on the frame.
        
        Args:
            frame: Input frame
            message: Feedback message to display
            is_valid: Whether the current detection is valid
            
        Returns:
            Frame with feedback overlay
        """
        # Create a copy to avoid modifying original
        display_frame = frame.copy()
        
        # Draw rectangle for face area guide
        height, width = frame.shape[:2]
        face_area = (
            int(width * 0.25), int(height * 0.2),
            int(width * 0.75), int(height * 0.8)
        )
        
        color = (0, 255, 0) if is_valid else (0, 0, 255)
        cv2.rectangle(display_frame, 
                     (face_area[0], face_area[1]), 
                     (face_area[2], face_area[3]), 
                     color, 2)
        
        # Draw center crosshair
        center_x, center_y = width // 2, height // 2
        cv2.line(display_frame, (center_x - 20, center_y), (center_x + 20, center_y), (255, 255, 255), 2)
        cv2.line(display_frame, (center_x, center_y - 20), (center_x, center_y + 20), (255, 255, 255), 2)
        
        # Draw message
        cv2.putText(display_frame, message, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Draw instructions
        instructions = [
            "Instructions:",
            "- Position your face in the green rectangle",
            "- Look directly at the camera",
            "- Ensure good lighting",
            "- Press SPACE when ready, ESC to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(display_frame, instruction, (10, height - 120 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return display_frame
    
    def _capture_face_image(self) -> np.ndarray:
        """
        Capture a high-quality face image from webcam with real-time feedback.
        
        Returns:
            Captured face image as numpy array
        """
        cap = self._initialize_camera()
        frame_count = 0
        
        print("🎯 Face capture started. Position yourself in front of the camera...")
        print("📸 Press SPACE when you see '✅ Face detected' message")
        print("❌ Press ESC to cancel enrollment")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    raise FaceEnrollmentError("Failed to capture frame from webcam")
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Process every nth frame for performance
                if frame_count % self.frame_skip == 0:
                    is_valid, message, faces = self._detect_faces(frame)
                else:
                    # Use previous results
                    pass
                
                # Draw feedback
                display_frame = self._draw_feedback(frame, message, is_valid)
                
                # Show the frame
                cv2.imshow('FaceAuth - Face Enrollment', display_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == 27:  # ESC key
                    raise FaceEnrollmentError("❌ Enrollment cancelled by user")
                
                elif key == 32:  # SPACE key
                    if is_valid and len(faces) > 0:
                        print("📸 Capturing face in 3 seconds...")
                        
                        # Countdown
                        for i in range(3, 0, -1):
                            ret, frame = cap.read()
                            if ret:
                                frame = cv2.flip(frame, 1)
                                countdown_frame = self._draw_feedback(
                                    frame, f"📸 Capturing in {i}...", True
                                )
                                cv2.imshow('FaceAuth - Face Enrollment', countdown_frame)
                                cv2.waitKey(1000)
                        
                        # Final capture
                        ret, final_frame = cap.read()
                        if ret:
                            final_frame = cv2.flip(final_frame, 1)
                            print("✅ Face captured successfully!")
                            return final_frame
                    else:
                        print("⚠️  Cannot capture - please ensure face is properly detected first")
                
                frame_count += 1
                
        finally:
            cap.release()
            cv2.destroyAllWindows()
    
    def _generate_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Generate face embedding using DeepFace.
        
        Args:
            face_image: Input face image
            
        Returns:
            Face embedding as numpy array
        """
        try:
            print(f"🧠 Generating face embedding using {self.model_name} model...")
            
            # Generate embedding
            embedding = DeepFace.represent(
                img_path=face_image,
                model_name=self.model_name,
                enforce_detection=True,
                detector_backend='opencv'
            )
            
            # Extract the embedding vector
            if isinstance(embedding, list) and len(embedding) > 0:
                embedding_vector = np.array(embedding[0]['embedding'])
            else:
                embedding_vector = np.array(embedding['embedding'])
            
            print(f"✅ Embedding generated successfully (dimension: {len(embedding_vector)})")
            return embedding_vector
            
        except Exception as e:
            raise FaceEnrollmentError(f"Failed to generate face embedding: {str(e)}")
    
    def _save_encrypted_embedding(self, embedding: np.ndarray, user_id: str, password: str) -> str:
        """
        Save the face embedding in encrypted format.
        
        Args:
            embedding: Face embedding array
            user_id: Unique identifier for the user
            password: Password for encryption
            
        Returns:
            Path to the saved encrypted file
        """
        try:
            print("🔐 Encrypting and saving face embedding...")
            
            # Encrypt the embedding with password
            encrypted_data = encrypt_embedding_with_password(embedding, password)
            
            # Save to file
            file_path = self.data_dir / f"{user_id}_face.dat"
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            
            print(f"✅ Face data encrypted and saved to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            raise FaceEnrollmentError(f"Failed to save encrypted embedding: {str(e)}")
    
    def _save_reference_image(self, face_image: np.ndarray, user_id: str) -> str:
        """
        Save a reference image for authentication purposes.
        
        Args:
            face_image: Captured face image
            user_id: User identifier
            
        Returns:
            Path to saved reference image
        """
        try:
            print("📸 Saving reference image for authentication...")
            
            # Save reference image
            reference_path = self.data_dir / f"{user_id}_reference.jpg"
            cv2.imwrite(str(reference_path), face_image)
            
            print(f"✅ Reference image saved to: {reference_path}")
            return str(reference_path)
            
        except Exception as e:
            raise FaceEnrollmentError(f"Failed to save reference image: {str(e)}")
    
    def enroll_new_user(self, user_id: str = None) -> Dict[str, Any]:
        """
        Complete face enrollment process for a new user.
        
        Args:
            user_id: Optional user identifier (will prompt if not provided)
            
        Returns:
            Dictionary with enrollment results
        """
        try:
            # Get user ID if not provided
            if not user_id:
                user_id = input("👤 Enter a unique user ID: ").strip()
                if not user_id:
                    raise FaceEnrollmentError("User ID cannot be empty")
            
            # Check if user already exists
            existing_file = self.data_dir / f"{user_id}_face.dat"
            if existing_file.exists():
                overwrite = input(f"⚠️  User '{user_id}' already exists. Overwrite? (y/N): ").strip().lower()
                if overwrite != 'y':
                    raise FaceEnrollmentError("❌ Enrollment cancelled - user already exists")
            
            # Get password for encryption
            password = getpass.getpass("🔒 Enter a password to encrypt your face data: ")
            if len(password) < 8:
                raise FaceEnrollmentError("❌ Password must be at least 8 characters long")
            
            confirm_password = getpass.getpass("🔒 Confirm password: ")
            if password != confirm_password:
                raise FaceEnrollmentError("❌ Passwords do not match")
            
            print(f"\n🚀 Starting face enrollment for user: {user_id}")
            print("=" * 50)
            
            # Step 1: Capture face image
            face_image = self._capture_face_image()
            
            # Step 2: Generate embedding
            embedding = self._generate_embedding(face_image)
            
            # Step 3: Save encrypted embedding
            file_path = self._save_encrypted_embedding(embedding, user_id, password)
            
            # Step 4: Save reference image for authentication
            reference_path = self._save_reference_image(face_image, user_id)
            
            # Success
            result = {
                'success': True,
                'user_id': user_id,
                'file_path': file_path,
                'reference_path': reference_path,
                'embedding_size': len(embedding),
                'model_used': self.model_name,
                'message': f'✅ Face enrollment completed successfully for user: {user_id}'
            }
            
            print("\n" + "=" * 50)
            print("🎉 ENROLLMENT SUCCESSFUL!")
            print(f"👤 User ID: {user_id}")
            print(f"📁 Data saved to: {file_path}")
            print(f"🧠 Model used: {self.model_name}")
            print(f"📊 Embedding dimension: {len(embedding)}")
            print("🔐 Your face data is encrypted and stored locally")
            print("⚠️  Remember your password - it cannot be recovered!")
            
            return result
            
        except KeyboardInterrupt:
            raise FaceEnrollmentError("❌ Enrollment interrupted by user")
        except Exception as e:
            raise FaceEnrollmentError(f"Enrollment failed: {str(e)}")


def enroll_new_user(user_id: str = None, model_name: str = "Facenet") -> Dict[str, Any]:
    """
    Convenience function to enroll a new user.
    
    Args:
        user_id: Optional user identifier
        model_name: Face recognition model to use
        
    Returns:
        Dictionary with enrollment results
    """
    enroller = FaceEnroller(model_name=model_name)
    return enroller.enroll_new_user(user_id)


if __name__ == "__main__":
    # Example usage
    try:
        result = enroll_new_user()
        print(f"\n✅ Enrollment result: {result}")
    except FaceEnrollmentError as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
