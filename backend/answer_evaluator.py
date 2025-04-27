from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from temps import EvaluationResult

def evaluate_answers(data, api_key):
    questions = data.get("questions", [])
    user_answers = data.get("user_answers", {})
    reference_answers = data.get("reference_answers", [])
    quiz_context = data.get("context", "")
    quiz_language = data.get("quiz_language", "English")

    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, openai_api_key=api_key)

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
        - **Feedback**: <Provide a concise explanation of the correctness of the answer and suggestions for improvement if needed, addressing the user as 'you'.>
        - **IsCorrect**: <true, false, or partially_correct>
        """
    )

    evaluations = {}
    for i in range(len(questions)):
        if i < len(reference_answers):
            try:
                chain = EVALUATION_PROMPT | llm.with_structured_output(EvaluationResult)
                evaluation = chain.invoke({
                    "quiz_context": quiz_context,
                    "question": questions[i],
                    "reference_answer": reference_answers[i],
                    "student_answer": user_answers[str(i)],
                    "quiz_language": quiz_language
                })
                evaluations[str(i)] = {
                    "feedback": evaluation.Feedback,
                    "is_correct": evaluation.IsCorrect
                }
            except Exception as e:
                evaluations[str(i)] = {
                    "feedback": "Error during evaluation. Please try again.",
                    "is_correct": False
                }
        else:
            evaluations[str(i)] = {
                "feedback": "No reference answer available for evaluation.",
                "is_correct": False
            }

    return evaluations