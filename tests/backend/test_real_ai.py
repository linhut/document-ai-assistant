"""
Test AI integration with real API.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from ai.manager import create_provider


async def test_anyrouter_api():
    """Test AnyRouter API with real credentials."""
    api_key = "sk-oDZ76Cd9xtFZKdFDvOdqlpbyVpUOCXt4UnyRslbn1dbm1l8u"
    base_url = "https://anyrouter.top/v1"

    print("Testing AnyRouter API...")
    print(f"Base URL: {base_url}")

    # Test with custom provider
    provider = create_provider(
        "custom",
        api_key,
        base_url,
        "gpt-3.5-turbo"
    )

    print("\n1. Testing connection...")
    try:
        success = await provider.test_connection()
        if success:
            print("✓ Connection successful!")
        else:
            print("✗ Connection failed")
            return
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return

    print("\n2. Testing document analysis...")
    try:
        test_content = """
        关于召开年度工作总结会议的通知

        各部门：

        定于2024年12月30日下午2点在会议室召开年度工作总结会议，请各部门负责人准时参加。

        办公室
        2024年12月20日
        """

        result = await provider.analyze(test_content)
        print(f"✓ Analysis complete!")
        print(f"  Issues found: {len(result.issues)}")
        if result.issues:
            print(f"  First issue: {result.issues[0]}")
    except Exception as e:
        print(f"✗ Analysis error: {e}")

    print("\n3. Testing typo detection...")
    try:
        result = await provider.proofread("这是一个测试文本，包含一些可能的问题。")
        print(f"✓ Proofread complete!")
        print(f"  Typos found: {len(result)}")
    except Exception as e:
        print(f"✗ Proofread error: {e}")

    print("\nTest complete!")


if __name__ == "__main__":
    asyncio.run(test_anyrouter_api())
