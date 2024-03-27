#!/usr/bin/env python3
import os
import re
import random
import argparse
import pypandoc

QUESTION_DELIMITER = r"^\s*\d+\\\.\s"
CHOICE_DELIMITER = r"^\s*[a-zA-Z]\\\)\s"
ANSWER_INDICATOR = r"+"

def parse_exam(string):
    """Return an exam from a string"""
    parts = re.split(QUESTION_DELIMITER, string, flags=re.MULTILINE)
    return {
        "preamble": parts[0],
        "questions": [parse_question(p, i+1) for i,p in enumerate(parts[1:])]
    }

def parse_question(string, question_id):
    """Return an question from a string"""
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
    """Return a new exam with questions and choices shuffled"""
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
    """Get the answers keys from an exam"""
    return [
        chr(q["choices"].index(q["answer"])+65)
        if q["answer"] in q["choices"]
        else " "
        for q in exam["questions"]
    ]

def create_versions(exam, n=4):
    """Create versions of an exam"""
    n = min(len(exam["questions"]), n)
    versions = []
    while len(versions) < n:
        version = shuffle_exam(exam)
        if not any([question_in_same_pos(version, other_version) for other_version in versions]):
            versions.append(version)
    return versions

def question_in_same_pos(exam1, exam2):
    """Verify if two exams has questions in same position"""
    return any([q1["id"] == q2["id"] for q1, q2 in zip(exam1["questions"], exam2["questions"])])

def exam_to_string(exam):
    """Return the exam's string representation"""
    return "\n".join([f"**{i+1}.** {question_to_string(q)}" for i, q in enumerate(exam["questions"])])

def question_to_string(question):
    """Return the question's string representation"""
    return question["statement"] + "\n" + "\n".join([f"{chr(i+65)}\\) {choice} \\" for i,choice in enumerate(question["choices"])])

def versions_to_string(versions):
    """Return the versions's string representation"""
    return "\n\n".join([f"# Versão {i+1}\n\n {exam_to_string(v)} \\newpage" for i, v in enumerate(versions)])

def exam_from_file(file_name):
    """Return an exam from a file"""
    directory = os.path.dirname(file_name)
    string = pypandoc.convert_file(file_name, "md", extra_args=[f"--extract-media={directory}"])
    exam = parse_exam(string)
    return exam

def versions_to_docx(versions, filename, template=None):
    """Write exam versions in a docx file"""
    extra_args = [f"--reference-doc={template}"] if template else []
    pypandoc.convert_text(versions_to_string(versions), to="docx", format="md", outputfile=filename, extra_args=extra_args)

def parse_args():
    parser = argparse.ArgumentParser(
        prog="Exam Shuffler",
        description="Programa para embaralhar questões de prova."
    )
    parser.add_argument("filename", help="nome do arquivo")
    parser.add_argument("-n", "--number", type=int, default=4, help="número de versões a serem geradas")
    return parser.parse_args()

def main():
    args = parse_args()
    exam = exam_from_file(args.filename)
    versions = create_versions(exam, args.number)

    directory, name_ext = os.path.split(args.filename)
    name, _ = os.path.splitext(name_ext)

    versions_to_docx(versions, os.path.join(directory, f"{name}-versions.docx"), args.filename)
    

if __name__ == "__main__":
    main()
