import requests
from bs4 import BeautifulSoup
import time
import re
import json
import urllib.robotparser as robotparser
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer

class AutomatedDataPipeline:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.crawl_delay = 1
        self.rp_cache = {}
        
        
        print("AutomatedDataPipeline 초기화 완료.")

    def _get_robot_parser(self, base_url: str):
        """
        주어진 기본 URL에 대한 robots.txt 파서 객체를 가져옵니다.
        캐싱을 사용하여 불필요한 robots.txt 요청을 줄입니다.
        """
        if base_url not in self.rp_cache:
            rp = robotparser.RobotFileParser()
            robots_txt_url = f"{base_url.rstrip('/')}/robots.txt"
            print(f"DEBUG: robots.txt 다운로드 시도: {robots_txt_url}")
            try:
                rp.set_url(robots_txt_url)
                rp.read()
                self.rp_cache[base_url] = rp
            except Exception as e:
                print(f"WARNING: robots.txt를 가져오거나 파싱하는 중 오류 발생: {robots_txt_url} - {e}")
                
                self.rp_cache[base_url] = None
        return self.rp_cache[base_url]

    def _is_crawl_allowed(self, url: str) -> bool:
        """
        robots.txt 규칙에 따라 주어진 URL의 크롤링이 허용되는지 확인합니다.
        """
        parsed_url = requests.utils.urlparse(url)

        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        rp = self._get_robot_parser(base_url)

        if rp:
            user_agent = self.headers["User-Agent"]
            allowed = rp.can_fetch(user_agent, url)
            if not allowed:
                print(f"WARNING: robots.txt에 의해 크롤링이 금지된 URL입니다: {url}")
            return allowed
        else:
         
            print(f"WARNING: robots.txt를 확인할 수 없어 '{url}'에 대한 크롤링을 기본적으로 허용합니다. 주의하십시오.")
            return True


    def _fetch_page_content(self, url: str) -> str | None:
        """
        주어진 URL에서 웹 페이지의 HTML 콘텐츠를 가져옵니다.
        네트워크 오류, HTTP 오류, 타임아웃 등에 대한 예외 처리를 포함합니다.
        """
      
        if not self._is_crawl_allowed(url):
            return None 

        try:
            print(f"DEBUG: fetching URL: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"ERROR: 웹 페이지를 가져오는 중 오류 발생: {url} - {e}")
            return None


    def _extract_main_content(self, html_content: str) -> str:
        """
        HTML 콘텐츠에서 본문 텍스트를 추출하고 1차 정제합니다.
        HTML 태그, 불필요한 공백, 개행 문자 등을 제거합니다.
        """
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, 'html.parser')

        main_content_elements = []
        potential_content_tags = ['p', 'div', 'article', 'main']
        
        for tag_name in potential_content_tags:
            found_elements = soup.find_all(tag_name)
            for element in found_elements:
                text = element.get_text(separator=' ', strip=True)
                if len(text) > 50:
                    main_content_elements.append(text)

        raw_text = "\n\n".join(main_content_elements)

        cleaned_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', raw_text)
        cleaned_text = re.sub(r'&[a-zA-Z0-9#]+;', '', cleaned_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        cleaned_text = re.sub(r'[^\w\s.,!?"\'()가-힣]', '', cleaned_text) 
        
        return cleaned_text

    def collect_data(self, urls: list[str]) -> list[dict]:
        """
        주어진 URL 목록에서 데이터를 수집하고 1차 정제합니다.
        각 수집 항목은 원본 URL과 정제된 텍스트를 포함하는 딕셔너리 형태입니다.
        """
        collected_data = []
        for url in urls:
            print(f"데이터 수집 시도: {url}")
            html_content = self._fetch_page_content(url)
            if html_content:
                main_text = self._extract_main_content(html_content)
                if main_text:
                    collected_data.append({
                        "original_url": url,
                        "raw_text": main_text
                    })
                else:
                    print(f"WARNING: '{url}' 에서 유효한 본문 텍스트를 추출하지 못했습니다.")
            time.sleep(self.crawl_delay)

        return collected_data

    def save_intermediate_data(self, data: list[dict], filepath: str):
        """
        수집 및 1차 정제된 데이터를 중간 파일로 저장합니다 (JSON Lines 형식).
        대상 폴더가 없으면 자동으로 생성합니다.
        """
        try:          
            directory = os.path.dirname(filepath)

            if directory: 
                os.makedirs(directory, exist_ok=True) 

            with open(filepath, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            print(f"중간 데이터가 성공적으로 저장되었습니다: {filepath}")
        except IOError as e:
            print(f"ERROR: 중간 데이터 저장 중 오류 발생: {filepath} - {e}")


if __name__ == "__main__":
    pipeline = AutomatedDataPipeline()

    test_urls = [
        "https://ko.wikipedia.org/wiki/%EC%8B%9C%EA%B0%84"
        #해당 URL은 예시입니다. 실제로는 크롤링할 URL 목록을 여기에 추가해야 합니다.
    ]

    print("\n--- 데이터 수집 단계 시작 ---")
    collected_raw_data = pipeline.collect_data(test_urls)
    
    if collected_raw_data:
        print(f"총 {len(collected_raw_data)}개의 문서에서 텍스트를 수집했습니다.")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '../../'))
        
        intermediate_filepath = os.path.join(project_root, 'data', 'intermediate', f'crawled_raw_text_data_{timestamp}.jsonl') 
        pipeline.save_intermediate_data(collected_raw_data, intermediate_filepath)
        
        print("\n--- 키워드 추출 단계 시작 ---")
        
        documents = [item['raw_text'] for item in collected_raw_data]

        tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000) 
        
        tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

        feature_names = tfidf_vectorizer.get_feature_names_out()

        for i, doc in enumerate(collected_raw_data):
            feature_scores = tfidf_matrix[i].T.todense()
            word_scores = []
            for col_idx, score in enumerate(feature_scores):
                word_scores.append((feature_names[col_idx], score[0, 0]))
            
            top_keywords = sorted(word_scores, key=lambda x: x[1], reverse=True)[:5]
            
            collected_raw_data[i]['extracted_keywords'] = [kw[0] for kw in top_keywords]
            print(f"문서 {i+1}의 키워드: {[kw[0] for kw in top_keywords]}")

        intermediate_filepath_with_keywords = os.path.join(project_root, 'data', 'intermediate', f'crawled_processed_data_with_keywords_{timestamp}.jsonl') 
        pipeline.save_intermediate_data(collected_raw_data, intermediate_filepath_with_keywords)
        print(f"키워드 추출된 중간 데이터가 성공적으로 저장되었습니다: {intermediate_filepath_with_keywords}")

    else:
        print("수집된 데이터가 없습니다.")

        
