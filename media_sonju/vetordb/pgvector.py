from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document
from langchain.vectorstores.base import VectorStore
import psycopg2
import psycopg2.extras
import json

class CustomPGVector(VectorStore):
    def __init__(self, db: Any, embedding_fn, table: str = "faq_vectordb"):
        self.db = db
        self.embedding_fn = embedding_fn
        self.table = table

    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding_fn,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        db:Any=None,
        table: str = "documents",
        **kwargs,
    ):
        store = cls(db, embedding_fn=embedding_fn, table=table)
        store.add_texts(texts, metadatas=metadatas)
        return store

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]] = None):
        metadatas = metadatas or [{} for _ in texts]
        embeddings = self.embedding_fn.embed_documents(texts)
        
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                for text, emb, meta in zip(texts, embeddings, metadatas):
                    cur.execute(
                        f"""
                        INSERT INTO {self.table} (content, embedding, metadata)
                        VALUES (%s, %s::vector, %s)
                        """,
                        (text, emb, psycopg2.extras.Json(meta)),
                    )
            conn.commit()
        finally:
            self.db.put_connection(conn)
    
    def similarity_search(self, query: str, k: int = 4,
                          filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        
        query_emb = self.embedding_fn.embed_query(query)
        
        # 쿼리 매개변수 리스트 초기화. 필터 매개변수가 있다면 여기에 먼저 추가됩니다.
        params = []
        
        # SQL 쿼리 기본 구조 설정
        sql_query_template = f"""
            SELECT content, metadata
            FROM {self.table}
        """
        
        # WHERE 절을 위한 리스트
        where_clauses = []
        
        if filter:
            # 1. 필터 딕셔너리를 JSON 문자열로 변환합니다.
            filter_json = json.dumps(filter)
            
            # 2. WHERE 절에 'metadata @> %s::jsonb' 조건을 추가합니다.
            where_clauses.append("metadata @> %s::jsonb")
            
            # 3. 필터 JSON 문자열을 params 리스트에 먼저 추가합니다.
            #    이것이 SQL 쿼리에서 가장 먼저 나오는 %s에 바인딩됩니다.
            params.append(filter_json)

        if where_clauses:
            sql_query_template += " WHERE " + " AND ".join(where_clauses)
        
        # ORDER BY 및 LIMIT 절 추가
        # ORDER BY에는 임베딩 비교가 들어가며, 이는 필터가 있든 없든 항상 두 번째 (혹은 첫 번째) %s가 됩니다.
        sql_query_template += """
            ORDER BY (1 - (embedding <=> %s::vector)) DESC
            LIMIT %s
        """
        
        # 4. 임베딩 벡터를 params에 추가합니다.
        #    이는 ORDER BY의 %s에 바인딩됩니다.
        params.append(query_emb)
        
        # 5. LIMIT 값 (k)을 params에 마지막으로 추가합니다.
        #    이는 LIMIT의 %s에 바인딩됩니다.
        params.append(k)
        
        # 최종 SQL 쿼리: (필터가 있을 경우) WHERE [조건] ORDER BY [임베딩] LIMIT [k]
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            # 쿼리와 매개변수를 실행
            # 매개변수의 순서는 SQL 쿼리에 나타나는 %s의 순서와 정확히 일치해야 합니다.
            cur.execute(sql_query_template, tuple(params))
            rows = self.__get_unique_documents(cur.fetchall())

        return [Document(page_content=row[0], metadata=row[1]) for row in rows]
       
    def similarity_search_with_score( self, query: str, k: int = 4 ) -> List[Tuple[Document, float]]: 
        """쿼리와 유사도 점수를 함께 반환""" 
        query_emb = self.embedding_fn.embed_query(query) 
        conn = self.db.get_connection() 
        with conn.cursor() as cur: 
            cur.execute( f""" 
                        SELECT content, metadata, (1-(embedding <=> %s::vector)) AS score 
                        FROM {self.table} ORDER BY score DESC LIMIT %s """
                        , (query_emb, k)
            )
            rows = self.__get_unique_documents(cur.fetchall()) 
            return [ (Document(page_content=row[0], metadata=row[1]), float(row[2])) for row in rows ]
    
    
    def similarity_search_with_filter_score(self, query: str, k: int = 3,
        filter: Optional[Dict[str, Any]] = None) -> List[Tuple[Document, float]]:
        
        query_emb = self.embedding_fn.embed_query(query)
        
        
        sql_query = f"""
            SELECT content, metadata, (1 - (embedding <=> %s::vector)) AS score
            FROM {self.table}
        """
        
        # WHERE 절 조건 추가
        params = [query_emb]
        where_clauses = []

        if filter:
            filter_json = json.dumps(filter)
            where_clauses.append("metadata @> %s::jsonb")
            # 필터는 params의 앞쪽에 넣어야 SQL 순서와 맞음
            params.append(filter_json)

        if where_clauses:
            sql_query += " WHERE " + " AND ".join(where_clauses)

        # score에 따른 order
        sql_query += " ORDER BY score DESC LIMIT %s"
        params.append(k) 

        # DB 연결 및 실행
        conn = self.db.get_connection()
        with conn.cursor() as cur:
            cur.execute(sql_query, tuple(params))
            rows = self.__get_unique_documents(cur.fetchall())

        # 반환
        return [
            (Document(page_content=row[0], metadata=row[1]), float(row[2]))
            for row in rows
        ]
    
    def __get_unique_documents(self, rows):
        # 중복 제거를 위한 후처리
        unique_ids = set()
        unique_documents = []
        
        for row in rows:
            metadata = row[1]
            doc_id = metadata.get("id") if metadata else None
        
            # id가 없거나 이미 본 id면 스킵
            if not doc_id or doc_id in unique_ids:
                continue
            
            unique_ids.add(doc_id)
            unique_documents.append(row) # 중복이 아닐 때 원본 튜플을 저장

        return unique_documents


def create_pgvector_store(db, embeddings, collection_name: str = "faq_vectordb"):
    """PGVector 스토어 생성"""
    try:
        vectorstore = CustomPGVector(
            db=db,
            embedding_fn=embeddings,
            table=collection_name, # 테이블 이름과 매칭
        )
        print(f"PGVector 스토어 '{collection_name}'이 생성되었습니다.")
        return vectorstore
    except Exception as e:
        print(f"PGVector 스토어 생성 중 오류: {e}")
        return None
    
    
def add_documents_to_pgvector(vectorstore, documents):
    """문서를 PGVector에 추가"""
    try:
        # add_documents 메서드로 문서 추가
        vectorstore.add_documents(documents)
        print(f"{len(documents)}개 문서가 성공적으로 추가되었습니다.")
        return True
    except Exception as e:
        print(f"문서 추가 중 오류 발생: {e}")
        return False
