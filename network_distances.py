import networkx as nx
import netrd
from netrd.utilities import entropy, ensure_undirected
import numpy as np
import community # install with "pip install python-louvain"
import cmocean as cmo
from collections import defaultdict
from collections import Counter
import scipy as sp
import scipy.sparse as sparse
import math
from ortools.linear_solver import pywraplp
import matplotlib.pyplot as plt
import glob
import itertools

from netrd.distance import PortraitDivergence
from netrd.distance import OnionDivergence
from netrd.distance import DistributionalNBD
from netrd.distance import NetSimile
from netrd.distance import PolynomialDissimilarity
from netrd.distance import CommunicabilityJSD
from netrd.distance import ResistancePerturbation
from netrd.distance import QuantumJSD
from netrd.distance import DeltaCon
from netrd.distance import HammingIpsenMikhailov
from netrd.distance import IpsenMikhailov
from netrd.distance import LaplacianSpectral
from netrd.distance import JaccardDistance
from netrd.distance import DegreeDivergence
from netrd.distance import Frobenius
from netrd.distance import Hamming
from netrd.distance import NetLSD
from netrd.distance import DMeasure
#from netrd.distance import ResilienceDistance

#from extra_distances import *



def LJ(G1, G2):
    D = netrd.distance.LaplacianSpectral()
    d = D.dist(G1, G2, kernel='lorentzian')
    return d


def LE(G1, G2):
    D = netrd.distance.LaplacianSpectral()
    d = D.dist(G1, G2, kernel='lorentzian', measure='euclidean')
    return d


def NJ(G1, G2):
    D = netrd.distance.LaplacianSpectral()
    d = D.dist(G1, G2)
    return d


def NE(G1, G2):
    D = netrd.distance.LaplacianSpectral()
    d = D.dist(G1, G2, measure='euclidean')
    return d

def dk3Distance():
    """
    
    """

    return


def euclidean_distance(x, y):
    return math.sqrt(sum((a - b)**2 for (a, b) in zip(x, y)))


def nbvals(graph, topk='automatic', batch=100, tol=1e-5):
    """Compute the largest-magnitude non-backtracking eigenvalues.

    Parameters
    ----------

    graph (nx.Graph): The graph.

    topk (int or 'automatic'): The number of eigenvalues to compute.  The
    maximum number of eigenvalues that can be computed is 2*n - 4, where n
    is the number of nodes in graph.  All the other eigenvalues are equal
    to +-1. If 'automatic', return all eigenvalues whose magnitude is
    larger than the square root of the largest eigenvalue.

    batch (int): If topk is 'automatic', compute this many eigenvalues at a
    time until the condition is met.  Must be at most 2*n - 4; default 100.

    tol (float): Numerical tolerance.  Default 1e-5.

    Returns
    -------

    An array with the eigenvalues.

    """
    if not isinstance(topk, str) and topk < 1:
        return np.array([[], []])

    # The eigenvalues are left untouched by removing the nodes of degree 1.
    # Moreover, removing them makes the computations faster.  This
    # 'shaving' leaves us with the 2-core of the graph.
    core = shave(graph)
    matrix = pseudo_hashimoto(core)
    if not isinstance(topk, str) and topk > matrix.shape[0] - 1:
        topk = matrix.shape[0] - 2
        print('Computing only {} eigenvalues'.format(topk))

    if topk == 'automatic':
        batch = min(batch, 2 * graph.order() - 4)
        if 2 * graph.order() - 4 < batch:
            print('Using batch size {}'.format(batch))
        topk = batch

    N = matrix.shape[0]
    v0 = np.ones(N) / N
    eigs = lambda k: sparse.linalg.eigs(
        matrix, k=k, v0=v0, return_eigenvectors=False, tol=tol
    )

    count = 1
    while True:
        vals = eigs(topk * count)
        largest = np.sqrt(abs(max(vals, key=abs)))
        if abs(vals[0]) <= largest or topk != 'automatic':
            break
        count += 1
    if topk == 'automatic':
        vals = vals[abs(vals) > largest]

    # The eigenvalues are returned in no particular order, which may yield
    # different feature vectors for the same graph.  For example, if a
    # graph has a + ib and a - ib as eigenvalues, the eigenvalue solver may
    # return [..., a + ib, a - ib, ...] in one call and [..., a - ib, a +
    # ib, ...] in another call.  To avoid this, we sort the eigenvalues
    # first by absolute value, then by real part, then by imaginary part.
    vals = sorted(vals, key=lambda x: x.imag)
    vals = sorted(vals, key=lambda x: x.real)
    vals = np.array(sorted(vals, key=np.linalg.norm))

    # Return eigenvalues as a 2D array, with one row per eigenvalue, and
    # each row containing the real and imaginary parts separately.
    vals = np.array([(z.real, z.imag) for z in vals])
    return vals


