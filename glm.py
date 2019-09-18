import statsmodels.api as sm


from mpl_toolkits.axes_grid1 import make_axes_locatable

def do_GLM(df, col, fam):
    g = df.groupby('trialID').mean()
    if not col == 'correctTrial':
        g = g.dropna()
    model = statsmodels.genmod.generalized_linear_model.GLM(g[col], g[['coh', 'groupsize']])
    if fam == 'binomial':
        glm = sm.GLM(model.endog, model.exog, family=sm.families.Binomial())
    else:
        glm = sm.GLM(model.endog, model.exog)
    res = glm.fit()

    coeffs = res.params
    depVars = model.data.xnames
    return coeffs, depVars

def plot_parspace(df, fig, ax):
    im = ax.imshow(df, origin='lower')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    xlabs = np.insert(df.columns.values, 0, 0)
    ylabs = np.insert(df.index.values, 0, 0)
    
    ax.set_xticklabels(xlabs)
    ax.set_yticklabels(ylabs)
    fig.colorbar(im, cax=cax)
    return

THRESHOLDS = [0.4,0.5,0.6,0.7,0.8,0.9]
minDurs = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8] 


trythese = ['correctTrial','RT','duration','IBI']
for trythis in trythese:

    resultDF = pd.DataFrame()
    for THRESHOLD in THRESHOLDS:
        for minDur in minDurs:
            bouts = pd.read_pickle('/media/recnodes/Dan_storage/190902_bouts_t'+ str(minDur) + '_C' + str(THRESHOLD)+ '.pickle')
            bouts = bouts.loc[bouts['coh'] != 0.0, :]
            if trythis == 'RT':
                bouts = bouts.loc[bouts['firstBout'] == 1, :]  
           
            if trythis == 'correctTrial':
                fam = 'binomial'
            else:
                fam = 'continuous'
                
            coeffs, deps = do_GLM(bouts, trythis, fam)
            resultDF = pd.concat([resultDF, pd.DataFrame({'C':THRESHOLD, 't':minDur, deps[0]:coeffs[0], deps[1]:coeffs[1]}, index=[0])], axis=0)
            
        

    h = resultDF.groupby(['C','t'])
    cos = h['coh'].mean().unstack()

    gs = h['groupsize'].mean().unstack()


    fig = plt.figure(figsize=(20,7))
    fig.suptitle(trythis)
    ax = fig.add_subplot(121)
    plot_parspace(cos, fig, ax)
    ax.set_xlabel('Time threshold (proportion of stim frames)')
    ax.set_ylabel('Rotation threshold (minimum order)')
    ax.set_title('Coefficient of coherence')


    ax = fig.add_subplot(122)
    plot_parspace(gs, fig, ax)
    ax.set_xlabel('Time threshold (proportion of stim frames)')
    ax.set_ylabel('Rotation threshold (minimum order)')
    ax.set_title('Coefficient of group size')

    plt.savefig('/media/recnodes/Dan_storage/190910_' + trythis + '.svg')
    plt.show()
