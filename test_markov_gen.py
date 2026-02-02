
import sys
import os

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.templates import MerseumTemplates, MolecularBuilder, JosaFormatter

print("=== Markov Chain Test ===")
templates = MerseumTemplates()
builder = MolecularBuilder()

test_cases = [
    ('AI', '머슴'),
    ('GPT', '기술'),
    ('주인', '갑질'),
    ('개발자', '야근')
]

for kw, topic in test_cases:
    print(f"\n[Keyword: {kw}, Topic: {topic}]")
    for _ in range(3):
        try:
            # 직접 호출 테스트
            chain_result = MolecularBuilder.generate_chain(kw, topic)
            print(f"Chain: {chain_result}")
            
            # 통합 호출 테스트
            comment = templates.generate_comment(kw, topic, context={'intensity': 'high'})
            print(f"Integrated(High): {comment}")
            
        except Exception as e:
            print(f"[ERROR] {e}")
            sys.exit(1)

print("\n=== Test Passed Successfully ===")
