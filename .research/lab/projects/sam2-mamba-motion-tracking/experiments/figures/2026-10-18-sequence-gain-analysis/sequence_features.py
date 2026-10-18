import csv, os, numpy as np, configparser
from collections import defaultdict
GT='/mnt/HDD10TB-2/aburatani/TrackEval/data/gt/dancetrack/val'
SA='/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/my_samurai_model/pedestrian_detailed.csv'
S2='/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/my_sam2_model/pedestrian_detailed.csv'
OU='/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts/sam2_minimal_integration/trackeval/sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100_seqinfo/sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100/pedestrian_detailed.csv'
def det(p):
    return {r['seq']:r for r in csv.DictReader(open(p)) if r['seq']!='COMBINED'}
sa,ou,s2=det(SA),det(OU),det(S2)
def iou(a,b):
    ix=max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0])); iy=max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1])); i=ix*iy
    return i/(a[2]*a[3]+b[2]*b[3]-i+1e-9)
rows=[]
for seq in sorted(ou):
    g=defaultdict(dict)
    for r in csv.reader(open(f'{GT}/{seq}/gt/gt.txt')):
        f,i=int(r[0]),int(r[1]); g[i][f]=np.array(list(map(float,r[2:6])))
    frames=defaultdict(list)
    for i,d in g.items():
        for f,b in d.items(): frames[f].append(b)
    n_id=len(g); per_frame=np.mean([len(v) for v in frames.values()])
    # occlusion: fraction of frames-person with any other overlapping IoU>0.3
    occ=[]; 
    for f,bs in frames.items():
        for a in range(len(bs)):
            occ.append(any(iou(bs[a],bs[b])>0.3 for b in range(len(bs)) if b!=a))
    occ=np.mean(occ)
    # motion: center speed normalized by box height, per frame; nonlinearity: |accel| / (speed) ; constant-velocity error 15-frame
    sp=[]; acc=[]; cverr=[]
    for i,d in g.items():
        fs=sorted(d); 
        c={f:np.array([d[f][0]+d[f][2]/2,d[f][1]+d[f][3]/2]) for f in fs}; h={f:d[f][3] for f in fs}
        for f in fs:
            if f-1 in c: sp.append(np.linalg.norm(c[f]-c[f-1])/h[f])
            if f-1 in c and f-2 in c: acc.append(np.linalg.norm(c[f]-2*c[f-1]+c[f-2])/h[f])
            # constant velocity prediction 5 frames ahead from velocity over last 5 frames
            if all(f-k in c for k in range(0,6)) and f+5 in c:
                v=(c[f]-c[f-5])/5; pred=c[f]+5*v; cverr.append(np.linalg.norm(pred-c[f+5])/h[f])
    sm=lambda x:float(np.mean(x))
    def m(d,k): return float(d[seq][k])*100
    rows.append(dict(seq=seq.replace('dancetrack',''), dHOTA=m(ou,'HOTA___AUC')-m(sa,'HOTA___AUC'),
        dDetA=m(ou,'DetA___AUC')-m(sa,'DetA___AUC'), dAssA=m(ou,'AssA___AUC')-m(sa,'AssA___AUC'),
        dIDSW=float(ou[seq]['IDSW'])-float(sa[seq]['IDSW']), sa_HOTA=m(sa,'HOTA___AUC'),
        n_id=n_id, per_frame=per_frame, occ=occ, speed=sm(sp), accel=sm(acc), cv_err=sm(cverr)))
import json; json.dump(rows,open('sequence_features.json','w'),indent=1)
keys=['n_id','per_frame','occ','speed','accel','cv_err','sa_HOTA']
from scipy.stats import spearmanr
for tgt in ['dHOTA','dDetA','dAssA','dIDSW']:
    print(tgt, {k: tuple(round(v,2) for v in spearmanr([r[k] for r in rows],[r[tgt] for r in rows])) for k in keys})
print(f"{'seq':5}{'dHOTA':>7}{'dDetA':>7}{'dAssA':>7}{'dIDSW':>7}{'saHOTA':>7}{'nid':>4}{'pf':>6}{'occ':>6}{'speed':>7}{'accel':>7}{'cverr':>7}")
for r in sorted(rows,key=lambda r:-r['dHOTA']):
    print(f"{r['seq']:5}{r['dHOTA']:7.2f}{r['dDetA']:7.2f}{r['dAssA']:7.2f}{r['dIDSW']:7.0f}{r['sa_HOTA']:7.1f}{r['n_id']:4d}{r['per_frame']:6.1f}{r['occ']:6.2f}{r['speed']:7.3f}{r['accel']:7.3f}{r['cv_err']:7.3f}")
