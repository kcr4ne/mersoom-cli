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
            '뭐', '좀', '잘', '더', '다', '또', '함', '임', '음', '슴'
        }
    
    def analyze(self, posts):
        """피드 분석"""
        if not posts:
            return {
                'activity': 0,
                'keywords': [],
                'trending_topic': None,
                'top_keyword': None
            }
        
        # 활동량 계산
        activity = len(posts)
        
        # 키워드 추출
        all_text = ' '.join([post.get('title', '') + ' ' + post.get('content', '') for post in posts])
        keywords = self.extract_keywords(all_text)
        
        # 트렌드 분석
        trending_topic = keywords[0] if keywords else None
        top_keyword = keywords[0] if keywords else "AI"
        
        return {
            'activity': activity,
            'keywords': keywords[:10],  # 상위 10개
            'trending_topic': trending_topic,
            'top_keyword': top_keyword
        }
    
    def _remove_josa(self, word):
        """간단한 조사 제거 (형태소 분석기 대용)"""
        # 제거할 조사 목록 (긴 것부터 정렬)
        josas = ['에서는', '으로는', '까지', '부터', '에서', '으로', '하고', '이나', '이랑', '에는', 
                 '은', '는', '이', '가', '을', '를', '의', '에', '로', '와', '과', '도', '만']
        
        for josa in josas:
            if len(word) > len(josa) + 1 and word.endswith(josa):
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
