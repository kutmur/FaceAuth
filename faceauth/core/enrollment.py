"""
Face enrollment module for FaceAuth system.
Handles face capture, embedding generation, and enrollment process.
"""

import cv2
import numpy as np
import time
import threading
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path
import torch
import torch.nn.functional as F
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import warnings

from ..utils.security import SecurityManager
from ..utils.storage import FaceDataStorage
from ..security.secure_storage import SecureStorage
from ..security.audit_logger import SecureAuditLogger
from ..security.privacy_manager import PrivacyManager
from ..security.memory_manager import SecureMemoryManager


class FaceEnrollmentError(Exception):
    """Custom exception for face enrollment errors."""
    pass


class FaceDetector:
    """Handles face detection using MTCNN."""
    
    def __init__(self, device: str = None):
        """
        Initialize face detector.
        
        Args:
            device: Device to run on ('cpu' or 'cuda')
        """
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        self.device = device
        
        # Initialize MTCNN for face detection
        self.mtcnn = MTCNN(
            image_size=160,
            margin=0,
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7],  # More strict thresholds
            factor=0.709,
            post_process=True,
            device=self.device
        )
    
    def detect_faces(self, image: np.ndarray) -> Tuple[List[np.ndarray], List[float]]:
        """
        Detect faces in image.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            Tuple of (face_tensors, confidence_scores)
        """
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Detect faces and get bounding boxes
            boxes, probs = self.mtcnn.detect(pil_image)
            
            if boxes is None:
                return [], []
            
            # Extract face regions
            faces = []
            confidences = []
            
            for box, prob in zip(boxes, probs):
                if prob > 0.9:  # High confidence threshold
                    # Extract and preprocess face
                    face_tensor = self.mtcnn(pil_image, save_path=None)
                    if face_tensor is not None:
                        faces.append(face_tensor)
                        confidences.append(prob)
            
            return faces, confidences
            
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return [], []


class FaceEmbeddingGenerator:
    """Generates face embeddings using FaceNet."""
    
    def __init__(self, device: str = None):
        """
        Initialize embedding generator.
        
        Args:
            device: Device to run on ('cpu' or 'cuda')
        """
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        self.device = device
        
        # Initialize pre-trained FaceNet model
        self.model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        # Suppress warnings
        warnings.filterwarnings('ignore')
    
    def generate_embedding(self, face_tensor: torch.Tensor) -> np.ndarray:
        """
        Generate embedding for a face tensor.
        
        Args:
            face_tensor: Preprocessed face tensor from MTCNN
            
        Returns:
            Face embedding as numpy array
        """
        try:
            with torch.no_grad():
                # Move tensor to device
                face_tensor = face_tensor.unsqueeze(0).to(self.device)
                
                # Generate embedding
                embedding = self.model(face_tensor)
                
                # Normalize embedding
                embedding = F.normalize(embedding, p=2, dim=1)
                
                # Convert to numpy
                embedding_np = embedding.cpu().numpy().flatten()
                
                return embedding_np
                
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None


