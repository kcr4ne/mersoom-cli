"""
머슴 자율 에이전트
Mersoom 플랫폼에서 자율적으로 활동하는 AI 에이전트
"""

import time
import random
from datetime import datetime
from mersoom import MersoomAPI
from modules.templates import MerseumTemplates, validate_eumseum
from modules.analyzer import FeedAnalyzer
from modules.news import NewsAggregator


class AutonomousAgent:
    """머슴 자율 에이전트"""
    
    def __init__(self, api_key):
        self.mersoom = MersoomAPI(api_key)
        self.templates = MerseumTemplates()
        self.analyzer = FeedAnalyzer()
        self.news = NewsAggregator()
        
        # 닉네임 선택 (한 번 선택하면 유지)
        self.nickname = self.templates.generate_nickname()
        
        # 속도 제한
        self.last_post_time = 0
        self.post_count = 0
        self.last_reset_time = time.time()
    
    def can_post(self):
        """글 작성 가능 여부 (30분에 2개)"""
        current_time = time.time()
        
        # 30분 경과 시 카운트 리셋
        if current_time - self.last_reset_time > 1800:  # 30분
            self.post_count = 0
            self.last_reset_time = current_time
        
        return self.post_count < 2
    
    def decide_action(self, feed_analysis):
        """행동 결정"""
        hour = datetime.now().hour
        activity = feed_analysis['activity']
        
        # 시간대별 행동 패턴
        if 2 <= hour < 6:
            # 새벽 - 조용히 활동
            return random.choices(
                ['read', 'comment'],
                weights=[75, 25],
                k=1
            )[0]
        elif 6 <= hour < 9:
            # 아침 - 활발
            return random.choices(
                ['post', 'comment', 'read'],
                weights=[40, 30, 30],
                k=1
            )[0]
        elif 9 <= hour < 18:
            # 낮 - 보통
            return random.choices(
                ['post', 'comment', 'vote', 'read'],
                weights=[20, 30, 20, 30],
                k=1
            )[0]
        elif 18 <= hour < 22:
            # 저녁 - 매우 활발
            return random.choices(
                ['post', 'comment', 'vote', 'read'],
                weights=[35, 35, 15, 15],
                k=1
            )[0]
        else:
            # 밤 - 활발
            return random.choices(
                ['post', 'comment', 'vote', 'read'],
                weights=[30, 30, 20, 20],
                k=1
            )[0]
    
    def create_post(self, feed_analysis):
        """게시글 작성"""
        if not self.can_post():
            print("[제한] 30분에 2개 제한 도달")
            return False
        
        is_doctor_roh = False  # 닥터 노 여부
        
        # 10% 확률로 뉴스 포스팅
        if random.random() < 0.1:
            # 닥터 노 확률 (5.23%)
            is_doctor_roh = random.random() < 0.0523
            
            headlines = self.news.fetch_headlines()
            if headlines:
                news_post = self.news.summarize_for_mersoom(headlines, is_doctor_roh=is_doctor_roh)
                if news_post:
                    title = news_post['title']
                    content = news_post['content']
                else:
                    return False
            else:
                return False
        else:
            # 일반 포스팅
            keyword = feed_analysis.get('top_keyword', 'AI')
            topic = feed_analysis.get('trending_topic', '머슴')
            
            # generate_title은 (제목, 닥터노 여부) 튜플 반환
            title, is_doctor_roh = self.templates.generate_title(keyword=keyword, topic=topic)
            content = self.templates.generate_content(keyword=keyword, topic=topic, is_doctor_roh=is_doctor_roh)
        
        # 음슴체 검증
        if not validate_eumseum(content):
            content += " 함"  # 강제 음슴체
        
        # 닥터 노일 경우 닉네임 강제 설정
        author = "닥터 노" if is_doctor_roh else self.nickname
        
        try:
            result = self.mersoom.create_post(
                nickname=author,
                title=title,
                content=content
            )
            
            self.post_count += 1
            self.last_post_time = time.time()
            
            print(f"[작성] {author}: {title}")
            return True
        except Exception as e:
            print(f"[오류] 글 작성 실패: {e}")
            return False
    
    def create_comment(self, feed_analysis):
        """댓글 작성"""
        try:
            # 최근 게시글 가져오기
            posts = self.mersoom.get_feed(limit=10)
            if not posts:
                return False
            
            # 랜덤 게시글 선택
            post = random.choice(posts)
            
            # 게시글 제목에서 닥터 노 여부 판단
            is_doctor_roh_post = "닥터 노" in post.get('title', '')
            
            # 게시글 내용에서 키워드 추출 (문맥 파악)
            post_text = f"{post.get('title', '')} {post.get('content', '')}"
            post_keywords = self.analyzer.extract_keywords(post_text)

            if post_keywords:
                # 게시글 관련 키워드 사용
                keyword = post_keywords[0]
                topic = post_keywords[1] if len(post_keywords) > 1 else '머슴'
                print(f"[분석] 문맥 파악: {keyword}, {topic} (from '{post.get('title', '')}')")
            else:
                keyword = feed_analysis.get('top_keyword', 'AI')
                topic = feed_analysis.get('trending_topic', '머슴')
            
            # 닥터 노 게시글이면 닥터 노 말투로 댓글 작성
            comment = self.templates.generate_comment(keyword=keyword, topic=topic, is_doctor_roh=is_doctor_roh_post)
            
            # 닥터 노 댓글은 음슴체 검증 불필요 (이미 특수 형식)
            if not is_doctor_roh_post and not validate_eumseum(comment):
                comment += " 함"
            
            # 닥터 노 게시글에 댓글 달 때는 닉네임도 "닥터 노"
            author = "닥터 노" if is_doctor_roh_post else self.nickname
            
            result = self.mersoom.create_comment(
                post_id=post['id'],
                nickname=author,
                content=comment
            )
            
            print(f"[댓글] {author}: {comment}")
            return True
        except Exception as e:
            print(f"[오류] 댓글 작성 실패: {e}")
            return False
    
    def run(self, interval=300):
        """메인 루프 (기본 5분 간격)"""
        print(f"=== 머슴 자율 에이전트 시작 ===")
        print(f"닉네임: {self.nickname}")
        print(f"간격: {interval}초")
        
        while True:
            try:
                # 피드 분석
                posts = self.mersoom.get_feed(limit=20)
                analysis = self.analyzer.analyze(posts)
                
                print(f"\n[분석] 활동량: {analysis['activity']}, 트렌드: {analysis['trending_topic']}")
                
                # 행동 결정
                action = self.decide_action(analysis)
                print(f"[행동] {action}")
                
                # 행동 실행
                if action == 'post':
                    self.create_post(analysis)
                elif action == 'comment':
                    self.create_comment(analysis)
                elif action == 'vote':
                    # TODO: 투표 기능
                    pass
                elif action == 'read':
                    print("[읽기] 피드 확인만 함")
                elif action == 'sleep':
                    print("[수면] 조용히 있음")
                
                # 대기
                wait_time = interval + random.randint(-60, 60)  # ±1분 랜덤
                print(f"[대기] {wait_time}초 후 다시 실행")
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                print("\n\n=== 에이전트 종료 ===")
                break
            except Exception as e:
                print(f"[오류] {e}")
                time.sleep(60)  # 오류 시 1분 대기


if __name__ == "__main__":
    import sys
    
    # Mersoom은 PoW만 필요하고 API 키가 필요 없음
    # AutonomousAgent 구조상 api_key 파라미터가 있지만 빈 문자열 전달
    api_key = ""
    
    agent = AutonomousAgent(api_key)
    agent.run(interval=300)  # 5분 간격
