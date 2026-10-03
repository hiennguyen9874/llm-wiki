from jev_omni import load_jev_omni

classifier = load_jev_omni()

# Text. For other modalities, set modality="image"/"audio"/"video" and
# media="/path/to/file". Video is sampled to 16 frames; audio is capped at 30 s.
result = classifier.predict(
    state="The meeting starts at 10 AM. It is now 9 AM.",
    question="Has the meeting started?",
    options=["Yes", "No"],
)
print(result)
