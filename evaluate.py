"""
DocuMind - RAGAS Evaluation Pipeline
Tests the RAG system quality using a golden Q&A dataset from CUTM docs.
Metrics: Faithfulness, Answer Relevancy, Context Precision, Context Recall

Run with: python -m src.eval.evaluate
"""

import json
import logging
from datetime import datetime
from typing import List, Dict

from datasets import Dataset

from src.retrieval.retriever import get_retriever
from src.retrieval.rag_chain import generate_answer

logger = logging.getLogger(__name__)

# ── Golden Test Dataset (CUTM-specific Q&A pairs) ────────────────────────────
# These are hand-crafted from the actual CUTM documents — this is your eval corpus
GOLDEN_QA = [
    {
        "question": "What is the minimum attendance required to appear in semester exams at CUTM?",
        "ground_truth": "Students must maintain a minimum of 75% attendance per subject (not aggregate) to appear in semester examinations. A maximum of 10% condoning is allowed for medical or other valid reasons by the Dean.",
    },
    {
        "question": "What grade is considered passing for theory papers in CUTM?",
        "ground_truth": "Grade D (40% and above) is the pass grade for theory papers. Grade C (50% and above) is the pass grade for Practical, Project, and Workshop mode papers.",
    },
    {
        "question": "What happens if a student is caught using unfair means in the exam?",
        "ground_truth": "A student found guilty of malpractice during examination will be awarded 'M' grade (0 points) in that subject. The university may also take additional disciplinary action, and such candidates will be allowed to appear only in subsequent examinations based on the university's decision. Heavy penalties include fail in the subject, cancellation of all subjects written in the semester, debarring from examination, or possible expulsion.",
    },
    {
        "question": "How many credits are required to get a BTech degree from CUTM?",
        "ground_truth": "A student must obtain 180 credits to be eligible for the award of a B.Tech degree, with required credits from each basket (Basket I through Basket V) and at least one domain track from Basket V.",
    },
    {
        "question": "What is the fee for Examination on Demand (EOD) at CUTM?",
        "ground_truth": "EOD fee is Rs 2000 for online registration and Rs 3000 for offline registration. Offline registration is only available once the EOD schedule is published and the specific subject is available.",
    },
    {
        "question": "How many EODs are conducted per semester at CUTM?",
        "ground_truth": "The university conducts two EODs per semester and one extended EOD during summertime to provide opportunities to students to clear their backlog papers.",
    },
    {
        "question": "What is the question paper pattern for end semester exams at CUTM?",
        "ground_truth": "The question paper is of 100 marks and 3 hours duration. Part A: 10 short questions (2 marks each = 20 marks). Part B: 5 long questions (12 marks each = 60 marks, may have sub-questions). Part C: 4 short notes (5 marks each = 20 marks).",
    },
    {
        "question": "What is the maximum duration to complete BTech at CUTM?",
        "ground_truth": "The maximum duration a student can take to graduate is 8 years from the date of registration to the degree program. The minimum duration is 4 years.",
    },
    {
        "question": "Can a student leave the exam hall after 30 minutes?",
        "ground_truth": "No. Without special permission, no candidate may leave the examination room until one hour of the examination period has elapsed. Also, candidates cannot leave their desk during the last 15 minutes of any examination.",
    },
    {
        "question": "What items are banned inside the CUTM examination hall?",
        "ground_truth": "The following are banned inside the examination hall: mobile phones, any kind of communication devices, books, printed or handwritten materials (except Registration Card, I-Card, Admit Card, calculator, and writing/drawing materials), and programmable calculators.",
    },
]


def run_evaluation(save_results: bool = True) -> Dict:
    """
    Runs the RAGAS evaluation pipeline on the golden Q&A dataset.
    Returns a dict of metric scores.
    """
    logger.info("=== DocuMind RAGAS Evaluation Started ===")
    logger.info(f"Evaluating on {len(GOLDEN_QA)} golden Q&A pairs")

    retriever = get_retriever()

    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for i, qa in enumerate(GOLDEN_QA):
        logger.info(f"Processing Q{i+1}/{len(GOLDEN_QA)}: {qa['question'][:60]}...")
        try:
            # Retrieve
            docs = retriever.retrieve(qa["question"])
            # Generate
            result = generate_answer(qa["question"], docs)

            questions.append(qa["question"])
            answers.append(result["answer"])
            contexts.append([doc.page_content for doc in docs])
            ground_truths.append(qa["ground_truth"])

        except Exception as e:
            logger.error(f"Error on Q{i+1}: {e}")
            # Add placeholder to keep indices aligned
            questions.append(qa["question"])
            answers.append("ERROR: " + str(e))
            contexts.append([])
            ground_truths.append(qa["ground_truth"])

    # Build RAGAS dataset
    eval_dataset = Dataset.from_dict(
        {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        }
    )

    # Run RAGAS metrics
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )

    logger.info("Running RAGAS metrics...")
    results = evaluate(
        dataset=eval_dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )

    scores = {
        "faithfulness": round(results["faithfulness"], 4),
        "answer_relevancy": round(results["answer_relevancy"], 4),
        "context_precision": round(results["context_precision"], 4),
        "context_recall": round(results["context_recall"], 4),
        "num_questions": len(GOLDEN_QA),
        "timestamp": datetime.now().isoformat(),
    }

    _print_results(scores)

    if save_results:
        _save_results(scores, eval_dataset)

    return scores


def _print_results(scores: Dict):
    print("\n" + "=" * 50)
    print("  DocuMind RAGAS Evaluation Results")
    print("=" * 50)
    print(f"  Faithfulness      : {scores['faithfulness']:.2%}  (Is answer grounded in context?)")
    print(f"  Answer Relevancy  : {scores['answer_relevancy']:.2%}  (Does answer address the question?)")
    print(f"  Context Precision : {scores['context_precision']:.2%}  (Are retrieved chunks relevant?)")
    print(f"  Context Recall    : {scores['context_recall']:.2%}  (Did retrieval find all needed info?)")
    print("=" * 50)
    avg = sum([scores[k] for k in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]]) / 4
    print(f"  Overall Average   : {avg:.2%}")
    print("=" * 50 + "\n")


def _save_results(scores: Dict, dataset: Dataset):
    import os
    os.makedirs("./data/eval_results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"./data/eval_results/eval_{timestamp}.json"

    output = {
        "scores": scores,
        "qa_results": [
            {
                "question": dataset["question"][i],
                "answer": dataset["answer"][i],
                "ground_truth": dataset["ground_truth"][i],
                "context_count": len(dataset["contexts"][i]),
            }
            for i in range(len(dataset["question"]))
        ],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"Eval results saved to {filepath}")


if __name__ == "__main__":
    run_evaluation()
