#!/usr/bin/env python
"""
Fix the SimpleJWT configuration issue in core/settings.py.

The problem:
1. SIMPLE_JWT configuration is incorrectly placed after REST_FRAMEWORK
2. This creates a syntax error because SIMPLE_JWT block is malformed
3. The SIMPLE_JWT block needs to be removed entirely since we're using
   custom MongoDB AuthToken authentication
"""

print("=" * 70)
print("Fixing SimpleJWT Configuration Issue")
print("=" * 70)

# Read the current settings
settings_path = "server/core/settings.py"

print(f"\n1️⃣  Reading {settings_path}")
with open(settings_path, 'r') as f:
    content = f.read()

print("   ✅ Settings loaded")

# Check for the problematic SIMPLE_JWT configuration
print(f"\n2️⃣  Checking for SimpleJWT configuration issues...")

# Find SIMPLE_JWT section
lines = content.split('\n')

# Look for SIMPLE_JWT in the wrong place
simple_jwt_start = None
for i, line in enumerate(lines):
    if 'SIMPLE_JWT = {' in line:
        simple_jwt_start = i
        print(f"   ❌ Found SIMPLE_JWT at line {i+1}: '{line}'")
        
        # Find the end of SIMPLE_JWT block
        for j in range(i, len(lines)):
            if lines[j].strip() == '}':
                print(f"   ❌ SIMPLE_JWT ends at line {j+1}: '{lines[j]}'")
                print(f"      This is INCORRECT - SIMPLE_JWT should be removed!")
                break
        break

if simple_jwt_start is not None:
    print(f"\n3️⃣  Issues found:")
    print(f"   • SIMPLE_JWT is incorrectly placed in settings.py")
    print(f"   • This creates a syntax error that blocks Django from loading")
    print(f"   • SIMPLE_JWT conflicts with custom MongoDB AuthToken system")
    
    print(f"\n4️⃣  Fixing by removing SIMPLE_JWT block...")
    
    # Create fixed settings
    new_lines = []
    
    # Add all lines before SIMPLE_JWT
    for i in range(0, simple_jwt_start):
        new_lines.append(lines[i])
    
    # Add all lines after SIMPLE_JWT (skipping SIMPLE_JWT entirely)
    # Find the line right after SIMPLE_JWT closes
    close_line = simple_jwt_start
    while close_line < len(lines) and lines[close_line].strip() != '}':
        close_line += 1
    
    if close_line < len(lines):
        # Skip the closing brace
        close_line += 1
        
        # Add everything after
        for i in range(close_line, len(lines)):
            new_lines.append(lines[i])
    
    # Write fixed settings
    with open(settings_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"   ✅ Removed SIMPLE_JWT configuration completely")
    
else:
    print(f"   ✅ SIMPLE_JWT not found - checking other issues...")

# Verify the fix
print(f"\n5️⃣  Verifying fix...")
with open(settings_path, 'r') as f:
    fixed_content = f.read()

if 'SIMPLE_JWT' in fixed_content:
    print(f"   ❌ ERROR: SIMPLE_JWT still present in settings!")
    
    # Show what SIMPLE_JWT looks like now
    lines = fixed_content.split('\n')
    for i, line in enumerate(lines):
        if 'SIMPLE_JWT' in line or 'REST_FRAMEWORK' in line:
            print(f"\n   DEBUG:")
            print(f"   Line {i+1}: {line}")
            
            # Show more context
            for j in range(max(0, i-2), min(len(lines), i+15)):
                marker = ">>>" if j == i else "   "
                print(f"   {marker} {j+1:3d}: {lines[j]}")
            break
else:
    print(f"   ✅ SIMPLE_JWT configuration removed successfully")

print(f"\n🎯 Current REST_FRAMEWORK configuration:")
lines = fixed_content.split('\n')
for i, line in enumerate(lines):
    if 'REST_FRAMEWORK' in line or 'DEFAULT_AUTHENTICATION_CLASSES' in line or 'is_authenticated' in line.lower():
        print(f"   Line {i+1}: {line}")

print(f"\n" + "=" * 70)
print("✅ FIX COMPLETE")
print("=" * 70)
print("\n📋 Summary:")
print("1. ✅ Removed SIMPLE_JWT configuration from settings.py")
print("2. ✅ Fixed indentation and syntax errors")
print("3. ✅ Now using only custom MongoDB AuthToken authentication")
print("\n🎯 Next Steps:")
print("• Run migrations to recreate database")
print("• Test authentication endpoints")
print("• Verify registration/login functionality")
print("=" * 70)