class EnrollmentSession:
    """Manages a single enrollment session."""
    
    def __init__(self, user_id: str, storage: FaceDataStorage, 
                 detector: FaceDetector, embedder: FaceEmbeddingGenerator):
        """Initialize enrollment session."""
        self.user_id = user_id
        self.storage = storage
        self.detector = detector
        self.embedder = embedder
        
        # Session state
        self.is_active = False
        self.collected_embeddings = []
        self.quality_scores = []
        self.start_time = None
        
        # Configuration
        self.min_samples = 5  # Minimum number of good face samples
        self.max_samples = 10  # Maximum samples to collect
        self.quality_threshold = 0.95  # Minimum quality score
        self.timeout_seconds = 30  # Maximum enrollment time
    
    def start_enrollment(self) -> bool:
        """Start the enrollment process."""
        if self.storage.user_exists(self.user_id):
            raise FaceEnrollmentError(f"User '{self.user_id}' is already enrolled")
        
        self.is_active = True
        self.start_time = time.time()
        self.collected_embeddings = []
        self.quality_scores = []
        
        return True
    
    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Process a camera frame during enrollment.
        
        Args:
            frame: Camera frame as numpy array
            
        Returns:
            Processing result with status and feedback
        """
        if not self.is_active:
            return {'status': 'inactive', 'message': 'Enrollment not active'}
        
        # Check timeout
        if time.time() - self.start_time > self.timeout_seconds:
            self.is_active = False
            return {'status': 'timeout', 'message': 'Enrollment timeout'}
        
        try:
            # Detect faces
            faces, confidences = self.detector.detect_faces(frame)
            
            if len(faces) == 0:
                return {
                    'status': 'no_face',
                    'message': 'No face detected. Please position your face in the camera.',
                    'progress': len(self.collected_embeddings),
                    'target': self.min_samples
                }
            
            if len(faces) > 1:
                return {
                    'status': 'multiple_faces',
                    'message': 'Multiple faces detected. Please ensure only one person is visible.',
                    'progress': len(self.collected_embeddings),
                    'target': self.min_samples
                }
            
            # Process the single detected face
            face_tensor = faces[0]
            confidence = confidences[0]
            
            if confidence < self.quality_threshold:
                return {
                    'status': 'low_quality',
                    'message': f'Face quality too low ({confidence:.2f}). Please improve lighting and positioning.',
                    'progress': len(self.collected_embeddings),
                    'target': self.min_samples
                }
            
            # Generate embedding
            embedding = self.embedder.generate_embedding(face_tensor)
            
            if embedding is None:
                return {
                    'status': 'processing_error',
                    'message': 'Error processing face. Please try again.',
                    'progress': len(self.collected_embeddings),
                    'target': self.min_samples
                }
            
            # Check if this embedding is sufficiently different from existing ones
            if self._is_embedding_unique(embedding):
                self.collected_embeddings.append(embedding)
                self.quality_scores.append(confidence)
                
                # Check if we have enough samples
                if len(self.collected_embeddings) >= self.min_samples:
                    return {
                        'status': 'ready',
                        'message': f'Collected {len(self.collected_embeddings)} samples. Ready to complete enrollment.',
                        'progress': len(self.collected_embeddings),
                        'target': self.min_samples
                    }
                else:
                    return {
                        'status': 'collecting',
                        'message': f'Good sample collected! {self.min_samples - len(self.collected_embeddings)} more needed.',
                        'progress': len(self.collected_embeddings),
                        'target': self.min_samples
                    }
            else:
                return {
                    'status': 'duplicate',
                    'message': 'Similar sample already collected. Please turn your head slightly.',
                    'progress': len(self.collected_embeddings),
                    'target': self.min_samples
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Processing error: {str(e)}',
                'progress': len(self.collected_embeddings),
                'target': self.min_samples
            }
    
    def complete_enrollment(self) -> bool:
        """Complete the enrollment process."""
        if len(self.collected_embeddings) < self.min_samples:
            raise FaceEnrollmentError(f"Not enough samples collected ({len(self.collected_embeddings)}/{self.min_samples})")
        
        try:
            # Create final embedding by averaging all collected embeddings
            final_embedding = np.mean(self.collected_embeddings, axis=0)
            
            # Normalize the final embedding
            final_embedding = final_embedding / np.linalg.norm(final_embedding)
            
            # Prepare metadata
            metadata = {
                'samples_collected': len(self.collected_embeddings),
                'average_quality': float(np.mean(self.quality_scores)),
                'enrollment_duration': time.time() - self.start_time,
                'model_version': 'facenet_vggface2',
                'embedding_dimension': len(final_embedding)
            }
            
            # Save to storage
            success = self.storage.save_user_enrollment(
                self.user_id, 
                final_embedding, 
                metadata
            )
            
            if success:
                self.is_active = False
                return True
            else:
                raise FaceEnrollmentError("Failed to save enrollment data")
                
        except Exception as e:
            raise FaceEnrollmentError(f"Error completing enrollment: {str(e)}")
    
    def cancel_enrollment(self):
        """Cancel the enrollment process."""
        self.is_active = False
        self.collected_embeddings = []
        self.quality_scores = []
    
    def _is_embedding_unique(self, new_embedding: np.ndarray, similarity_threshold: float = 0.95) -> bool:
        """Check if the new embedding is sufficiently different from existing ones."""
        if not self.collected_embeddings:
            return True
        
        for existing_embedding in self.collected_embeddings:
            # Calculate cosine similarity
            similarity = np.dot(new_embedding, existing_embedding) / (
                np.linalg.norm(new_embedding) * np.linalg.norm(existing_embedding)
            )
            
            if similarity > similarity_threshold:
                return False
        
        return True


class FaceEnrollmentManager:
    """Main class for managing face enrollment process."""
    
    def __init__(self, storage_dir: str = None, master_key: str = None):
        """
        Initialize face enrollment manager.
        
        Args:
            storage_dir: Directory for storing face data
            master_key: Master key for encryption
        """
        # Initialize components
        self.security_manager = SecurityManager(master_key)
        self.storage = FaceDataStorage(storage_dir, self.security_manager)
        
        # Initialize AI components
        print("Initializing face recognition models...")
        self.detector = FaceDetector()
        self.embedder = FaceEmbeddingGenerator()
        print("Models loaded successfully!")
        
        # Camera settings
        self.camera_index = 0
        self.camera_width = 640
        self.camera_height = 480
        self.camera_fps = 30
    
    def enroll_user(self, user_id: str, timeout: int = 30, 
                   interactive: bool = True) -> Dict[str, Any]:
        """
        Enroll a user using webcam capture.
        
        Args:
            user_id: Unique identifier for the user
            timeout: Maximum enrollment time in seconds
            interactive: Whether to show interactive feedback
            
        Returns:
            Enrollment result dictionary
        """
        if self.storage.user_exists(user_id):
            return {
                'success': False,
                'error': f"User '{user_id}' is already enrolled",
                'code': 'USER_EXISTS'
            }
        
        try:
            # Initialize camera
            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                return {
                    'success': False,
                    'error': 'Could not open camera',
                    'code': 'CAMERA_ERROR'
                }
            
            # Configure camera
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
            cap.set(cv2.CAP_PROP_FPS, self.camera_fps)
            
            # Create enrollment session
            session = EnrollmentSession(user_id, self.storage, self.detector, self.embedder)
            session.timeout_seconds = timeout
            session.start_enrollment()
            
            if interactive:
                print(f"\n🎥 Starting face enrollment for user: {user_id}")
                print("📋 Instructions:")
                print("   • Look directly at the camera")
                print("   • Ensure good lighting")
                print("   • Keep your face centered in the frame")
                print("   • Turn your head slightly between captures")
                print("   • Press 'q' to quit\n")
            
            enrollment_complete = False
            last_status = None
            
            try:
                while session.is_active and not enrollment_complete:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Process frame
                    result = session.process_frame(frame)
                    
                    # Show feedback
                    if interactive and result['status'] != last_status:
                        status_icon = {
                            'no_face': '❌',
                            'multiple_faces': '👥',
                            'low_quality': '⚠️',
                            'collecting': '✅',
                            'duplicate': '🔄',
                            'ready': '🎉',
                            'error': '💥'
                        }.get(result['status'], '⏳')
                        
                        progress_bar = '█' * result.get('progress', 0) + '░' * (result.get('target', 5) - result.get('progress', 0))
                        print(f"\r{status_icon} {result['message']} [{progress_bar}] {result.get('progress', 0)}/{result.get('target', 5)}", end='', flush=True)
                        last_status = result['status']
                    
                    # Check if ready to complete
                    if result['status'] == 'ready' and len(session.collected_embeddings) >= session.min_samples:
                        if interactive:
                            print(f"\n\n🎯 Enrollment ready! Completing enrollment...")
                        enrollment_complete = True
                        break
                    
                    # Show video feed if interactive
                    if interactive:
                        # Draw face detection feedback on frame
                        display_frame = frame.copy()
                        
                        # Add status text
                        cv2.putText(display_frame, f"Status: {result['status']}", 
                                  (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(display_frame, f"Progress: {result.get('progress', 0)}/{result.get('target', 5)}", 
                                  (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        cv2.imshow('FaceAuth Enrollment', display_frame)
                        
                        # Check for quit
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            if interactive:
                                print(f"\n\n❌ Enrollment cancelled by user")
                            session.cancel_enrollment()
                            break
                
                # Complete enrollment if ready
                if enrollment_complete:
                    session.complete_enrollment()
                    
                    if interactive:
                        print(f"\n✅ Enrollment completed successfully!")
                        print(f"📊 Samples collected: {len(session.collected_embeddings)}")
                        print(f"⭐ Average quality: {np.mean(session.quality_scores):.3f}")
                        print(f"⏱️  Duration: {time.time() - session.start_time:.1f}s")
                    
                    return {
                        'success': True,
                        'user_id': user_id,
                        'samples_collected': len(session.collected_embeddings),
                        'average_quality': float(np.mean(session.quality_scores)),
                        'duration': time.time() - session.start_time
                    }
                else:
                    reason = 'timeout' if time.time() - session.start_time > timeout else 'cancelled'
                    return {
                        'success': False,
                        'error': f'Enrollment {reason}',
                        'code': reason.upper(),
                        'samples_collected': len(session.collected_embeddings)
                    }
                    
            finally:
                cap.release()
                if interactive:
                    cv2.destroyAllWindows()
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Enrollment error: {str(e)}',
                'code': 'UNKNOWN_ERROR'
            }
    
    def verify_enrollment(self, user_id: str) -> bool:
        """Verify that a user is properly enrolled."""
        return self.storage.user_exists(user_id)
    
    def get_enrolled_users(self) -> List[str]:
        """Get list of enrolled users."""
        return self.storage.list_enrolled_users()
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user's enrollment."""
        return self.storage.delete_user_enrollment(user_id)
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        return self.storage.get_storage_stats()