#!/usr/bin/env python

import warnings
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC
import sys, argparse, os
from collections import defaultdict
from natsort import natsorted 
import backports.functools_lru_cache

import numpy as np
from scipy import stats
import random
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from PyPDF2 import PdfFileMerger, PdfFileReader

parser = argparse.ArgumentParser(description="")
parser.add_argument("dir", help="Input dir")
parser.add_argument("--window", nargs="+", default=["1000"], help="")
parser.add_argument("--events", action="store_true", default=False, help="")
parser.add_argument("--events_range", default = "10", help="")
parser.add_argument("--local_z", action = "store_true", default = False, help="")
parser.add_argument("--min_contig", default = "1000", help="")
parser.add_argument("--bins", default="100", help="")
parser.add_argument("--out", default="GC_plot.pdf", help="")
parser.add_argument("--out_stats", default="GC_plot.txt", help="")
parser.add_argument("--plot_len", action="store_true", default=False, help="")
parser.add_argument("--plot_no_title", action="store_true", default=False, help="")
parser.add_argument("--plot_sd", action="store_true", default=False, help="")
parser.add_argument("--plot_count_pdf", default="20", help="")
args = parser.parse_args()

pp_out = PdfPages(args.out)
pp_out.close()
pp = PdfPages(args.out+"_tmp")
pp.close()
plots = []

