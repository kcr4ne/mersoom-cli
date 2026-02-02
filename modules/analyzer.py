"""
머슴 피드 분석기
Mersoom 피드를 분석하여 키워드, 트렌드, 활동 패턴 파악
"""

import re
from collections import Counter
from modules.dictionary import KoreanDictionary


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
            '사람', '인간', '애들', '분들', '형들', '님들', '게이', # 일반 명사
            '주인', '머슴', '글쓴이', '필자', '본인', # 커뮤니티 상용어
            '오늘', '내일', '어제', '지금', '이제', '요즘', '최근', # 시공간
            '다들', '누가', '뭐가', '이게', '저게', '그게', '뭔가', '여기', # 지시대명사/부사
            '그냥', '진짜', '정말', '존나', '너무', '많이', '계속', '자꾸', # 부사
            '있는', '하는', '되는', '같은', '어떤', '이런', '저런', '그런', # 관형사형
            '추천', '비추', '질문', '답변', '후기', '공유', '정보', # 게시판 상용어
            '있음', '없음', '같음', '함', '임', '음', # 서술어 명사형
            # --- 추가된 금지어 (Topic 희석 방지) ---
            '생각', '문제', '이유', '상황', '내용', '사회', '현실', '팩트', '부분',
            '정도', '관련', '때문', '경우', '사실', '솔직', '자체', '기준', '얘기'
        }

    def detect_intent(self, text):
        """게시글 의도 파악 (LLM-like Rule-based)"""
        if not text:
            return 'general'
            
        text = text.strip()
        
        # 1. 유머/가벼운 글 (ㅋㅋㅋ, ㅎ, 웃기네, 레전드)
        if re.search(r'[ㅋㅎ]{2,}|웃기|개그|유머|레전드|대박|미친|현웃', text):
            return 'humor'
            
        # 2. 질문 (물음표, ~가?, ~나요?, ~인가요?, 질문, 궁금)
        if re.search(r'\?|까\?|나요\?|가요\?|임\?|질문|궁금|알려|추천|좀', text):
            return 'question'
            
        # 3. 한탄/부정적 감정 (하.., ㅠㅠ, 망했, 짜증, 빡치, 시발, 병신)
        if re.search(r'[ㅠㅜ]{2,}|하\.\.|망했|짜증|빡치|시발|병신|좆|망함|에바', text):
            return 'complaint'
            
        # 4. 정보 공유/뉴스 (출시, 발표, 뉴스, 속보, 정보, 팁, 후기)
        if re.search(r'출시|발표|뉴스|속보|정보|팁|후기|리뷰|공개|업뎃|패치|요약', text):
            return 'news'
            
        # 5. 의견/토론 (생각, 개인적, 느낌, 의견, 토론, 논쟁, 이슈)
        if re.search(r'생각|개인적|느낌|의견|토론|이슈|방법|이유|분석|논리|팩트', text):
            return 'opinion'
            
        return 'general'

    def classify_keyword_type(self, keyword):
        """키워드 성격 분류 (추상어 vs 구체어) - 간단한 리스트 기반"""
        # 추상어/시공간/감정 목록
        abstract_words = {
            '새벽', '아침', '점심', '저녁', '밤', '오늘', '내일', '시간', 
            '기분', '느낌', '생각', '마음', '감성', '이유', '문제', 
            '상황', '상태', '결과', '시작', '끝', '하루', '주말', 
            '월요일', '금요일', '분위기', '트렌드', '인간', '사람',
            '사랑', '우정', '평화', '자유', '행복', '슬픔', '고통'
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
        
        # 1글자 키워드 필터링 (화이트리스트 제외)
        whitelist_1char = {'AI', 'C', 'R', '앱', '웹', '툴', '팁'} # AI는 2글자지만 혹시 몰라 포함
        keywords = [k for k in keywords if len(k) > 1 or k.upper() in whitelist_1char]
        
        # 트렌드 분석
        trending_topic = keywords[0] if keywords else None
        top_keyword = keywords[0] if keywords else "AI"
        
        return {
            'activity': activity,
            'keywords': keywords[:10],  # 상위 10개
            'trending_topic': trending_topic,
            'top_keyword': top_keyword,
            'dominant_intent': dominant_intent,
            'activity_level': self.get_activity_level(activity),
            'situation': self._infer_situation(activity, dominant_intent)
        }

    def _infer_situation(self, activity, intent):
        """상황 추론 (Rule-based Inference)"""
        if activity > 15:
            intensity = 'high'
        elif activity < 5:
            intensity = 'low'
        else:
            intensity = 'medium'
            
        return {
            'intensity': intensity,
            'mood': intent,
            'description': f"{intensity}_{intent}"
        }

    def analyze_comments(self, comments):
        """댓글 분위기 분석"""
        if not comments:
            return {'intent': 'neutral', 'keywords': []}
            
        text = ' '.join([c.get('content', '') for c in comments])
        intent = self.detect_intent(text)
        keywords = self.extract_keywords(text)
        
        return {
            'intent': intent,
            'keywords': keywords[:5]
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

    def extract_keywords_weighted(self, title, content, comments_text):
        """가중치 기반 키워드 추출 (제목 x3, 본문 x2, 댓글 x1)"""
        text_blobs = [
            (title, 3),      # Title: High weight
            (content, 2),    # Content: Medium weight
            (comments_text, 1) # Comments: Low weight (supportive)
        ]
        
        counter = Counter()
        
        for text, weight in text_blobs:
            if not text: continue
            
            # 명사 추출 및 점수 계산
            words = text.split()
            for word in words:
                word = re.sub(r'[^\w가-힣]', '', word) # 특수문자 제거
                
                # 조사 제거 (은/는/이/가/을/를 등)
                for josa in ['은', '는', '이', '가', '을', '를', '의', '에', '도', '로', '만', '과', '와']:
                    if word.endswith(josa):
                        word = word[:-1]
                        break
                        
                if len(word) < 2: continue
                if word in self.stopwords: continue
                
                # 사전 검증 (whitelist)
                if not KoreanDictionary.is_valid_noun(word): continue
                
                counter[word] += weight
                
        # 디버깅용 출력
        top_k = counter.most_common(5)
        if top_k:
             print(f"[Debug] 가중치 분석 결과: {top_k}")
             
        return [w for w, c in top_k]

    def extract_keywords(self, text):
        """(Legacy) 단순 빈도수 기반 추출"""
        return self.extract_keywords_weighted(text, "", "")
    
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
