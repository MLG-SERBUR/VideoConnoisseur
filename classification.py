def classify_clip(audio_score, visual_score):
    """Combine audio and visual scores to classify the clip"""
    total_score = audio_score + visual_score
    
    # Apply additional classification logic if needed
    if total_score >= 0:
        return total_score, "Keep (positive score)"
    else:
        return total_score, "Junk (negative score)"

if __name__ == "__main__":
    # Test the classification
    audio_score = 40
    visual_score = 50
    total_score, reason = classify_clip(audio_score, visual_score)
    print(f"Total Score: {total_score}")
    print(f"Reason: {reason}")