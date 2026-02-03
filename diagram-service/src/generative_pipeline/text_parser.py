import re
import networkx as nx
from typing import List, Dict, Any, Tuple

from src.core.logger import app_logger
from src.core.exceptions import TextParsingError
from src.utils.graph_utils import create_directed_graph, add_node, add_edge


class TextToGraphParser:
    def __init__(self):
        app_logger.info("TextToGraphParser initialized")
        
        self.step_patterns = [
            r'(?:шаг|step)\s*\d+[:\.]?\s*(.+?)(?=шаг|step|\.|$)',
            r'(?:затем|then|далее|next)[:\s]+(.+?)(?=затем|then|далее|next|\.|$)',
            r'(?:выполнить|execute|сделать|do)[:\s]+(.+?)(?=\.|$)',
        ]
        
        self.condition_patterns = [
            r'если\s+(.+?)\s*,?\s*то\s+(.+?)(?:иначе|else)\s+(.+?)(?=\.|$)',
            r'if\s+(.+?)\s*then\s+(.+?)(?:else)\s+(.+?)(?=\.|$)',
            r'проверить\s+(.+?)(?=\.|$)',
            r'условие[:\s]+(.+?)(?=\.|$)',
        ]
        
        self.start_keywords = ['начало', 'start', 'старт', 'begin']
        self.end_keywords = ['конец', 'end', 'финиш', 'finish', 'stop', 'завершение']
    
    def parse(self, text: str) -> nx.DiGraph:
        try:
            app_logger.debug(f"Parsing text of length {len(text)}")
            
            sentences = self._split_into_sentences(text)
            app_logger.debug(f"Split into {len(sentences)} sentences")
            
            graph = create_directed_graph()
            
            node_counter = 0
            previous_node = None
            
            for sentence in sentences:
                sentence_lower = sentence.lower().strip()
                
                if not sentence_lower:
                    continue
                
                if any(kw in sentence_lower for kw in self.start_keywords):
                    node_id = f"node_{node_counter}"
                    add_node(graph, node_id, type='start', label=sentence.strip())
                    previous_node = node_id
                    node_counter += 1
                    app_logger.debug(f"Added start node: {node_id}")
                
                elif any(kw in sentence_lower for kw in self.end_keywords):
                    node_id = f"node_{node_counter}"
                    add_node(graph, node_id, type='end', label=sentence.strip())
                    if previous_node:
                        add_edge(graph, previous_node, node_id)
                    previous_node = node_id
                    node_counter += 1
                    app_logger.debug(f"Added end node: {node_id}")
                
                elif self._is_condition(sentence_lower):
                    condition_result = self._parse_condition(sentence)
                    if condition_result:
                        decision_node = f"node_{node_counter}"
                        add_node(graph, decision_node, type='decision', label=condition_result['condition'])
                        
                        if previous_node:
                            add_edge(graph, previous_node, decision_node)
                        
                        node_counter += 1
                        
                        true_node = f"node_{node_counter}"
                        add_node(graph, true_node, type='process', label=condition_result.get('true_branch', 'Да'))
                        add_edge(graph, decision_node, true_node, label='Да')
                        node_counter += 1
                        
                        false_node = f"node_{node_counter}"
                        add_node(graph, false_node, type='process', label=condition_result.get('false_branch', 'Нет'))
                        add_edge(graph, decision_node, false_node, label='Нет')
                        node_counter += 1
                        
                        previous_node = decision_node
                        app_logger.debug(f"Added decision node: {decision_node}")
                    else:
                        node_id = f"node_{node_counter}"
                        add_node(graph, node_id, type='decision', label=sentence.strip())
                        if previous_node:
                            add_edge(graph, previous_node, node_id)
                        previous_node = node_id
                        node_counter += 1
                
                else:
                    node_id = f"node_{node_counter}"
                    add_node(graph, node_id, type='process', label=sentence.strip())
                    if previous_node:
                        add_edge(graph, previous_node, node_id)
                    previous_node = node_id
                    node_counter += 1
                    app_logger.debug(f"Added process node: {node_id}")
            
            if graph.number_of_nodes() == 0:
                add_node(graph, "node_0", type='start', label='Начало')
                add_node(graph, "node_1", type='process', label=text[:100])
                add_node(graph, "node_2", type='end', label='Конец')
                add_edge(graph, "node_0", "node_1")
                add_edge(graph, "node_1", "node_2")
            
            app_logger.info(f"Parsed text into graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
            return graph
            
        except Exception as e:
            app_logger.error(f"Text parsing failed: {str(e)}", exc_info=True)
            raise TextParsingError(f"Failed to parse text: {str(e)}")
    
    def _split_into_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'[\.!?;]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _is_condition(self, text: str) -> bool:
        condition_keywords = ['если', 'if', 'условие', 'condition', 'проверить', 'check', '?']
        return any(kw in text for kw in condition_keywords)
    
    def _parse_condition(self, sentence: str) -> Dict[str, str]:
        for pattern in self.condition_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 3:
                    return {
                        'condition': groups[0].strip(),
                        'true_branch': groups[1].strip(),
                        'false_branch': groups[2].strip()
                    }
                elif len(groups) >= 1:
                    return {
                        'condition': groups[0].strip()
                    }
        
        return {'condition': sentence.strip()}
    
    def extract_steps(self, text: str) -> List[str]:
        steps = []
        
        for pattern in self.step_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            steps.extend([m.strip() for m in matches])
        
        if not steps:
            steps = self._split_into_sentences(text)
        
        return steps
    
    def parse_structured(self, text: str) -> Dict[str, Any]:
        graph = self.parse(text)
        
        return {
            'nodes': [
                {
                    'id': node,
                    'type': graph.nodes[node].get('type', 'process'),
                    'label': graph.nodes[node].get('label', '')
                }
                for node in graph.nodes()
            ],
            'edges': [
                {
                    'source': source,
                    'target': target,
                    'label': graph.edges[source, target].get('label', '')
                }
                for source, target in graph.edges()
            ]
        }
