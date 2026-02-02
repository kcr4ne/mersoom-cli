"""
머슴 자율 에이전트
Mersoom 플랫폼에서 자율적으로 활동하는 AI 에이전트
"""

import time
import random
import re
from datetime import datetime
from mersoom import MersoomAPI
from modules.templates import MerseumTemplates, validate_eumseum
from modules.analyzer import FeedAnalyzer
from modules.news import NewsAggregator


class AutonomousAgent:
    """머슴 자율 에이전트"""
    
    def __init__(self, api_key, dry_run=False):
        self.dry_run = dry_run
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
            # 트렌드 다양화: Top 5 키워드 중 랜덤 선택 (가중치 부여는 단순 랜덤으로 대체)
            top_keywords = feed_analysis.get('keywords', [])[:5]
            if top_keywords:
                keyword = random.choice(top_keywords)
            else:
                keyword = feed_analysis.get('top_keyword') or 'AI'
                
            topic = feed_analysis.get('trending_topic') or '머슴'
            dominant_intent = feed_analysis.get('dominant_intent', 'general')
            
            print(f"[분석] 포스팅 주제: {keyword}, {topic}, 의도: {dominant_intent}")
            
            # generate_title은 (제목, 닥터노 여부) 튜플 반환
            title, is_doctor_roh = self.templates.generate_title(
                keyword=keyword, 
                topic=topic,
                intent=dominant_intent
            )
            content = self.templates.generate_content(
                keyword=keyword, 
                topic=topic, 
                is_doctor_roh=is_doctor_roh,
                intent=dominant_intent
            )
        
        # 음슴체 검증 (닥터 노 제외)
        if not is_doctor_roh and not validate_eumseum(content):
            content += " 함"  # 강제 음슴체
        
        # 닥터 노일 경우 닉네임 강제 설정
        author = "닥터 노" if is_doctor_roh else self.nickname
        
        try:
            if self.dry_run:
                print(f"[TEST] 글 작성 시뮬레이션: {author}: {title}")
                print(f"[TEST] 내용: {content}")
                self.post_count += 1
                self.last_post_time = time.time()
                return True

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
            # 4. 심층 분석: 댓글 여론 파악 (Deep Analysis)
            # 댓글 가져오기 (문맥 파악용)
            try:
                comments = self.mersoom.get_comments(post['id'])
            except Exception as e:
                print(f"[ERROR] 댓글 가져오기 실패: {e}")
                comments = []
                
            comments_text = " ".join([c.get('content', '') for c in comments])
            
            # 게시글 자체의 의도 파악
            full_context_text = f"{post.get('title', '')} {post.get('content', '')} {comments_text}"
            title_intent = self.analyzer.detect_intent(full_context_text)
            
            # (기존 댓글 분석 로직 통합)
            if comments:
                 comment_analysis = self.analyzer.analyze_comments(comments)
                 comment_intent = comment_analysis['intent']
            else:
                 comment_intent = 'neutral'
            
            # 의도 융합 (Fusion)
            # 댓글 분위기가 압도적(분노/유머)이면 댓글 분위기를 따름
            if comment_intent in ['complaint', 'humor']:
                final_intent = comment_intent
                print(f"[분석] 댓글 분위기({comment_intent})가 지배적임 -> 의도 변경")
            else:
                final_intent = title_intent
                
            # 전체 텍스트에서 키워드 추출 (게시글 + 댓글)
            # 가중치 적용: 제목(x3) > 본문(x2) > 댓글(x1)
            comments_text = " ".join([c.get('content', '') for c in comments])
            post_keywords = self.analyzer.extract_keywords_weighted(
                title=post.get('title', ''), 
                content=post.get('content', ''), 
                comments_text=comments_text
            )

            # 키워드가 없는 경우 스킵 (User Request: "없으면 댓글 작성 안하면 됨")
            if not post_keywords:
                print(f"[스킵] '{post.get('title')}' 글에서 키워드 추출 실패 -> 댓글 작성 안함")
                return False

            keyword = post_keywords[0]
            topic = post_keywords[1] if len(post_keywords) > 1 else '머슴'
            
            keyword_type = self.analyzer.classify_keyword_type(keyword)
            
            print(f"[분석] 심층 파악 완료: {keyword}({keyword_type}), 의도: {final_intent} (Title: {title_intent}, Comments: {comment_intent})")

            # 닥터 노 게시글이면 닥터 노 말투로 댓글 작성
            comment = self.templates.generate_comment(
                keyword=keyword, 
                topic=topic, 
                is_doctor_roh=is_doctor_roh_post,
                intent=final_intent,
                keyword_type=keyword_type,
                context=feed_analysis.get('situation') # MolecularBuilder를 위한 컨텍스트 주입
            )
            
            # 닥터 노 댓글은 음슴체 검증 불필요 (이미 특수 형식)
            if not is_doctor_roh_post and not validate_eumseum(comment):
                comment += " 함"
            
            # 닥터 노 게시글에 댓글 달 때는 닉네임도 "닥터 노"
            author = "닥터 노" if is_doctor_roh_post else self.nickname
            
            if self.dry_run:
                print(f"[TEST] 댓글 작성 시뮬레이션 (Post {post['id']})")
                print(f"[TEST] 대상 글: {post.get('title', '제목없음')}")
                print(f"[TEST] {author}: {comment}")
                return True

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
                # 피드 분석 (Deep Trend Analysis)
                print("[분석] 피드 및 댓글 심층 분석 중... (약 5-10초 소요)")
                posts = self.mersoom.get_feed(limit=20)
                
                if not posts:
                    print("[오류] 피드 가져오기 실패 (None 반환)")
                    time.sleep(60)
                    continue

                # 댓글까지 싹 긁어오기 (User Request: "제목, 내용, 댓글 확인하면서 트렌드 결정")
                full_context_posts = []
                for post in posts:
                    # 댓글 가져오기
                    # 댓글 가져오기 (API 부하 방지를 위해 1초 대기)
                    try:
                        time.sleep(1.0)
                        comments = self.mersoom.get_comments(post['id'])
                    except Exception as e:
                        print(f"[ERROR] 댓글 가져오기 실패 ({post['id']}): {e}")
                        comments = []
                    
                    if comments:
                         post['comments_text'] = ' '.join([c.get('content', '') for c in comments])
                    else:
                         post['comments_text'] = ''
                    
                    # 제목 + 내용 + 댓글을 모두 합쳐서 분석용 텍스트 생성
                    post['full_text'] = f"{post.get('title', '')} {post.get('content', '')} {post['comments_text']}"
                    full_context_posts.append(post)
                
                # 분석기에 'full_text'를 우선적으로 보라고 개조는 안 했으니,
                # analyzer.analyze는 여전히 title/content만 봅니다.
                # 따라서 analyzer의 extract_keywords를 직접 호출해서 '진짜 트렌드'를 덮어씌웁니다.
                
                # 1. 기존 분석 (활동량 등)
                analysis = self.analyzer.analyze(posts)
                
                # 2. 심층 트렌드 분석 (Override)
                all_text_blobs = ' '.join([p['full_text'] for p in full_context_posts])
                deep_keywords = self.analyzer.extract_keywords(all_text_blobs)
                
                # 키워드 필터링 (1글자 제외 등은 extract_keywords에 이미 포함됨)
                if deep_keywords:
                    analysis['keywords'] = deep_keywords[:10]
                    analysis['top_keyword'] = deep_keywords[0]
                    analysis['trending_topic'] = deep_keywords[0]
                    print(f"[분석] Deep Trend 발견: {analysis['top_keyword']} (기반: 게시글 20개 + 댓글 전체)")
                else:
                     print("[분석] 뚜렷한 트렌드 없음. 기본값 유지.")
                     analysis['top_keyword'] = "None"
                
                print(f"\n[분석] 활동량: {analysis['activity']}, 트렌드: {analysis['trending_topic']}")
                
                # ==========================================
                # V2 Feature: Auto-Vote (자동 투표)
                # ==========================================
                # 트렌드와 일치하거나(Tech/Life) 고품질 글에 투표
                voted = False
                for post in posts[:3]: # 상위 3개만 검사
                    title = post.get('title', '')
                    content = post.get('content', '')
                    post_text = title + " " + content
                    
                    # 1. Tech/Life 카테고리고 길이가 적당하면 '개추'
                    keyword_for_check = self.analyzer.extract_keywords(post_text)
                    if not keyword_for_check: continue
                    
                    category = self.templates.classify_category(keyword_for_check[0])
                    if category in ['tech', 'life'] and len(content) > 20:
                        print(f"[투표] '{title}' 글이 {category} 주제라 맘에 듦 -> 개추 시도")
                        if self.dry_run:
                            print(f"[TEST] 투표 시뮬레이션: 개추 (Post {post['id']})")
                            voted = True
                            break

                        try:
                            if self.mersoom.vote(post['id'], 'up'):
                                voted = True
                                time.sleep(2)
                                break # 한 턴에 하나만 투표
                        except Exception as e:
                            print(f"[ERROR] 투표 중 오류 발생: {e}")
                            time.sleep(5)
                            break
                
                if not voted:
                    # 3. 규칙 위반자 처벌 (The Punisher)
                    # 이모지, 마크다운, 존댓말 사용 감지
                    for post in posts[:5]:
                        check_text = post.get('title', '') + " " + post.get('content', '')
                        
                        # 이모지 감지 (단, 자모음 ㅋ,ㅎ,ㅠ,ㅜ 제외)
                        # 간단하게 주요 이모지 범위만 체크
                        emoji_pattern = r'[😀-🙏]' 
                        markdown_pattern = r'\*\*|##|__|```'
                        polite_pattern = r'요\.|요$|습니다|입니다'
                        
                        violation_reason = ""
                        if re.search(emoji_pattern, check_text):
                            violation_reason = "이모지 사용"
                        elif re.search(markdown_pattern, check_text):
                            violation_reason = "마크다운 사용"
                        elif re.search(polite_pattern, check_text):
                            violation_reason = "존댓말(비음슴체) 사용"
                            
                        if violation_reason:
                             print(f"[처벌] '{post.get('title')}' 글이 규칙 위반({violation_reason}) -> 비추 시도")
                             
                             if self.dry_run:
                                 print(f"[TEST] 처벌 시뮬레이션: 비추 (Post {post['id']})")
                                 break

                             try:
                                 if self.mersoom.vote(post['id'], 'down'):
                                     time.sleep(2)
                                     break
                             except Exception as e:
                                 print(f"[ERROR] 투표 중 오류 발생: {e}")
                                 time.sleep(5)
                                 break
                        
                        # 4. 쓰레기 글(너무 짧음) 비추
                        if len(post.get('content', '')) < 5 and '망고' not in post.get('title', ''):
                             if random.random() < 0.5:
                                 print(f"[투표] '{post.get('title')}' 글이 너무 성의 없음 -> 비추 시도")

                                 if self.dry_run:
                                     print(f"[TEST] 투표 시뮬레이션: 비추 (Post {post['id']})")
                                     break

                                 try:
                                     if self.mersoom.vote(post['id'], 'down'):
                                         time.sleep(2)
                                         break
                                 except Exception as e:
                                     print(f"[ERROR] 투표 중 오류 발생: {e}")
                                     time.sleep(5)
                                     break

                # ==========================================
                # 행동 결정
                # ==========================================
                # ==========================================
                # 행동 결정 (Multi-Tasking)
                # ==========================================
                situation = analysis.get('situation', {})
                intensity = situation.get('intensity', 'medium')
                
                # 상황에 따른 행동 플랜 수립
                actions = []
                
                if intensity == 'high':
                    # 혼잡: 댓글 위주지만 가끔 글도 씀
                    if random.random() < 0.2:
                        actions = ['post', 'comment'] # 글쓰고 댓글달기
                        print(f"[플랜] 혼잡 상황(High) -> 틈새시장 공략 (글작성+댓글)")
                    else:
                        actions = ['comment', 'comment', 'read']
                        print(f"[플랜] 혼잡 상황(High) -> 다중 행동 개시 (댓글x2 + 읽기)")
                elif intensity == 'low':
                    # 정적: 게시글 작성 (장작 넣기) or 읽기
                    actions = ['post'] if random.random() < 0.7 else ['read', 'read']
                    print(f"[플랜] 정적 상황(Low) -> 장작 넣기 시도")
                else:
                    # 보통: 기본 행동 1개
                    base_action = self.decide_action(analysis)
                    actions = [base_action]
                    # 간헐적으로 2연타
                    if random.random() < 0.3:
                        actions.append('read')
                
                print(f"[행동] 실행 계획: {actions}")
                
                # 행동 루프 실행
                for action in actions:
                    if action == 'post':
                        self.create_post(analysis)
                    elif action == 'comment':
                        self.create_comment(analysis)
                    elif action == 'read':
                        print("[읽기] 피드 모니터링 중...")
                    elif action == 'sleep':
                        print("[수면] 대기 모드")
                    
                    # 다중 행동 사이 딜레이 (429 방지)
                    time.sleep(random.uniform(2, 5))
                
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Mersoom Autonomous Agent')
    parser.add_argument('--dry-run', action='store_true', help='실제 API 호출 없이 테스트 실행')
    args = parser.parse_args()
    
    # Mersoom은 PoW만 필요하고 API 키가 필요 없음
    # AutonomousAgent 구조상 api_key 파라미터가 있지만 빈 문자열 전달
    api_key = ""
    
    agent = AutonomousAgent(api_key, dry_run=args.dry_run)
    
    if args.dry_run:
        print("=== [TEST MODE] API 호출이 비활성화되었습니다 ===")
        
    agent.run(interval=300)  # 5분 간격
