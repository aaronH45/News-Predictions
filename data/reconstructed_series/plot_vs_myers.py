"""Overlay reconstructed expectations vs Myers' shared one-year series."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
R=Path("/home/rpa9/IBES_Expectations/reconstructed_series"); B=Path("/home/rpa9/IBES_Expectations")
plt.rcParams.update({"font.size":10,"axes.grid":True,"grid.alpha":0.25})

A=pd.read_csv(R/"reconstructed_series.csv",parse_dates=["qe"])
A["Year"]=A.qe.dt.year; A["Q"]=A.qe.dt.quarter; A["t"]=A.Year+(A.Q-1)/4
me=pd.read_excel(B/"Earnings_growth_expectations.xlsx",header=None).iloc[2:,[0,1,2]]
me.columns=["Year","Q","m"]; me=me.apply(pd.to_numeric,errors="coerce").dropna(); me["t"]=me.Year+(me.Q-1)/4
md=pd.read_excel(B/"Dividend_growth_expectations.xlsx",header=0).iloc[:,[0,1,2]]
md.columns=["Year","Q","m"]; md=md.apply(pd.to_numeric,errors="coerce").dropna(); md["t"]=md.Year+(md.Q-1)/4
je=A.merge(me,on=["Year","Q"]); jd=A.merge(md,on=["Year","Q"])

fig,ax=plt.subplots(2,2,figsize=(12,8))
def ts(a,t_r,y_r,t_m,y_m,ylab,tag):
    a.plot(t_r,y_r,color="#1f4e79",lw=1.4,label="Reconstructed (this build)")
    a.plot(t_m,y_m,color="#c00000",lw=1.4,ls="--",label="Myers (shared file)")
    a.axvline(t_m.max(),color="gray",lw=0.7,ls=":"); a.set_ylabel(ylab)
    a.legend(frameon=False,fontsize=8.5,loc="upper left",bbox_to_anchor=(0.0,0.99))
    a.text(0.985,0.94,tag,transform=a.transAxes,fontweight="bold",ha="right")
def sc(a,x,y,ylab,tag):
    a.scatter(x,y,s=14,color="#1f4e79",alpha=0.55,edgecolor="none")
    lo,hi=min(x.min(),y.min()),max(x.max(),y.max()); a.plot([lo,hi],[lo,hi],color="gray",lw=0.8,ls=":")
    a.set_xlabel("Myers"); a.set_ylabel("Reconstructed")
    a.text(0.985,0.94,tag,transform=a.transAxes,fontweight="bold",ha="right")
    a.text(0.04,0.90,f"corr = {pd.Series(x).corr(pd.Series(y)):.3f}\nn = {len(x)}",transform=a.transAxes,fontsize=9)
ts(ax[0,0],A.t,A.e1,me.t,me.m,"E$_t$[$\\Delta e_{t+1}$]  (1-yr earnings)","(a)")
ts(ax[0,1],A.t,A.d1,md.t,md.m,"E$_t$[$\\Delta d_{t+1}$]  (1-yr dividends)","(b)")
sc(ax[1,0],je.m.values,je.e1.values,"Reconstructed","(c)")
sc(ax[1,1],jd.m.values,jd.d1.values,"Reconstructed","(d)")
plt.tight_layout()
plt.savefig(R/"comparison_vs_myers.png",dpi=150,bbox_inches="tight")
plt.savefig(R/"comparison_vs_myers.pdf",bbox_inches="tight")
print("earnings corr",round(je.e1.corr(je.m),3)," dividend corr",round(jd.d1.corr(jd.m),3))
print("saved comparison_vs_myers.png / .pdf")
