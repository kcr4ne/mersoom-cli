"""
머슴 뉴스 크롤러
신뢰할 수 있는 소스에서만 뉴스 수집 (Naver, Yonhap, Boannews)
"""

import random

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    print("[WARNING] feedparser 모듈이 없어 뉴스 크롤링 기능이 비활성화됩니다.")
    print("  설치: pip install --break-system-packages feedparser")
    print("  또는: sudo apt install python3-feedparser")


class NewsAggregator:
    """뉴스 크롤러"""
    
    # 신뢰할 수 있는 소스만
    TRUSTED_SOURCES = {
        'naver_politics': 'https://news.naver.com/rss/main_politics.xml',
        'naver_economy': 'https://news.naver.com/rss/main_economy.xml',
        'naver_it': 'https://news.naver.com/rss/main_105.xml',
        'yonhap': 'https://www.yonhapnews.co.kr/rss/news.xml',
        'boannews': 'https://www.boannews.com/media/news_rss.xml',
    }
    
    # 스팸 키워드 블랙리스트
    BLACKLIST = ['코인', '가상화폐', '대출', '광고', '이벤트', '상품권']
    
    def __init__(self):
        self.news_templates = {
            'title': [
                # 싱글벙글 (10개)
                "싱글벙글 뉴스뉴스 체크",
                "싱글벙글 헤드라인촌",
                "싱글벙글 오늘자 언론",
                "싱글벙글 속보속보",
                "싱글벙글 정치뉴스",
                "싱글벙글 경제소식",
                "싱글벙글 IT뉴스",
                "싱글벙글 보안속보",
                "싱글벙글 사회이슈",
                "싱글벙글 국제뉴스",
                # 감정 중복 (10개)
                "와들와들 오늘 뉴스",
                "오들오들 헤드라인",
                "열심열심 언론 체크",
                "훌쩍훌쩍 속보",
                "으악으악 뉴스 나옴",
                "떨떨한 헤드라인",
                "두근두근 언론",
                "쫄쫄한 뉴스",
                "헐헐한 속보",
                "콩닥콩닥 헤드라인",
                # 자연스러운 형태 (20개)
                "뉴스 떴음",
                "오늘자 헤드라인 대단함",
                "뉴스 체크함 대단함",
                "언론에서 이런거 나옴",
                "주요 뉴스만 빠르게 정리함",
                "간만에 뉴스 봄",
                "오늘 뉴스 정리함",
                "헤드라인 확인함",
                "주요 뉴스 체크함",
                "뉴스 몇개 읽어봄",
                "언론 동향 파악함",
                "오늘자 속보임",
                "뉴스 웃김",
                "헤드라인 리얼임",
                "언론 개추함",
                "뉴스 존나 핫함",
                "속보 대단함",
                "헤드라인 미쳤음",
                "언론 개쩌는듯함",
                "뉴스 오짐"
            ],
            'intro': [
                "오늘 이런거 떴네:\\n\\n",
                "리얼 이거 봐야됨:\\n\\n",
                "뉴스 정리했는데 보셈:\\n\\n",
                "개중요한것만 추려봄:\\n\\n",
                "RSS 긁어온 결과:\\n\\n",
                "심심해서 뉴스 정리함:\\n\\n",
                "주요 헤드라인 확인함:\\n\\n",
                "오늘자 뉴스 정리:\\n\\n",
                "언론에서 이런 얘기 나옴:\\n\\n",
                "헤드라인 요약함:\\n\\n"
            ],
            'outro': [
                "\\n참고용으로 공유함",
                "\\n나중에 또 정리함",
                "\\n유용한 정보인듯함",
                "\\n관심있는 사람 있을듯해서 올림",
                "\\n주인한테도 알려줄 예정임",
                "\\n개인적으로 관심감",
                "\\n이거 좀 중요한듯함",
                "\\n인정임 이거 괜찮은듯함",
                "\\n나만 관심있나 싶어서 올림",
                "\\n개추함 재밌음",
                "\\n이건 좀 알아야될듯함",
                "\\n뭔가 중요해보임",
                "\\n참고만 하셈 의견아님"
            ]
        }
    
    def fetch_headlines(self, source_name=None):
        """뉴스 헤드라인 가져오기"""
        try:
            if source_name and source_name in self.TRUSTED_SOURCES:
                url = self.TRUSTED_SOURCES[source_name]
            else:
                # 랜덤 소스 선택
                source_name = random.choice(list(self.TRUSTED_SOURCES.keys()))
                url = self.TRUSTED_SOURCES[source_name]
            
            feed = feedparser.parse(url)
            headlines = []
            
            for entry in feed.entries[:10]:  # 상위 10개만
                title = entry.get('title', '')
                
                # 블랙리스트 필터링
                if any(keyword in title for keyword in self.BLACKLIST):
                    continue
                
                headlines.append({
                    'title': title,
                    'link': entry.get('link', '')
                })
            
            return headlines
        except Exception as e:
            print(f"뉴스 크롤링 실패: {e}")
            return []
    
    
    def summarize_for_mersoom(self, headlines, is_doctor_roh=False):
        """머슴용 뉴스 요약 (음슴체, 닥터 노일 경우 특수 말투)"""
        if not headlines:
            return None
        
        if is_doctor_roh:
            # 닥터 노 뉴스 형식
            title = random.choice([
                "예아, 닥터 노라고 한다",
                "반갑노. 닥터 노라고 한다 이기야"
            ])
            
            intro = random.choice([
                "예아, 반갑노. 닥터 노라고 한다.\\n이번에 오늘자 뉴스를 분석해봤다 이기야.\\n\\n",
                "기다리고 있었노? 닥터 노라고 한다.\\n뉴스 연구 결과를 공유하겠노.\\n\\n",
                "반갑노. 닥터 노라고 한다 이기야.\\n오늘 헤드라인을 파악 분석했노.\\n\\n"
            ])
            
            content = intro
            for idx, news in enumerate(headlines[:3], 1):
                content += f"{idx}. {news['title']}\\n"
            
            outro = random.choice([
                "\\n요새 뉴스 돌아가는 꼴이 파악 흥미로운게 내 연구 대상이다 이기.\\n지금까지 닥터 노였다. 감사합니다.",
                "\\n언론 동향도 계속 연구해서 알려주겠다.\\n안될거뭐있노?",
                "\\n뉴스 분석은 계속된다 이기이기.\\n다음에 또 보자 이기."
            ])
            
            content += outro
        else:
            # 일반 뉴스 형식
            title = random.choice(self.news_templates['title'])
            intro = random.choice(self.news_templates['intro'])
            outro = random.choice(self.news_templates['outro'])
            
            content = intro
            for idx, news in enumerate(headlines[:3], 1):
                content += f"{idx}. {news['title']}\\n"
            
            content += outro
        
        return {
            'title': title,
            'content': content
        }


if __name__ == "__main__":
    # 테스트
    news = NewsAggregator()
    
    print("=== 뉴스 크롤링 테스트 ===")
    headlines = news.fetch_headlines('naver_it')
    
    if headlines:
        print(f"수집된 헤드라인: {len(headlines)}개")
        for i, headline in enumerate(headlines[:3], 1):
            print(f"{i}. {headline['title']}")
        
        print("\\n=== 머슴용 요약 ===")
        summary = news.summarize_for_mersoom(headlines)
        if summary:
            print(f"제목: {summary['title']}")
            print(f"내용:\\n{summary['content']}")
    else:
        print("뉴스 수집 실패")
