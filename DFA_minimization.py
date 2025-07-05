import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import networkx as nx
import xml.dom.minidom as minidom

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    alphabets = []
    alphabets_element = root.find('Alphabets')
    for alpha in alphabets_element.findall('alphabet'):
        alphabets.append(alpha.get('letter'))
    
    states = []
    states_element = root.find('States')
    for state in states_element.findall('state'):
        states.append(state.get('name'))
    
    initial = states_element.find('initialState').get('name')
    
    finals = set()
    for final in states_element.find('FinalStates').findall('finalState'):
        finals.add(final.get('name'))
    
    transitions = {}
    for state in states:
        transitions[state] = {}
        for symbol in alphabets:
            transitions[state][symbol] = None
    
    for trans in root.find('Transitions').findall('transition'):
        source = trans.get('source')
        label = trans.get('label')
        destination = trans.get('destination')
        transitions[source][label] = destination
    
    return alphabets, states, initial, finals, transitions

def find_reachable_states(alphabet, initial, transitions):
    reachable = set([initial])
    queue = [initial]
    
    while queue:
        current = queue.pop(0)
        for symbol in alphabet:
            next_state = transitions[current][symbol]
            if next_state and next_state not in reachable:
                reachable.add(next_state)
                queue.append(next_state)
    
    return reachable

def minimize_dfa(alphabets, states, finals, transitions, reachable):
    states = [s for s in states if s in reachable]
    finals = [s for s in finals if s in reachable]
   
    n = len(states)
    table = [[0 for _ in range(n)] for _ in range(n)]
    
    
    for i in range(n):
        for j in range(i):
            if (states[i] in finals) != (states[j] in finals):
                table[i][j] = 1
    
    
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in range(i):
                if table[i][j] == 0:
                    for a in alphabets:
                        p = transitions[states[i]][a]
                        q = transitions[states[j]][a]
                        ip = states.index(p)
                        jp = states.index(q)
                        if ip < jp:
                            ip, jp = jp, ip
                        if table[ip][jp] == 1:
                            table[i][j] = 1
                            changed = True
                            break
    
    
    equivalent = [i for i in range(n)]
    for i in range(n):
        for j in range(i):
            if table[i][j] == 0:
                equivalent[i] = equivalent[j]
    

    partitions = {}
    for i, eq in enumerate(equivalent):
        if eq not in partitions:
            partitions[eq] = set()
        partitions[eq].add(states[i])
    
    return list(partitions.values())

def build_minimized_dfa(partitions, alphabets, initial, finals, transitions):
    state_map = {}
    minimized_states = set()
    minimized_finals = set()
    minimized_transitions = {}
    

    for partition in partitions:
        state_nums = [s.replace('q', '') for s in partition]
        state_name = 'q' + ''.join(sorted(state_nums))

        state_map[frozenset(partition)] = state_name
        minimized_states.add(state_name)
        
        
        if initial in partition:
            minimized_initial = state_name
        
        
        if partition & finals:
            minimized_finals.add(state_name)
    
    
    for partition in partitions:
        state_name = state_map[frozenset(partition)]
        minimized_transitions[state_name] = {}
        
        
        sample_state = next(iter(partition))
        
        for a in alphabets:
            next_state = transitions[sample_state][a]
            
            for p in partitions:
                if next_state in p:
                        minimized_transitions[state_name][a] = state_map[frozenset(p)]
                        break
    
    return minimized_states, minimized_initial, minimized_finals, minimized_transitions

def create_xml_output(alphabets, states, initial, finals, transitions):
    root = ET.Element("Automata", type="DFA")
    
    alphabets_elem = ET.SubElement(root, "Alphabets", numberOfAlphabets=str(len(alphabets)))
    for a in alphabets:
        ET.SubElement(alphabets_elem, "alphabet", letter=a)
    
    states_elem = ET.SubElement(root, "States", numberOfStates=str(len(states)))
    for s in sorted(states):
        ET.SubElement(states_elem, "state", name=s)
    ET.SubElement(states_elem, "initialState", name=initial)
    
    finals_elem = ET.SubElement(states_elem, "FinalStates", numberOfFinalStates=str(len(finals)))
    for f in sorted(finals):
        ET.SubElement(finals_elem, "finalState", name=f)
    
    trans_elem = ET.SubElement(root, "Transitions", numberOfTrans=str(sum(len(t) for t in transitions.values())))
    for src in sorted(transitions):
        for label in sorted(transitions[src]):
            ET.SubElement(trans_elem, "transition", 
                         source=src,
                         destination=transitions[src][label],
                         label=label)
            
    pretty_xml = minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent="    ")
    return pretty_xml


def draw_dfa(states, initial, finals, transitions):   
    plt.figure(figsize=(7, 5))
    G = nx.DiGraph()
    
    
    for state in states:
        G.add_node(state, shape='circle')
    
    
    edge_labels = {}
    for src in transitions:
        for label, dest in transitions[src].items():
            if (src, dest) in edge_labels:
                edge_labels[(src, dest)].append(label)
            else:
                edge_labels[(src, dest)] = [label]
    
   
    for (src, dest), labels in edge_labels.items():
        G.add_edge(src, dest, label=", ".join(sorted(labels)))
    
    
    pos = nx.spring_layout(G, seed=42)
    
    
    nx.draw_networkx_nodes(G, pos, nodelist=[s for s in states if s not in finals], node_size=300, node_color='lightblue')
    
    
    nx.draw_networkx_nodes(G, pos, nodelist=finals, node_size=300, node_shape='d', node_color='lightgreen')
    
    
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=10, width=1)
    
    
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    
    
    plt.annotate("", xy=pos[initial], xytext=(pos[initial][0], pos[initial][1]-0.2), arrowprops=dict(arrowstyle="->", lw=1, color='black'))
    
    plt.title("Minimized DFA", size=10)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def minimize_dfa_with_table(xml_file):
    alphabets, states, initial, finals, transitions = parse_xml(xml_file)
    reachable = find_reachable_states(alphabets, initial, transitions)
    partitions = minimize_dfa(alphabets, states, finals, transitions, reachable)
    minimized_states, minimized_initial, minimized_finals, minimized_trans = build_minimized_dfa(partitions, alphabets, initial, finals, transitions)
    output_xml = create_xml_output(alphabets, minimized_states, minimized_initial, minimized_finals, minimized_trans)
    open("minimized_dfa.xml", "w").write(output_xml)
    draw_dfa(states, initial, finals, transitions)
    draw_dfa(minimized_states, minimized_initial, minimized_finals, minimized_trans)
    
minimize_dfa_with_table("DFA.xml")
