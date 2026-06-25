import ollama

response = ollama.embed(
    model='embeddinggemma',
    input='The sky is blue because of Rayleigh scattering',
)
print(response.embeddings)
print(len(response.embeddings[0]))