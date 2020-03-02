from heapq import heappush, heappop
from itertools import combinations, chain # requires python 2.6+
from operator import itemgetter
from collections import defaultdict
from copy import copy
from centroidtracker import CentroidTracker #in github.com/fishMAD, modified from PyImageSearch
import overlay_data_on_position 
from overlay_data_on_position import * 
from overlay_data_on_position import plot_network_communities 
from overlay_data_on_position import plot_data_on_video 
from utilities import create_colourlist
import imgstore
import networkx as nx


class HLC:
    def __init__(self,adj,edges):
        self.adj   = adj # node -> set of neighbors
        self.edges = edges # list of edges
        self.Mfactor  = 2.0 / len(edges)
        self.edge2cid = {}
        self.cid2nodes,self.cid2edges = {},{}
        self.orig_cid2edge = {}
        self.curr_maxcid = 0
        self.linkage = []  # dendrogram

        self.initialize_edges() # every edge in its own comm
        self.D = 0.0 # partition density
    
    def initialize_edges(self):
        for cid,edge in enumerate(self.edges):
            edge = swap(*edge) # just in case
            self.edge2cid[edge] = cid
            self.cid2edges[cid] = set([edge])
            self.orig_cid2edge[cid]  = edge
            self.cid2nodes[cid] = set( edge )
        self.curr_maxcid = len(self.edges) - 1
    
    def merge_comms(self,edge1,edge2,S,dendro_flag=False):
        if not edge1 or not edge2: # We'll get (None, None) at the end of clustering
            return
        cid1,cid2 = self.edge2cid[edge1],self.edge2cid[edge2]
        if cid1 == cid2: # already merged!
            return
        m1,m2 = len(self.cid2edges[cid1]),len(self.cid2edges[cid2])
        n1,n2 = len(self.cid2nodes[cid1]),len(self.cid2nodes[cid2])
        Dc1, Dc2 = Dc(m1,n1), Dc(m2,n2)
        if m2 > m1: # merge smaller into larger
            cid1,cid2 = cid2,cid1

        if dendro_flag:
            self.curr_maxcid += 1; newcid = self.curr_maxcid
            self.cid2edges[newcid] = self.cid2edges[cid1] | self.cid2edges[cid2]
            self.cid2nodes[newcid] = set()
            for e in chain(self.cid2edges[cid1], self.cid2edges[cid2]):
                self.cid2nodes[newcid] |= set(e)
                self.edge2cid[e] = newcid
            del self.cid2edges[cid1], self.cid2nodes[cid1]
            del self.cid2edges[cid2], self.cid2nodes[cid2]
            m,n = len(self.cid2edges[newcid]),len(self.cid2nodes[newcid]) 
            
            self.linkage.append( (cid1, cid2, S) )

        else:
            self.cid2edges[cid1] |= self.cid2edges[cid2]
            for e in self.cid2edges[cid2]: # move edges,nodes from cid2 to cid1
                self.cid2nodes[cid1] |= set( e )
                self.edge2cid[e] = cid1
            del self.cid2edges[cid2], self.cid2nodes[cid2]
            
            m,n = len(self.cid2edges[cid1]),len(self.cid2nodes[cid1]) 

        Dc12 = Dc(m,n)
        self.D = self.D + ( Dc12 -Dc1 - Dc2) * self.Mfactor # update partition density

    def single_linkage(self, threshold=None, w=None, dendro_flag=False):
        print("clustering...")
        self.list_D = [(1.0,0.0)] # list of (S_i,D_i) tuples...
        self.best_D = 0.0
        self.best_S = 1.0 # similarity threshold at best_D
        self.best_P = None # best partition, dict: edge -> cid

        if w == None: # unweighted
            H = similarities_unweighted( self.adj ) # min-heap ordered by 1-s
        else: 
            H = similarities_weighted( self.adj, w )
        S_prev = -1
        
        # (1.0, (None, None)) takes care of the special case where the last
        # merging gives the maximum partition density (e.g. a single clique). 
        for oms,eij_eik in chain(H, [(1.0, (None, None))] ):
            S = 1-oms # remember, H is a min-heap
            if threshold and S < threshold:
                break
                
            if S != S_prev: # update list
                if self.D >= self.best_D: # check PREVIOUS merger, because that's
                    self.best_D = self.D  # the end of the tie
                    self.best_S = S
                    self.best_P = copy(self.edge2cid) # slow...
                self.list_D.append( (S,self.D) )
                S_prev = S

            self.merge_comms( eij_eik[0], eij_eik[1], S, dendro_flag )
        
        #self.list_D.append( (0.0,self.list_D[-1][1]) ) # add final val
        if threshold != None:
            return self.edge2cid, self.D
        if dendro_flag:
            return self.best_P, self.best_S, self.best_D, self.list_D, self.orig_cid2edge, self.linkage
        else:
            return self.best_P, self.best_S, self.best_D, self.list_D


