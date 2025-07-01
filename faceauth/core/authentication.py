"""
Face authentication module for FaceAuth system.
Handles real-time face verification and authentication via webcam.
"""

import cv2
import numpy as np
import time
import threading
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path
import torch
import torch.nn.functional as F
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import warnings

from ..utils.storage import FaceDataStorage
from ..utils.security import SecurityManager


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class FaceAuthenticator:
    """Real-time face authentication using webcam."""
    
    def __init__(self, storage: FaceDataStorage = None, device: str = None, 
                 similarity_threshold: float = 0.6):
        """
        Initialize the authenticator.
        
        Args:
            storage: Face data storage instance
            device: Device to run on ('cpu' or 'cuda')
            similarity_threshold: Minimum cosine similarity for authentication
        """
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        self.device = device
        self.similarity_threshold = similarity_threshold
        self.storage = storage or FaceDataStorage()
        
        # Initialize face detection and embedding models
        self._init_models()
        
        # Performance metrics
        self.authentication_times = []
        self.false_positives = 0
        self.false_negatives = 0
        self.total_attempts = 0
        
    def _init_models(self):
        """Initialize MTCNN and FaceNet models."""
        # Initialize MTCNN for face detection
        self.mtcnn = MTCNN(
            image_size=160,
            margin=0,
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7],  # Strict thresholds for accuracy
            factor=0.709,
            post_process=True,
            device=self.device
        )
        
        # Initialize pre-trained FaceNet model
        self.model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        # Suppress warnings
        warnings.filterwarnings('ignore')
    
    def _capture_frame_from_webcam(self, cap: cv2.VideoCapture) -> Optional[np.ndarray]:
        """Capture a frame from webcam."""
        ret, frame = cap.read()
        if not ret:
            return None
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame_rgb
    
    def _assess_image_quality(self, image: np.ndarray) -> Dict[str, float]:
        """
        Assess image quality for face authentication.
        
        Returns:
            Dictionary with quality metrics
        """
        # Convert to grayscale for quality analysis
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Calculate sharpness using Laplacian variance
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate brightness
        brightness = np.mean(gray)
        
        # Calculate contrast
        contrast = gray.std()
        
        return {
            'sharpness': sharpness,
            'brightness': brightness,
            'contrast': contrast
        }
    
    def _is_good_quality(self, quality_metrics: Dict[str, float]) -> Tuple[bool, str]:
        """
        Check if image quality is sufficient for authentication.
        
        Returns:
            (is_good, reason) tuple
        """
        # Quality thresholds
        min_sharpness = 100.0
        min_brightness = 80
        max_brightness = 200
        min_contrast = 30
        
        if quality_metrics['sharpness'] < min_sharpness:
            return False, "Image too blurry"
        
        if quality_metrics['brightness'] < min_brightness:
            return False, "Image too dark"
        
        if quality_metrics['brightness'] > max_brightness:
            return False, "Image too bright"
        
        if quality_metrics['contrast'] < min_contrast:
            return False, "Poor contrast"
        
        return True, "Good quality"
    
    def _extract_face_and_embedding(self, image: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        Extract face from image and generate embedding.
        
        Returns:
            (embedding, error_message) tuple
        """
        try:
            # Detect face
            face_tensor = self.mtcnn(Image.fromarray(image))
            
            if face_tensor is None:
                return None, "No face detected"
            
            # Generate embedding
            with torch.no_grad():
                face_tensor = face_tensor.unsqueeze(0).to(self.device)
                embedding = self.model(face_tensor)
                embedding = F.normalize(embedding, p=2, dim=1)
                embedding_np = embedding.cpu().numpy().flatten()
            
            return embedding_np, None
            
        except Exception as e:
            return None, f"Error processing face: {str(e)}"
    
    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        return np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
    
    def authenticate_realtime(self, user_id: str, timeout: int = 10, 
                            max_attempts: int = 5) -> Dict[str, Any]:
        """
        Perform real-time face authentication via webcam.
        
        Args:
            user_id: User ID to authenticate
            timeout: Maximum time to attempt authentication (seconds)
            max_attempts: Maximum number of authentication attempts
            
        Returns:
            Authentication result dictionary
        """
        start_time = time.time()
        self.total_attempts += 1
        
        # Load enrolled embedding
        try:
            enrolled_embedding = self.storage.load_user_embedding(user_id)
            if enrolled_embedding is None:
                return {
                    'success': False,
                    'error': f'User {user_id} not enrolled',
                    'error_type': 'user_not_found',
                    'duration': time.time() - start_time
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error loading user data: {str(e)}',
                'error_type': 'storage_error',
                'duration': time.time() - start_time
            }
        
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return {
                'success': False,
                'error': 'Cannot access webcam',
                'error_type': 'webcam_error',
                'duration': time.time() - start_time
            }
        
        try:
            # Set camera properties for better performance
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            attempt = 0
            best_similarity = 0.0
            authentication_attempts = []
            
            print(f"🔍 Authenticating user: {user_id}")
            print("📷 Please look at the camera...")
            print("Press 'q' to quit or wait for automatic authentication")
            
            while attempt < max_attempts and (time.time() - start_time) < timeout:
                # Capture frame
                frame = self._capture_frame_from_webcam(cap)
                if frame is None:
                    continue
                
                # Display frame (convert back to BGR for OpenCV)
                display_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                cv2.putText(display_frame, f"Attempt {attempt + 1}/{max_attempts}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_frame, f"Time: {int(timeout - (time.time() - start_time))}s", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow('FaceAuth - Authentication', display_frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # Assess image quality
                quality_metrics = self._assess_image_quality(frame)
                is_good, quality_reason = self._is_good_quality(quality_metrics)
                
                if not is_good:
                    cv2.putText(display_frame, f"Quality: {quality_reason}", 
                               (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    cv2.imshow('FaceAuth - Authentication', display_frame)
                    continue
                
                # Extract face and embedding
                current_embedding, error = self._extract_face_and_embedding(frame)
                
                if error:
                    cv2.putText(display_frame, f"Error: {error}", 
                               (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    cv2.imshow('FaceAuth - Authentication', display_frame)
                    
                    if "No face detected" in error:
                        continue
                    elif "Multiple faces" in error:
                        attempt += 1
                        authentication_attempts.append({
                            'attempt': attempt,
                            'error': error,
                            'similarity': 0.0,
                            'timestamp': time.time()
                        })
                        continue
                    else:
                        attempt += 1
                        continue
                
                # Calculate similarity
                similarity = self._calculate_similarity(current_embedding, enrolled_embedding)
                best_similarity = max(best_similarity, similarity)
                
                authentication_attempts.append({
                    'attempt': attempt + 1,
                    'similarity': similarity,
                    'quality_metrics': quality_metrics,
                    'timestamp': time.time()
                })
                
                # Display similarity
                cv2.putText(display_frame, f"Similarity: {similarity:.3f}", 
                           (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                cv2.imshow('FaceAuth - Authentication', display_frame)
                
                # Check if authentication successful
                if similarity >= self.similarity_threshold:
                    duration = time.time() - start_time
                    self.authentication_times.append(duration)
                    
                    result = {
                        'success': True,
                        'user_id': user_id,
                        'similarity': similarity,
                        'threshold': self.similarity_threshold,
                        'duration': duration,
                        'attempts': attempt + 1,
                        'best_similarity': best_similarity,
                        'authentication_attempts': authentication_attempts,
                        'quality_metrics': quality_metrics
                    }
                    
                    print(f"✅ Authentication successful!")
                    print(f"   Similarity: {similarity:.3f} (threshold: {self.similarity_threshold})")
                    print(f"   Duration: {duration:.2f}s")
                    
                    return result
                
                attempt += 1
                time.sleep(0.1)  # Brief pause between attempts
            
            # Authentication failed
            duration = time.time() - start_time
            self.false_negatives += 1
            
            if attempt >= max_attempts:
                error_msg = f"Authentication failed after {max_attempts} attempts"
                error_type = "max_attempts_exceeded"
            else:
                error_msg = f"Authentication timeout after {timeout}s"
                error_type = "timeout"
            
            return {
                'success': False,
                'error': error_msg,
                'error_type': error_type,
                'user_id': user_id,
                'best_similarity': best_similarity,
                'threshold': self.similarity_threshold,
                'duration': duration,
                'attempts': attempt,
                'authentication_attempts': authentication_attempts
            }
            
        finally:
            cap.release()
            cv2.destroyAllWindows()
    
    def authenticate(self, user_id: str, timeout: int = 10) -> bool:
        """
        Simple authentication method that returns True/False.
        
        Args:
            user_id: User ID to authenticate
            timeout: Maximum time to attempt authentication
            
        Returns:
            True if authentication successful, False otherwise
        """
        result = self.authenticate_realtime(user_id, timeout)
        return result['success']
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get authentication performance metrics."""
        if not self.authentication_times:
            avg_time = 0
        else:
            avg_time = sum(self.authentication_times) / len(self.authentication_times)
        
        if self.total_attempts == 0:
            false_positive_rate = 0
            false_negative_rate = 0
        else:
            false_positive_rate = self.false_positives / self.total_attempts
            false_negative_rate = self.false_negatives / self.total_attempts
        
        return {
            'average_authentication_time': avg_time,
            'total_attempts': self.total_attempts,
            'successful_attempts': len(self.authentication_times),
            'false_positive_rate': false_positive_rate,
            'false_negative_rate': false_negative_rate,
            'false_positives': self.false_positives,
            'false_negatives': self.false_negatives
        }