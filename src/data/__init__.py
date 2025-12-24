"""Media Recommender System - Data Module"""

# Media database (no dependencies)
from .media_database import (
    MEDIA_DATABASE,
    get_all_media,
    get_media_by_id,
    get_media_by_genre,
    get_recommendations_for_user,
    get_similar_items,
    get_trending,
    get_top_rated
)

# User profiles (no dependencies)
from .user_profiles import (
    UserProfile,
    UserType,
    USER_PROFILES,
    get_user_profile,
    get_personalized_recommendations,
    get_user_profile_summary,
    get_recommendation_explanation
)

# Optional imports that require torch/numpy
try:
    from .dataset import (
        DataConfig,
        DataProcessor,
        InteractionDataset,
        SequenceDataset,
        ContentDataset,
        ContrastiveDataset,
        collate_sequences
    )
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    DataConfig = None
    DataProcessor = None
    InteractionDataset = None
    SequenceDataset = None
    ContentDataset = None
    ContrastiveDataset = None
    collate_sequences = None

try:
    from .preprocessor import (
        PreprocessConfig,
        TextPreprocessor,
        NumericPreprocessor,
        CategoricalPreprocessor,
        InteractionPreprocessor,
        DataPreprocessingPipeline
    )
except ImportError:
    PreprocessConfig = None
    TextPreprocessor = None
    NumericPreprocessor = None
    CategoricalPreprocessor = None
    InteractionPreprocessor = None
    DataPreprocessingPipeline = None

try:
    from .feature_engineering import (
        FeatureConfig,
        UserFeatureExtractor,
        ItemFeatureExtractor,
        FeatureStore,
        FeatureEngineeringPipeline
    )
except ImportError:
    FeatureConfig = None
    UserFeatureExtractor = None
    ItemFeatureExtractor = None
    FeatureStore = None
    FeatureEngineeringPipeline = None

__all__ = [
    # Media Database
    "MEDIA_DATABASE",
    "get_all_media",
    "get_media_by_id",
    "get_media_by_genre",
    "get_recommendations_for_user",
    "get_similar_items",
    "get_trending",
    "get_top_rated",
    # User Profiles
    "UserProfile",
    "UserType",
    "USER_PROFILES",
    "get_user_profile",
    "get_personalized_recommendations",
    "get_user_profile_summary",
    "get_recommendation_explanation",
    # Dataset (optional)
    "DataConfig",
    "DataProcessor",
    "InteractionDataset",
    "SequenceDataset",
    "ContentDataset",
    "ContrastiveDataset",
    "collate_sequences",
    # Preprocessor (optional)
    "PreprocessConfig",
    "TextPreprocessor",
    "NumericPreprocessor",
    "CategoricalPreprocessor",
    "InteractionPreprocessor",
    "DataPreprocessingPipeline",
    # Feature Engineering (optional)
    "FeatureConfig",
    "UserFeatureExtractor",
    "ItemFeatureExtractor",
    "FeatureStore",
    "FeatureEngineeringPipeline"
]
