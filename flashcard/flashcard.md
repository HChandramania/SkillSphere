# Flashcards Feature

## Overview

The Flashcards feature in Saarthi automatically generates study flashcards from various content sources using AI-powered content analysis. It allows users to create concise, focused flashcards in a question-answer format optimized for efficient learning and retention.

## Features

- **Multiple Input Sources**
  - Plain text input
  - URL content extraction
  - PDF document processing

- **Customizable Generation**
  - Adjustable number of flashcards (5-50)
  - Configurable word limits per card side (20-50 words)
  - Maintains clarity and conciseness

- **AI-Powered Content Analysis**
  - Uses Google's Gemini AI to extract key concepts
  - Generates well-balanced question-answer pairs
  - Tracks difficulty levels for each flashcard

- **Persistent Storage**
  - Save flashcard sets to MongoDB
  - View generation history
  - Retrieve past flashcard sets for review

## How It Works

### 1. Content Input
Users can provide content through three methods:
- **Text**: Paste content directly (100+ characters required)
- **URL**: System extracts text from web pages
- **PDF**: Upload PDF files for text extraction

### 2. Flashcard Generation
The system processes the input content to:
- Extract key concepts and important information
- Generate focused question-answer pairs
- Apply strict word limits to ensure conciseness
- Validate each card meets content requirements

### 3. Preview & Customization
Users can:
- Review generated flashcards before saving
- Adjust card count and word limits if needed
- Study flashcards interactively
- Toggle between front and back of cards

### 4. Storage & Retrieval
- Flashcard sets are saved with metadata
- Each set includes original content source
- Full study history is maintained
- Sets can be retrieved and reviewed anytime

## API Endpoints

### Generate Flashcards
**POST** `/api/flashcards/generate`

Generate flashcards from text, URL, or PDF.

**Request (multipart/form-data):**
```
- text: string (optional) - Plain text content
- url: string (optional) - URL to extract content from
- pdf: file (optional) - PDF file upload
- num_cards: integer (default: 10) - Number of flashcards to generate (5-50)
- words_per_card: integer (default: 35) - Max words per card side (20-50)
```

**Response:**
```json
{
  "flashcards": [
    {
      "id": 1,
      "front": "What is photosynthesis?",
      "back": "The process by which plants use sunlight to make glucose...",
      "difficulty": "intermediate"
    }
  ],
  "original_content": "Full extracted content...",
  "content_source": "text|url|pdf"
}
```

**Error Responses:**
- `400`: No input provided, invalid num_cards or words_per_card values
- `500`: Content extraction or generation failure

---

### Save Flashcard Set
**POST** `/api/flashcards/save`

Persist a generated flashcard set to the database.

**Request (JSON):**
```json
{
  "flashcards": [
    {
      "front": "Question",
      "back": "Answer",
      "difficulty": "easy|intermediate|hard"
    }
  ],
  "original_content": "Original extracted content",
  "content_source": "text|url|pdf",
  "num_cards": 10,
  "words_per_card": 35
}
```

**Response:**
```json
{
  "success": true,
  "flashcard_id": 1,
  "message": "Flashcard set saved successfully"
}
```

**Error Response:**
- `500`: Database save failure

---

### Get Flashcard History
**GET** `/api/flashcards/history`

Retrieve all flashcard sets for the current user.

**Response:**
```json
{
  "success": true,
  "flashcard_sets": [
    {
      "flashcard_id": 1,
      "user_id": "user123",
      "total_cards": 10,
      "words_per_card": 35,
      "content_source": "text",
      "created_at": "2024-02-27T10:30:00",
      "updated_at": "2024-02-27T10:30:00"
    }
  ],
  "count": 1
}
```

---

### Get Specific Flashcard Set
**GET** `/api/flashcards/history/{flashcard_id}`

Retrieve a complete flashcard set by ID.

**Response:**
```json
{
  "success": true,
  "flashcard_set": {
    "flashcard_id": 1,
    "user_id": "user123",
    "flashcards": [...],
    "total_cards": 10,
    "original_content": "...",
    "content_source": "text",
    "created_at": "2024-02-27T10:30:00"
  }
}
```

**Error Responses:**
- `404`: Flashcard set not found

## Data Models

