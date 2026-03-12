from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

from config import MONGO_URI, MONGO_DB
from logger import get_logger

logger = get_logger(__name__)

logger.info(f"Connecting to MongoDB: {MONGO_URI.split('@')[-1] if '@' in MONGO_URI else MONGO_URI}")

# Configure connection pooling for better performance under load
client = AsyncIOMotorClient(
    MONGO_URI,
    maxPoolSize=50,          # Maximum connections in the pool
    minPoolSize=10,          # Keep 10 connections warm
    maxIdleTimeMS=45000,     # Close idle connections after 45 seconds
    serverSelectionTimeoutMS=5000,  # 5 second timeout for server selection
    socketTimeoutMS=30000,   # 30 second timeout for socket operations
    connectTimeoutMS=10000,  # 10 second timeout for initial connection
)

db = client[MONGO_DB]
logger.info(f"Connected to database: {MONGO_DB}")


async def create_indexes():
    """
    Create database indexes for optimal query performance.
    Should be called during application startup.
    """
    logger.info("Creating database indexes...")
    
    try:
        # User authentication and lookups
        await db.users.create_index("email", unique=True)
        logger.info("✓ Index created: users.email (unique)")
        
        # User-specific queries (most common query pattern)
        await db.user_profiles.create_index("user_id")
        logger.info("✓ Index created: user_profiles.user_id")
        
        # Job applications - frequently sorted by date
        await db.job_applications.create_index([("user_id", 1), ("updated_at", -1)])
        logger.info("✓ Index created: job_applications.user_id + updated_at")
        
        # Career conversations - chat history lookups
        await db.career_conversations.create_index([("user_id", 1), ("updated_at", -1)])
        await db.career_conversations.create_index("conversation_id", unique=True)
        logger.info("✓ Index created: career_conversations.user_id + updated_at")
        logger.info("✓ Index created: career_conversations.conversation_id (unique)")
        
        # Learning roadmaps - user's saved roadmaps
        await db.user_roadmaps.create_index([("user_id", 1), ("created_at", -1)])
        logger.info("✓ Index created: user_roadmaps.user_id + created_at")
        
        # Flashcards - user's flashcard sets
        await db.flashcards.create_index([("user_id", 1), ("created_at", -1)])
        logger.info("✓ Index created: flashcards.user_id + created_at")
        
        # Presentations - user's generated presentations
        await db.presentations.create_index([("user_id", 1), ("created_at", -1)])
        logger.info("✓ Index created: presentations.user_id + created_at")
        
        # Job tracker - scraped jobs with match scores
        await db.jobs.create_index([("user_id", 1), ("scraped_at", -1)])
        await db.jobs.create_index([("user_id", 1), ("match_score", -1)])
        logger.info("✓ Index created: jobs.user_id + scraped_at")
        logger.info("✓ Index created: jobs.user_id + match_score")
        
        # Cache lookups - frequently accessed by topic
        await db.roadmap_cache.create_index("topic")
        await db.learning_resources.create_index("topic")
        logger.info("✓ Index created: roadmap_cache.topic")
        logger.info("✓ Index created: learning_resources.topic")
        
        # Company applications (cold mail feature)
        await db.company_applications.create_index([("user_id", 1), ("created_at", -1)])
        await db.companies.create_index("company_type")
        logger.info("✓ Index created: company_applications.user_id + created_at")
        logger.info("✓ Index created: companies.company_type")
        
        # Interview sessions
        await db.interviews.create_index([("user_id", 1), ("created_at", -1)])
        logger.info("✓ Index created: interviews.user_id + created_at")
        
        # Explanations feature
        await db.explanations.create_index([("user_id", 1), ("created_at", -1)])
        logger.info("✓ Index created: explanations.user_id + created_at")
        
        logger.info("✅ All database indexes created successfully")
        
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {e}")
        # Don't raise - allow app to continue even if indexes fail


async def get_next_sequence(name: str) -> int:
    doc = await db["counters"].find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
        projection={"seq": 1, "_id": 0},
    )
    logger.debug(f"Generated next sequence for '{name}': {doc['seq']}")
    return doc["seq"]
