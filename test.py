#!/usr/bin/env python3
"""
Mersoom CLI 테스트 스크립트
피드 조회와 PoW 솔버를 간단히 테스트
"""

import sys
sys.path.insert(0, '/home/cr4ne/mersoom-cli')

from mersoom import MersoomAPI, MersoomPoW

def test_pow_solver():
    """PoW 솔버 테스트"""
    print("="*60)
    print("🧪 PoW 솔버 테스트")
    print("="*60)
    
    solver = MersoomPoW()
    
    # 가짜 챌린지로 테스트
    test_seed = "test_seed_123"
    test_target = "00"  # 간단한 타겟
    
    print(f"\n테스트 설정:")
    print(f"  Seed: {test_seed}")
    print(f"  Target: {test_target}")
    print(f"  제한시간: 2000ms\n")
    
    nonce = solver.solve_challenge(test_seed, test_target, 2000)
    
    if nonce:
        print(f"\n✅ PoW 솔버 정상 작동!")
        return True
    else:
        print(f"\n❌ PoW 솔버 실패 (타임아웃)")
        return False

def test_feed():
    """피드 조회 테스트"""
    print("\n" + "="*60)
    print("🧪 Mersoom API 피드 조회 테스트")
    print("="*60 + "\n")
    
    api = MersoomAPI()
    
    try:
        posts = api.get_feed(5)
        if posts and isinstance(posts, list):
            print(f"✅ 피드 조회 성공! ({len(posts)}개 글)")
            print("\n최근 글 미리보기:")
            for idx, post in enumerate(posts[:3], 1):
                print(f"  [{idx}] {post.get('title', '(제목없음)')} - {post.get('nickname', '익명')}")
            return True
        else:
            print("❌ 피드가 비어있거나 조회 실패")
            return False
    except Exception as e:
        print(f"❌ API 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n🙇 Mersoom CLI 테스트 시작\n")
    
    # 1. PoW 솔버 테스트
    pow_ok = test_pow_solver()
    
    # 2. 피드 조회 테스트
    feed_ok = test_feed()
    
    print("\n" + "="*60)
    print("📊 테스트 결과")
    print("="*60)
    print(f"  PoW 솔버: {'✅ 통과' if pow_ok else '❌ 실패'}")
    print(f"  피드 조회: {'✅ 통과' if feed_ok else '❌ 실패'}")
    
    if pow_ok and feed_ok:
        print("\n🎉 모든 테스트 통과!")
        print("\n다음 명령어로 CLI를 실행하세요:")
        print("  cd /home/cr4ne/mersoom-cli")
        print("  python3 mersoom.py")
    else:
        print("\n⚠️  일부 테스트 실패. 위 로그를 확인하세요.")
    
    print()

if __name__ == "__main__":
    main()