gc_stats = defaultdict(list)
out_stats_file = open(args.out.replace("pdf","txt"),"w")
out_stats_file.write("Input\t"+"\t".join(natsorted([str(x+"\t"+x+"_SD") for x in args.window]))+"\n")
files = sorted(os.listdir(args.dir))
for fi,f1 in enumerate(files):
	with open(args.dir+"/"+f1) as f:
		first = True
		for l in f:
			if len(l.split()) > 0:
				print l
				fname = l.split()[0]
				win = l.split()[1]
				#slide = win
				#min_contig = l.split()[2]
				#n50 = l.split()[3]
				#gc_data_raw = l.split()[4:]
				
				slide = l.split()[2]
				min_contig = l.split()[3]
				n50 = l.split()[4]
				gc_data_raw = l.split()[5:]
				gc_data = []
				
				if win in natsorted(args.window) and int(min_contig) >= int(args.min_contig):
					if first == True:
						out_stats_file.write(f1)
						first = False
					if args.plot_len == False:
						if len(gc_data_raw) >= 1:
							if gc_data_raw[0].find("_") == -1:
								gc_data = [float(x) for x in gc_data_raw]
							else:
								for w in gc_data_raw:
									for gc in w.split("_"):
										gc_data.append(float(gc))
							#print gc_data
							#print gc_data_raw
							bins = np.linspace(0,1,int(args.bins)+1)
							fig = plt.figure()
							ax = plt.gca()
							ax.xaxis.set_ticklabels(['{:2.0f}%'.format(x) for x in np.linspace(0,100,11)])
							ax.set_xlabel('GC content')
							ax.xaxis.set_ticks_position("bottom")
							ax.xaxis.set_tick_params(width=2)
							plt.xlim([0,1])
							plt.xticks(np.linspace(0,1,11))
							
							if args.plot_no_title == False:
								plt.title(f1+"_w"+win+"_s"+slide+"_m"+min_contig+"_n"+n50,fontsize=10)
							print str(fi+1)+"/"+str(len(files)),f1,win,"plotting ("+str(len(gc_data))+" points)"
							sys.stdout.flush()
							mean_gc = np.mean(gc_data)
							std_gc = np.std(gc_data)
							plt.hist(gc_data, bins=bins, label="GC"+"_"+"{:.2f}".format(mean_gc*100)+"_"+"{:.2f}".format(std_gc*100), alpha=0.5, color="red")
							out_stats_file.write("\t"+str(mean_gc)+"\t"+str(std_gc))
							out_stats_file.flush()
					else:
						contig_breaks = []
						if gc_data_raw[0].find("_") == -1:
							gc_data = [float(x) for x in gc_data_raw]
							print str(fi+1)+"/"+str(len(files)),f1,win,"plotting ("+str(len(gc_data))+" points)"
							sys.stdout.flush()
							
							ticks = 0
							mod = 1
							mod = 1000000/int(win)
							mod = 1000000/int(slide)
							
							ticks = ((len(gc_data)/mod)+1)
							
							fig = plt.figure()
							plt.xlim([0,ticks*mod])
							plt.xticks(np.linspace(0,ticks*mod,ticks+1))
							plt.ylim([0,1])
					
							ax = plt.gca()
							ax.xaxis.set_ticks_position("bottom")
							ax.xaxis.set_tick_params(width=2)
							
							ax.xaxis.set_ticklabels(['{:2.0f}'.format(x) for x in np.linspace(0,ticks,ticks+1)])
							ax.set_xlabel('Genome position (Mb)')
							
							plt.yticks(np.linspace(0,1,11))
							ax.yaxis.set_ticklabels(['{:3.0f}%'.format(x) for x in np.linspace(0,100,11)])
							ax.set_ylabel('GC content')
							if args.plot_no_title == False:
								plt.title(f1+"_w"+win+"_s"+slide+"_m"+min_contig+"_n"+n50,fontsize=10)
							for y in np.linspace(0,1,11):
								plt.axhline(y, color="lightgrey",linewidth=1)
							mean_gc = np.mean(gc_data)
							std_gc = np.std(gc_data)
							plt.plot(gc_data, label="GC"+"_"+"{:.2f}".format(mean_gc*100)+"_"+"{:.2f}".format(std_gc*100), alpha=0.5, color="red")
							plt.axhline(mean_gc, color="blue")
							out_stats_file.write("\t"+str(mean_gc)+"\t"+str(std_gc))
							out_stats_file.flush()
						else:
							all_gc = []
							for w in gc_data_raw:
								for gc in w.split("_"):
									all_gc.append(float(gc))
							print str(fi+1)+"/"+str(len(files)),f1,win,"plotting ("+str(len(all_gc))+" points)"
							
							sys.stdout.flush()
							ticks = 0
							mod = 1
							mod = 1000000/int(win)
							mod = 1000000/int(slide)
							
							
							ticks = ((len(all_gc)/mod)+1)
							fig = plt.figure()
							plt.xlim([0,ticks*mod])
							plt.xticks(np.linspace(0,ticks*mod,ticks+1))
							plt.ylim([0,1])
							
							ax = plt.gca()
							ax.xaxis.set_ticks_position("bottom")
							ax.xaxis.set_tick_params(width=1)
							ax.xaxis.set_ticklabels(['{:2.0f}'.format(x) for x in np.linspace(0,ticks,ticks+1)])
							ax.set_xlabel('Genome position (Mb)')
							
							plt.yticks(np.linspace(0,1,11))
							ax.yaxis.set_ticklabels(['{:3.0f}%'.format(x) for x in np.linspace(0,100,11)])
							ax.set_ylabel('GC content')
							
							if args.plot_no_title == False:
								plt.title(f1+"_w"+win+"_s"+slide+"_m"+min_contig+"_n"+n50,fontsize=10)
							for y in np.linspace(0,1,11):
								plt.axhline(y, color="lightgrey", alpha=0.5, linewidth=1)
							mean_gc = np.mean(all_gc)
							std_gc = np.std(all_gc)
							plt.plot(0, label="GC"+"_"+"{:.2f}".format(mean_gc*100)+"_"+"{:.2f}".format(std_gc*100), alpha=1, color="red")
														
							shift = 0
							#out_stats_file.write(f1+"\t"+str(mean_gc)+"\t"+str(std_gc)+"\n")
							out_stats_file.write("\t"+str(mean_gc)+"\t"+str(std_gc))
							out_stats_file.flush()
							for i,w in enumerate(gc_data_raw):
								plt.axvline(shift+len(w.split("_")), color="lightblue",alpha=1,linewidth=1)
								gc_data_win = []	
								for gc in w.split("_"):
									gc_data_win.append(float(gc))
								
								#ANALYZE WINDOW
								if args.events == True:
									w_gc_min = min(gc_data_win)
									
									w_gc_max = max(gc_data_win)
									w_gc_mean = np.mean(gc_data_win)
									w_gc_std = np.std(gc_data_win)
									w_gc_median = np.median(gc_data_win)
									w_gc_mode = stats.mode(gc_data_win)
									#w_gc_zscore = stats.zscore(gc_data_win)
									#for gc,z in zip(gc_data_win,w_gc_zscore):
									#	print gc_mean,gc,z
									t_down = -2
									t_up = 2
									for j,gc in enumerate(gc_data_win):
										#if gc == w_gc_min:
											#plt.axvline(shift+j, ymax=gc,color="green", alpha=0.5, linewidth=1)
										z = (gc-mean_gc)/std_gc
										if z > t_up or z < t_down:
											#print str(i+1),(shift+j)*int(win),"{:.3f}".format(gc-mean_gc),"{:.3f}".format(mean_gc),"{:.3f}".format(gc),z
											if z > t_up:
												plt.axvline(shift+j, ymin=gc, color="orange", alpha=0.5, linewidth=1)
											if z < t_down:
												plt.axvline(shift+j, ymax=gc,color="violet", alpha=1, linewidth=1)
									if args.local_z == True:
										loc_mean = 0
										loc_size = 10
										for j,gc in enumerate(gc_data_win):
											if j > loc_size and j < len(gc_data_win)-loc_size:
												loc_mean = np.mean(gc_data_win[j-loc_size:j+loc_size])
												loc_std = np.std(gc_data_win[j-loc_size:j+loc_size])
												loc_z = (gc-loc_mean)/loc_std
												if loc_z > t_up or loc_z < t_down:
													#print str(i+1),(shift+j)*int(win),"{:.3f}".format(gc-loc_mean),"{:.3f}".format(loc_mean),"{:.3f}".format(gc),loc_z	
													if loc_z > t_up:
														plt.axvline(shift+j, ymin=gc, color="orange", alpha=0.5, linewidth=1)
													if loc_z < t_down:
														plt.axvline(shift+j, ymax=gc,color="violet", alpha=0.5, linewidth=1)
								#plt.plot(range(shift,shift+len(gc_data_win)), gc_data_win, alpha=0.5, color="red")
								shift += len(w.split("_"))
							plt.plot(all_gc, alpha=0.5, color="red", linewidth=1)
							plt.axhline(mean_gc, color="blue")
							if args.plot_sd == True:
								ax.fill_between(range(1,len(all_gc)),mean_gc-2*std_gc,mean_gc+2*std_gc,color="silver")
								ax.fill_between(range(1,len(all_gc)),mean_gc-std_gc,mean_gc+std_gc,color="lightgray")
							#plt.axhline(mean_gc+std_gc, color="blue")
							#plt.axhline(mean_gc-std_gc, color="blue")
							#plt.axhline(mean_gc+2*std_gc, color="lightblue")
							#plt.axhline(mean_gc-2*std_gc, color="lightblue")
							
							for i,w in enumerate(gc_data_raw):
								gc_data_win = []	
								for gc in w.split("_"):
									gc_data_win.append(float(gc))
								
								
					plt.legend(loc="upper right")
					plots.append(fig)
					if (len(plots)%int(args.plot_count_pdf)) == 0:
						pp = PdfPages(args.out+"_tmp")
						for p in plots:
							p.savefig(pp,format="pdf")
							plt.close(p)
						pp.close()
						merger = PdfFileMerger()
						merger.append(PdfFileReader(file(args.out, 'rb')))
						merger.append(PdfFileReader(file(args.out+"_tmp", 'rb')))
						merger.write(args.out)
						plots = []
					#plt.savefig(pp,format="pdf")
					#pp.savefig(format="pdf")
					#plt.close()
					#pp.close()
					#merger = PdfFileMerger()
					#merger.append(PdfFileReader(file(args.out, 'rw')))
					#merger.append(PdfFileReader(file(args.out+"_tmp", 'rb')))
					#merger.write(args.out)
		out_stats_file.write("\n")

pp = PdfPages(args.out+"_tmp")
for p in plots:
	p.savefig(pp,format="pdf")
	plt.close(p)
pp.close()
merger = PdfFileMerger()
merger.append(PdfFileReader(file(args.out, 'rb')))
merger.append(PdfFileReader(file(args.out+"_tmp", 'rb')))
merger.write(args.out)

if os.path.exists(args.out+"_tmp"):
	os.remove(args.out+"_tmp")
out_stats_file.close()