### Flashcard Schema (Frontend)
```python
class Flashcard(BaseModel):
    id: int                  # Card identifier
    front: str              # Question/prompt (max word limit)
    back: str               # Answer/response (max word limit)
    difficulty: str         # easy | intermediate | hard
```

### FlashcardGenerateRequest
```python
class FlashcardGenerateRequest(BaseModel):
    text: Optional[str] = None           # Plain text input
    url: Optional[str] = None            # URL input
    num_cards: int = 10                  # Cards to generate (5-50)
    words_per_card: int = 35             # Max words per side (20-50)
```

### SaveFlashcardSetRequest
```python
class SaveFlashcardSetRequest(BaseModel):
    flashcards: List[Dict[str, Any]]     # Generated cards
    original_content: str                # Source content
    content_source: str                  # text | url | pdf
    num_cards: int                       # Cards requested
    words_per_card: int                  # Word limit applied
```

### MongoDB Document Structure
```javascript
{
  flashcard_id: 1,                      // Unique ID
  user_id: "user123",                   // Owner
  user_email: "user@example.com",       // Email
  flashcards: [...],                    // All cards
  total_cards: 10,                      // Count of cards
  num_cards_requested: 10,              // Original request
  words_per_card: 35,                   // Word limit
  original_content: "...",              // First 5000 chars
  content_source: "text|url|pdf",       // Source type
  created_at: ISODate("2024-02-27"),    // Creation time
  updated_at: ISODate("2024-02-27")     // Last update
}
```

## Content Validation

### Input Requirements
- **Minimum content length**: 100 characters
- **Maximum content length**: 15,000 characters (auto-truncated)
- **Number of cards**: 5-50
- **Words per card**: 20-50 per side

### Word Counting
- Words are counted by splitting on whitespace
- Each card's front and back are validated independently
- Violations return specific error messages

## Integration Points

### Core Dependencies
- **Gemini AI Client** (`core/gemini_client.py`): AI-powered content generation
- **PDF Extractor** (`core/pdf_extractor.py`): PDF text extraction
- **URL Extractor** (`core/url_extractor.py`): Web content extraction
- **Validators** (`core/validators.py`): Content validation
- **Prompts** (`core/prompts.py`): Flashcard generation prompts

### Authentication
- Routes require user authentication via `Depends(get_current_user)`
- User identity ensures data isolation and privacy
- All operations logged with user context

### Database
- Uses MongoDB for persistent storage
- Stores in `db["flashcards"]` collection
- Implements sequence counter for unique flashcard IDs

## Logging

The feature includes comprehensive logging at multiple levels:

```
[FLASHCARD] - General information
[FLASHCARD ERROR] - Generation errors
[FLASHCARD ROUTE] - API request handling
[FLASHCARD ROUTE ERROR] - API errors
[SAVE FLASHCARD ROUTE] - Database save operations
[FLASHCARD HISTORY ROUTE] - History retrieval
[FLASHCARD BY ID ROUTE] - Individual set retrieval
```

Each operation logs:
- Input parameters
- Processing steps
- Content lengths
- Success/failure status
- Error details with stack traces

## Frontend Integration

The frontend component (`frontend/app/dashboard/flashcards/page.tsx`) provides:

1. **Input Selection**: Text, URL, or PDF upload
2. **Settings Configuration**: Adjust card count and word limits
3. **Preview Mode**: Review before saving
4. **Study Mode**: Interactive card flipping
5. **History Access**: View and retrieve past sets

## Error Handling

| Error | Status | Details |
|-------|--------|---------|
| No input provided | 400 | Provide text, PDF, or URL |
| Invalid num_cards | 400 | Must be 5-50 |
| Invalid words_per_card | 400 | Must be 20-50 |
| Content too short | 400 | Minimum 100 characters |
| Generation failure | 500 | AI service error |
| Save failure | 500 | Database error |
| Set not found | 404 | Invalid flashcard_id or unauthorized access |

## Performance Considerations

- **Content truncation**: Content >15,000 chars is truncated automatically
- **Storage optimization**: Original content limited to 5,000 chars in DB
- **Lazy loading**: History queries exclude full content by default
- **Batch operations**: Efficient MongoDB queries with field filtering

## Future Enhancements

- Image support in flashcards
- Spaced repetition algorithm
- Performance statistics
- Collaborative flashcard decks
- Export to Anki format
- Custom card templates
- Multi-language support
