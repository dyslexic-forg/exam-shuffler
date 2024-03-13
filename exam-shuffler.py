#!/usr/bin/env python3
import re
import random
import argparse
import pypandoc
from docxcompose.composer import Composer

QUESTION_DELIMITER = r"^\s*\d+\.\s"
CHOICE_DELIMITER = r"^\s*[a-zA-Z]\)\s"
IMAGE_DELIMITER = r"\[\[.+:(.*)\]\]"
ANSWER_INDICATOR = r"+"

def parse_exam(string):
    parts = re.split(QUESTION_DELIMITER, string, flags=re.MULTILINE)
    return {
        "preamble": parts[0],
        "questions": [parse_question(p, i+1) for i,p in enumerate(parts[1:])]
    }

def parse_question(string, question_id):
    parts = re.split(CHOICE_DELIMITER, string, flags=re.MULTILINE)
    question = {
        "statement": parts[0],
        "choices": [p.strip() for p in parts[1:]],
        "id": question_id,
        "answer": ""
    }
    for idx, choice in enumerate(question["choices"]):
        if choice[-len(ANSWER_INDICATOR):] == ANSWER_INDICATOR:
            question["choices"][idx] = choice[:len(choice)-len(ANSWER_INDICATOR)]
            question["answer"] = question["choices"][idx]
            break
    return question

def shuffle_exam(exam):
    return {
        "preamble": exam["preamble"],
        "questions":
        [
            {
                "statement": q["statement"],
                "id": q["id"],
                "choices": random.sample(q["choices"], len(q["choices"])),
                "answer": q["answer"]
            }
        for q in random.sample(exam["questions"], len(exam["questions"]))
        ]
    }

def get_answers(exam):
    return [
        chr(q["choices"].index(q["answer"])+65)
        if q["answer"] in q["choices"]
        else " "
        for q in exam["questions"]
    ]

def create_versions(exam, n=4):
    n = min(len(exam["questions"]), n)
    versions = []
    while len(versions) < n:
        version = shuffle_exam(exam)
        if not any([question_in_same_pos(version, other_version) for other_version in versions]):
            versions.append(version)
    return versions

def question_in_same_pos(exam1, exam2):
    return any([q1["id"] == q2["id"] for q1, q2 in zip(exam1["questions"], exam2["questions"])])

def exam_to_string(exam):
    return "\n\n".join([f"*{i+1}*. {question_to_string(q)}" for i, q in enumerate(exam["questions"])])

def question_to_string(question):
    return question["statement"] + "\n".join([f"{chr(i+65)}) {choice}" for i,choice in enumerate(question["choices"])])

def exam_from_file(file_name):
    string = pypandoc.convert_file(file_name, "org", extra_args=["--extract-media=."])
    exam = parse_exam(string)
    return exam

def exam_to_file(exam, file_name):
    _, extension = file_name.split(".")
    pypandoc.convert_text(exam_to_string(exam), extension, "org", outputfile="teste.docx", extra_args=["--lua-filter=filter.lua", f"--reference-doc={file_name}"])

def parse_args():
    parser = argparse.ArgumentParser(
        prog="Exam Shuffler",
        description="Programa para embaralhar questões de prova."
    )
    parser.add_argument("filename", help="nome do arquivo")
    parser.add_argument("-n", "--number", type=int, default=4, help="número de versões a serem geradas")
    parser.add_argument("-t", "--template", help="arquivo docx com formatação e cabeçalho")
    return parser.parse_args()

def main():
    args = parse_args()
    exam = exam_from_file(args.filename)
    exam_to_file(exam, "teste.docx")

if __name__ == "__main__":
    main()
