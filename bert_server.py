from transformers import pipeline
import argparse

qa_pipeline = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")

def answer_question(question, context):
  result = qa_pipeline(question=question, context=context)
  return result['answer']

if __name__ == "__main__":
  # Set up argument parsing
    parser = argparse.ArgumentParser(description="Answer a question using BERT.")
    parser.add_argument("--question", type=str, required=True, help="The question to answer.")
    parser.add_argument("--context", type=str, required=True, help="The context to use for answering the question.")
    args = parser.parse_args()

    # Get question and context from command-line arguments
    question = args.question
    context = args.context

    # Call the function and print the result
    answer = answer_question(question, context)
    print(f"Question: {question}")
    print(f"Answer: {answer}")