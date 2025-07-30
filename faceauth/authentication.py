"""
Face Authentication Module for FaceAuth
========================================

This module handles real-time face authentication by comparing live webcam
feed against stored face embeddings. It provides fast, secure, and robust
identity verification with comprehensive error handling.

Key Features:
- Real-time face verification via webcam
- Direct embedding-to-embedding comparison for maximum security
- No reference images stored - only encrypted numerical embeddings
- Secure decryption of stored face embeddings
- Visual feedback during authentication process
- Sub-2-second authentication performance
- Comprehensive error handling for edge cases
"""

import cv2
import numpy as np
import time
import os
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import getpass
from deepface import DeepFace
from scipy.spatial.distance import cosine
import hashlib

from .crypto import SecureEmbeddingStorage, CryptoError


class FaceAuthenticationError(Exception):
    """Custom exception for face authentication errors"""
    pass


class FaceAuthenticator:
    """
    Real-time face authentication class that compares live video feed
    against stored encrypted face embeddings using direct embedding comparison.
    """
    
    def __init__(self, model_name: str = "Facenet", data_dir: str = "face_data"):
        """
        Initialize the Face Authenticator.
        
        Args:
            model_name: Deep learning model for face embedding generation
            data_dir: Directory containing encrypted face data
        """
        self.model_name = model_name
        self.data_dir = Path(data_dir)
        self.storage = SecureEmbeddingStorage(str(data_dir))
        
        # Authentication parameters
        self.verification_timeout = 15.0  # Maximum time to attempt verification
        self.similarity_threshold = 0.6  # Cosine similarity threshold (0.6 = 60% similar)
        self.frame_skip = 2  # Process every nth frame for performance
        self.frame_counter = 0
        
        # Visual feedback colors (BGR format)
        self.color_verifying = (0, 255, 255)    # Yellow
        self.color_success = (0, 255, 0)        # Green
        self.color_denied = (0, 0, 255)         # Red
        self.color_info = (255, 255, 255)       # White
        
        # Status tracking
        self.current_status = "INITIALIZING"
        self.verification_result = None
        self.confidence_score = 0.0


    def load_stored_embedding(self, user_id: str, password: str) -> np.ndarray:
        """
        Load and decrypt the stored face embedding for a user.
        
        Args:
            user_id: User identifier
            password: User's password for decryption
            
        Returns:
            Decrypted face embedding as NumPy array
            
        Raises:
            FaceAuthenticationError: If loading fails
        """
        try:
            # Use the secure storage to load embedding
            embedding = self.storage.load_user_embedding(user_id, password)
            return embedding
            
        except CryptoError as e:
            if "No face data found" in str(e):
                raise FaceAuthenticationError(
                    f"No face data found for user '{user_id}'. "
                    "Please enroll first using: python main.py enroll-face"
                )
            elif "Decryption failed" in str(e):
                raise FaceAuthenticationError("Incorrect password or corrupted face data")
            else:
                raise FaceAuthenticationError(f"Decryption error: {str(e)}")
        except Exception as e:
            raise FaceAuthenticationError(f"Failed to load face data: {str(e)}")

    def generate_live_embedding(self, frame: np.ndarray) -> np.ndarray:
        """
        Generate face embedding from a live webcam frame.
        
        Args:
            frame: OpenCV frame containing a face
            
        Returns:
            Face embedding as NumPy array
            
        Raises:
            FaceAuthenticationError: If embedding generation fails
        """
        try:
            # Generate embedding using DeepFace
            embedding = DeepFace.represent(
                img_path=frame,
                model_name=self.model_name,
                enforce_detection=True,
                detector_backend='opencv'
            )
            
            # Extract the embedding vector
            if isinstance(embedding, list) and len(embedding) > 0:
                embedding_vector = np.array(embedding[0]['embedding'])
            else:
                embedding_vector = np.array(embedding['embedding'])
            
            return embedding_vector
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'face could not be detected' in error_msg:
                raise FaceAuthenticationError('NO_FACE_DETECTED')
            elif 'more than one face' in error_msg:
                raise FaceAuthenticationError('MULTIPLE_FACES')
            else:
                raise FaceAuthenticationError(f'EMBEDDING_ERROR: {str(e)}')

    def compare_embeddings(self, embedding1: np.ndarray, embedding2: np.ndarray) -> Dict[str, float]:
        """
        Compare two face embeddings using cosine similarity.
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            
        Returns:
            Dictionary with similarity score and verification result
        """
        try:
            # Normalize embeddings to unit vectors
            embedding1_norm = embedding1 / np.linalg.norm(embedding1)
            embedding2_norm = embedding2 / np.linalg.norm(embedding2)
            
            # Calculate cosine similarity (1 - cosine distance)
            cosine_distance = cosine(embedding1_norm, embedding2_norm)
            similarity = 1 - cosine_distance
            
            # Convert to percentage confidence
            confidence = max(0, min(100, similarity * 100))
            
            # Determine if verified based on threshold
            is_verified = similarity >= self.similarity_threshold
            
            return {
                'verified': is_verified,
                'similarity': similarity,
                'confidence': confidence,
                'distance': cosine_distance,
                'threshold': self.similarity_threshold
            }
            
        except Exception as e:
            raise FaceAuthenticationError(f"Embedding comparison failed: {str(e)}")

    def verify_face_against_stored(self, frame: np.ndarray, stored_embedding: np.ndarray) -> Dict[str, Any]:
        """
        Verify current frame against stored face embedding.
        
        Args:
            frame: Current webcam frame
            stored_embedding: Stored face embedding
            
        Returns:
            Dictionary containing verification result and confidence
        """
        try:
            # Generate live embedding from frame
            live_embedding = self.generate_live_embedding(frame)
            
            # Compare embeddings
            comparison_result = self.compare_embeddings(stored_embedding, live_embedding)
            
            return comparison_result
            
        except FaceAuthenticationError as e:
            # Return error information
            return {'error': str(e)}
        except Exception as e:
            return {'error': f'VERIFICATION_ERROR: {str(e)}'}

    def draw_verification_overlay(self, frame: np.ndarray, faces: list = None) -> np.ndarray:
        """
        Draw verification status overlay on the frame.
        
        Args:
            frame: OpenCV frame to draw on
            faces: List of detected faces (optional)
            
        Returns:
            Frame with overlay
        """
        height, width = frame.shape[:2]
        overlay = frame.copy()
        
        # Draw status text
        status_text = self.current_status
        text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
        text_x = (width - text_size[0]) // 2
        text_y = 50
        
        # Choose color based on status
        if "ACCESS GRANTED" in status_text:
            color = self.color_success
        elif "ACCESS DENIED" in status_text:
            color = self.color_denied
        elif "VERIFYING" in status_text:
            color = self.color_verifying
        else:
            color = self.color_info
        
        # Draw text background
        cv2.rectangle(overlay, (text_x - 10, text_y - 35), 
                     (text_x + text_size[0] + 10, text_y + 10), (0, 0, 0), -1)
        
        # Draw text
        cv2.putText(overlay, status_text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)
        
        # Draw confidence score if available
        if hasattr(self, 'confidence_score') and self.confidence_score > 0:
            conf_text = f"Confidence: {self.confidence_score:.1f}%"
            cv2.putText(overlay, conf_text, (10, height - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.color_info, 2)
        
        # Draw similarity threshold info
        threshold_text = f"Threshold: {self.similarity_threshold:.1f} ({self.similarity_threshold*100:.0f}%)"
        cv2.putText(overlay, threshold_text, (10, height - 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.color_info, 1)
        
        # Draw center crosshair for guidance
        center_x, center_y = width // 2, height // 2
        cv2.line(overlay, (center_x - 20, center_y), (center_x + 20, center_y), 
                self.color_info, 2)
        cv2.line(overlay, (center_x, center_y - 20), (center_x, center_y + 20), 
                self.color_info, 2)
        
        # Draw face rectangles if provided
        if faces:
            for face in faces:
                x, y, w, h = face
                cv2.rectangle(overlay, (x, y), (x + w, y + h), color, 2)
        
        # Add instructions
        instructions = [
            "Look directly at the camera",
            "Ensure good lighting",
            "Press 'q' to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(overlay, instruction, (10, height - 140 + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.color_info, 1)
        
        return overlay


    def detect_faces_opencv(self, frame: np.ndarray) -> list:
        """
        Detect faces in frame using OpenCV for quick pre-filtering.
        
        Args:
            frame: Input frame
            
        Returns:
            List of detected face rectangles
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Load cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            return faces.tolist() if len(faces) > 0 else []
            
        except Exception:
            return []


    def verify_user_face(self, user_id: str = None) -> bool:
        """
        Main face verification function. Opens webcam and performs real-time
        face authentication against stored embedding using direct embedding comparison.
        
        Args:
            user_id: User ID to verify against (will prompt if not provided)
            
        Returns:
            True if authentication successful, False otherwise
        """
        cap = None
        
        try:
            # Get user ID if not provided
            if not user_id:
                user_id = input("Enter user ID to verify: ").strip()
                if not user_id:
                    raise FaceAuthenticationError("User ID is required")
            
            # Get password for decryption
            print(f"🔐 Enter password for user '{user_id}':")
            password = getpass.getpass("Password: ")
            if not password:
                raise FaceAuthenticationError("Password is required")
            
            print("🔍 Loading stored face data...")
            
            # Load stored embedding
            stored_embedding = self.load_stored_embedding(user_id, password)
            print(f"✅ Face data loaded successfully ({len(stored_embedding)} dimensions)")
            
            # Initialize webcam
            print("📹 Starting webcam...")
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                raise FaceAuthenticationError("Cannot access webcam")
            
            # Set camera properties for better performance
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            print("🚀 Starting face verification...")
            print("📋 Instructions:")
            print("  • Look directly at the camera")
            print("  • Ensure good lighting")
            print("  • Keep your face centered")
            print("  • Press 'q' to quit")
            print(f"  • Similarity threshold: {self.similarity_threshold:.1f} ({self.similarity_threshold*100:.0f}%)")
            print()
            
            # Verification loop
            start_time = time.time()
            self.current_status = "VERIFYING..."
            last_verification_time = 0
            verification_interval = 1.0  # Verify every 1 second
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    raise FaceAuthenticationError("Failed to capture frame")
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Check timeout
                elapsed_time = time.time() - start_time
                if elapsed_time > self.verification_timeout:
                    self.current_status = "TIMEOUT"
                    break
                
                # Detect faces for visual feedback
                faces = self.detect_faces_opencv(frame)
                
                # Skip frames for performance
                self.frame_counter += 1
                current_time = time.time()
                
                # Perform verification at intervals
                if (current_time - last_verification_time) >= verification_interval:
                    if len(faces) == 1:
                        # Attempt verification with direct embedding comparison
                        verification_result = self.verify_face_against_stored(
                            frame, stored_embedding
                        )
                        
                        if 'error' not in verification_result:
                            if verification_result['verified']:
                                self.current_status = "ACCESS GRANTED"
                                self.confidence_score = verification_result['confidence']
                                self.verification_result = True
                                
                                # Draw success overlay
                                frame_with_overlay = self.draw_verification_overlay(frame, faces)
                                cv2.imshow('FaceAuth - Verification', frame_with_overlay)
                                cv2.waitKey(2000)  # Show success for 2 seconds
                                
                                return True
                            else:
                                self.current_status = f"ACCESS DENIED (Confidence: {verification_result['confidence']:.1f}%)"
                                self.confidence_score = verification_result['confidence']
                        else:
                            # Handle errors
                            error = verification_result['error']
                            if 'NO_FACE_DETECTED' in error:
                                self.current_status = "NO FACE DETECTED"
                            elif 'MULTIPLE_FACES' in error:
                                self.current_status = "MULTIPLE FACES"
                            else:
                                self.current_status = "VERIFICATION ERROR"
                    
                    elif len(faces) == 0:
                        self.current_status = "NO FACE DETECTED"
                    elif len(faces) > 1:
                        self.current_status = "MULTIPLE FACES - Use one person only"
                    
                    last_verification_time = current_time
                
                # Draw overlay
                frame_with_overlay = self.draw_verification_overlay(frame, faces)
                
                # Add timing information
                remaining_time = max(0, self.verification_timeout - elapsed_time)
                time_text = f"Time remaining: {remaining_time:.1f}s"
                cv2.putText(frame_with_overlay, time_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.color_info, 1)
                
                # Show frame
                cv2.imshow('FaceAuth - Verification', frame_with_overlay)
                
                # Check for quit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
            
            # Return result
            return self.current_status == "ACCESS GRANTED"
                
        except FaceAuthenticationError:
            raise
        except KeyboardInterrupt:
            print("\n❌ Verification cancelled by user")
            return False
        except Exception as e:
            raise FaceAuthenticationError(f"Verification failed: {str(e)}")
        finally:
            # Cleanup - Always release resources
            if cap is not None:
                cap.release()
            cv2.destroyAllWindows()


def verify_user_face(user_id: str = None, model_name: str = "Facenet", 
                    data_dir: str = "face_data") -> bool:
    """
    Convenience function for face verification.
    
    Args:
        user_id: User ID to verify
        model_name: AI model to use for verification
        data_dir: Directory containing face data
        
    Returns:
        True if verification successful, False otherwise
    """
    authenticator = FaceAuthenticator(model_name=model_name, data_dir=data_dir)
    return authenticator.verify_user_face(user_id)


if __name__ == "__main__":
    # Test the authentication module
    try:
        result = verify_user_face()
        if result:
            print("✅ Authentication successful!")
        else:
            print("❌ Authentication failed!")
    except FaceAuthenticationError as e:
        print(f"❌ Authentication error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