def shave(graph):
    """Return the 2-core of a graph.

    Iteratively remove the nodes of degree 0 or 1, until all nodes have
    degree at least 2.

    """
    core = graph.copy()
    while True:
        to_remove = [node for node, neighbors in core.adj.items()
                     if len(neighbors) < 2]
        core.remove_nodes_from(to_remove)
        if len(to_remove) == 0:
            break
    return core


def pseudo_hashimoto(graph):
    """Return the pseudo-Hashimoto matrix.

    The pseudo Hashimoto matrix of a graph is the block matrix defined as
    B' = [0  D-I]
         [-I  A ]

    Where D is the degree-diagonal matrix, I is the identity matrix and A
    is the adjacency matrix.  The eigenvalues of B' are always eigenvalues
    of B, the non-backtracking or Hashimoto matrix.

    Parameters
    ----------

    graph (nx.Graph): A NetworkX graph object.

    Returns
    -------

    A sparse matrix in csr format.

    """
    # Note: the rows of nx.adjacency_matrix(graph) are in the same order as
    # the list returned by graph.nodes().
    degrees = graph.degree()
    degrees = sparse.diags([degrees[n] for n in graph.nodes()])
    adj = nx.adjacency_matrix(graph)
    ident = sparse.eye(graph.order())
    pseudo = sparse.bmat([[None, degrees - ident], [-ident, adj]])
    return pseudo.asformat('csr')


