#!/usr/bin/env python3
"""
Test script for Video Templates
"""

from app.services.video_templates import get_template_manager, get_template

def test_templates():
    """Test the video template system"""
    try:
        print("🎬 Testing Video Template System...")
        
        # Get template manager
        tm = get_template_manager()
        print(f"✅ Template Manager loaded with {len(tm.get_all_templates())} templates")
        
        # Test getting all templates
        all_templates = tm.get_all_templates()
        print("\n📋 Available Templates:")
        for name, template in all_templates.items():
            print(f"  • {template.name} ({template.category})")
            print(f"    {template.description}")
        
        # Test getting specific template
        business_template = get_template("business")
        if business_template:
            print(f"\n✅ Business Template loaded:")
            print(f"  Name: {business_template.name}")
            print(f"  Category: {business_template.category}")
            print(f"  Resolution: {business_template.settings.get('resolution', 'N/A')}")
            print(f"  Colors: {business_template.color_scheme}")
            print(f"  Visual Elements: {len(business_template.visual_elements)}")
        
        # Test template categories
        business_templates = tm.get_templates_by_category("Business")
        print(f"\n📊 Business Category Templates: {len(business_templates)}")
        
        # Test template info
        template_info = tm.get_template_info("educational")
        if template_info:
            print(f"\n📝 Educational Template Info:")
            print(f"  Typography: {template_info['typography']}")
            print(f"  Transitions: {template_info['transitions']}")
        
        print("\n🎉 Video Template System Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Video Template System Test FAILED: {e}")
        return False

if __name__ == "__main__":
    test_templates()
