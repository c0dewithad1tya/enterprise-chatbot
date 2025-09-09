"""
Improved Document Indexing with Better Chunking
===============================================
Creates more focused chunks for better search results
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict

def extract_sections_from_markdown(content: str) -> List[Dict]:
    """Extract meaningful sections from markdown content"""
    sections = []
    
    # Split by h2 headers (##)
    parts = re.split(r'\n## ', content)
    
    for i, part in enumerate(parts):
        if i == 0 and not part.startswith('## '):
            # First part might be document header
            continue
            
        # Add back the ## for proper markdown
        if i > 0:
            part = '## ' + part
            
        # Extract section title
        lines = part.split('\n')
        title = lines[0].replace('## ', '').replace('#', '').strip()
        
        # Get section content
        section_content = '\n'.join(lines)
        
        if len(section_content.strip()) > 50:  # Skip very short sections
            sections.append({
                'title': title,
                'content': section_content
            })
    
    # Also split by h3 headers (###) for more granular chunks
    detailed_sections = []
    for section in sections:
        h3_parts = re.split(r'\n### ', section['content'])
        
        if len(h3_parts) > 1:
            # Has subsections
            for j, h3_part in enumerate(h3_parts):
                if j == 0:
                    # Main section intro
                    if len(h3_part.strip()) > 50:
                        detailed_sections.append({
                            'title': section['title'],
                            'content': h3_part
                        })
                else:
                    # Subsection
                    h3_part = '### ' + h3_part
                    h3_lines = h3_part.split('\n')
                    h3_title = h3_lines[0].replace('### ', '').strip()
                    
                    detailed_sections.append({
                        'title': f"{section['title']} - {h3_title}",
                        'content': h3_part
                    })
        else:
            # No subsections
            detailed_sections.append(section)
    
    return detailed_sections

def index_documents(doc_folder: str = 'documentation') -> Dict:
    """Index all markdown documents with better chunking"""
    
    if not os.path.exists(doc_folder):
        print(f"Creating {doc_folder} directory...")
        os.makedirs(doc_folder)
        return {'chunks': [], 'metadata': {}}
    
    all_chunks = []
    metadata = {}
    
    # Process all markdown files
    for filename in os.listdir(doc_folder):
        if filename.endswith('.md'):
            filepath = os.path.join(doc_folder, filename)
            print(f"Indexing: {filename}")
            
            # Read document
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract document title
            doc_title = filename.replace('_', ' ').replace('.md', '').title()
            
            # Extract sections
            sections = extract_sections_from_markdown(content)
            
            print(f"  - Found {len(sections)} sections")
            
            # Create chunks from sections
            for i, section in enumerate(sections):
                chunk = {
                    'document_title': doc_title,
                    'document_path': filepath,
                    'section_title': section['title'],
                    'chunk_id': f"{filename}_section_{i}",
                    'content': section['content'],
                    'chunk_index': i,
                    'total_chunks': len(sections)
                }
                all_chunks.append(chunk)
    
    # Create index summary
    index_summary = {
        'total_documents': len(set(c['document_title'] for c in all_chunks)),
        'total_chunks': len(all_chunks),
        'indexed_at': datetime.now().isoformat()
    }
    
    # Save index files
    with open('document_chunks_improved.json', 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    with open('document_index_improved.json', 'w', encoding='utf-8') as f:
        json.dump(index_summary, f, indent=2)
    
    print(f"\nIndexing complete!")
    print(f"Total documents: {index_summary['total_documents']}")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Chunks saved to: document_chunks_improved.json")
    
    return {'chunks': all_chunks, 'summary': index_summary}

def search_test(chunks: List[Dict], query: str) -> None:
    """Test search in chunks"""
    query_lower = query.lower()
    results = []
    
    for chunk in chunks:
        content_lower = chunk['content'].lower()
        section_lower = chunk.get('section_title', '').lower()
        
        # Check both content and section title
        score = 0
        for word in query_lower.split():
            score += content_lower.count(word) * 2  # Weight content matches
            score += section_lower.count(word) * 5  # Weight title matches more
        
        if score > 0:
            results.append({
                'chunk': chunk,
                'score': score
            })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\nSearch results for '{query}':")
    for i, result in enumerate(results[:5]):
        chunk = result['chunk']
        print(f"\n{i+1}. {chunk['document_title']} - {chunk['section_title']}")
        print(f"   Score: {result['score']}")
        print(f"   Preview: {chunk['content'][:100]}...")

if __name__ == "__main__":
    # Index documents
    result = index_documents()
    chunks = result['chunks']
    
    # Test with ML query
    print("\n" + "="*60)
    search_test(chunks, "machine learning stack")
    search_test(chunks, "technology stack")
    search_test(chunks, "frontend technologies")