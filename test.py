from wcwidth import wcwidth, wcswidth

def center_with_wide_chars(text, width, fillchar=' '):
    text_width = wcswidth(text)
    if text_width >= width:
        return text
    
    total_padding = width - text_width
    left_padding = total_padding // 2
    right_padding = total_padding - left_padding
    
    return f"{fillchar * left_padding}{text}{fillchar * right_padding}"

# Example usage
text = "こんにちは😊"
width = 124
centered_text = center_with_wide_chars(text, width)
print(f"'{centered_text}'")

