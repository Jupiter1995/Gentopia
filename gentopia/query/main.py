import transformers
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
import torch
from huggingface_hub import login
from pinecone.grpc import PineconeGRPC as Pinecone


def main():
    PINECONE_API_KEY = "ba5bd7fb-a491-4530-9eb9-a0c2d2ae831c"
    LLaMA3_API_KEY = (
        "LL-vnxTAeV9a6GHXf3LVnIgh6xYMBtrdEFjIKFsKN3IVkp1zhDkL78nPLgNdQeUGpqn"
    )

    pc = Pinecone(api_key=PINECONE_API_KEY)
    login("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")

    tokenizer = AutoTokenizer.from_pretrained(
        "meta-llama/Meta-Llama-3.1-8B", use_auth_token=True
    )
    model = AutoModel.from_pretrained(
        "meta-llama/Meta-Llama-3.1-8B", torch_dtype=torch.float16, use_auth_token=True
    )

    text = "*movie description*"  # replace with movie description
    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        # vector = outputs.last_hidden_state[:, 0, :].numpy()
        last_hidden_states = outputs.last_hidden_state

    vector = last_hidden_states[0]
    print(vector)

    index = pc.Index("sample-movies")

    print(
        index.query(
            vector=vector[0],
            top_k=5,
            include_values=True,
            include_metadata=True,
        )
    )


if __name__ == "__main__":
    main()
