import pandas as pd
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def create_document(conn):
    df = pd.read_sql("SELECT * FROM skmagic_faq;", conn)
    
    docs = [
        Document(
            page_content= f"Question: {row['title']}  Answer: {row['text']}",   # 두 컬럼 합치기
            metadata={
                "table":"skmagic_faq",
                "id": row["id"],# 테이블의 id 컬럼
                "category": row["sub_category"]   
            }
        )
    for _, row in df.iterrows()
    ]
    print(f"document 생성 완료 -> 길이 {len(docs)}")
    
    return docs


def make_chunk(db):
    conn = db.get_connection()
    recursive_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=150, chunk_overlap=50
    )
    chunks = recursive_text_splitter.split_documents(create_document(conn))
    print(f"chunk 생성 -> {len(chunks)}개")
    return chunks
