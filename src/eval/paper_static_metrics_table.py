import argparse

from eval.compute_entropies import pg_from

cmas_simple = 251.26
cmas_random1 = 187.19
cmas_random3 = 81.93
cmas_random0 = 107.99
cmas_unident_s = 102.12

marc_simple = 387.87
marc_random1 = 266.01
marc_random3 = 62.5
marc_random0 = 395.01
marc_unident_s = 757.71


performance = {
    'simple':{
        '11':cmas_simple-190.3,
        '12':cmas_simple-216.6,
        '13':cmas_simple-226.0,
        '14':cmas_simple-243.9,
        '21':marc_simple*0.05,
        '22':marc_simple*0.04,
        '23':marc_simple*0.02,
        '24':marc_simple*0.01,
        '31':cmas_simple,
        '32':cmas_simple,
        '33':cmas_simple,
        '34':cmas_simple,
        '41':marc_simple,
        '42':marc_simple,
        '43':marc_simple,
        '44':marc_simple,
    },
    'random1':{
        '11':cmas_random1-114.5,
        '12':cmas_random1-167.1,
        '13':cmas_random1-124.2,
        '14':cmas_random1-178.6,
        '21':marc_random1,
        '22':marc_random1,
        '23':marc_random1,
        '24':marc_random1,
        '31':cmas_random1,
        '32':cmas_random1,
        '33':cmas_random1,
        '34':cmas_random1,
        '41':marc_random1,
        '42':marc_random1,
        '43':marc_random1,
        '44':marc_random1,
    },
    'random3':{
        '11':cmas_random3-56.7,
        '12':cmas_random3-51.8,
        '13':cmas_random3-67.9,
        '14':cmas_random3-76.5,
        '21':marc_random3,
        '22':marc_random3,
        '23':marc_random3,
        '24':marc_random3,
        '31':cmas_random3,
        '32':cmas_random3,
        '33':cmas_random3,
        '34':cmas_random3,
        '41':marc_random3,
        '42':marc_random3,
        '43':marc_random3,
        '44':marc_random3,
    },
    'random0':{
        '11':cmas_random0-0,
        '12':cmas_random0-0,
        '13':cmas_random0-108.6,
        '14':cmas_random0-116.6,
        '21':marc_random0*0.05,
        '22':marc_random0*0.04,
        '23':marc_random0*0.03,
        '24':marc_random0*0.05,
        '31':cmas_random0,
        '32':cmas_random0,
        '33':cmas_random0,
        '34':cmas_random0,
        '41':marc_random0,
        '42':marc_random0,
        '43':marc_random0,
        '44':marc_random0,
    },
    'unident_s':{
        '11':cmas_unident_s-89.1,
        '12':cmas_unident_s-91.3,
        '13':cmas_unident_s-88.9,
        '14':cmas_unident_s-88.4,
        '21':marc_unident_s*0.01,
        '22':marc_unident_s,
        '23':marc_unident_s,
        '24':marc_unident_s,
        '31':cmas_unident_s,
        '32':cmas_unident_s,
        '33':cmas_unident_s,
        '34':cmas_unident_s,
        '41':marc_unident_s,
        '42':marc_unident_s,
        '43':marc_unident_s,
        '44':marc_unident_s,
    }
}

disc_to_agent = {
    '1':"\cmasone",
    '2':"\marcone",
    '3':"\cmashuman",
    '4':"\marctwo"
}

def extract_full_table(args):
    tracked_metrics = ['Environment', 'Disc', 'H', 'H_a', 'H_w']
    for domain in args.domains:
        new_domain=True
        prev_disc='x'
        for disc in args.discretisers:
            disc = str(disc)
            results = dict()
            x = pg_from(domain, disc)
            results['H_a'] = x.compute_entropy("agent")
            results['H_w'] = x.compute_entropy("world")
            results['H'] = results['H_a'] + results['H_w']
            results['delta_r'] = f"{-performance[domain][disc]:.2f}" if disc[0]=='1' or disc[0]=='2' else ""
            if new_domain:
                new_domain=False
                print("\multirow{"+ str(len(args.discretisers)) +"}*{\\"+domain+"} &", end=' ')
            else: print("&", end=' ')
            if prev_disc != disc[0]:
                agent = disc_to_agent[disc[0]]
                prev_disc = disc[0]
                print(" \multirow{"+ str(4) +"}*{"+agent+"} &", end=' ')
            else: print("&", end=' ')
            print(f"{disc[1]} & {results['H']:.2f} & {results['H_a']:.2f} & {results['H_w']:.2f} & {results['delta_r']} \\\\")



def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-do",
        "--domains",
        nargs="+",
        type=str,
        help="Domains to analyse"
    )
    parser.add_argument(
        "-dc",
        "--discretisers",
        nargs="+",
        type=int,
        help="Discretisers"
    )
    return parser.parse_args()

if __name__=='__main__':
    args = get_args()
    extract_full_table(args)
