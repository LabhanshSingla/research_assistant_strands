# config.py
from strands.models import BedrockModel

BEDROCK_REGION = "ap-southeast-2"  # or your preferred region

MODEL = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name=BEDROCK_REGION,
    temperature=0.2,
    max_tokens=2000,
)
