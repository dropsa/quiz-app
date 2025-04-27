from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from temps import create_the_quiz_prompt_template, create_quiz_chain, QuizMultipleChoice, QuizTrueFalse, QuizOpenEnded

def generate_quiz(context, file_content, quiz_type, num_questions, quiz_language, api_key):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, openai_api_key=api_key)

    if quiz_type == "multiple-choice":
        schema = QuizMultipleChoice
    elif quiz_type == "true-false":
        schema = QuizTrueFalse
    else:
        schema = QuizOpenEnded

    prompt_template = create_the_quiz_prompt_template()
    chain = create_quiz_chain(prompt_template, llm, schema)

    if file_content:
        try:
            doc = Document(page_content=file_content)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=500)
            chunks = text_splitter.split_documents([doc])
            embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            vector_store = FAISS.from_documents(chunks, embeddings)
            retriever = vector_store.as_retriever(search_kwargs={"k": 3})
            query = context if context else "Generate a quiz on this topic"
            relevant_chunks = retriever.invoke(query)
            retrieved_content = "\n".join([chunk.page_content for chunk in relevant_chunks])
            combined_context = context + "\n\nRetrieved Content:\n" + retrieved_content
        except Exception as e:
            combined_context = context + "\n\n" + file_content
    else:
        combined_context = context

    quiz_response = chain.invoke({
        "quiz_type": quiz_type,
        "num_quest": num_questions,
        "quiz_context": combined_context,
        "quiz_language": quiz_language
    })

    response_data = {
        "questions": quiz_response.questions if quiz_response.questions else [],
    }
    if quiz_type == "multiple-choice":
        response_data["alternatives"] = quiz_response.alternatives if hasattr(quiz_response, "alternatives") else []
        response_data["answers"] = quiz_response.answers if quiz_response.answers else []
    elif quiz_type == "true-false":
        response_data["answers"] = quiz_response.answers if quiz_response.answers else []
    else:
        response_data["reference_answers"] = quiz_response.reference_answers if hasattr(quiz_response, "reference_answers") else []

    return response_data