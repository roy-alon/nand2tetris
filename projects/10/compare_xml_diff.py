"""
XML Comparison Tool with Diff - Compares *Cmp.xml files with *.xml files
Ignores whitespace and indentation differences
Shows detailed diffs for mismatches
"""

import os
import re
from pathlib import Path
from typing import Tuple, List
from difflib import unified_diff


def normalize_xml(xml_content: str) -> str:
    """
    Normalize XML by removing excess whitespace and indentation.
    Preserves only meaningful content.
    """
    # Remove leading/trailing whitespace
    xml_content = xml_content.strip()
    
    # Remove newlines and extra spaces between tags
    # This regex removes all whitespace between > and <
    xml_content = re.sub(r'>\s+<', '><', xml_content)
    
    # Remove leading/trailing whitespace inside tags (but not in text content)
    # Match tags and remove spaces around content
    xml_content = re.sub(r'<(\w+)>\s+', r'<\1>', xml_content)
    xml_content = re.sub(r'\s+</(\w+)>', r'</\1>', xml_content)
    
    return xml_content


def read_xml_file(filepath: str) -> str:
    """Read and normalize XML file content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return normalize_xml(f.read())
    except Exception as e:
        return f"ERROR: {e}"


def read_xml_file_pretty(filepath: str) -> List[str]:
    """Read XML file with pretty formatting for display."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception as e:
        return [f"ERROR: {e}"]


def compare_xml_files(cmp_file: str, xml_file: str) -> Tuple[bool, str, str, str]:
    """
    Compare two XML files ignoring whitespace.
    Returns (match: bool, message: str, cmp_content: str, xml_content: str)
    """
    if not os.path.exists(xml_file):
        return False, f"Missing: {xml_file}", "", ""
    
    cmp_content = read_xml_file(cmp_file)
    xml_content = read_xml_file(xml_file)
    
    if "ERROR:" in cmp_content:
        return False, cmp_content, "", ""
    if "ERROR:" in xml_content:
        return False, xml_content, "", ""
    
    if cmp_content == xml_content:
        return True, "✓ Match", cmp_content, xml_content
    else:
        return False, "✗ Content differs", cmp_content, xml_content


def find_and_compare_xml_files(root_dir: str) -> List[Tuple[str, bool, str, str, str]]:
    """
    Find all *Cmp.xml files and compare them with *.xml files.
    Returns list of (filepath, match_status, message, cmp_content, xml_content)
    """
    results = []
    
    root_path = Path(root_dir)
    
    # Find all *Cmp.xml files
    for cmp_file in sorted(root_path.rglob('*Cmp.xml')):
        # Get the corresponding *.xml file
        base_path = str(cmp_file).replace('Cmp.xml', '.xml')
        
        match, message, cmp_content, xml_content = compare_xml_files(str(cmp_file), base_path)
        results.append((str(cmp_file), match, message, cmp_content, xml_content))
    
    return results


def show_diff(cmp_file: str, xml_file: str) -> None:
    """Show side-by-side diff of mismatched files."""
    print(f"\nDetailed comparison:")
    print(f"  Expected (Cmp): {cmp_file}")
    print(f"  Generated:      {xml_file}")
    print("\nShowing first difference (normalized XML):\n")
    
    cmp_content = read_xml_file(cmp_file)
    xml_content = read_xml_file(xml_file)
    
    # Find first difference position
    for i, (c1, c2) in enumerate(zip(cmp_content, xml_content)):
        if c1 != c2:
            # Show context around the difference
            start = max(0, i - 50)
            end = min(len(cmp_content), i + 50)
            print(f"First difference at position {i}:")
            print(f"  Expected: ...{cmp_content[start:end]}...")
            print(f"  Got:      ...{xml_content[start:end]}...")
            break
    
    if len(cmp_content) != len(xml_content):
        print(f"\nContent length differs:")
        print(f"  Expected: {len(cmp_content)} characters")
        print(f"  Got:      {len(xml_content)} characters")


def print_report(results: List[Tuple[str, bool, str, str, str]], show_diffs: bool = False) -> None:
    """Print a formatted comparison report."""
    if not results:
        print("No *Cmp.xml files found.")
        return
    
    print("=" * 80)
    print("XML Comparison Report")
    print("=" * 80)
    
    matches = 0
    mismatches = 0
    
    for filepath, match, message, cmp_content, xml_content in results:
        status = "✓ PASS" if match else "✗ FAIL"
        print(f"\n{status}: {filepath}")
        print(f"  {message}")
        
        if match:
            matches += 1
        else:
            mismatches += 1
            if show_diffs:
                base_path = filepath.replace('Cmp.xml', '.xml')
                show_diff(filepath, base_path)
    
    print("\n" + "=" * 80)
    print(f"Summary: {matches} passed, {mismatches} failed (Total: {len(results)})")
    print("=" * 80)
    
    if mismatches == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {mismatches} test(s) failed.")


if __name__ == "__main__":
    import sys
    
    # Use current directory or argument
    root_directory = sys.argv[1] if len(sys.argv) > 1 else "."
    show_diffs = "--diff" in sys.argv or "-d" in sys.argv
    
    print(f"Scanning directory: {root_directory}")
    results = find_and_compare_xml_files(root_directory)
    print_report(results, show_diffs=show_diffs)
