from config import Config

def mock_image_generation(prompt: str) -> str:
    return f"https://placehold.co/600x400?text={prompt[:30]}"

def mock_text_generation(prompt: str) -> str:
    return f"Mock response for: {prompt[:50]}"

def should_mock() -> bool:
    return Config.TEST_MODE