def half_incidence(graph, ordering='blocks', return_ordering=False):
    """Return the 'half-incidence' matrices of the graph.

    If the graph has n nodes and m *undirected* edges, then the
    half-incidence matrices are two matrices, P and Q, with n rows and 2m
    columns.  That is, there is one row for each node, and one column for
    each *directed* edge.  For P, the entry at (n, e) is equal to 1 if node
    n is the source (or tail) of edge e, and 0 otherwise.  For Q, the entry
    at (n, e) is equal to 1 if node n is the target (or head) of edge e,
    and 0 otherwise.

    Parameters
    ----------

    graph (nx.Graph): The graph.

    ordering (str): If 'blocks' (default), the two columns corresponding to
    the i'th edge are placed at i and i+m.  That is, choose an arbitarry
    direction for each edge in the graph.  The first m columns correspond
    to this orientation, while the latter m columns correspond to the
    reversed orientation.  Columns are sorted following graph.edges().  If
    'consecutive', the first two columns correspond to the two orientations
    of the first edge, the third and fourth row are the two orientations of
    the second edge, and so on.  In general, the two columns for the i'th
    edge are placed at 2i and 2i+1.

    return_ordering (bool): if True, return a function that maps an edge id
    to the column placement.  That is, if ordering=='blocks', return the
    function lambda x: (x, m+x), if ordering=='consecutive', return the
    function lambda x: (2*x, 2*x + 1).  If False, return None.


    Returns
    -------

    P (sparse matrix), Q (sparse matrix), ordering (function or None).


    Notes
    -----

    The nodes in graph must be labeled by consecutive integers starting at
    0.  This function always returns three values, regardless of the value
    of return_ordering.

    """
    numnodes = graph.order()
    numedges = graph.size()

    if ordering == 'blocks':
        src_pairs = lambda i, u, v: [(u, i), (v, numedges + i)]
        tgt_pairs = lambda i, u, v: [(v, i), (u, numedges + i)]
    if ordering == 'consecutive':
        src_pairs = lambda i, u, v: [(u, 2 * i), (v, 2 * i + 1)]
        tgt_pairs = lambda i, u, v: [(v, 2 * i), (u, 2 * i + 1)]

    def make_coo(make_pairs):
        """Make a sparse 0-1 matrix.

        The returned matrix has a positive entry at each coordinate pair
        returned by make_pairs, for all (idx, node1, node2) edge triples.

        """
        coords = list(
            zip(
                *(
                    pair
                    for idx, (node1, node2) in enumerate(graph.edges())
                    for pair in make_pairs(idx, node1, node2)
                )
            )
        )
        data = np.ones(2 * graph.size())
        return sparse.coo_matrix((data, coords), shape=(numnodes, 2*numedges))

    src = make_coo(src_pairs).asformat('csr')
    tgt = make_coo(tgt_pairs).asformat('csr')

    if return_ordering:
        if ordering == 'blocks':
            func = lambda x: (x, numedges + x)
        else:
            func = lambda x: (2 * x, 2 * x + 1)
        return src, tgt, func
    else:
        return src, tgt



def NonBacktrackingSpectral(G1, G2, topk='automatic', batch=100, tol=1e-5):
    """Non-Backtracking Distance between two graphs.

    Parameters
    ----------

    G1, G2 (nx.Graph)
        The graphs to compare.

    topk (int or 'automatic')
        The number of eigenvalues to compute. If `'automatic'` (default),
        use only the eigenvalues that are larger than the square root
        of the largest eigenvalue.  Note this may yield different
        number of eigenvalues for each graph.

    batch (int)
        If topk is `'automatic'`, this is the number of eigenvalues to
        compute each time until the condition is met. Default
        :math:`100`.

    tol (float)
        Numerical tolerance when computing eigenvalues.

    Returns
    -------
    float
        The distance between `G1` and `G2`

    """
    vals1 = nbvals(G1, topk, batch, tol)
    vals2 = nbvals(G2, topk, batch, tol)

    vals1 = [tuple(vals1[i]) for i in range(len(vals1))]
    vals2 = [tuple(vals2[i]) for i in range(len(vals2))]

    dist = earthmover_distance(vals1, vals2)

    return dist


