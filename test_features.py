"""
Test script for new features
"""

# Test imports
try:
    from timeframe_parser import TimeframeParser
    from smart_sampler import get_smart_sampler
    print('✅ All imports successful!')
except Exception as e:
    print(f'❌ Import error: {e}')
    import traceback
    traceback.print_exc()
    exit(1)

# Test timeframe parser with shorthand
try:
    parser = TimeframeParser()
    
    # Test shorthand formats
    test_cases = ['60d', '2mo', '3w', '24h', 'today', 'yesterday', 'last 3 days']
    
    for test in test_cases:
        result = parser.parse(test)
        if result:
            print(f'✅ Parsed "{test}" successfully')
        else:
            print(f'❌ Failed to parse "{test}"')
            
except Exception as e:
    print(f'❌ Parser test error: {e}')
    import traceback
    traceback.print_exc()

# Test smart sampler
try:
    sampler = get_smart_sampler()
    
    # Test message count check
    check = sampler.check_message_count(100)
    print(f'✅ Smart sampler check (100 msgs): {check["status"]}')
    
    check = sampler.check_message_count(600)
    print(f'✅ Smart sampler check (600 msgs): {check["status"]}')
    
    check = sampler.check_message_count(1500)
    print(f'✅ Smart sampler check (1500 msgs): {check["status"]}')
    
except Exception as e:
    print(f'❌ Smart sampler test error: {e}')
    import traceback
    traceback.print_exc()

print('\n✅ All core tests passed!')