def simple_adj(edges):
    """pass a nx.graph.edges() object"""
    adj = defaultdict(set)
    for (a,b) in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj
    

def swap(a,b):
    if a > b:
        return b,a
    return a,b


def Dc(m,n):
    """partition density"""
    try:
        return m*(m-n+1.0)/(n-2.0)/(n-1.0)
    except ZeroDivisionError: # numerator is "strongly zero"
        return 0.0

def similarities_unweighted(adj):
    """Get all the edge similarities. Input dict maps nodes to sets of neighbors.
    Output is a list of decorated edge-pairs, (1-sim,eij,eik), ordered by similarity.
    """
    #print "computing similarities..."
    i_adj = dict( (n,adj[n] | set([n])) for n in adj)  # node -> inclusive neighbors
    min_heap = [] # elements are (1-sim,eij,eik)
    for n in adj: # n is the shared node
        if len(adj[n]) > 1:
            for i,j in combinations(adj[n],2): # all unordered pairs of neighbors
                edge_pair = swap( swap(i,n),swap(j,n) )
                inc_ns_i,inc_ns_j = i_adj[i],i_adj[j] # inclusive neighbors
                S = 1.0 * len(inc_ns_i&inc_ns_j) / len(inc_ns_i|inc_ns_j) # Jacc similarity...
                heappush( min_heap, (1-S,edge_pair) )
    return [ heappop(min_heap) for i in range(len(min_heap)) ] # return ordered edge pairs

def rank_on_column(df, col, nRanks):
    """
    pass a dfcolumn, returns an index-matched series grouping col into nRanks groups
    """
    bounds = np.linspace(0,1,nRanks+1)
    df = df.copy()
    df['rank'] = np.nan
    for i in range(nRanks):
        if i == 0:
            INKL=True
        else:
            INKL=False
        df.loc[df[col].between(df.quantile(bounds[i])[col], 
                               df.quantile(bounds[i+1])[col] + 1e5, #tiny hack for inclusive upper bound
                               inclusive=INKL),
              'rank'] = int(i)
    return df['rank']
    
def distance(A, B):
    return np.sqrt((A[0]-B[0])**2 + (A[1]-B[1])**2)



def get_communities(graph,  _threshold):
    adj = simple_adj(graph.edges()) 
    edge2cid, D = HLC(adj, graph.edges).single_linkage(threshold=_threshold) #thresholding is bad

    #create node-based communities based on their majority membership in edge-based communities
    membership = defaultdict(list) 
    for group in set(edge2cid.values()): 
        members = [a for a in edge2cid.keys() if edge2cid[a] == group] 
        if len(members) > 5: 
            for (a,b) in members: 
                membership[a].append(group) 
                membership[b].append(group)                
    communities = dict(zip(membership.keys(),[max(set(membership[k]), key=membership[k].count) for k in membership.keys()]))                  
    return communities


        
