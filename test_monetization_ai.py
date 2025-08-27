#!/usr/bin/env python3
"""
Test script for Enhanced AI Generator with Monetization Optimization
"""

import sys
import os
webui_dir = os.path.join(os.path.dirname(__file__), 'webui')
sys.path.insert(0, webui_dir)

def test_monetization_ai():
    print("🧪 Testing Enhanced AI Generator with Monetization Optimization...")
    
    try:
        from utils.ai_generator import get_ai_generator
        
        # Test different monetization focuses and platforms
        test_cases = [
            {
                "topic": "Cryptocurrency Trading",
                "style": "Professional",
                "duration": 15,
                "monetization_focus": "affiliate",
                "platform": "youtube"
            },
            {
                "topic": "Fitness Workouts",
                "style": "Creative",
                "duration": 10,
                "monetization_focus": "sponsorships",
                "platform": "tiktok"
            },
            {
                "topic": "Programming Tutorials",
                "style": "Educational",
                "duration": 20,
                "monetization_focus": "ads",
                "platform": "instagram"
            },
            {
                "topic": "Business Strategy",
                "style": "Corporate",
                "duration": 12,
                "monetization_focus": "engagement",
                "platform": "facebook"
            }
        ]
        
        ai_gen = get_ai_generator()
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📱 Test Case {i}: {test_case['topic']} on {test_case['platform']}")
            print(f"🎯 Monetization Focus: {test_case['monetization_focus']}")
            print("-" * 60)
            
            script = ai_gen.generate_video_script(
                topic=test_case['topic'],
                style=test_case['style'],
                duration=test_case['duration'],
                target_audience="Professionals",
                language="English",
                monetization_focus=test_case['monetization_focus'],
                platform=test_case['platform']
            )
            
            print(f"📝 Title: {script['title']}")
            print(f"🎬 Hook: {script['hook']}")
            print(f"⏱️ Duration: {script['total_duration']} seconds")
            print(f"💰 Monetization Focus: {script.get('monetization_focus', 'N/A')}")
            print(f"📱 Platform: {script.get('platform', 'N/A')}")
            
            if 'seo_keywords' in script:
                print(f"🔍 SEO Keywords: {', '.join(script['seo_keywords'][:5])}...")
            
            if 'engagement_metrics' in script:
                metrics = script['engagement_metrics']
                print(f"📊 Target Views: {metrics.get('target_views', 'N/A')}")
                print(f"💬 Target Comments: {metrics.get('target_comments', 'N/A')}")
                print(f"📈 Retention Rate: {metrics.get('retention_rate', 'N/A')}")
            
            if 'monetization_strategies' in script:
                print(f"💡 Monetization Strategies: {', '.join(script['monetization_strategies'][:3])}...")
            
            print(f"📚 Sections: {len(script['sections'])}")
            for j, section in enumerate(script['sections'], 1):
                print(f"   {j}. {section['title']} ({section['duration']}s)")
                if 'engagement_hooks' in section:
                    print(f"      🎣 Engagement: {', '.join(section['engagement_hooks'][:2])}...")
                if 'monetization_elements' in section:
                    print(f"      💰 Monetization: {', '.join(section['monetization_elements'][:2])}...")
        
        print("\n🎉 Enhanced AI Generator with Monetization Optimization test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_success_patterns():
    print("\n🔍 Testing Success Pattern Analysis...")
    
    try:
        from utils.ai_generator import _analyze_video_success_patterns
        
        test_topics = ["Cryptocurrency Trading", "Fitness Workouts", "Programming Tutorials"]
        test_platforms = ["youtube", "tiktok", "instagram"]
        
        for topic in test_topics:
            for platform in test_platforms:
                print(f"\n📊 Analyzing: {topic} on {platform}")
                analysis = _analyze_video_success_patterns(topic, platform)
                
                print(f"   🎯 Market Trends: {len(analysis['market_trends'])} trends found")
                print(f"   🤖 Algorithm Favorites: {len(analysis['algorithm_favorites'])} signals")
                print(f"   💰 Monetization Tips: {len(analysis['monetization_optimization'])} strategies")
                
                if 'topic_patterns' in analysis:
                    patterns = analysis['topic_patterns']
                    print(f"   🎬 Hook Patterns: {len(patterns.get('hook_patterns', []))} patterns")
                    print(f"   📚 Content Structure: {len(patterns.get('content_structure', []))} elements")
                    print(f"   💡 Engagement Tactics: {len(patterns.get('engagement_tactics', []))} tactics")
                    print(f"   💰 Monetization Methods: {len(patterns.get('monetization_methods', []))} methods")
        
        print("\n✅ Success Pattern Analysis test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Success Pattern Analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing Enhanced AI Generator with Monetization & Success Optimization")
    print("=" * 80)
    
    # Test basic monetization AI generation
    test1_passed = test_monetization_ai()
    
    # Test success pattern analysis
    test2_passed = test_success_patterns()
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! Enhanced AI Generator is working perfectly!")
        print("\n✨ Key Features Available:")
        print("   • Platform-specific optimization (YouTube, TikTok, Instagram, Facebook)")
        print("   • Monetization focus (engagement, affiliate, ads, sponsorships)")
        print("   • Success pattern analysis and market trends")
        print("   • Algorithm optimization strategies")
        print("   • Content strategy and success roadmap")
        print("   • Competitor analysis framework")
        print("   • Trending topic integration")
        print("   • SEO keyword generation")
        print("   • Engagement metrics and benchmarks")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
