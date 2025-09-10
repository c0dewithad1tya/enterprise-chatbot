"""
Enhanced Search Engine for WhoKnows? Chatbot
============================================
Provides intelligent document search with context-aware ranking
and structured result presentation.
"""

import re
import json
import faiss
import pickle
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from sentence_transformers import SentenceTransformer


class QueryType(Enum):
    """Categorize queries for specialized handling"""
    PERSON = "person"
    TECHNOLOGY = "technology"
    PROCESS = "process"
    ARCHITECTURE = "architecture"
    GENERAL = "general"


@dataclass
class SearchHit:
    """Represents a single search result with metadata"""
    content: str
    document_title: str
    section_title: str
    document_path: str
    score: float
    chunk_id: str
    highlights: List[str]
    context_before: Optional[str] = None
    context_after: Optional[str] = None


class QueryAnalyzer:
    """Analyzes queries to understand intent and extract key terms"""
    
    def __init__(self):
        self.person_indicators = [
            'who is', 'who are', 'responsibility', 'responsibilities',
            'cto', 'cio', 'ceo', 'manager', 'lead', 'team', 'member'
        ]
        self.tech_indicators = [
            'technology', 'stack', 'framework', 'library', 'tool',
            'language', 'database', 'api', 'frontend', 'backend',
            'ml', 'machine learning', 'ai', 'model'
        ]
        self.process_indicators = [
            'how to', 'process', 'procedure', 'deploy', 'build',
            'test', 'release', 'workflow', 'pipeline'
        ]
        self.architecture_indicators = [
            'architecture', 'design', 'structure', 'component',
            'system', 'integration', 'pattern'
        ]
        
        self.synonyms = {
            'ml': ['machine learning', 'ai', 'artificial intelligence', 'deep learning'],
            'tech': ['technology', 'technical'],
            'stack': ['technology stack', 'tech stack', 'technologies', 'tools'],
            'cto': ['chief technology officer', 'technology officer', 'tech lead'],
            'cio': ['chief information officer', 'information officer', 'it lead'],
            'backend': ['back-end', 'server', 'api', 'server-side'],
            'frontend': ['front-end', 'ui', 'interface', 'client-side', 'user interface'],
            'database': ['db', 'storage', 'data store', 'persistence'],
            'deploy': ['deployment', 'release', 'rollout', 'launch'],
            'test': ['testing', 'qa', 'quality assurance', 'verification']
        }
    
    def analyze(self, query: str) -> Dict:
        """Analyze query to extract intent and key terms"""
        query_lower = query.lower()
        
        # Determine query type
        query_type = self._classify_query(query_lower)
        
        # Extract and expand key terms
        key_terms = self._extract_key_terms(query_lower)
        expanded_terms = self._expand_terms(key_terms)
        
        # Extract entities (names, technologies, etc.)
        entities = self._extract_entities(query)
        
        return {
            'original_query': query,
            'query_type': query_type,
            'key_terms': key_terms,
            'expanded_terms': expanded_terms,
            'entities': entities,
            'is_question': query.strip().endswith('?')
        }
    
    def _classify_query(self, query: str) -> QueryType:
        """Classify the query type based on indicators"""
        query_lower = query.lower()
        
        # Check each category
        scores = {
            QueryType.PERSON: sum(1 for ind in self.person_indicators if ind in query_lower),
            QueryType.TECHNOLOGY: sum(1 for ind in self.tech_indicators if ind in query_lower),
            QueryType.PROCESS: sum(1 for ind in self.process_indicators if ind in query_lower),
            QueryType.ARCHITECTURE: sum(1 for ind in self.architecture_indicators if ind in query_lower)
        }
        
        # Return the type with highest score, or GENERAL if no matches
        max_score = max(scores.values())
        if max_score == 0:
            return QueryType.GENERAL
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract important terms from the query"""
        # Remove common question words
        stop_words = {'what', 'is', 'the', 'a', 'an', 'are', 'can', 'you', 'tell', 'me', 'about', 'of'}
        
        # Tokenize and filter
        words = query.lower().split()
        key_terms = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Also extract multi-word phrases
        phrases = []
        if 'machine learning' in query:
            phrases.append('machine learning')
        if 'technology stack' in query or 'tech stack' in query:
            phrases.append('technology stack')
        if 'chief technology officer' in query:
            phrases.append('cto')
        if 'chief information officer' in query:
            phrases.append('cio')
        
        return key_terms + phrases
    
    def _expand_terms(self, terms: List[str]) -> List[str]:
        """Expand terms with synonyms"""
        expanded = list(terms)
        
        for term in terms:
            if term in self.synonyms:
                expanded.extend(self.synonyms[term])
        
        return list(set(expanded))
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract named entities from the query"""
        entities = {
            'people': [],
            'technologies': [],
            'roles': []
        }
        
        # Extract people names (simple heuristic - capitalized words)
        words = query.split()
        for i, word in enumerate(words):
            if word[0].isupper() and word.lower() not in ['what', 'who', 'how', 'when', 'where', 'why']:
                # Check if it's a person name (followed by another capitalized word)
                if i < len(words) - 1 and words[i + 1][0].isupper():
                    entities['people'].append(f"{word} {words[i + 1]}")
        
        # Extract roles
        query_lower = query.lower()
        for role in ['cto', 'cio', 'ceo', 'manager', 'lead', 'developer', 'engineer']:
            if role in query_lower:
                entities['roles'].append(role)
        
        # Extract technologies
        tech_patterns = [
            'python', 'javascript', 'react', 'node', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'mongodb', 'postgresql', 'redis'
        ]
        for tech in tech_patterns:
            if tech in query_lower:
                entities['technologies'].append(tech)
        
        return entities