def edge_community(graph, communityObjects, threshold=0.4): 
    #pass networkx graph and a CommunityTracker object                                                                                  
    #use pandas because we are sane here.
    df = pd.concat([pd.DataFrame(graph.nodes.data()[k], columns=graph.nodes.data()[k].keys(), index=[k]) for k in graph.nodes.keys()]) 
    df['trackid'] = df.index.copy()
    #positions = dict(zip(graph.nodes.keys(),[(graph.nodes.data()[k][XPOS],graph.nodes.data()[k][YPOS]) for k in graph.nodes.keys()])) 
                     
    #create edge-based communities using HLC
    adj = simple_adj(graph.edges()) 
    edge2cid, D = HLC(adj, graph.edges).single_linkage(threshold=threshold) #thresholding is bad

    #create node-based communities based on their majority membership in edge-based communities
    membership = defaultdict(list) 
    for group in set(edge2cid.values()): 
        members = [a for a in edge2cid.keys() if edge2cid[a] == group] 
        if len(members) > 1: 
            for (a,b) in members: 
                membership[a].append(group) 
                membership[b].append(group)                
    communities = dict(zip(membership.keys(),[max(set(membership[k]), key=membership[k].count) for k in membership.keys()]))   
    
    #remove communities with only one member
    comdf = pd.DataFrame(communities.keys(), index=communities.values()) 
    gcomdf = comdf.groupby(comdf.index).count() >2
    com_members = comdf.loc[gcomdf.loc[gcomdf[0]].index].reset_index()
    com_members.columns = ['community','trackid']   
                   
    #c = pd.DataFrame.from_dict(communities, orient='index')[0]   
    #c.name = 'community'   
    df = df.merge(com_members) #merges on 'trackid'  
    foo = df.groupby('community', as_index=True).median()    
    foo['community'] = foo.index.copy()   
    communityCentres = dict(zip(foo.index, [(foo.loc[x,XPOS],foo.loc[x,YPOS]) for x in foo.index])) 
    #use PyImageSearch centroidtracker to track community ids:
    objects = communityObjects.update(list(communityCentres.values()))
    objdf = pd.DataFrame.from_dict(objects).T 
    objdf.columns=[XPOS,YPOS]
    objdf['objID'] = objdf.index.values 
    foo = foo.merge(objdf) 
    foo.columns = ['comm_cx','comm_cy','comm_vx','comm_vy','comm_R','comm_EigenCen','community','objID'] 
    
    return df.merge(foo), edge2cid
    
from overlay_data_on_position import plot_data_on_video    

MAIN_DIR = '/media/recnodes/recnode_2mfish/reversals3m_128_dotbot_20181211_151201.stitched/'


from local_properties import sync_rotation  
import stim_handling as stims 
local = pd.read_pickle(MAIN_DIR +'track/localData_FBF.pickle')        
local = sync_rotation(local, stims.get_logfile(MAIN_DIR), store)   
local['trackid'] = local['trackid'].astype(object) 
cols = ['R', 'EigenCen', 'objID', 'comm_R', 'comm_EigenCen', 'localArea',
       'localPackingFraction', 'localMedianRotation', 'localRscore',
       'localPolarization', 'localPScore', 'localSpeedScore']

store = imgstore.new_for_filename(MAIN_DIR + 'metadata.yaml')
CT = CentroidTracker()
FBF = pd.DataFrame()

cl = create_colourlist(15, cmap='hsv') 
#make a repeating colourlist
cl = np.concatenate([cl,cl,cl,cl,cl])  
for i in range(1823,3823):
    try:
        img, (f,t) = store.get_image(store.frame_min + i) 
    except:
        img, (f,t) = store.get_next_image()
    
    graph = nx.read_graphml(MAIN_DIR +'track/graphs/%06d.graphml'%i )  
    f0 = local[local['frame'] == 0].copy()          
    poxy = dict(zip(graph.nodes.keys(),[(graph.nodes.data()[k][XPOS],graph.nodes.data()[k][YPOS]) for k in graph.nodes.keys()])) 
    data, edgecomms = edge_community(graph, CT, threshold=0.375)
    print(len(set(edgecomms.values())),len(set(data.community)), set(data.objID), len(set(data.trackid)))
    if len(set(data.trackid)) < 100: #FIXME to a percentage of graph nodes
        print('try again')
        data, edgecomms = edge_community(graph, CT, threshold=0.36)
        print(len(set(edgecomms.values())),len(set(data.community)), set(data.objID), len(set(data.trackid)))
    data['frame'] = i 
    #fig = plot_network_communities(img, graph, edgecomms, poxy, BY='edges', colours=cl)
    #plt.savefig(MAIN_DIR + 'track/communityvid_fromEdges/%06d.png'%i, dpi=300)
    #fig = plot_data_on_video(img, data[XPOS], data[YPOS], np.array([cl[k] for k in data.objID]), str(i))
    #plt.savefig(MAIN_DIR + 'track/communityvid/%06d.png'%i, dpi=300)
    fig = plt.figure(figsize=(12,12))
    for a in range(len(cols)):
        ax = fig.add_subplot(3,4,a+1)
        plot_data_on_video(img, m[XPOS], m[YPOS], m[cols[a]], cols[a], fig=fig, ax=ax)
        plt.colorbar()
    plt.savefig(MAIN_DIR + 'track/localdata/%06d.png'%i, dpi=300)
    
    plt.close('all')
    FBF = pd.concat([FBF, data], axis=0)

FBF.to_pickle(MAIN_DIR + 'track/community_tracked_FBF.pickle')



