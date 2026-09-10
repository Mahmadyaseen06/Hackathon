"""ML Package for AI Placement Predictor"""
from .model_trainer import predict_student_employability, load_or_train_model
from .pipeline import extract_features_from_student
from .dataset_generator import generate_student_dataset
