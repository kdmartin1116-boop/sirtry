#!/usr/bin/env python3
"""
VeroBrix Command Line Interface

A user-friendly CLI for the VeroBrix legal intelligence system.
"""

import sys
import os
import argparse
import json
from datetime import datetime

# Add modules to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules')))

from verobrix_launcher import VeroBrixSystem
from agents.FRIDAY.friday_agent import log_provenance

def print_banner():
    """Print the VeroBrix banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                        VeroBrix 1.0                         ║
║              Sovereignty-Aligned Legal Intelligence          ║
║                                                              ║
║  Democratizing access to lawful remedies and legal clarity  ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def analyze_file(filepath: str, system: VeroBrixSystem):
    """Analyze a legal document from file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 Analyzing file: {filepath}")
        print("=" * 60)
        
        results = system.analyze_situation(content)
        system.print_analysis_summary(results)
        
        return results
        
    except FileNotFoundError:
        print(f"❌ Error: File '{filepath}' not found.")
        return None
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")
        return None

def analyze_text(text: str, system: VeroBrixSystem):
    """Analyze legal text directly."""
    print("📝 Analyzing provided text...")
    print("=" * 60)
    
    results = system.analyze_situation(text)
    system.print_analysis_summary(results)
    
    return results

def generate_document_interactive(system: VeroBrixSystem):
    """Interactive document generation."""
    print("\n📋 Available Document Templates:")
    templates = system.get_available_templates()
    
    for i, template in enumerate(templates, 1):
        print(f"  {i}. {template}")
    
    try:
        choice = input("\nSelect template number (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            return
        
        template_idx = int(choice) - 1
        if template_idx < 0 or template_idx >= len(templates):
            print("❌ Invalid selection.")
            return
        
        template_name = templates[template_idx].split('.')[-1]  # Get template name without category
        
        print(f"\n📝 Generating document: {template_name}")
        print("Please provide the following information:")
        
        variables = {}
        
        # Common variables for most templates
        common_vars = {
            'INDIVIDUAL_NAME': 'Your full name',
            'NAME': 'Your name for signature',
            'OFFICER': 'Officer name (if applicable)',
            'AGENCY': 'Agency/Department name (if applicable)',
            'SIGNATURE': 'Your signature line'
        }
        
        for var, description in common_vars.items():
            value = input(f"  {description}: ").strip()
            if value:
                variables[var] = value
        
        # Generate document
        document = system.generate_document(template_name, variables)
        
        print("\n" + "="*60)
        print("GENERATED DOCUMENT")
        print("="*60)
        print(document)
        
        # Offer to save
        save = input("\nSave document to file? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"output/{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(document)
                print(f"✅ Document saved to: {filename}")
            except Exception as e:
                print(f"❌ Error saving document: {e}")
        
    except (ValueError, IndexError):
        print("❌ Invalid selection.")
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")

def interactive_mode():
    """Run VeroBrix in interactive mode."""
    print_banner()
    system = VeroBrixSystem()
    
    while True:
        print("\n🔧 VeroBrix Main Menu:")
        print("  1. Analyze legal document from file")
        print("  2. Analyze legal text (paste/type)")
        print("  3. Generate legal document")
        print("  4. View recent analysis results")
        print("  5. Help")
        print("  6. Exit")
        
        try:
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                filepath = input("Enter file path: ").strip()
                if filepath:
                    analyze_file(filepath, system)
            
            elif choice == '2':
                print("\nEnter your legal text (press Ctrl+D when finished):")
                try:
                    lines = []
                    while True:
                        line = input()
                        lines.append(line)
                except EOFError:
                    text = '\n'.join(lines)
                    if text.strip():
                        analyze_text(text, system)
            
            elif choice == '3':
                generate_document_interactive(system)
            
            elif choice == '4':
                # List recent analysis files
                try:
                    output_files = [f for f in os.listdir('output') if f.startswith('verobrix_analysis_')]
                    if output_files:
                        print("\n📊 Recent Analysis Results:")
                        for i, filename in enumerate(sorted(output_files, reverse=True)[:5], 1):
                            print(f"  {i}. {filename}")
                        
                        file_choice = input("\nSelect file to view (number or filename): ").strip()
                        try:
                            if file_choice.isdigit():
                                selected_file = sorted(output_files, reverse=True)[int(file_choice) - 1]
                            else:
                                selected_file = file_choice
                            
                            with open(f'output/{selected_file}', 'r') as f:
                                data = json.load(f)
                            
                            print(f"\n📋 Analysis Summary for {selected_file}:")
                            print(f"  Session: {data['session_id']}")
                            print(f"  Timestamp: {data['timestamp']}")
                            print(f"  Situation: {data['situation_analysis']['type']}")
                            print(f"  Risk Level: {data['legal_analysis']['legal_summary']['risk_level']}")
                            
                        except (IndexError, ValueError, FileNotFoundError):
                            print("❌ Invalid selection or file not found.")
                    else:
                        print("📭 No recent analysis results found.")
                except FileNotFoundError:
                    print("📭 Output directory not found. Run an analysis first.")
            
            elif choice == '5':
                print_help()
            
            elif choice == '6':
                print("\n👋 Thank you for using VeroBrix!")
                break
            
            else:
                print("❌ Invalid option. Please select 1-6.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")

def print_help():
    """Print help information."""
    help_text = """
📚 VeroBrix Help

OVERVIEW:
VeroBrix is a sovereignty-aligned legal intelligence system designed to help
individuals understand their legal situations and generate appropriate remedies.

FEATURES:
• Situation Analysis: Interprets legal documents and situations
• Contradiction Detection: Identifies conflicting legal language
• Risk Assessment: Evaluates potential legal risks
• Remedy Generation: Suggests lawful remedies and strategies
• Document Generation: Creates legal notices and templates

USAGE TIPS:
• For best results, provide complete and accurate information
• Review all generated documents with qualified legal counsel
• Keep records of all analysis results for future reference
• Use the system as a research tool, not as legal advice

LEGAL DISCLAIMER:
VeroBrix provides information and analysis tools. It does not provide legal
advice. Always consult with qualified legal counsel for specific legal matters.

PHILOSOPHY:
VeroBrix is built on principles of autonomy, transparency, lawful remedy,
and honoring those who have fought for sovereignty and truth.
    """
    print(help_text)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="VeroBrix - Sovereignty-Aligned Legal Intelligence System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-f', '--file',
        help='Analyze legal document from file'
    )
    
    parser.add_argument(
        '-t', '--text',
        help='Analyze legal text directly'
    )
    
    parser.add_argument(
        '-g', '--generate',
        help='Generate document from template'
    )
    
    parser.add_argument(
        '--list-templates',
        action='store_true',
        help='List available document templates'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='VeroBrix 1.0'
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, run interactive mode
    if len(sys.argv) == 1:
        interactive_mode()
        return
    
    # Initialize system
    system = VeroBrixSystem()
    
    if args.interactive:
        interactive_mode()
    
    elif args.file:
        analyze_file(args.file, system)
    
    elif args.text:
        analyze_text(args.text, system)
    
    elif args.list_templates:
        print("📋 Available Document Templates:")
        templates = system.get_available_templates()
        for template in templates:
            print(f"  • {template}")
    
    elif args.generate:
        print(f"📝 Generating document: {args.generate}")
        # This would need additional input for variables
        print("Use interactive mode (-i) for full document generation.")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