class ContentExtractor:
    """Extracts and formats relevant content from search results"""
    
    def extract_highlights(self, content: str, query_terms: List[str], max_highlights: int = 3) -> List[str]:
        """Extract the most relevant sentences as highlights"""
        sentences = self._split_into_sentences(content)
        scored_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            score = 0
            
            # Score based on term matches
            for term in query_terms:
                if len(term) > 2:
                    occurrences = sentence_lower.count(term.lower())
                    score += occurrences * (len(term) / 3)  # Longer terms get more weight
            
            # Boost for structured content
            if any(marker in sentence for marker in [':', '**', '- ', '• ']):
                score *= 1.5
            
            # Skip very short or very long sentences
            if 20 < len(sentence) < 300:
                scored_sentences.append((score, sentence))
        
        # Sort by score and return top highlights
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        highlights = [sent for _, sent in scored_sentences[:max_highlights]]
        
        return highlights
    
    def extract_structured_content(self, content: str) -> Dict:
        """Extract structured information from content"""
        structured = {
            'lists': [],
            'key_values': {},
            'sections': [],
            'code_blocks': []
        }
        
        lines = content.split('\n')
        current_list = []
        
        for line in lines:
            line = line.strip()
            
            # Extract key-value pairs
            if ':' in line and not line.startswith('-'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().replace('**', '').replace('*', '')
                    value = parts[1].strip().replace('**', '').replace('*', '')
                    if key and value:
                        structured['key_values'][key] = value
            
            # Extract list items
            if line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                item = line[2:].strip()
                current_list.append(item)
            elif current_list and not line.startswith(('- ', '• ', '* ')):
                if current_list:
                    structured['lists'].append(current_list)
                    current_list = []
            
            # Extract section headers
            if line.startswith('###'):
                section = line.replace('#', '').strip()
                structured['sections'].append(section)
        
        # Add any remaining list
        if current_list:
            structured['lists'].append(current_list)
        
        return structured
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be improved with NLTK or spaCy)
        sentences = re.split(r'[.!?]\s+', text)
        
        # Clean up sentences
        cleaned = []
        for sent in sentences:
            sent = sent.strip()
            if sent and len(sent) > 10:
                # Ensure sentence ends with punctuation
                if not sent[-1] in '.!?':
                    sent += '.'
                cleaned.append(sent)
        
        return cleaned
    
    def clean_text(self, text: str) -> str:
        """Remove markdown artifacts and clean up text for display"""
        # Remove markdown headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # Remove excessive asterisks
        text = re.sub(r'\*{3,}', '', text)
        # Clean up bullet points
        text = re.sub(r'^[\-\*]\s+', '• ', text, flags=re.MULTILINE)
        # Remove escape characters
        text = text.replace('\\n', '\n').replace('\\t', ' ').replace('\\', '')
        # Clean up excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        return text.strip()
    
    def format_for_display(self, hit: SearchHit, query_analysis: Dict, max_length: int = 2000) -> str:
        """Format a search hit for user display with character limit"""
        formatted_parts = []
        
        # Clean the content first
        clean_content = self.clean_text(hit.content)
        
        # Add section context if available (cleaned)
        if hit.section_title:
            clean_title = self.clean_text(hit.section_title)
            formatted_parts.append(f"**{clean_title}**\n")
        
        # Extract structured content
        structured = self.extract_structured_content(clean_content)
        
        # For technology queries, prioritize structured data
        if query_analysis['query_type'] == QueryType.TECHNOLOGY:
            # Add key-value pairs
            if structured['key_values']:
                for key, value in list(structured['key_values'].items())[:4]:
                    clean_key = self.clean_text(key)
                    clean_value = self.clean_text(value)[:100]  # Limit value length
                    formatted_parts.append(f"{clean_key}: {clean_value}")
            
            # Add relevant lists
            if structured['lists']:
                for lst in structured['lists'][:1]:  # Show first list only
                    if len(lst) <= 5:
                        for item in lst[:3]:  # Limit items
                            clean_item = self.clean_text(item)[:100]
                            formatted_parts.append(f"• {clean_item}")
        
        else:
            # For other query types, use highlights
            if hit.highlights:
                for highlight in hit.highlights[:3]:
                    clean_highlight = self.clean_text(highlight)
                    # Don't bold terms, keep it clean
                    formatted_parts.append(f"• {clean_highlight}")
            
            # Add some key-value pairs if relevant
            if structured['key_values']:
                relevant_keys = []
                for key, value in structured['key_values'].items():
                    key_lower = key.lower()
                    if any(term in key_lower for term in query_analysis['key_terms'] if len(term) > 2):
                        clean_key = self.clean_text(key)
                        clean_value = self.clean_text(value)[:100]
                        relevant_keys.append(f"{clean_key}: {clean_value}")
                
                if relevant_keys:
                    formatted_parts.extend(relevant_keys[:2])
        
        # If we have no formatted content, use clean content excerpt
        if len(formatted_parts) <= 1:
            # Take first 500 chars of clean content
            excerpt = clean_content[:500]
            if len(excerpt) < len(clean_content):
                excerpt += "..."
            formatted_parts.append(excerpt)
        
        # Join and apply character limit
        result = '\n'.join(formatted_parts)
        if len(result) > max_length:
            result = result[:max_length-3] + "..."
        
        return result


