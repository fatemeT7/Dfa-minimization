### DFA Minimization Tool

This Python project implements a Deterministic Finite Automaton (DFA) minimization algorithm using the table-filling method. It reads a DFA from an XML file, minimizes it, outputs the minimized DFA as XML, and generates visualizations of both original and minimized DFAs.

## Features
- XML Parsing: Reads DFA definitions from structured XML files
- Reachability Analysis: Identifies and removes unreachable states
- Minimization Algorithm: Implements the table-filling method for DFA minimization
- Visualization: Generates graph visualizations using NetworkX and Matplotlib
- XML Output: Saves minimized DFA in XML format with pretty-printing

## Requirements
- Python 3.6+
- Required libraries:
 
  pip install matplotlib networkx
  
## Usage
1. Prepare your DFA definition in DFA.xml (see format below)
2. Run the minimization script:
  
   python DFA_minimization.py
   
3. Outputs:
   - minimized_dfa.xml: Minimized DFA in XML format
   - Two pop-up windows showing:
     - Original DFA visualization
     - Minimized DFA visualization
