import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from scipy.stats import truncnorm, norm, multivariate_normal as mvn
import time
import pandas as pd

COLORS = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000']

def truncnorm_local_rvs(peak, std, sign):
    if sign == 1:
        return truncnorm.rvs(-peak/std, np.inf, scale=std) + peak
    else:
        return truncnorm.rvs(-np.inf, -peak/std, scale=std) + peak


def pdf_s_given_t_rvs(m1, m2, s1, s2, st, t):
    """
        m1: mean of variable s_1
        m2: mean of variable s_2
        s1: std of variable s_1
        s2: std of variable s_2
        st: std of variable t
        t: given sample of variable t
    """
    cov_s_given_t = np.linalg.inv( 1/(s1**2 * s2**2) * np.diag([s2**2, s1**2]) + 1/st**2 * np.array([[1, -1],[-1, 1]]) )
    cov_s_inv = np.linalg.inv(np.diag([s1**2, s2**2]))
    m_s = np.array([[m1],[m2]])
    M_transpose = np.array([[1],[-1]])

    m_s_given_t = cov_s_given_t @ (cov_s_inv @ m_s + M_transpose/st**2 * t)

    return mvn.rvs(mean=m_s_given_t.flatten(), cov=cov_s_given_t)


def pdf_t_given_s_and_y_rvs(s_1, s_2, st, y):
    return truncnorm_local_rvs(s_1 - s_2, st, y)

def posterior(s_1_gibbs, s_2_gibbs):
    """
        given samples from gibbs sampler, returns frozen gaussians
    """
    return norm.freeze(loc=np.mean(s_1_gibbs), scale=np.std(s_1_gibbs)), norm.freeze(loc=np.mean(s_2_gibbs), scale=np.std(s_2_gibbs))

def gibbs_q4(K, m1, m2, s1, s2, st, y0, t0, burn_in):
    
    s_1 = np.zeros(K)
    s_2 = np.zeros(K)
    t = np.zeros(K)
    t[0] = t0
    for k in range(K):
        if k == burn_in:
            timer_0 = time.clock()
        if k % 1000 == 0:
            print(k, '/', K)
        (s_1[k], s_2[k]) = pdf_s_given_t_rvs(m1, m2, s1, s2, st, t[k-1])
        t[k] = pdf_t_given_s_and_y_rvs(s_1[k], s_2[k], st, y0)

    return s_1, s_2, t, time.clock() - timer_0

def gibbs_q5(K, m1, m2, s1, s2, st, y0, t0, burn_in):

    s_1 = np.zeros(K)
    s_2 = np.zeros(K)
    t = np.zeros(K)
    t[0] = t0
    for k in range(K):
        if k == burn_in:
            timer_0 = time.clock()
        # if k % 1000 == 0:
        #     print(k, '/', K)
        (s_1[k], s_2[k]) = pdf_s_given_t_rvs(m1, m2, s1, s2, st, t[k-1])
        t[k] = pdf_t_given_s_and_y_rvs(s_1[k], s_2[k], st, y0)

    return s_1, s_2, t, time.clock() - timer_0