class SearchEngine:
    """Main search engine with improved relevance and presentation"""
    
    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        self.content_extractor = ContentExtractor()
        self.model = None
        self.index = None
        self.chunks = []
        self.metadata = {}
        
    def initialize(self):
        """Load search index and model"""
        try:
            # Load FAISS index
            self.index = faiss.read_index('faiss_index.index')
            
            # Load metadata
            with open('faiss_index_metadata.pkl', 'rb') as f:
                self.metadata = pickle.load(f)
                self.chunks = self.metadata['chunks']
            
            # Load sentence transformer model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            return True
        except Exception as e:
            print(f"Failed to initialize search engine: {e}")
            return False
    
    def search(self, query: str, top_k: int = 10) -> Dict:
        """Perform intelligent search with context-aware ranking"""
        
        # Analyze the query
        query_analysis = self.query_analyzer.analyze(query)
        
        # Perform vector search
        search_results = self._vector_search(query, query_analysis, top_k * 2)
        
        # Re-rank results based on query type and context
        ranked_results = self._rerank_results(search_results, query_analysis)
        
        # Group and aggregate results
        aggregated_results = self._aggregate_results(ranked_results, query_analysis)
        
        # Format the response
        response = self._format_response(aggregated_results, query_analysis)
        
        return response
    
    def _vector_search(self, query: str, query_analysis: Dict, k: int) -> List[SearchHit]:
        """Perform vector similarity search"""
        if not self.model or not self.index:
            return []
        
        # Encode query with expanded terms
        expanded_query = query + " " + " ".join(query_analysis['expanded_terms'])
        query_embedding = self.model.encode([expanded_query])
        
        # Search in FAISS index
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Create SearchHit objects
        hits = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx]
                
                # Extract highlights
                highlights = self.content_extractor.extract_highlights(
                    chunk['content'],
                    query_analysis['expanded_terms']
                )
                
                hit = SearchHit(
                    content=chunk['content'],
                    document_title=chunk['document_title'],
                    section_title=chunk.get('section_title', ''),
                    document_path=chunk.get('document_path', ''),
                    score=float(1 / (1 + dist)),  # Convert distance to similarity
                    chunk_id=chunk.get('chunk_id', ''),
                    highlights=highlights
                )
                hits.append(hit)
        
        return hits
    
    def _rerank_results(self, results: List[SearchHit], query_analysis: Dict) -> List[SearchHit]:
        """Re-rank results based on query type and relevance"""
        
        for hit in results:
            # Base score from vector similarity
            relevance_score = hit.score
            
            # Apply query-type specific boosting
            if query_analysis['query_type'] == QueryType.PERSON:
                if any(term in hit.section_title.lower() for term in ['team', 'people', 'responsibilities']):
                    relevance_score *= 2.0
                if any(role in hit.content.lower() for role in query_analysis['entities']['roles']):
                    relevance_score *= 1.5
            
            elif query_analysis['query_type'] == QueryType.TECHNOLOGY:
                # Strong boost for technology stack document
                if 'technology stack' in hit.document_title.lower():
                    relevance_score *= 3.0
                    
                    # Extra boost if it's the ML section
                    if 'machine learning' in query_analysis['original_query'].lower():
                        if 'machine learning stack' in hit.section_title.lower():
                            relevance_score *= 5.0
                        elif 'embedding' in hit.section_title.lower() or 'vector' in hit.section_title.lower():
                            relevance_score *= 3.0
                        elif 'language model' in hit.section_title.lower():
                            relevance_score *= 3.0
                            
                # Boost for tech entities
                if any(tech in hit.content.lower() for tech in query_analysis['entities']['technologies']):
                    relevance_score *= 1.5
                    
                # Penalize non-technical content
                if 'learning resources' in hit.section_title.lower() or 'professional development' in hit.section_title.lower():
                    relevance_score *= 0.1
            
            elif query_analysis['query_type'] == QueryType.PROCESS:
                if any(term in hit.section_title.lower() for term in ['process', 'workflow', 'deployment']):
                    relevance_score *= 1.8
            
            # Boost for exact phrase matches
            query_lower = query_analysis['original_query'].lower()
            content_lower = hit.content.lower()
            section_lower = hit.section_title.lower()
            
            # Check for exact phrase match in section title
            if 'machine learning' in query_lower and 'machine learning stack' in section_lower:
                relevance_score *= 10.0
            elif query_lower in content_lower:
                relevance_score *= 2.5
            
            # Boost for title matches
            for term in query_analysis['key_terms']:
                if len(term) > 3 and term.lower() in hit.section_title.lower():
                    relevance_score *= 1.5
                if len(term) > 3 and term.lower() in hit.document_title.lower():
                    relevance_score *= 1.3
            
            # Update score
            hit.score = relevance_score
        
        # Sort by new scores
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results
    
    def _aggregate_results(self, results: List[SearchHit], query_analysis: Dict) -> List[SearchHit]:
        """Aggregate related chunks for better context"""
        
        # Group by document
        doc_groups = {}
        for hit in results:
            if hit.document_title not in doc_groups:
                doc_groups[hit.document_title] = []
            doc_groups[hit.document_title].append(hit)
        
        # Select best results with context
        final_results = []
        
        # Take top results from most relevant documents
        for doc_title, hits in doc_groups.items():
            # Sort hits within document by score
            hits.sort(key=lambda x: x.score, reverse=True)
            
            # Take top hits from this document
            doc_limit = 3 if len(doc_groups) == 1 else 2
            for hit in hits[:doc_limit]:
                final_results.append(hit)
        
        # Sort all results by score
        final_results.sort(key=lambda x: x.score, reverse=True)
        
        return final_results[:5]  # Return top 5 aggregated results
    
    def _format_response(self, results: List[SearchHit], query_analysis: Dict) -> Dict:
        """Format the final response for the user"""
        
        if not results:
            return self._no_results_response(query_analysis)
        
        # Build the main message
        message_parts = []
        
        # Add a clean contextual title
        title = self._generate_response_title(query_analysis)
        clean_title = self.content_extractor.clean_text(title)
        message_parts.append(clean_title)
        
        # Format top results with character limit
        seen_content = set()
        formatted_results = []
        total_chars = len(clean_title) + 2  # Account for title and newline
        
        for hit in results[:3]:  # Show top 3 results
            # Avoid duplicate content
            content_hash = hash(hit.content[:100])
            if content_hash in seen_content:
                continue
            seen_content.add(content_hash)
            
            # Calculate remaining space
            remaining_chars = 2000 - total_chars - 200  # Leave space for links
            if remaining_chars < 200:
                break
            
            # Format this hit with character limit
            formatted = self.content_extractor.format_for_display(hit, query_analysis, remaining_chars)
            if formatted:
                formatted_results.append(formatted)
                total_chars += len(formatted) + 2  # Add formatted text + newlines
        
        # Combine formatted results
        if formatted_results:
            message_parts.extend(formatted_results)
        else:
            # Fallback to simple clean excerpt
            for hit in results[:2]:
                if hit.highlights:
                    clean_highlight = self.content_extractor.clean_text(hit.highlights[0])
                    message_parts.append(f"• {clean_highlight}")
        
        # Add link section if results were truncated
        if len(results) > 1 or (results and len(results[0].content) > 2000):
            message_parts.append("\n📄 **View full documentation:**")
        
        # Build sources list with document links
        sources = []
        seen_docs = set()
        for hit in results[:3]:
            if hit.document_title not in seen_docs:
                seen_docs.add(hit.document_title)
                doc_name = hit.document_path.split('/')[-1] if hit.document_path else 'document'
                sources.append({
                    'type': 'document',
                    'title': hit.document_title,
                    'path': hit.document_path,
                    'relevance': round(hit.score, 2),
                    'link': f"/docs/{doc_name}"  # Frontend will handle this
                })
                
                # Add to message as clickable reference
                if len(sources) <= 3:
                    message_parts.append(f"→ {hit.document_title}")
        
        # Clean up the final message
        final_message = '\n\n'.join(message_parts)
        # Final cleanup of any remaining artifacts
        final_message = re.sub(r'\s*\n{3,}', '\n\n', final_message)
        final_message = final_message.replace('•', '•').replace('→', '→')
        
        return {
            'message': final_message[:2000],  # Hard limit at 2000 chars
            'sources': sources[:3],
            'query_analysis': {
                'type': query_analysis['query_type'].value,
                'key_terms': query_analysis['key_terms']
            }
        }
    
    def _generate_response_title(self, query_analysis: Dict) -> str:
        """Generate an appropriate title for the response"""
        query = query_analysis['original_query']
        query_type = query_analysis['query_type']
        
        if query_type == QueryType.PERSON:
            # Extract person name if possible
            if query_analysis['entities']['people']:
                person = query_analysis['entities']['people'][0]
                return f"## {person}"
            elif 'cto' in query.lower():
                return "## Chief Technology Officer (CTO)"
            elif 'cio' in query.lower():
                return "## Chief Information Officer (CIO)"
            else:
                return "## Team Information"
        
        elif query_type == QueryType.TECHNOLOGY:
            if 'stack' in query.lower():
                return "## Technology Stack"
            elif query_analysis['entities']['technologies']:
                tech = query_analysis['entities']['technologies'][0]
                return f"## {tech.title()} Information"
            else:
                return "## Technical Information"
        
        elif query_type == QueryType.PROCESS:
            return "## Process & Workflow"
        
        elif query_type == QueryType.ARCHITECTURE:
            return "## System Architecture"
        
        else:
            # Generic title
            if query_analysis['is_question']:
                return "## Answer"
            else:
                return "## Information"
    
    def _no_results_response(self, query_analysis: Dict) -> Dict:
        """Generate a helpful response when no results are found"""
        
        suggestions = []
        
        if query_analysis['query_type'] == QueryType.PERSON:
            suggestions = [
                "Team structure and roles",
                "CTO: Alexandra Chen",
                "CIO: Marcus Williams",
                "Development team members"
            ]
        elif query_analysis['query_type'] == QueryType.TECHNOLOGY:
            suggestions = [
                "Technology stack overview",
                "Frontend frameworks (React, TypeScript)",
                "Backend technologies (Python, Node.js)",
                "Machine learning tools"
            ]
        else:
            suggestions = [
                "Application architecture",
                "Technology stack",
                "Team members and roles",
                "Development processes"
            ]
        
        message = f"""## No Results Found

I couldn't find specific information about "{query_analysis['original_query']}" in the documentation.

### Try asking about:
"""
        
        for suggestion in suggestions:
            message += f"• {suggestion}\n"
        
        return {
            'message': message,
            'sources': [],
            'query_analysis': {
                'type': query_analysis['query_type'].value,
                'key_terms': query_analysis['key_terms']
            }
        }


