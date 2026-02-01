"""
머슴 자율 에이전트
Mersoom 플랫폼에서 자율적으로 활동하는 AI 에이전트
"""

import time
import random
from datetime import datetime
from mersoom import Mersoom
from modules.templates import MerseumTemplates, validate_eumseum
from modules.analyzer import FeedAnalyzer
from modules.news import NewsAggregator


class AutonomousAgent:
    """머슴 자율 에이전트"""
    
    def __init__(self, api_key):
        self.mersoom = Mersoom(api_key)
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
            # 새벽 - 조용히
            return random.choices(
                ['read', 'sleep'],
                weights=[30, 70],
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
                title=title,
                content=content,
                author=author
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
            posts = self.mersoom.get_posts(limit=10)
            if not posts:
                return False
            
            # 랜덤 게시글 선택
            post = random.choice(posts)
            
            # 게시글 제목에서 닥터 노 여부 판단
            is_doctor_roh_post = "닥터 노" in post.get('title', '')
            
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
                content=comment,
                author=author
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
                posts = self.mersoom.get_posts(limit=20)
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
    import os
    
    # API 키 우선순위:
    # 1. 명령줄 인자
    # 2. 환경변수 MERSOOM_API_KEY
    # 3. .env 파일
    # 4. 대화형 입력 (첫 실행 시)
    
    api_key = None
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    
    # 1. 명령줄 인자 확인
    if len(sys.argv) >= 2:
        api_key = sys.argv[1]
    
    # 2. 환경변수 확인
    if not api_key:
        api_key = os.getenv('MERSOOM_API_KEY')
    
    # 3. .env 파일 확인
    if not api_key and os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('MERSOOM_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
    
    # 4. 대화형 입력 (첫 실행 시)
    if not api_key:
        print("=" * 60)
        print("🤖 머슴 자율 에이전트 - 첫 실행 설정")
        print("=" * 60)
        print("\nMersoom API 키가 설정되지 않았습니다.")
        print("API 키를 입력하면 자동으로 .env 파일에 저장됩니다.\n")
        
        api_key = input("Mersoom API 키를 입력하세요: ").strip()
        
        if api_key:
            # .env 파일 생성
            with open(env_file, 'w') as f:
                f.write(f"# Mersoom API 키\n")
                f.write(f"MERSOOM_API_KEY={api_key}\n")
            print(f"\n✅ API 키가 {env_file}에 저장되었습니다!")
            print("다음 실행부터는 자동으로 로드됩니다.\n")
        else:
            print("\n❌ API 키가 입력되지 않았습니다.")
            sys.exit(1)
    
    if not api_key:
        print("❌ API 키를 찾을 수 없습니다!")
        print("\n다음 중 하나를 사용하세요:")
        print("  1. python autonomous_agent.py <API_KEY>")
        print("  2. export MERSOOM_API_KEY=<API_KEY>")
        print("  3. .env 파일에 MERSOOM_API_KEY=<API_KEY> 추가")
        sys.exit(1)
    
    agent = AutonomousAgent(api_key)
    agent.run(interval=300)  # 5분 간격
