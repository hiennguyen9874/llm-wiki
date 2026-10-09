# ViSoNorm: Vietnamese Text Normalization Model

ViSoNorm is a state-of-the-art Vietnamese text normalization model that converts informal, non-standard Vietnamese text into standard Vietnamese. The model uses a multi-task learning approach with NSW (Non-Standard Word) detection, mask prediction, and lexical normalization heads.

## Model Architecture

- **Base Model**: ViSoBERT (Vietnamese Social Media BERT)
- **Multi-task Heads**:
  - NSW Detection: Identifies tokens that need normalization
  - Mask Prediction: Determines how many masks to add for multi-token expansions
  - Lexical Normalization: Predicts normalized tokens

## Features

- **Self-contained inference**: Built-in `normalize_text` method
- **NSW detection**: Built-in `detect_nsw` method for detailed analysis
- **HuggingFace compatible**: Works seamlessly with `AutoModelForMaskedLM`
- **Production ready**: No hardcoded patterns, works for any Vietnamese text
- **Multi-token expansion**: Handles cases like "sv" → "sinh viên", "ctrai" → "con trai"
- **Confidence scoring**: Provides confidence scores for NSW detection and normalization

## Installation

```bash
pip install transformers torch
```

## Usage

### Basic Usage

```python
from transformers import AutoTokenizer, AutoModelForMaskedLM

# Load model and tokenizer
model_repo = "hadung1802/visobert-normalizer"
tokenizer = AutoTokenizer.from_pretrained(model_repo)
model = AutoModelForMaskedLM.from_pretrained(model_repo, trust_remote_code=True)

# Normalize text
text = "sv dh gia dinh chua cho di lam :))"
normalized_text, source_tokens, predicted_tokens = model.normalize_text(
    tokenizer, text, device='cpu'
)

print(f"Original: {text}")
print(f"Normalized: {normalized_text}")
```

### NSW Detection

```python
# Detect Non-Standard Words (NSW) in text
text = "nhìn thôi cung thấy đau long quá đi :))"
nsw_results = model.detect_nsw(tokenizer, text, device='cpu')

print(f"Text: {text}")
for result in nsw_results:
    print(f"NSW: '{result['nsw']}' → '{result['prediction']}' (confidence: {result['confidence_score']})")
```

### Batch Processing

```python
texts = [
    "sv dh gia dinh chua cho di lam :))",
    "chúng nó bảo em là ctrai", 
    "t vs b chơi vs nhau đã lâu"
]

for text in texts:
    normalized_text, _, _ = model.normalize_text(tokenizer, text, device='cpu')
    print(f"{text} → {normalized_text}")
```

### Expected Output

#### Text Normalization
```
sv dh gia dinh chua cho di lam :)) → sinh viên đại học gia đình chưa cho đi làm :))
chúng nó bảo em là ctrai → chúng nó bảo em là con trai
t vs b chơi vs nhau đã lâu → tôi với bạn chơi với nhau đã lâu
```

#### NSW Detection
```python
# Input: "nhìn thôi cung thấy đau long quá đi :))"
[
  {
    "index": 3,
    "start_index": 10,
    "end_index": 14,
    "nsw": "cung",
    "prediction": "cũng",
    "confidence_score": 0.9415
  },
  {
    "index": 6,
    "start_index": 24,
    "end_index": 28,
    "nsw": "long",
    "prediction": "lòng",
    "confidence_score": 0.7056
  }
]
```

### NSW Detection Output Format

The `detect_nsw` method returns a list of dictionaries with the following structure:

- **`index`**: Position of the token in the sequence
- **`start_index`**: Start character position in the original text
- **`end_index`**: End character position in the original text  
- **`nsw`**: The original non-standard word (detokenized)
- **`prediction`**: The predicted normalized word (detokenized)
- **`confidence_score`**: Combined confidence score (0.0 to 1.0)