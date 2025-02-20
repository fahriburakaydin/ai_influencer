from config import Config

def mock_image_generation(prompt: str) -> str:
    return f"https://placehold.co/600x400?text={prompt[:30]}"

def mock_text_generation(prompt: str) -> str:
    return f"Mock response for: {prompt[:50]}"

def should_mock() -> bool:
    return Config.TEST_MODE

def mock_research(niche: str) -> dict:
     return {
            "niche_trends": "\n".join([
                "Mock Trend 1: Virtual Fitness Classes",
                "Mock Trend 2: AI-Powered Workouts"
            ]),
            "content_strategies": "\n".join([
                "Content Strategy 1: Before/After Transformations",
                "Content Strategy 2: 30-Second Exercise Tutorials"
            ])
        }