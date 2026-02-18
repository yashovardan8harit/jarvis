from brain.llm import LocalLLM

llm = LocalLLM()

response = llm.generate("Say hello in a cool AI assistant style.")

print("\nJarvis Response:")
print(response)
