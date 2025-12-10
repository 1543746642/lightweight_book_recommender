import os
import gradio as gr
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

from db import get_or_create_db

load_dotenv()

books = pd.read_csv("books_with_emotions.csv")
books["large_thumbnail"] = books['thumbnail'].apply(lambda x:x + '&file800' if isinstance(x, str) else x)
books["large_thumbnail"] = np.where(
    books["large_thumbnail"].isna(),
    "not_found.jpg",
    books["large_thumbnail"],
)

raw_documents = TextLoader("tagged_description.txt", encoding="utf-8").load()


def character_spliter(raw: list):
    content = raw[0].page_content
    lines = [line for line in content.split("\n") if line.strip()]

    document = [Document(page_content=line, metadata=raw[0].metadata) for line in lines]
    return document


documents = character_spliter(raw_documents)

db_books = get_or_create_db()

def retrieve_semantic_recommendation(
        query: str,
        category: str = None,
        tone: str = None,
        initial_top_k: int = 50,
        final_top_k: int = 16,
) -> pd.DataFrame:
    recs = db_books.similarity_search(query, k=initial_top_k)
    book_lists = [int(rec.page_content.split(':')[0].strip('"')) for rec in recs]
    book_recs = books[books["isbn13"].isin(book_lists)].head(final_top_k)

    if category != "All":
        book_recs = book_recs[book_recs["simple_category"] == category].head(final_top_k)
    else:
        book_recs = book_recs.head(final_top_k)

    if tone == "Happy":
        book_recs.sort_values(by="joy", ascending=False, inplace=True)
    elif tone == "Surprising":
        book_recs.sort_values(by="surprise", ascending=False, inplace=True)
    elif tone == "Angry":
        book_recs.sort_values(by="anger", ascending=False, inplace=True)
    elif tone == "Suspenseful":
        book_recs.sort_values(by="fear", ascending=False, inplace=True)
    elif tone == "Sad":
        book_recs.sort_values(by="sadness", ascending=False, inplace=True)

    return book_recs


def recommendation_book(
        query: str,
        category: str = None,
        tone: str = None,
):
    recommendation = retrieve_semantic_recommendation(query, category, tone)
    results = []

    for _, row in recommendation.iterrows():
        description = row["description"]
        truncated_desc_split = description.split()
        truncated_description = " ".join(truncated_desc_split[:30]) + "..."

        author_split = row["authors"].split(";")
        if len(author_split) == 2:
            author_str = f"{author_split[0]} {author_split[1]}"
        elif len(author_split) > 3:
            author_str = f"{",".join(author_split[:-1]), author_split[-1]}"
        else:
            # 某一行中的 “author” 这一列的数据。
            author_str = row["authors"]

        caption = f"{row['title']} by {author_str}: {truncated_description}"
        results.append((row["large_thumbnail"], caption))
    return results

categories = ["All"] + sorted(books["simple_categories"].unique())
tones = ['All'] + ["Happy", "Surprising","Angry","Sad","Suspenseful"]

with gr.Blocks() as dashboard:

    gr.Markdown("# semantic book recommender")

    with gr.Row():
        user_query = gr.Textbox(label="Please enter a book description of a book:",
                                placeholder="e.g a story about forgiveness.")
        category_dropdown = gr.Dropdown(choices=categories, label="Please select a category:", value="All")
        tone_dropdown = gr.Dropdown(choices=tones, label="Please select a tone:", value="All")
        submit_button = gr.Button("Find recommendations")

    gr. Markdown("## recommendation")
    output = gr.Gallery(label= "Recommendation books", columns=8, rows=2)

    submit_button.click(fn=recommendation_book,
                        inputs=[user_query, category_dropdown, tone_dropdown],
                        outputs=output,)


if __name__ == "__main__":
    dashboard.launch()