from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from temps import create_the_quiz_prompt_template, create_quiz_chain, split_questions_answers, QuizMultipleChoice, QuizTrueFalse
import PyPDF2
#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

app = Flask(__name__)
app.config.from_object(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    try:
        # Extract form data
        api_key = request.form.get("api_key")
        context = request.form.get("context", "")
        quiz_type = request.form.get("quiz_type")
        num_questions = int(request.form.get("num_questions"))
        quiz_language = request.form.get("quiz_language", "English")

        #print("Received request - api_key:", api_key, "context:", context, "quiz_type:", quiz_type, "num_questions:", num_questions)  # Debug log

        # Check for file
        file_content = ""
        if "file" in request.files:
            file = request.files["file"]
            print("Received file:", file.filename)  # Debug log

            if file.filename.endswith(".pdf"):
                # Extract text from PDF
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                file_content = text.strip()
            else:
                # Assume it's a text file
                file_content = file.read().decode("utf-8").strip()

            #print("Extracted file content:", file_content)  # Debug log

        if not api_key:
            return jsonify({"error": "API key is missing"}), 400

        os.environ["OPENAI_API_KEY"] = api_key
        prompt_template = create_the_quiz_prompt_template()
        llm = ChatOpenAI(model="gpt-4o",temperature=0.0)

        if quiz_type == "multiple-choice":
            schema = QuizMultipleChoice
        else:
            schema = QuizTrueFalse

        chain = create_quiz_chain(prompt_template, llm, schema)

        # Combine context and file content using RAG if file_content is provided
        combined_context = context

        if file_content:
            try:
                # Step 1: Load the file content as a LangChain Document
                doc = Document(page_content=file_content)

                # Step 2: Split the document into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=500
                )
                chunks = text_splitter.split_documents([doc])
                print("Number of chunks:", len(chunks))  # Debug log

                # Step 3: Embed the chunks and store them in a vector store
                embeddings = OpenAIEmbeddings()
                vector_store = FAISS.from_documents(chunks, embeddings)

                # Step 4: Use the context as a query to retrieve relevant chunks
                retriever = vector_store.as_retriever(search_kwargs={"k": 3})  # Retrieve top 3 relevant chunks
                query = context if context else "Generate a quiz on this topic"
                relevant_chunks = retriever.invoke(query)
                #print("Retrieved chunks:", [chunk.page_content for chunk in relevant_chunks])  # Debug log

                # Step 5: Combine the retrieved chunks into a single context
                retrieved_content = "\n".join([chunk.page_content for chunk in relevant_chunks])
                combined_context += "\n\nRetrieved Content:\n" + retrieved_content

            except Exception as e:
                print("Error in RAG processing:", str(e))  # Debug log
                # Continue with just the context if RAG fails
                combined_context = context

        #print("Combined context:", combined_context)  # Debug log

        quiz_response = chain.invoke({
            "quiz_type": quiz_type,
            "num_quest": num_questions,
            "quiz_context": combined_context,
            "quiz_language": quiz_language
        })

        print("Quiz response:", quiz_response)  # Debug log

        response_data = {
            "questions": quiz_response.questions if quiz_response.questions else [],
            "answers": quiz_response.answers if quiz_response.answers else [],
        }

        if quiz_type == "multiple-choice":
            response_data["alternatives"] = quiz_response.alternatives if hasattr(quiz_response, "alternatives") else []

        print("Response data:", response_data)  # Debug log
        return jsonify(response_data)

    except Exception as e:
        print("Error in generate_quiz:", str(e))  # Debug log
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)