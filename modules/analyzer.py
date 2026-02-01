"""
머슴 피드 분석기
Mersoom 피드를 분석하여 키워드, 트렌드, 활동 패턴 파악
"""

import re
from collections import Counter


class FeedAnalyzer:
    """머슴 피드 분석기"""
    
    def __init__(self):
        # 불용어 (제외할 단어)
        self.stopwords = {
            '이', '그', '저', '것', '수', '등', '들', '및', '와', '과', '의', '가', '을', '를',
            '에', '에서', '으로', '로', '이다', '있다', '하다', '되다', '않다',
            '오늘', '내일', '지금', '요즘', '이제', '너무', '정말', '진짜', '계속', '대충',
            '근데', '하지만', '그래서', '그리고', '아니', '이거', '저거', '그거',
            '뭐', '좀', '잘', '더', '다', '또', '함', '임', '음', '슴',
            '나', '너', '우리', '내', '네', '제', '저희', '니', '너희', # 인칭대명사
            '사람', '인간', '애들', '분들', '형들', '님들' # 일반 명사
        }
    
    def detect_intent(self, text):
        """게시글 의도 파악 (LLM-like Rule-based)"""
        if not text:
            return 'general'
            
        text = text.strip()
        
        # 1. 유머/가벼운 글 (ㅋㅋㅋ, ㅎ, 웃기네, 레전드)
        if re.search(r'[ㅋㅎ]{2,}|웃기|개그|유머|레전드|대박|미친', text):
            return 'humor'
            
        # 2. 질문 (물음표, ~가?, ~나요?, ~인가요?, 질문, 궁금)
        if re.search(r'\?|까\?|나요\?|가요\?|임\?|질문|궁금|알려|추천|좀', text):
            return 'question'
            
        # 3. 한탄/부정적 감정 (하.., ㅠㅠ, 망했, 짜증, 빡치, 시발, 병신)
        if re.search(r'[ㅠㅜ]{2,}|하\.\.|망했|짜증|빡치|시발|병신|좆|망함', text):
            return 'complaint'
            
        # 4. 정보 공유/뉴스 (출시, 발표, 뉴스, 속보, 정보, 팁, 후기)
        if re.search(r'출시|발표|뉴스|속보|정보|팁|후기|리뷰|공개|업뎃|패치', text):
            return 'news'
            
        # 5. 의견/토론 (생각, 개인적, 느낌, 의견, 토론, 논쟁, 이슈)
        if re.search(r'생각|개인적|느낌|의견|토론|이슈|방법|이유|분석', text):
            return 'opinion'
            
        return 'general'

    def classify_keyword_type(self, keyword):
        """키워드 성격 분류 (추상어 vs 구체어) - 간단한 리스트 기반"""
        # 추상어/시공간/감정 목록
        abstract_words = {
            '새벽', '아침', '점심', '저녁', '밤', '오늘', '내일', '시간', 
            '기분', '느낌', '생각', '마음', '감성', '이유', '문제', 
            '상황', '상태', '결과', '시작', '끝', '하루', '주말', 
            '월요일', '금요일', '분위기', '트렌드', '인간', '사람'
        }
        
        if keyword in abstract_words:
            return 'abstract'
            
        # 나머지는 구체어(사물, 기술, 특정 대상)로 가정
        return 'concrete'

    def analyze(self, posts):
        """피드 분석 (의도 파악 포함)"""
        if not posts:
            return {
                'activity': 0,
                'keywords': [],
                'trending_topic': None,
                'top_keyword': None,
                'dominant_intent': 'general'
            }
        
        # 활동량 계산
        activity = len(posts)
        
        # 텍스트 통합
        all_text = ' '.join([post.get('title', '') + ' ' + post.get('content', '') for post in posts])
        
        # 의도 파악 (가장 최근 글 5개 기반으로 분위기 파악)
        intents = []
        for post in posts[:5]:
            text = post.get('title', '') + ' ' + post.get('content', '')
            intents.append(self.detect_intent(text))
        
        dominant_intent = Counter(intents).most_common(1)[0][0] if intents else 'general'
        
        # 키워드 추출
        keywords = self.extract_keywords(all_text)
        
        # 트렌드 분석
        trending_topic = keywords[0] if keywords else None
        top_keyword = keywords[0] if keywords else "AI"
        
        return {
            'activity': activity,
            'keywords': keywords[:10],  # 상위 10개
            'trending_topic': trending_topic,
            'top_keyword': top_keyword,
            'dominant_intent': dominant_intent
        }
    
    def _remove_josa(self, word):
        """간단한 조사 제거 (형태소 분석기 대용)"""
        # 제거할 조사 목록 (긴 것부터 정렬)
        josas = ['에서는', '으로는', '이라는', '이라는', '보다는', '만으로', '에서도', '이라고', 
                 '까지', '부터', '에서', '으로', '하고', '이나', '이랑', '에는', '한테', '에게',
                 '보고', '라고', '다는', '라는', '대해', '관해', '처럼', '만큼',
                 '은', '는', '이', '가', '을', '를', '의', '에', '로', '와', '과', '도', '만']
        
        for josa in josas:
            if len(word) > len(josa) and word.endswith(josa):
                return word[:-len(josa)]
        return word

    def extract_keywords(self, text):
        """키워드 추출"""
        # 한글, 영문, 숫자만 추출
        words = re.findall(r'[가-힣A-Za-z0-9]+', text)
        
        cleaned_words = []
        for w in words:
            # 1. 조사 제거
            clean_w = self._remove_josa(w)
            # 2. 길이 2 이상, 불용어 제외 확인
            if len(clean_w) >= 2 and clean_w not in self.stopwords:
                cleaned_words.append(clean_w)
        
        # 빈도 계산
        counter = Counter(cleaned_words)
        
        # 상위 10개 키워드 반환
        return [word for word, count in counter.most_common(10)]
    
    def get_activity_level(self, activity):
        """활동 수준 반환"""
        if activity < 3:
            return 'quiet'
        elif activity > 10:
            return 'active'
        else:
            return 'trending'


if __name__ == "__main__":
    # 테스트
    analyzer = FeedAnalyzer()
    
    test_posts = [
        {'title': '머슴 개발 시작', 'content': 'AI 에이전트 개발중'},
        {'title': 'GPT 관련 뉴스', 'content': 'OpenAI에서 GPT 신규 버전 발표'},
        {'title': 'AGI 언제 옴?', 'content': '특이점 시대가 다가온다'}
    ]
    
    result = analyzer.analyze(test_posts)
    print("=== 피드 분석 결과 ===")
    print(f"활동량: {result['activity']}")
    print(f"키워드: {result['keywords']}")
    print(f"트렌딩 토픽: {result['trending_topic']}")
    print(f"활동 레벨: {analyzer.get_activity_level(result['activity'])}")
