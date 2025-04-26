from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Union

class QuizTrueFalse(BaseModel):
    quiz_text: str = Field(description="The quiz text")
    questions: List[str] = Field(description="The quiz questions")
    answers: List[str] = Field(description="The quiz answers for each question as True or False only.")

class QuizMultipleChoice(BaseModel):
    quiz_text: str = Field(description="The quiz text")
    questions: List[str] = Field(description="The quiz questions")
    alternatives: List[List[str]] = Field(description="The quiz alternatives for each question as a list of lists")
    answers: List[str] = Field(description="The quiz answers")

class QuizOpenEnded(BaseModel):
    quiz_text: str = Field(description="The quiz text")
    questions: List[str] = Field(description="The open-ended quiz questions")
    reference_answers: List[str] = Field(description="Reference answers for evaluation purposes")

def create_the_quiz_prompt_template():
    "Prompt minta készítése"

    template = """You are an expert quiz maker. Let's think step by step and create
    a quiz with {num_quest} {quiz_type} questions about the following concept/content: {quiz_context}
    
    ### Language:
    Generate the quiz in the following language: {quiz_language}. All questions, answers, and alternatives must be in this language.

    The quiz should be designed for students who are learning about this topic.
    The questions should be clear and concise, and the answers should be accurate and relevant.
    True-false questions should be phrased in a way that requires the student to think critically about the topic.
    The distribution of true and false answers should be roughly balanced, but not exactly 50-50 — varying around a 40%–60% to 60%–40 range.
    Design questions suitable for students at an intermediate level of understanding of the topic, ensuring they are neither too basic nor overly complex.
    Verify that all questions and answers are factually accurate and directly relevant to the provided quiz_context. Avoid generating questions based on assumptions or external knowledge not present in the context.

    The format of the quiz could be one of the following:
    -Multiple-choice:
        -Questions:
            <Question1>: <a. Answer 1>, <b. Answer 2>, <c. Answer 3>, <d. Answer 4>
            <Question2>: <a. Answer 1>, <b. Answer 2>, <c. Answer 3>, <d. Answer 4>
        -Answers:
            <Answer1>: <a|b|c|d>
            <Answer2>: <a|b|c|d>
        Example:
        -1. Which of the following best describes the key feature of SIMD (Single Instruction, Multiple Data) architecture?
        
            A) Each processor core executes a different instruction on different data simultaneously.
            B) A single instruction operates on multiple data elements in parallel.
            C) Multiple instructions operate on a single piece of data.
            D) Instructions are executed in sequence with no parallelism.
        - Answers:
            1. b   
    - True-false:
        - Questions:
            <Question1>: <True|False>
            <Question2>: <True|False>
        - Answers:
            <Answer1>: <True|False>
            <Answer2>: <True|False>
        Example:
        - Questions:
            - 1. RISC architectures use a large set of complex instructions to perform tasks in fewer lines of code.
            - 2. In RISC architectures, most instructions are designed to execute in a single clock cycle.
        - Answers:
            - 1. False
            - 2. True
    - Open-ended:
        - Questions:
            <Question1>
        - Reference Answers:
            <Reference Answer1>
        Example:
            - 1. Explain the main difference between RISC and CISC architectures.
        Reference Answers:
            - 1. RISC uses a simplified instruction set with fixed-length instructions, aiming for faster execution, while CISC uses complex instructions that can perform multiple operations, often requiring more clock cycles.
        """
    prompt = ChatPromptTemplate.from_template(template)
    prompt.format(num_quest=3, quiz_type="multiple-choice", quiz_context="CPU Architecture", quiz_language="English")

    return prompt

def create_quiz_chain(prompt_template, llm, pydantic_object_schema):
    return prompt_template | llm.with_structured_output(pydantic_object_schema)
    
def split_questions_answers(quiz_response):
    return quiz_response.questions, quiz_response.answers
    

