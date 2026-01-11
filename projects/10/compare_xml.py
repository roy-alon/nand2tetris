"""
XML Comparison Tool - Compares *Cmp.xml files with *.xml files
Ignores whitespace and indentation differences
"""

import os
import re
from pathlib import Path
from typing import Tuple, List


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


def compare_xml_files(cmp_file: str, xml_file: str) -> Tuple[bool, str]:
    """
    Compare two XML files ignoring whitespace.
    Returns (match: bool, message: str)
    """
    if not os.path.exists(xml_file):
        return False, f"Missing: {xml_file}"
    
    cmp_content = read_xml_file(cmp_file)
    xml_content = read_xml_file(xml_file)
    
    if "ERROR:" in cmp_content:
        return False, cmp_content
    if "ERROR:" in xml_content:
        return False, xml_content
    
    if cmp_content == xml_content:
        return True, "✓ Match"
    else:
        return False, "✗ Content differs"


def find_and_compare_xml_files(root_dir: str) -> List[Tuple[str, bool, str]]:
    """
    Find all *Cmp.xml files and compare them with *.xml files.
    Returns list of (filepath, match_status, message)
    """
    results = []
    
    root_path = Path(root_dir)
    
    # Find all *Cmp.xml files
    for cmp_file in sorted(root_path.rglob('*Cmp.xml')):
        # Get the corresponding *.xml file
        base_path = str(cmp_file).replace('Cmp.xml', '.xml')
        
        match, message = compare_xml_files(str(cmp_file), base_path)
        results.append((str(cmp_file), match, message))
    
    return results


def print_report(results: List[Tuple[str, bool, str]]) -> None:
    """Print a formatted comparison report."""
    if not results:
        print("No *Cmp.xml files found.")
        return
    
    print("=" * 80)
    print("XML Comparison Report")
    print("=" * 80)
    
    matches = 0
    mismatches = 0
    
    for filepath, match, message in results:
        status = "✓ PASS" if match else "✗ FAIL"
        print(f"\n{status}: {filepath}")
        print(f"  {message}")
        
        if match:
            matches += 1
        else:
            mismatches += 1
    
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
    
    print(f"Scanning directory: {root_directory}")
    results = find_and_compare_xml_files(root_directory)
    print_report(results)