# Fallback search for when vector index is not available
def keyword_search(query: str, chunks_file: str = 'document_chunks_improved.json') -> Dict:
    """Simple keyword-based search as fallback"""
    try:
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
    except FileNotFoundError:
        return {
            'message': "No documentation indexed yet. Please run the indexing script.",
            'sources': []
        }
    
    query_lower = query.lower()
    query_terms = query_lower.split()
    
    results = []
    for chunk in chunks:
        content_lower = chunk['content'].lower()
        section_lower = chunk.get('section_title', '').lower()
        
        # Calculate relevance score
        score = 0
        for term in query_terms:
            if len(term) > 2:
                score += content_lower.count(term)
                score += section_lower.count(term) * 3  # Weight section matches higher
        
        if score > 0:
            results.append({
                'chunk': chunk,
                'score': score
            })
    
    # Sort and return top results
    results.sort(key=lambda x: x['score'], reverse=True)
    
    if not results:
        return {
            'message': f"No results found for '{query}'",
            'sources': []
        }
    
    # Format top result
    top_chunk = results[0]['chunk']
    message = f"## {top_chunk.get('section_title', 'Information')}\n\n"
    
    # Extract key sentences
    sentences = top_chunk['content'].split('.')[:3]
    for sent in sentences:
        if sent.strip():
            message += f"• {sent.strip()}.\n"
    
    return {
        'message': message,
        'sources': [{
            'title': top_chunk['document_title'],
            'path': top_chunk.get('document_path', '')
        }]
    }