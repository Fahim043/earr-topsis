import graphviz
import os

out_dir = "/Users/fahimafridi/Downloads/Folders10000/Research/thesis-topsis/diagrams"
os.makedirs(out_dir, exist_ok=True)

def create_m1():
    dot = graphviz.Digraph(comment='M1: Normal Fuzzy TOPSIS', format='png')
    dot.attr(rankdir='TD', size='8,8', dpi='300')
    dot.attr('node', shape='box', style='filled', fillcolor='#E8F5E9', fontname='Arial')
    
    dot.node('A', 'All K Decision Makers\n(Fuzzy Ratings)')
    dot.node('B', 'Aggregate Fuzzy Ratings\n(Min L, Mean M, Max U)')
    dot.node('C', 'Normalize Fuzzy Decision Matrix')
    dot.node('D', 'Apply Criteria Weights')
    dot.node('E', 'Calculate Distances to\nFPIS (d*) and FNIS (d-)')
    dot.node('F', 'Compute Closeness Coefficient (CC_i)')
    dot.node('G', 'Final Ranking\n(Vulnerable to Bias)', fillcolor='#FFCDD2')
    
    dot.edges(['AB', 'BC', 'CD', 'DE', 'EF', 'FG'])
    dot.render(os.path.join(out_dir, 'm1_normal_topsis'), cleanup=True)

def create_m2():
    dot = graphviz.Digraph(comment='M2: Bagged Fuzzy TOPSIS', format='png')
    dot.attr(rankdir='TD', size='10,8', dpi='300')
    dot.attr('node', shape='box', style='filled', fillcolor='#E3F2FD', fontname='Arial')
    
    dot.node('A', 'All K Decision Makers')
    dot.node('S', 'Uniform Random Sampling\n(With Replacement)', fillcolor='#FFF9C4', shape='ellipse')
    
    with dot.subgraph(name='cluster_bags') as c:
        c.attr(style='dashed', color='gray', label='Ensemble Process')
        c.node('B1', 'Bag 1\n(S DMs)')
        c.node('B2', 'Bag 2\n(S DMs)')
        c.node('Dots', '...', shape='none', fillcolor='white')
        c.node('BN', 'Bag B\n(S DMs)')
        
        c.node('T1', 'Fuzzy TOPSIS')
        c.node('T2', 'Fuzzy TOPSIS')
        c.node('TN', 'Fuzzy TOPSIS')
        
        c.edge('B1', 'T1')
        c.edge('B2', 'T2')
        c.edge('BN', 'TN')
        
    dot.node('AGG', 'Mean Ensemble Aggregation\n(Average CC_i)', fillcolor='#FFF9C4', shape='ellipse')
    dot.node('R', 'Variance-Reduced Ranking', fillcolor='#C8E6C9')

    dot.edge('A', 'S')
    dot.edge('S', 'B1')
    dot.edge('S', 'B2')
    dot.edge('S', 'BN')
    dot.edge('T1', 'AGG')
    dot.edge('T2', 'AGG')
    dot.edge('TN', 'AGG')
    dot.edge('AGG', 'R')
    dot.render(os.path.join(out_dir, 'm2_bagged_topsis'), cleanup=True)

def create_m3():
    dot = graphviz.Digraph(comment='M3: ML-Filtered Fuzzy TOPSIS', format='png')
    dot.attr(rankdir='TD', size='10,8', dpi='300')
    dot.attr('node', shape='box', style='filled', fillcolor='#F3E5F5', fontname='Arial')
    
    dot.node('A', 'All K Decision Makers')
    dot.node('F', 'Feature Extraction\n(Vectorize Ratings)')
    dot.node('ML', 'Machine Learning\n(K-Means / Isolation Forest)', fillcolor='#FFF9C4', shape='ellipse')
    dot.node('R', 'Calculate Reliability Score (R_k)\nvia Distance to Majority')
    
    dot.node('Cond', 'Filter: Is R_k > \u03C4?', shape='diamond', fillcolor='#FFE0B2')
    dot.node('Discard', 'Discard DM', fillcolor='#FFCDD2')
    dot.node('Keep', 'Keep Trustworthy DMs', fillcolor='#C8E6C9')
    
    dot.node('T', 'Standard Fuzzy TOPSIS')
    dot.node('Final', 'Cleaned Ranking')

    dot.edge('A', 'F')
    dot.edge('F', 'ML')
    dot.edge('ML', 'R')
    dot.edge('R', 'Cond')
    dot.edge('Cond', 'Keep', label='Yes')
    dot.edge('Cond', 'Discard', label='No')
    dot.edge('Keep', 'T')
    dot.edge('T', 'Final')
    dot.render(os.path.join(out_dir, 'm3_ml_filtered'), cleanup=True)

