#!/usr/bin/env python3
"""
Test script to verify i18n implementation works correctly.
"""

import sys
import os

def test_translations_exist():
    """Test that translation files exist."""
    base_path = os.path.join('lute', 'translations')
    
    # Check Spanish translations
    es_po = os.path.join(base_path, 'es', 'LC_MESSAGES', 'messages.po')
    es_mo = os.path.join(base_path, 'es', 'LC_MESSAGES', 'messages.mo')
    assert os.path.exists(es_po), f"Spanish .po file not found: {es_po}"
    assert os.path.exists(es_mo), f"Spanish .mo file not found: {es_mo}"
    
    # Check French translations  
    fr_po = os.path.join(base_path, 'fr', 'LC_MESSAGES', 'messages.po')
    fr_mo = os.path.join(base_path, 'fr', 'LC_MESSAGES', 'messages.mo')
    assert os.path.exists(fr_po), f"French .po file not found: {fr_po}"
    assert os.path.exists(fr_mo), f"French .mo file not found: {fr_mo}"
    
    print("✓ Translation files exist")

def test_translation_content():
    """Test that translation files contain expected content."""
    # Check Spanish translations
    with open('lute/translations/es/LC_MESSAGES/messages.po', 'r', encoding='utf-8') as f:
        es_content = f.read()
        assert 'msgstr "Inicio"' in es_content  # Home -> Inicio
        assert 'msgstr "Libros"' in es_content  # Books -> Libros
        
    # Check French translations
    with open('lute/translations/fr/LC_MESSAGES/messages.po', 'r', encoding='utf-8') as f:
        fr_content = f.read()
        assert 'msgstr "Accueil"' in fr_content  # Home -> Accueil  
        assert 'msgstr "Livres"' in fr_content   # Books -> Livres
        
    print("✓ Translation content is correct")

if __name__ == '__main__':
    try:
        print("Testing i18n implementation...")
        test_translations_exist() 
        test_translation_content()
        print("\n🎉 All i18n tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)