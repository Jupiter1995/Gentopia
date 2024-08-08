from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

"""

"""


def main():
    PINECONE_API_KEY = "ba5bd7fb-a491-4530-9eb9-a0c2d2ae831c"
    LLaMA3_API_KEY = (
        "LL-vnxTAeV9a6GHXf3LVnIgh6xYMBtrdEFjIKFsKN3IVkp1zhDkL78nPLgNdQeUGpqn"
    )

    # embedding sample text query -> vector?


    index = pc.Index("sample-movies")

    print(
        index.query(
            vector=query_vector,
            top_k=5,
            include_values=True,
            include_metadata=True,
            # filter={"genre": {"$eq": "action"}},
        )
    )


def embedding():
    # model_id = "meta-llama/Meta-Llama-3-8B"

    # pipeline = transformers.pipeline(
    #     "text-generation",
    #     model=model_id,
    #     model_kwargs={"torch_dtype": torch.bfloat16},
    #     device_map="auto",
    # )
    # pipeline("Hey how are you doing today?")
    print()


if __name__ == "__main__":
    embedding()