def earthmover_distance(p1, p2):
    '''
    Output the Earthmover distance between the two given points.
    Arguments:
     - p1: an iterable of hashable iterables of numbers (i.e., list of tuples)
     - p2: an iterable of hashable iterables of numbers (i.e., list of tuples)
    '''
    dist1 = {x: count / len(p1) for (x, count) in Counter(p1).items()}
    dist2 = {x: count / len(p2) for (x, count) in Counter(p2).items()}
    solver = pywraplp.Solver('earthmover_distance',
                             pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

    variables = dict()

    # for each pile in dist1, constraint says all the dirt must leave this pile
    dirt_leaving_constraints = defaultdict(lambda: 0)

    # for each hole in dist2, constraint says this hole must be filled
    dirt_filling_constraints = defaultdict(lambda: 0)

    # the objective
    objective = solver.Objective()
    objective.SetMinimization()

    for (x, dirt_at_x) in dist1.items():
        for (y, capacity_of_y) in dist2.items():
            amount_to_move_x_y = solver.NumVar(0,
                                               solver.infinity(),
                                               'z_{%s, %s}' % (x, y))
            variables[(x, y)] = amount_to_move_x_y
            dirt_leaving_constraints[x] += amount_to_move_x_y
            dirt_filling_constraints[y] += amount_to_move_x_y
            objective.SetCoefficient(amount_to_move_x_y,
                                     sp.spatial.distance.euclidean(x, y))

    for x, linear_combination in dirt_leaving_constraints.items():
        solver.Add(linear_combination == dist1[x])

    for y, linear_combination in dirt_filling_constraints.items():
        solver.Add(linear_combination == dist2[y])

    status = solver.Solve()
    if status not in [solver.OPTIMAL, solver.FEASIBLE]:
        raise Exception('Unable to find feasible solution')

    for ((x, y), variable) in variables.items():
        if variable.solution_value() != 0:
            cost = euclidean_distance(x, y) * variable.solution_value()

    return objective.Value()

def matusita_dist(X, Y):
    r"""
    Return the Matusita distance between two vectors, $X$ and $Y$
    $$
    \sqrt{\sum_i \sum_j \left( \sqrt{X_{ij}} - \sqrt{Y_{ij}} \right)^{2}}
    $$

    Params
    ------
    X (np.ndarray): the first vector to compare
    Y (np.ndarray): the second vector to compare

    Returns
    -------
    d (float): the Matusita distance between X and Y

    """
    return np.sqrt(np.sum(np.square(np.sqrt(X) - np.sqrt(Y))))

def dk2Distance(G1, G2):
    r"""Compute the distance between two graphs by using the Jensen-Shannon
    divergence between the :math:`2k`-series of the graphs.
    The :math:`dk`-series of a graph is the collection of distributions of
    size :math:`d` subgraphs, where nodes are labelled by degrees. For
    simplicity, we consider only the :math:`2k`-series, i.e., the
    distribution of edges between nodes of degree :math:`(k_i, k_j)`. The
    distance between these :math:`2k`-series is calculated using the
    Jensen-Shannon divergence.
    Parameters
    ----------
    G1, G2 (nx.Graph)
        two networkx graphs to be compared
    Returns
    -------
    dist (float)
        the distance between `G1` and `G2`.
    References
    ----------
    .. [1] Orsini, Chiara, Marija M. Dankulov, Pol Colomer-de-Simón,
           Almerima Jamakovic, Priya Mahadevan, Amin Vahdat, Kevin E.
           Bassler, et al. 2015. “Quantifying Randomness in Real Networks.”
           Nature Communications 6 (1). https://doi.org/10.1038/ncomms9627.
    """

    def dk2_series(G):
        """
        Calculate the 2k-series (i.e. the number of edges between
        degree-labelled edges) for G.
        """

        k_dict = dict(nx.degree(G))
        dk2 = defaultdict(int)

        for (i, j) in G.edges:
            k_i = k_dict[i]
            k_j = k_dict[j]
            if k_i <= k_j:
                dk2[(k_i, k_j)] += 1
            else:
                dk2[(k_j, k_i)] += 1

        # every edge should be counted once
        assert sum(list(dk2.values())) == G.size()

        return dk2

    G1 = ensure_undirected(G1)
    G2 = ensure_undirected(G2)

    G1_dk = dk2_series(G1)
    G2_dk = dk2_series(G2)

    N = max(len(G1), len(G2))

    # note N^2 dense matrices 
    D1 = np.zeros((N, N))
    D2 = np.zeros((N, N))

    for (i, j), k in G1_dk.items():
        D1[i, j] = k
    for (i, j), k in G2_dk.items():
        D2[i, j] = k

    # these should be normalized by the number of edges
    D1 = D1 / G1.size()
    D2 = D2 / G2.size()

    # flatten matrices. this is safe because we've padded to the same size
    G1_dk_normed = D1[np.triu_indices(N)].ravel()
    G2_dk_normed = D2[np.triu_indices(N)].ravel()

    assert np.isclose(G1_dk_normed.sum(), 1)
    assert np.isclose(G2_dk_normed.sum(), 1)

    dist = entropy.js_divergence(G1_dk_normed, G2_dk_normed)
#     self.results["dist"] = dist

    return dist


def get_entropies(handle):
    for fn in glob.glob('/media/recnodes/recnode_2mfish/*' + handle +'*'):
        ret, pf = stims.sync_data(pd.read_pickle(fn+'track/perframe_stats.pickle'), stims.get_logfile(slashdir(fn)), imgstore.new_for_filename(slashdir(fn) + 'metadata.yaml'))
    
    # FINISH ME PLEASE
    return    
        
        
def check_networks(G, ideal_size=150, min_index=1):

    missing = [str(x) for x in list(set(list(range(min_index,ideal_size+min_index))) - set(list([int(x) for x in G.nodes()])))]
    if len(missing) > 0:
        for i in missing:
            G.add_edge(i, np.random.choice(G.nodes()))
    
    while not nx.is_connected(G):
        minG = str(min([int(x) for x in [*nx.connected_components(G)][0]]))
        maxG = str(max([int(x) for x in [*nx.connected_components(G)][0]]))
        #minG = min(nx.connected_components(G), key=len)
        #maxG = max(nx.connected_components(G), key=len)
        rand_i = np.random.choice(list(minG))
        rand_j = np.random.choice(list(maxG))
        G.add_edge(rand_i,rand_j)
    
    return G   

def s_entropy(freq_list):
    ''' This function computes the shannon entropy of a given frequency distribution.
    USAGE: shannon_entropy(freq_list)
    ARGS: freq_list = Numeric vector represnting the frequency distribution
    OUTPUT: A numeric value representing shannon's entropy'''
    freq_list = [element for element in freq_list if element != 0]
    sh_entropy = 0.0
    for freq in freq_list:
        sh_entropy += freq * np.log(freq)
    sh_entropy = -sh_entropy
    return(sh_entropy)

def ordinal_patterns(ts, embdim, embdelay):
    ''' This function computes the ordinal patterns of a time series
    for a given embedding dimension and embedding delay.
    USAGE: ordinal_patterns(ts, embdim, embdelay)
    ARGS: ts = Numeric vector represnting the time series,
    embdim = embedding dimension (3<=embdim<=7 prefered range), embdelay =  embdding delay
    OUPTUT: A numeric vector representing frequencies of ordinal patterns'''
    time_series = ts
    possible_permutations = list(itertools.permutations(range(embdim)))
    lst = list()
    for i in range(len(time_series) - embdelay * (embdim - 1)):
        sorted_index_array = list(np.argsort(time_series[i:(embdim+i)]))
        lst.append(sorted_index_array)
    lst = np.array(lst)
    element, freq = np.unique(lst, return_counts = True, axis = 0)
    freq = list(freq)
    if len(freq) != len(possible_permutations):
        for i in range(len(possible_permutations)-len(freq)):
            freq.append(0)
        return(freq)
    else:
        return(freq)

def p_entropy(op):
    ordinal_pat = op
    max_entropy = np.log(len(ordinal_pat))
    p = np.divide(np.array(ordinal_pat), float(sum(ordinal_pat)))
    return(s_entropy(p)/max_entropy)

def complexity(op):
    ''' 
    This function computes the complexity of a time series
    defined as: Comp_JS = Q_o * JSdivergence * pe
    Q_o = Normalizing constant
    JSdivergence = Jensen-Shannon divergence
    pe = permutation entopry
    ARGS: ordinal pattern
    '''
    pe = p_entropy(op)
    constant1 = (0.5+((1 - 0.5)/len(op)))* np.log(0.5+((1 - 0.5)/len(op)))
    constant2 = ((1 - 0.5)/len(op))*np.log((1 - 0.5)/len(op))*(len(op) - 1)
    constant3 = 0.5*np.log(len(op))
    Q_o = -1/(constant1+constant2+constant3)

    temp_op_prob = np.divide(op, sum(op))
    temp_op_prob2 = (0.5*temp_op_prob)+(0.5*(1/len(op)))
    JSdivergence = (s_entropy(temp_op_prob2) - 0.5 * s_entropy(temp_op_prob) - 0.5 * np.log(len(op)))
    Comp_JS = Q_o * JSdivergence * pe
    return(Comp_JS)

def weighted_ordinal_patterns(ts, embdim, embdelay):
    time_series = ts
    possible_permutations = list(itertools.permutations(range(embdim)))
    temp_list = list()
    wop = list()
    for i in range(len(time_series) - embdelay * (embdim - 1)):
        Xi = time_series[i:(embdim+i)]
        Xn = time_series[(i+embdim-1): (i+embdim+embdim-1)]
        Xi_mean = np.mean(Xi)
        Xi_var = (Xi-Xi_mean)**2
        weight = np.mean(Xi_var)
        sorted_index_array = list(np.argsort(Xi))
        temp_list.append([''.join(map(str, sorted_index_array)), weight])
    result = pd.DataFrame(temp_list,columns=['pattern','weights'])
    freqlst = dict(result['pattern'].value_counts())
    for pat in (result['pattern'].unique()):
        wop.append(np.sum(result.loc[result['pattern']==pat,'weights'].values))
    return(wop)

def average_every_n(xvec, yvec, n=2):
    """
    Utility function that spits out a smoothed x and y vector
    
    Parameters
    ----------
    xvec, yvec (np.array): vectors of x and y data
    n (int): average every n terms together
    
    Returns
    -------
    out_x, out_y (np.array): two smoothed vectors according to
                             however many n were specified
    """
    
    out_x = []
    out_y = []
    
    min_xdiff = xvec[1] - xvec[0]
    
    for i in range(0,len(xvec),n):
        xnumerat = 0
        ynumerat = 0
        
        if i + n <= len(xvec):
            for j in range(n):
                xnumerat += xvec[i+j]
                ynumerat += yvec[i+j]
        
            out_x.append(xnumerat / n)
            out_y.append(ynumerat / n)
    
    out_x = np.array(out_x)
    out_y = np.array(out_y)

    if n > 1:
        out_x = out_x + min_xdiff / n
    
    return out_x, out_y        
        
        
def plot_network_distances(fish_dict):

    from matplotlib import gridspec
    fig = plt.figure(dpi=300, figsize=(11,13))
    ns = 15
    lw = 1.35
    ew = 1
    ncols = 5
    nrows = 11
    nv = 2

    fish_distance = {}
    for di, j in enumerate(list(range(1,len(good_dists)+1))):
        dtype = list(good_dists.keys())[di]
        print(dtype)
        fish_distance[dtype] = []
        distance_measure = good_dists[dtype]
        for gi in list(fish_dict.keys())[:-1]:
            G0_i = fish_dict[gi]
            G1_i = fish_dict[gi+1]
            G0_i = check_networks(G0_i)
            G1_i = check_networks(G1_i)
                
            dd = distance_measure(G0_i, G1_i)
            fish_distance[dtype].append(dd)
    
    dents = []
    for di, j in enumerate(list(range(1,len(good_dists)+1))):
        dtype = list(good_dists.keys())[di]
    
        dists_i = fish_distance[dtype]
        dents.append(p_entropy(ordinal_patterns(dists_i, 4, 1)))
    gs = gridspec.GridSpec(len(good_dists)+1, ncols, width_ratios=[1]*ncols, height_ratios=[2]+[1]*len(good_dists))
    G_f = fish_dict[min(fish_dict.keys())]
    G_f = check_networks(G_f)
    pos = nx.kamada_kawai_layout(G_f)
    pos = nx.spring_layout(G_f, pos=pos, iterations=1)
    partition = community.best_partition(G_f)
    comms = np.array([partition[i] for i in G_f.nodes()])
    node_colors_co = [colors[i] for i in comms]

    ginds = np.arange(0, len(fish_dict), len(fish_dict)/ncols) + min(fish_dict.keys())
    ginds = [1950, 1975, 2000, 2025, 2049]


    for i in range(ncols):
        axi = plt.subplot(gs[i])
        Gt_i = fish_dict[ginds[i]]
        partition = community.best_partition(Gt_i)
        comms = np.array([partition[i] for i in Gt_i.nodes()])
        node_colors_co = [colors[i] for i in comms]
        pos = nx.kamada_kawai_layout(Gt_i)
        pos = nx.spring_layout(Gt_i, pos=pos, iterations=1)

        nx.draw_networkx_nodes(Gt_i, pos, node_color=node_colors_co, edgecolors='#333333',
                               node_size=ns, linewidths=lw, alpha=0.95, ax=axi)
        nx.draw_networkx_edges(Gt_i, pos, edge_color="#999999", width=ew, alpha=0.35, ax=axi)
        axi.set_axis_off()
        axi.set_title("t = %i"%ginds[i], fontsize=12)
        
        
    for di, j in enumerate(list(range(1,len(good_dists)+1))):
        axi = plt.subplot(gs[j,:])
        dtype = list(good_dists.keys())[di]
        
        dists_i = fish_distance[dtype]
        
        xvals = np.array(list(range(1,len(fish_dict)-2)))
        yvals = np.array(dists_i)
        yvals = (yvals-yvals.min()) / (yvals.max()-yvals.min())
        xvals, yvals = average_every_n(xvals, yvals, nv)
        
    #     cc = cmo.cm.curl((yvals[:-10].mean()-yvals[:10].mean()) / 0.5) 
        cval = np.array((dents-min(dents))/(max(dents)-min(dents)))
        cc = cmo.cm.thermal(cval[di]*0.85 + 0.075)
        
        axi.plot(xvals, yvals, linewidth=2.5, color='#333333')
        axi.plot(xvals, yvals, linewidth=2.5, color=cc, label=dtype, alpha=0.9)
        
        axi.legend(loc=1, framealpha=0.85)

        xticks = np.array(list(range(0,max(fish_dict.keys())+1,20)))
        yticks = np.linspace(0,1,3)
        axi.set_xticks(xticks)
        axi.set_yticks(yticks)
        axi.set_yticklabels(yticks, fontsize=8)
        axi.set_ylabel(r'$d(G_{t}, G_{t+1})$', fontsize=9)
        axi.set_xlim(-0.25, len(fish_dict)-1.25)
        axi.set_ylim(-0.075, 1.075)
        
        axi.grid(linewidth=1.5, color='#999999', alpha=0.3)
        
        if j != nrows-1:
            axi.set_xticklabels(['']*len(xticks))
        
        else:
            axi.set_xticklabels(xticks)
            axi.set_xlabel('Time', fontsize=14)

    # plt.savefig("../figs/pngs/sample_distances_fish.png", dpi=425, bbox_inches='tight')
    # plt.savefig("../figs/pdfs/sample_distances_fish.pdf", dpi=425, bbox_inches='tight')

    
    return fig
    


titles_of_dists = ["JaccardDistance", 
                   "Hamming", 
                   "HammingIpsenMikhailov", 
                   "Frobenius", 
                   "PolynomialDissimilarity", 
                   "DegreeDivergence", 
#                    "dK2Distance", 
                   "PortraitDivergence",
#                    "OnionDivergence",
                   "QuantumJSD",
                   "CommunicabilitySequence", 
#                   "ResilienceDistance",
                   "ResistancePerturbation", 
                   "NetLSD",
                    "LaplacianSpectralLorenzJSD", 
                   "LaplacianSpectralGaussianJSD", 
                   "LaplacianSpectralLorenzEuc",
                   "IpsenMikhailov", 
                   "NonBacktrackingDistance",
                   "DistributionalNBD",
                   "D-measure",
                   "DeltaCon",
                   "NetSimile"
                   ]

dist_functions={'LaplacianSpectralLorenzJSD':    LJ,\
                'LaplacianSpectralLorenzEuc':    LE,\
                'LaplacianSpectralGaussianJSD':  NJ,\
                'NonBacktrackingDistance':       NonBacktrackingSpectral,\
                'dK2Distance':                   dk2Distance,\
                }

additional_dists={
    'PolynomialDissimilarity':  PolynomialDissimilarity(),\
    'JaccardDistance':          JaccardDistance(), \
    'Hamming':                  Hamming(), \
    'HammingIpsenMikhailov':    HammingIpsenMikhailov(), \
    'IpsenMikhailov':           IpsenMikhailov(), \
    'PortraitDivergence':       PortraitDivergence(), \
    'ResistancePerturbation':   ResistancePerturbation(), \
    'Frobenius':                Frobenius(), \
    'NetSimile':                NetSimile(), \
    'DegreeDivergence':         DegreeDivergence(), \
    'DeltaCon':                 DeltaCon(),
#     'OnionDivergence':          OnionDivergence(), \
    'DistributionalNBD':        DistributionalNBD(),\
    'NetLSD':                   NetLSD(),\
    'QuantumJSD':               QuantumJSD(),\
    'CommunicabilitySequence':  CommunicabilityJSD(),\
    'D-measure':                DMeasure(),\
#    'ResilienceDistance':       ResilienceDistance(),\
    }

# place the actual functions into the dist_functions dict
for dist_name, dist_object in additional_dists.items():
    dist_functions[dist_name] = dist_object.dist
    
distances = {}
for title in titles_of_dists:
    distances[title] = dist_functions[title]

good_dists = {'JaccardDistance':distances['JaccardDistance'],
#              'Hamming':distances['Hamming'], #requires constant network size
              'DegreeDivergence':distances['DegreeDivergence'],
              'PortraitDivergence':distances['PortraitDivergence'], #slow processing
#              'QuantumJSD':distances['QuantumJSD'], #requires constant network size
#              'ResistancePerturbation':distances['ResistancePerturbation'], #requires constant network size
              'NetLSD':distances['NetLSD'],
              'IpsenMikhailov':distances['IpsenMikhailov'],
              'NonBacktrackingDistance':distances['NonBacktrackingDistance'], #slow processing
#              'D-measure':distances['D-measure'] #requires constant network size
             }





colors = ["#91b43f","#7463cd","#54bc5b","#c560c7","#49925d","#cf4085","#49bfba",
          "#cf4d2b","#6f8bce","#dd862f","#98558b",
          "#c7a745","#dd85a8", "#777d35","#c64855",
          "#9b5e2f","#e0906e"]
np.random.shuffle(colors)



















#get data


fish_dict = {}

filelist = []
FN = '/media/recnodes/recnode_2mfish/reversals3m_512_dotbot_20181017_111201.stitched'
#FN = '/media/recnodes/recnode_2mfish/coherencetestangular3m_128_dotbot_20181009_115202.stitched'
for fn in glob.glob( FN + '/track/graphs/*'):
    filelist.append(fn)
    
filelist = sorted(filelist)

for i in range(0,7500):#1,len(filelist)): #FIXME
   if i%100==0:
       print(i)
   fish_dict[i] = nx.read_graphml(filelist[i])
try:       
    nx.write_graphml(fish_dict, '/home/dan/Desktop/graphs_temp.graphml')
except:
    print( "couldn't save")
    pass
fig = plot_network_distances(fish_dict)
plt.savefig('/home/dan/Desktop/network_distances.svg', dpi=425, bbox_inches='tight')
plt.show()
    
