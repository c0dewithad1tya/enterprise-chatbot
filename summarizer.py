"""
AI-powered summarization module for WhoKnows? chatbot.
Uses transformer models for high-quality abstractive summarization.
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SummaryResult:
    """Container for summarization results"""
    summary: str
    key_points: List[str]
    confidence: float
    model_used: str

class Summarizer:
    """
    Advanced summarization using transformer models.
    Provides both abstractive summaries and key point extraction.
    """
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        """
        Initialize the summarizer with a pre-trained model.
        
        Args:
            model_name: HuggingFace model to use. Options:
                - "facebook/bart-large-cnn" (best quality, larger)
                - "philschmid/bart-large-cnn-samsum" (good for conversations)
                - "google/flan-t5-small" (smaller, faster)
        """
        self.model_name = model_name
        self.device = 0 if torch.cuda.is_available() else -1
        
        try:
            # Use smaller model if specified for faster inference
            if "t5-small" in model_name or "distilbart" in model_name:
                logger.info(f"Loading lightweight model: {model_name}")
                self.summarizer = pipeline(
                    "summarization", 
                    model=model_name,
                    device=self.device,
                    max_length=150,
                    min_length=30
                )
            else:
                # Load full model for better quality
                logger.info(f"Loading model: {model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                if torch.cuda.is_available():
                    self.model = self.model.cuda()
                
                self.summarizer = pipeline(
                    "summarization",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=self.device,
                    max_length=200,
                    min_length=50
                )
            
            self.initialized = True
            logger.info("Summarizer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            logger.info("Falling back to extractive summarization")
            self.initialized = False
            self.summarizer = None
    
    def summarize_text(self, 
                       text: str, 
                       max_length: int = 150,
                       summary_type: str = "brief") -> SummaryResult:
        """
        Generate AI summary of text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            summary_type: "brief" (1-2 sentences) or "detailed" (paragraph)
        
        Returns:
            SummaryResult with summary and metadata
        """
        if not self.initialized or not self.summarizer:
            # Fallback to extractive summarization
            return self._extractive_summary(text, max_length)
        
        try:
            # Clean and prepare text
            text = self._clean_text(text)
            
            # Adjust parameters based on summary type
            if summary_type == "brief":
                max_len = min(max_length, 80)
                min_len = 20
            else:
                max_len = max_length
                min_len = 50
            
            # Generate summary
            result = self.summarizer(
                text,
                max_length=max_len,
                min_length=min_len,
                do_sample=False,
                truncation=True
            )
            
            summary = result[0]['summary_text'] if result else ""
            
            # Extract key points
            key_points = self._extract_key_points(text, summary)
            
            return SummaryResult(
                summary=summary,
                key_points=key_points,
                confidence=0.85,  # Model-based summaries have high confidence
                model_used=self.model_name
            )
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return self._extractive_summary(text, max_length)
    
    def summarize_search_results(self, 
                                 results: List[Dict],
                                 query: str,
                                 summary_type: str = "brief") -> str:
        """
        Summarize search results into a coherent response.
        For now, using intelligent extraction rather than AI generation
        due to T5-small limitations.
        """
        if not results:
            return "No relevant information found."
        
        # Get the top result content
        if not results[0].get('content'):
            return "No content available."
        
        content = results[0]['content']
        query_lower = query.lower()
        
        # Smart extraction based on query keywords
        # This will find relevant sections and extract meaningful content
        lines = content.split('\n')
        relevant_sections = []
        current_section = []
        section_relevance = 0
        
        # Keywords to look for based on common queries
        query_keywords = query_lower.split()
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if this line is relevant to the query
            relevance_score = sum(1 for keyword in query_keywords if keyword in line_lower)
            
            # If we find a header or relevant line, start/continue section
            if relevance_score > 0 or line.startswith('#') or line.startswith('*'):
                if relevance_score > 0:
                    section_relevance = max(section_relevance, relevance_score)
                current_section.append(line)
                
                # Also grab the next few lines for context
                for j in range(1, min(4, len(lines) - i)):
                    if i + j < len(lines):
                        next_line = lines[i + j]
                        if next_line.strip():  # Non-empty line
                            current_section.append(next_line)
                        if next_line.startswith('#'):  # Stop at next header
                            break
            
            # When we hit a blank line or new section, save the current section if relevant
            if (not line.strip() or line.startswith('#')) and current_section and section_relevance > 0:
                section_text = '\n'.join(current_section)
                if len(section_text) > 50:  # Only keep meaningful sections
                    relevant_sections.append((section_relevance, section_text))
                current_section = []
                section_relevance = 0
        
        # Add the last section if relevant
        if current_section and section_relevance > 0:
            section_text = '\n'.join(current_section)
            if len(section_text) > 50:
                relevant_sections.append((section_relevance, section_text))
        
        # Sort by relevance and combine
        relevant_sections.sort(key=lambda x: x[0], reverse=True)
        
        if not relevant_sections:
            # If no relevant sections found, return the beginning of the content
            return self._clean_text(content[:1000])
        
        # Combine top relevant sections up to ~1000 characters
        summary_parts = []
        total_length = 0
        
        for _, section in relevant_sections:
            clean_section = self._clean_text(section)
            if total_length + len(clean_section) < 1000:
                summary_parts.append(clean_section)
                total_length += len(clean_section)
            else:
                # Add partial section to reach ~1000 chars
                remaining = 1000 - total_length
                if remaining > 100:
                    summary_parts.append(clean_section[:remaining] + "...")
                break
        
        return '\n\n'.join(summary_parts)
    
    def _clean_text(self, text: str) -> str:
        """Clean text for summarization"""
        # Remove markdown formatting
        text = re.sub(r'#{1,6}\s*', '', text)
        text = re.sub(r'\*{1,2}([^\*]+)\*{1,2}', r'\1', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()
    
    def _extract_key_points(self, text: str, summary: str) -> List[str]:
        """Extract key points from text"""
        # Simple sentence-based extraction
        sentences = text.split('.')
        key_points = []
        
        # Find sentences with important markers
        important_markers = ['important', 'key', 'main', 'primary', 'critical', 
                            'essential', 'must', 'should', 'responsible', 'include']
        
        for sentence in sentences[:10]:  # Check first 10 sentences
            sentence_lower = sentence.lower()
            if any(marker in sentence_lower for marker in important_markers):
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 20 and len(clean_sentence) < 200:
                    key_points.append(clean_sentence)
                    if len(key_points) >= 3:
                        break
        
        return key_points
    
    def _extractive_summary(self, text: str, max_length: int) -> SummaryResult:
        """Fallback extractive summarization using sentence scoring"""
        sentences = text.split('.')
        
        if len(sentences) <= 2:
            return SummaryResult(
                summary=text[:max_length],
                key_points=[],
                confidence=0.6,
                model_used="extractive"
            )
        
        # Score sentences by position and length
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if 20 < len(sentence) < 300:
                # Higher score for earlier sentences
                score = 1.0 / (i + 1) + len(sentence) / 100
                scored_sentences.append((score, sentence))
        
        # Sort by score and take top sentences
        scored_sentences.sort(reverse=True)
        summary_sentences = [s[1] for s in scored_sentences[:3]]
        summary = '. '.join(summary_sentences) + '.'
        
        return SummaryResult(
            summary=summary[:max_length],
            key_points=summary_sentences[:2],
            confidence=0.6,
            model_used="extractive"
        )
    
    def _combine_results(self, results: List[Dict], query: str) -> str:
        """Combine search results - focus on the top result for better relevance"""
        combined = []
        
        logger.info(f"Combining {len(results)} results for query: {query}")
        
        # For summarization, primarily use the TOP result (highest relevance)
        # This avoids mixing in lower-quality content
        if results:
            # Take the full content of the top result (up to 2000 chars)
            top_content = results[0].get('content', '')
            logger.info(f"Top result content length: {len(top_content)} chars")
            logger.info(f"Top result preview: {top_content[:200]}...")
            
            # Clean and use more of the top result
            clean_content = self._clean_text(top_content[:2000])
            combined.append(clean_content)
            
            # Only add secondary results if they're highly relevant and we need more context
            if len(clean_content) < 500 and len(results) > 1:
                # Add a bit from the second result if the first is too short
                second_content = results[1].get('content', '')[:500]
                clean_second = self._clean_text(second_content)
                if clean_second:
                    combined.append(clean_second)
        
        combined_text = '\n\n'.join(combined)
        logger.info(f"Combined text length: {len(combined_text)} chars")
        return combined_text
    
    def _create_structured_summary(self, results: List[Dict], query: str) -> str:
        """Create a structured summary from search results"""
        if not results:
            return "No information available."
        
        # Extract key information from results
        key_points = []
        
        for result in results[:3]:
            content = result.get('content', '')
            if content:
                # Extract first meaningful sentence
                sentences = content.split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 20 and len(sentence) < 150:
                        # Clean the sentence
                        sentence = self._clean_text(sentence)
                        if sentence and sentence not in key_points:
                            key_points.append(sentence)
                            break
        
        if key_points:
            # Create a concise summary from key points
            summary = '. '.join(key_points[:2]) + '.'
            return summary[:300]  # Limit length
        
        # Ultimate fallback
        content = results[0].get('content', '')[:200]
        return self._clean_text(content)


class ConversationalContext:
    """
    Manages conversational context for follow-up queries.
    """
    
    def __init__(self, window_size: int = 2):
        """
        Initialize context manager.
        
        Args:
            window_size: Number of previous messages to consider
        """
        self.window_size = window_size
        self.context_window = []
    
    def add_interaction(self, query: str, response: str):
        """Add a query-response pair to context"""
        self.context_window.append({
            'query': query,
            'response': response[:500]  # Limit response size
        })
        
        # Maintain window size
        if len(self.context_window) > self.window_size:
            self.context_window.pop(0)
    
    def expand_query(self, query: str) -> Tuple[str, bool]:
        """
        Expand query using conversational context.
        
        Args:
            query: Current user query
        
        Returns:
            Tuple of (expanded_query, was_expanded)
        """
        if not self.context_window:
            return query, False
        
        query_lower = query.lower()
        
        # Check for follow-up patterns
        follow_up_patterns = [
            'tell me more',
            'more about',
            'what about',
            'how about',
            'and what',
            'anything else',
            'elaborate',
            'explain further',
            'more details',
            'more information'
        ]
        
        is_follow_up = any(pattern in query_lower for pattern in follow_up_patterns)
        
        # Check for pronouns that need resolution
        pronouns = ['it', 'this', 'that', 'these', 'those', 'them', 'their', 'his', 'her']
        has_pronoun = any(f' {pronoun} ' in f' {query_lower} ' for pronoun in pronouns)
        
        if is_follow_up or has_pronoun:
            # Get last interaction
            last_interaction = self.context_window[-1]
            last_query = last_interaction['query']
            last_response = last_interaction['response']
            
            # Extract main topic from last interaction
            topic = self._extract_topic(last_query, last_response)
            
            if is_follow_up:
                # Expand follow-up query
                if 'tell me more' in query_lower:
                    expanded = f"{topic} - provide more detailed information"
                elif 'what about' in query_lower:
                    # Keep the part after "what about"
                    parts = query_lower.split('what about')
                    if len(parts) > 1:
                        expanded = f"{parts[1].strip()} related to {topic}"
                    else:
                        expanded = f"More information about {topic}"
                else:
                    expanded = f"{query} regarding {topic}"
            else:
                # Pronoun resolution
                expanded = self._resolve_pronouns(query, topic)
            
            return expanded, True
        
        return query, False
    
    def _extract_topic(self, query: str, response: str) -> str:
        """Extract main topic from previous interaction"""
        # Simple extraction - take key nouns from query
        # In production, would use NER or more sophisticated extraction
        
        # Remove common words
        stop_words = {'what', 'who', 'where', 'when', 'how', 'is', 'are', 'the', 
                     'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        
        words = query.lower().split()
        topic_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        if topic_words:
            return ' '.join(topic_words[:3])  # Take first 3 meaningful words
        return "the previous topic"
    
    def _resolve_pronouns(self, query: str, topic: str) -> str:
        """Simple pronoun resolution"""
        # Replace pronouns with the topic
        resolved = query
        pronouns_to_replace = {
            ' it ': f' {topic} ',
            ' its ': f" {topic}'s ",
            ' this ': f' {topic} ',
            ' that ': f' {topic} ',
        }
        
        for pronoun, replacement in pronouns_to_replace.items():
            resolved = resolved.replace(pronoun, replacement)
        
        return resolved
    
    def get_context_prompt(self) -> str:
        """Get formatted context for inclusion in prompts"""
        if not self.context_window:
            return ""
        
        context_parts = []
        for interaction in self.context_window:
            context_parts.append(f"Previous Q: {interaction['query']}")
            context_parts.append(f"Previous A: {interaction['response'][:200]}...")
        
        return "\n".join(context_parts)
    
    def clear(self):
        """Clear conversation context"""
        self.context_window = []