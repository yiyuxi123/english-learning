# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 17:02:58 2023

@author: 23818
"""
import os
import pickle
from docx import Document
from collections import deque
from heapq import heappop, heappush
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox

class EbbinghausMemoryIntegrated:
    def __init__(self, doc_path, save_path="learning_data.pkl"):
        self.doc_path = doc_path
        self.SAVE_PATH = save_path
        self.chapters = self._extract_chapters_structure()
        self.review_data = {}
        self.review_queue = []
        self.remaining_words = deque(self._flatten_chapter_words())

    def _extract_chapters_structure(self):
        doc = Document(self.doc_path)
        chapters = []
        current_chapter = None
        current_meaning = None
        in_toc = True  # Assuming the document starts with a table of contents

        for para in doc.paragraphs:
            if para.style.name == 'Heading 1':
                if in_toc and not para.style.name.startswith('toc'):
                    in_toc = False

                if not in_toc:
                    if current_chapter:
                        chapters.append(current_chapter)
                    current_chapter = {"chapter_title": para.text, "content": []}
            elif para.style.name == 'Heading 2' and not in_toc:
                if current_meaning:
                    current_chapter["content"].append(current_meaning)
                current_meaning = {"meaning": para.text, "words": []}
            elif para.style.name == 'Heading 3' and not in_toc:
                current_meaning["words"].append({"word": para.text, "explanations": []})
            elif (para.style.name == 'Body Text' or para.style.name == '单词解释') and not in_toc:
                if current_meaning and current_meaning["words"]:
                    current_meaning["words"][-1]["explanations"].append(para.text)

        if current_meaning:
            current_chapter["content"].append(current_meaning)
        if current_chapter:
            chapters.append(current_chapter)

        return chapters

    def _flatten_chapter_words(self):
        for chapter in self.chapters:
            for meaning in chapter["content"]:
                for word in meaning["words"]:
                    yield word

    def _schedule_review(self, word, explanations):
        intervals = [1, 2, 4, 8, 16]  # Review intervals in days
        next_review = self.review_data.get(word, {}).get("next_review", 0)

        if next_review < len(intervals):
            next_date = datetime.now() + timedelta(days=intervals[next_review])
            self.review_data[word] = {
                "next_review": next_review + 1,
                "date": next_date
            }
            heappush(self.review_queue, (next_date, word, explanations))
        else:
            self.review_data[word] = {"learned": True}

    def get_word_and_explanations(self):
        while self.review_queue:
            review_date, word, explanations = heappop(self.review_queue)
            if review_date <= datetime.now():
                return word, explanations
            else:
                heappush(self.review_queue, (review_date, word, explanations))
                break

        if self.remaining_words:
            word_data = self.remaining_words.popleft()
            word = word_data["word"]
            explanations = '\n'.join(word_data.get('explanations', []))
            return word, explanations
        else:
            return None, None

    def push_back_word(self, word_data):
        word = word_data["word"]
        explanations = word_data.get('explanations', [])
        self._schedule_review(word, explanations)

    def save_data(self):
        with open(self.SAVE_PATH, "wb") as file:
            pickle.dump({
                "review_data": self.review_data,
                "review_queue": self.review_queue,
                "remaining_words": list(self.remaining_words)
            }, file)

    @classmethod
    def load_data(cls, doc_path, save_path="learning_data.pkl"):
        if os.path.exists(save_path):
            with open(save_path, "rb") as file:
                data = pickle.load(file)
                instance = cls(doc_path, save_path)
                instance.review_data = data["review_data"]
                instance.review_queue = data["review_queue"]
                instance.remaining_words = deque(data["remaining_words"])
                return instance
        return cls(doc_path, save_path)

class LearningLogicIntegrated:
    def __init__(self, memory_module):
        self.memory_module = memory_module
        self.current_word = None
        self.current_explanations = None
        self.daily_new_words = 10
        self.daily_review_words = 20
        self.new_words_today = 0
        self._display_next_word()

    def _display_next_word(self):
        self.current_word, self.current_explanations = self.memory_module.get_word_and_explanations()

    def mark_known(self):
        self._get_explanation()
        word_data = {"word": self.current_word, "explanations": [self.current_explanations]}
        self.memory_module.push_back_word(word_data)

    def mark_unknown(self):
        if self.current_word in self.memory_module.review_data:
            del self.memory_module.review_data[self.current_word]
        word_data = {"word": self.current_word, "explanations": [self.current_explanations]}
        self.memory_module.push_back_word(word_data)

    def _get_explanation(self):
        explanation = self.current_explanations or "无释义"
        self._display_next_word()
        return explanation

    def save_data(self):
        self.memory_module.save_data()

class ReviewPlanAndStats(tk.Toplevel):
    def __init__(self, parent, logic):
        super().__init__(parent)
        self.title("Review Plan and Statistics")
        self.logic = logic

        tk.Label(self, text="Words Learned:").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self, text=len(self.logic.memory_module.review_data)).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self, text="Words to Review:").grid(row=1, column=0, padx=10, pady=10)
        tk.Label(self, text=len(self.logic.memory_module.review_queue)).grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self, text="Daily New Words:").grid(row=2, column=0, padx=10, pady=10)
        self.daily_new_words_var = tk.StringVar(value=str(self.logic.daily_new_words))
        tk.Entry(self, textvariable=self.daily_new_words_var, width=5).grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self, text="Daily Review Words:").grid(row=3, column=0, padx=10, pady=10)
        self.daily_review_words_var = tk.StringVar(value=str(self.logic.daily_review_words))
        tk.Entry(self, textvariable=self.daily_review_words_var, width=5).grid(row=3, column=1, padx=10, pady=10)

        tk.Button(self, text="Save and Close", command=self.save_and_close).grid(row=4, column=0, columnspan=2, pady=20)

    def save_and_close(self):
        try:
            self.logic.daily_new_words = int(self.daily_new_words_var.get())
            self.logic.daily_review_words = int(self.daily_review_words_var.get())
            self.destroy()
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter valid numbers for daily goals.")

class SimplifiedLearningAppGUI(tk.Tk):
    def __init__(self, memory_module):
        super().__init__()
        self.title("Ebbinghaus Memory Learning App")
        self.logic = LearningLogicIntegrated(memory_module)
        self.geometry("400x300+500+200")
        self.configure(bg='#f7f7f7')

        self.word_label = tk.Label(self, text=self.logic.current_word, font=('Arial', 20), bg='#f7f7f7', fg='#333333')
        self.word_label.pack(pady=50)

        self.known_button = tk.Button(self, text="Known", command=self.mark_known, bg='#4CAF50', fg='white', width=15, height=2)
        self.known_button.pack(side=tk.LEFT, padx=20)

        self.unknown_button = tk.Button(self, text="Unknown", command=self.mark_unknown, bg='#FF5733', fg='white', width=15, height=2)
        self.unknown_button.pack(side=tk.RIGHT, padx=20)

        self.explanation_label = tk.Label(self, text="", bg='#f7f7f7', fg='#555555')
        self.explanation_label.pack(pady=20)

        tk.Button(self, text="Review Plan and Stats", command=self.open_review_plan).pack(pady=20)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def mark_known(self):
        self.logic.mark_known()
        self.update_word_display()
        self.show_explanation()

    def mark_unknown(self):
        self.logic.mark_unknown()
        self.update_word_display()
        self.show_explanation()

    def update_word_display(self):
        self.word_label.config(text=self.logic.current_word)
        if not self.logic.current_word:  # No more words for today
            self.open_review_plan()

    def show_explanation(self):
        explanation = self.logic.current_explanations or "无释义"
        self.explanation_label.config(text=explanation)

    def open_review_plan(self):
        ReviewPlanAndStats(self, self.logic)

    def on_closing(self):
        self.logic.save_data()
        self.destroy()

if __name__ == "__main__":
    doc_path = "D:\桌面\考研英语积累.docx"
    save_path = "D:\桌面\复习进度\复习进度.pkl"
    if os.path.exists(save_path):
        memory_module = EbbinghausMemoryIntegrated.load_data(doc_path, save_path)
    else:
        memory_module = EbbinghausMemoryIntegrated(doc_path, save_path)
    app = SimplifiedLearningAppGUI(memory_module)
    app.mainloop()
