from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from temps import create_the_quiz_prompt_template, create_quiz_chain, QuizMultipleChoice, QuizTrueFalse, QuizOpenEnded, EvaluationResult
import PyPDF2
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    try:
        # Extract form data
        api_key = os.getenv("OPENAI_API_KEY")
        context = request.form.get("context", "")
        quiz_type = request.form.get("quiz_type")
        num_questions = int(request.form.get("num_questions"))
        quiz_language = request.form.get("quiz_language", "English")

        #print("Received request - api_key:", api_key, "context:", context, "quiz_type:", quiz_type, "num_questions:", num_questions)

        # Check for file
        file_content = ""
        if "file" in request.files:
            file = request.files["file"]
            print("Received file:", file.filename)

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

            #print("Extracted file content:", file_content)

        if not api_key:
            return jsonify({"error": "API key is missing"}), 400

        os.environ["OPENAI_API_KEY"] = api_key
        prompt_template = create_the_quiz_prompt_template()
        llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

        if quiz_type == "multiple-choice":
            schema = QuizMultipleChoice
        elif quiz_type == "true-false":
            schema = QuizTrueFalse
        else:  # open-ended
            schema = QuizOpenEnded

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
                print("Number of chunks:", len(chunks))

                # Step 3: Embed the chunks and store them in a vector store
                embeddings = OpenAIEmbeddings()
                vector_store = FAISS.from_documents(chunks, embeddings)

                # Step 4: Use the context as a query to retrieve relevant chunks
                retriever = vector_store.as_retriever(search_kwargs={"k": 3})
                query = context if context else "Generate a quiz on this topic"
                relevant_chunks = retriever.invoke(query)
                #print("Retrieved chunks:", [chunk.page_content for chunk in relevant_chunks])

                # Step 5: Combine the retrieved chunks into a single context
                retrieved_content = "\n".join([chunk.page_content for chunk in relevant_chunks])
                combined_context += "\n\nRetrieved Content:\n" + retrieved_content

            except Exception as e:
                print("Error in RAG processing:", str(e))
                combined_context = context

        #print("Combined context:", combined_context)

        quiz_response = chain.invoke({
            "quiz_type": quiz_type,
            "num_quest": num_questions,
            "quiz_context": combined_context,
            "quiz_language": quiz_language
        })

        #print("Quiz response:", quiz_response)

        response_data = {
            "questions": quiz_response.questions if quiz_response.questions else [],
        }

        if quiz_type == "multiple-choice":
            response_data["alternatives"] = quiz_response.alternatives if hasattr(quiz_response, "alternatives") else []
            response_data["answers"] = quiz_response.answers if quiz_response.answers else []
        elif quiz_type == "true-false":
            response_data["answers"] = quiz_response.answers if quiz_response.answers else []
        else:  # open-ended
            response_data["reference_answers"] = quiz_response.reference_answers if hasattr(quiz_response, "reference_answers") else []

        #print("Response data:", response_data)
        return jsonify(response_data)

    except Exception as e:
        print("Error in generate_quiz:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/evaluate-answers', methods=['POST'])
def evaluate_answers():
    try:
        data = request.get_json()
        questions = data.get("questions", [])
        user_answers = data.get("user_answers", {})
        reference_answers = data.get("reference_answers", [])
        quiz_context = data.get("context", "")
        quiz_language = data.get("quiz_language", "English")

        if not questions:
            return jsonify({"error": "No questions provided"}), 400
        if not user_answers:
            return jsonify({"error": "No user answers provided"}), 400

        # Ellenőrizd, hogy minden kérdéshez van-e válasz
        for i in range(len(questions)):
            if str(i) not in user_answers or not user_answers[str(i)].strip():
                return jsonify({"error": f"Answer missing for question {i+1}"}), 400

        # Inicializáld a GPT modellt
        llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

        # Új prompt sablon az open-ended válaszok kiértékeléséhez
        EVALUATION_PROMPT = ChatPromptTemplate.from_template(
            """You are an expert evaluator. Your task is to evaluate a student's open-ended quiz answer based on the provided context, question, reference answer, and the student's answer. Provide feedback on whether the student's answer is correct, partially correct, or incorrect, and explain why. Keep the feedback concise, clear, and educational, suitable for an intermediate-level student. Return the evaluation in the following language: {quiz_language}.

            ### Context:
            {quiz_context}

            ### Question:
            {question}

            ### Reference Answer:
            {reference_answer}

            ### Student's Answer:
            {student_answer}

            ### Output Format:
            - **Feedback**: <Provide a concise explanation of the correctness of the answer and suggestions for improvement if needed.>
            - **IsCorrect**: <true, false, or partially_correct>
            """
        )       

        evaluations = {}
        for i in range(len(questions)):
            # Open-ended kérdések kiértékelése
            if reference_answers and i < len(reference_answers):
                try:
                    # Hívd meg a GPT-t az értékeléshez
                    chain = EVALUATION_PROMPT | llm.with_structured_output(EvaluationResult)
                    evaluation = chain.invoke({
                        "quiz_context": quiz_context,
                        "question": questions[i],
                        "reference_answer": reference_answers[i],
                        "student_answer": user_answers[str(i)],
                        "quiz_language": quiz_language
                    })

                    # Az evaluation egy StructuredOutput, feltételezzük, hogy dictionary-t ad vissza
                    evaluations[str(i)] = {
                        "feedback": evaluation.Feedback,
                        "is_correct": evaluation.IsCorrect
                    }
                except Exception as e:
                    print(f"Error evaluating question {i}: {str(e)}")
                    evaluations[str(i)] = {
                        "feedback": "Error during evaluation. Please try again.",
                        "is_correct": False
                    }
            else:
                # Ha nincs referencia válasz, adj vissza alapértelmezett hibát
                evaluations[str(i)] = {
                    "feedback": "No reference answer available for evaluation.",
                    "is_correct": False
                }

        return jsonify({"evaluations": evaluations})

    except Exception as e:
        print("Error in evaluate_answers:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)