def run_q4():

    burn_in = 10
    m1 = 25
    m2 = 25 
    s1 = 25/3 
    s2 = 25/3
    st = 5 # small 'st' implies that the outcome is more telling of the skill
    y = 1 # i.e. player 1 wins
    t0 = 3
    
    K = 20
    s_1, s_2, t, runtime = gibbs_q4(K, m1, m2, s1, s2, st, y, t0, burn_in)
    s_1_post, s_2_post = posterior(s_1, s_2)

    # plot the samples of the posterior distributions generated by the Gibbs when y=1
    plt.figure(1)
    plt.plot(s_1, label='s1')
    plt.plot(s_2, label='s2')
    plt.legend()
    plt.grid()

    # Plot the histogram of the samples generated (after
    # burn-in) together with the fitted Gaussian posterior for at least four (4) different numbers of
    # samples and report the time required to draw the samples.
    x_eval = np.linspace(10,50,100)
    plt.figure(2)
    plt.subplot(221)
    plt.title('K='+ str(K-burn_in)+', time: '+str(np.round(runtime, 3))+'s')
    plt.hist(s_1[burn_in::], color='C0', density=1,alpha=0.6, bins=50)
    plt.plot(x_eval, s_1_post.pdf(x_eval), 'C0')
    plt.ylim(0,.1)
    plt.xlim(10, 50)

    K = 40
    s_1, s_2, t, runtime = gibbs_q4(K, m1, m2, s1, s2, st, y, t0, burn_in)
    s_1_post, s_2_post = posterior(s_1, s_2)
    plt.figure(2)
    plt.subplot(222)
    plt.title('K='+ str(K-burn_in)+', time: '+str(np.round(runtime, 3))+'s')
    plt.hist(s_1[burn_in::], color='C0', density=1,alpha=0.6, bins=50)
    plt.plot(x_eval, s_1_post.pdf(x_eval), 'C0')    
    plt.ylim(0,.1)
    plt.xlim(10, 50)

    K = 80
    s_1, s_2, t, runtime = gibbs_q4(K, m1, m2, s1, s2, st, y, t0, burn_in)
    s_1_post, s_2_post = posterior(s_1, s_2)
    plt.figure(2)
    plt.subplot(223)
    plt.title('K='+ str(K-burn_in)+', time: '+str(np.round(runtime, 3))+'s')
    plt.hist(s_1[burn_in::], color='C0', density=1,alpha=0.6, bins=50)
    plt.plot(x_eval, s_1_post.pdf(x_eval), 'C0') 
    plt.ylim(0,.1)
    plt.xlim(10, 50)

    K = 1000
    s_1, s_2, t, runtime = gibbs_q4(K, m1, m2, s1, s2, st, y, t0, burn_in)
    s_1_post, s_2_post = posterior(s_1, s_2)
    plt.figure(2)
    plt.subplot(224)
    plt.title('K='+ str(K-burn_in)+', time: '+str(np.round(runtime, 3))+'s')
    plt.hist(s_1[burn_in::], color='C0', density=1,alpha=0.6, bins=50)
    plt.plot(x_eval, s_1_post.pdf(x_eval), 'C0') 
    plt.ylim(0,.1)
    plt.xlim(10, 50)
    plt.tight_layout()

    # Compare the prior p(s1) with the Gaussian approximation of the posterior p(s1|y = 1);
    # similarly compare p(s2) with p(s2|y = 1).
    s_1_prior = norm.freeze(loc=m1, scale=s1)
    s_2_prior = norm.freeze(loc=m2, scale=s2)

    plt.figure(3)
    plt.plot(np.sort(s_1), s_1_prior.pdf(np.sort(s_1)), 'C0', label='Prior') 
    plt.plot(np.sort(s_1), s_1_post.pdf(np.sort(s_1)), 'C1--', label='Posterior s1') 
    plt.plot(np.sort(s_2), s_2_post.pdf(np.sort(s_2)), 'C2--', label='Posterior s2') 
    plt.legend()
    plt.grid()
    plt.tight_layout()


def run_q5():
    serie_A = pd.read_csv('SerieA.csv')
    teamnames = list(serie_A.team1.unique())
    N_teams = len(teamnames)

    t = np.array(serie_A.score1 - serie_A.score2)
    y = np.sign(t)
    M = len(y) # number of matches
    
    team_dict = {}
    std_dict = {}
    for team in teamnames:
        team_dict[team] = list([[25], [25/3]])
    
    team1 = np.array(serie_A.team1)
    team2 = np.array(serie_A.team2)


    # variance for t st:
    st = 5

    # burn in from q4
    burn_in = 10
    K = 80
    for m in range(M):
            if m % 20 == 0:
                print(m, '/', M)
            # determine what teams are playing
            t1 = team1[m]
            t2 = team2[m]

            # extract means and std for both teams
            m1 = team_dict[t1][0][-1]
            s1 = team_dict[t1][1][-1]
            m2 = team_dict[t2][0][-1]
            s2 = team_dict[t2][1][-1]

            if t[m] != 0: # we skip matches that were draw and repeat the previous value instead
                # get samples from the gibbs sampler
                s_1, s_2, _, _ = gibbs_q5(K, m1, m2, s1, s2, st, y[m], t[m], burn_in)

                # compute mean and std disregarding the burn in phase
                m1_new = np.mean(s_1[burn_in::])
                s1_new = np.std(s_1[burn_in::])
                m2_new = np.mean(s_2[burn_in::])
                s2_new = np.std(s_2[burn_in::])
            else:
                m1_new = m1
                s1_new = s1
                m2_new = m2
                s2_new = s2
            # update the dictionary for the two teams
            team_dict[t1][0].append(m1_new)
            team_dict[t1][1].append(s1_new)
            team_dict[t2][0].append(m2_new)
            team_dict[t2][1].append(s2_new)

    plt.figure()
    c_count = 0
    for team in teamnames:
        m = np.array(team_dict[team][0])
        s = np.array(team_dict[team][1])
        m_up = m + s
        m_dn = m - s
        plt.plot(m, color=COLORS[c_count], label=team)
        # plt.plot(m_up, color=COLORS[c_count])
        # plt.plot(m_dn, color=COLORS[c_count])
        c_count += 1
    fontP = FontProperties()
    fontP.set_size('xx-small')
    plt.legend(prop=fontP, ncol=7) 
    plt.grid()
    plt.tight_layout()


# run_q4()
run_q5()
plt.show()    