def create_m4():
    dot = graphviz.Digraph(comment='M4: Weighted Bagging', format='png')
    dot.attr(rankdir='TD', size='10,8', dpi='300')
    dot.attr('node', shape='box', style='filled', fillcolor='#FFF3E0', fontname='Arial')

    dot.node('A', 'All K Decision Makers')
    dot.node('R', 'Compute Reliability Score (R_k)\nper DM via ML', fillcolor='#FFF9C4', shape='ellipse')
    dot.node('W', 'Weighted Sampling\nProbability P(k) \u221D R_k')
    
    with dot.subgraph(name='cluster_bags') as c:
        c.attr(style='dashed', color='gray', label='Reliability-Biased Ensemble')
        c.node('B1', 'Bag 1\n(High Reliable DMs chosen more)')
        c.node('Dots', '...', shape='none', fillcolor='white')
        c.node('BN', 'Bag B\n(High Reliable DMs chosen more)')
        
        c.node('T1', 'Fuzzy TOPSIS')
        c.node('TN', 'Fuzzy TOPSIS')
        
        c.edge('B1', 'T1')
        c.edge('BN', 'TN')

    dot.node('AGG', 'Mean Ensemble Aggregation', fillcolor='#FFF9C4', shape='ellipse')
    dot.node('Final', 'Reliability-Biased Ranking', fillcolor='#C8E6C9')

    dot.edge('A', 'R')
    dot.edge('R', 'W')
    dot.edge('W', 'B1')
    dot.edge('W', 'BN')
    dot.edge('T1', 'AGG')
    dot.edge('TN', 'AGG')
    dot.edge('AGG', 'Final')
    dot.render(os.path.join(out_dir, 'm4_weighted_bagging'), cleanup=True)

def create_m5():
    dot = graphviz.Digraph(comment='M5: Cluster-Stratified Bagging', format='png')
    dot.attr(rankdir='TD', size='10,8', dpi='300')
    dot.attr('node', shape='box', style='filled', fillcolor='#E0F7FA', fontname='Arial')

    dot.node('A', 'All K Decision Makers')
    dot.node('C', 'Spectral Clustering\n(Identify Optimistic, Pessimistic, Central Groups)', fillcolor='#FFF9C4', shape='ellipse')
    dot.node('S', 'Proportional Stratified Sampling\n(Maintain cluster ratios in every bag)')
    
    with dot.subgraph(name='cluster_bags') as c:
        c.attr(style='dashed', color='gray', label='Stratified Ensemble')
        c.node('B1', 'Bag 1\n(Balanced Mix of DMs)')
        c.node('Dots', '...', shape='none', fillcolor='white')
        c.node('BN', 'Bag B\n(Balanced Mix of DMs)')
        
        c.node('T1', 'Fuzzy TOPSIS')
        c.node('TN', 'Fuzzy TOPSIS')
        
        c.edge('B1', 'T1')
        c.edge('BN', 'TN')

    dot.node('AGG', 'Mean Ensemble Aggregation', fillcolor='#FFF9C4', shape='ellipse')
    dot.node('Final', 'Stratified Robust Ranking', fillcolor='#C8E6C9')

    dot.edge('A', 'C')
    dot.edge('C', 'S')
    dot.edge('S', 'B1')
    dot.edge('S', 'BN')
    dot.edge('T1', 'AGG')
    dot.edge('TN', 'AGG')
    dot.edge('AGG', 'Final')
    dot.render(os.path.join(out_dir, 'm5_cluster_stratified'), cleanup=True)

def create_m6():
    dot = graphviz.Digraph(comment='M6: Reliability-Weighted Aggregation', format='png')
    dot.attr(rankdir='TD', size='10,8', dpi='300')
    dot.attr('node', shape='box', style='filled', fillcolor='#FBE9E7', fontname='Arial')

    dot.node('A', 'All K Decision Makers')
    dot.node('U', 'Uniform Random Sampling')
    
    with dot.subgraph(name='cluster_bags') as c:
        c.attr(style='dashed', color='gray', label='Weighted Aggregation Process')
        
        c.node('B1', 'Bag 1')
        c.node('R1', 'Compute Bag\nReliability (R_B1)', shape='ellipse', fillcolor='#FFF9C4')
        c.node('T1', 'Fuzzy TOPSIS')
        c.edge('B1', 'R1')
        c.edge('B1', 'T1')
        
        c.node('Dots', '...', shape='none', fillcolor='white')
        
        c.node('BN', 'Bag B')
        c.node('RN', 'Compute Bag\nReliability (R_BN)', shape='ellipse', fillcolor='#FFF9C4')
        c.node('TN', 'Fuzzy TOPSIS')
        c.edge('BN', 'RN')
        c.edge('BN', 'TN')

    dot.node('W', 'Calculate Normalized\nEnsemble Weights (W_b)')
    dot.node('AGG', 'Weighted Summation:\nCC_i = \u2211(W_b * CC_i_b)', fillcolor='#FFF9C4', shape='ellipse')
    dot.node('Final', 'Final Robust Ranking', fillcolor='#C8E6C9')

    dot.edge('A', 'U')
    dot.edge('U', 'B1')
    dot.edge('U', 'BN')
    dot.edge('R1', 'W')
    dot.edge('RN', 'W')
    dot.edge('W', 'AGG')
    dot.edge('T1', 'AGG')
    dot.edge('TN', 'AGG')
    dot.edge('AGG', 'Final')
    dot.render(os.path.join(out_dir, 'm6_reliability_weighted'), cleanup=True)

if __name__ == '__main__':
    create_m1()
    create_m2()
    create_m3()
    create_m4()
    create_m5()
    create_m6()
    print("Graphviz diagram generation complete.")
