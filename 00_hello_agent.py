from strands import Agent

agent = Agent(model="anthropic.claude-3-5-sonnet-20241022-v2:0")  # defaults to Bedrock (Claude Sonnet 4, us-west-2) unless you override
print(agent("One sentence: what is an agentic AI system?"))
