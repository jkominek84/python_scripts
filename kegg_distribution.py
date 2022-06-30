#!/usr/bin/env python2

import os, sys, argparse
from collections import defaultdict

def getzero(a):
	b = kegg_cluster_freq[a]
	for i,c in enumerate(b):
		if c == 0:
			return i

def getnonzero(a):
	b = kegg_cluster_freq[a]
	for i,c in enumerate(b):
		if c != 0:
			return i

def getzerocount(a):
	b = kegg_cluster_freq[a]
	count = 0
	for i,c in enumerate(b):
		if c == 0:
			count += 1
	return count

parser = argparse.ArgumentParser(description='Obtain distribution of KEGG modules')
parser.add_argument("f", nargs="+", help="Files with input data.")
parser.add_argument("--inputlist", action="store_true", default=False, help="Input file contains file list")
parser.add_argument("--binary", action="store_true", default=False, help="Store KEGG absence/presence instead of counts")
parser.add_argument("--print_kegg_counts", action="store_true", default=False, help="Print KEGG counts")
parser.add_argument("--print_kegg_counts_cluster", action="store_true", default=False, help="Print KEGG counts")
parser.add_argument("--pathway", nargs="+", default="", help="Print out KEGGS from a specific pathway")

parser.add_argument("--cons", action="store_true", default=False, help="Print conserved KEGGs")
parser.add_argument("--cluster_specific", action="store_true", default=False, help="Print cluster-specific losses")

parser.add_argument("--pathway_only", action="store_true", default=False, help="PathwayOnly")
parser.add_argument("--cluster_threshold", nargs="?", default="0.001", help="Cluster species percentage frequency treshold")
parser.add_argument("--cnv", action="store_true", default=False, help="Perform CNV analysis")
parser.add_argument("--transpose", action="store_true", default=True, help="Transpose the KEGG matrix")
args = parser.parse_args()

clus = defaultdict(list)
files = []
files_short = []
if args.inputlist == True:
	with open(args.f[0], "r") as inputfile:
		for l in inputfile:
			if len(l.split()) == 1:
				files.append(l.strip())
				files_short.append(l.strip().split("/")[-1])
				clus[1].append(l.strip())
			elif len(l.split()) == 2:
				file1 = l.split()[0]
				files.append(file1)
				files_short.append(file1.split("/")[-1])
				clus_id = int(l.split()[1])
				clus[clus_id].append(file1)
else:
	files = args.f
	clus = {1:files}
num_clusters = len(clus.keys())

#GET LIST OF ALL KEGGS 
keggs_list = set()
for input_file in files:
	with open(input_file, "r") as f:
		for l in f:
			k = ""
			if len(l.strip().split("\t")) == 2:
				k = l.strip().split("\t")[1]
			if len(l.strip().split("\t")) >= 5:
				k = l.strip().split("\t")[4]
			keggs_list.add(k)

#READ KEGG FREQUENCIES FOR ALL SPECIES
kegg_matrix = {}
for input_file in files:
	input_file_short = input_file.split("/")[-1]
	with open(input_file, "r") as f:
		kegg = dict.fromkeys(keggs_list,0)
		for l in f:
			l = l.strip()
			if len(l.split("\t")) >= 2:
				if l.split("\t")[1] != "":
					if args.binary == True:
						kegg[l.split("\t")[1]] = 1
					else:
						kegg[l.split("\t")[1]] += 1
	kegg_matrix[input_file_short] = kegg 
	#print input_file_short,kegg

#PRINT KEGG FREQUENCIES FOR ALL SPECIES	
if args.print_kegg_counts == True:
	species = []
	for c in clus.keys():
		for s in clus[c]:
			s = s.split("/")[-1]
			species.append(s)
	print "KEGG\t"+"\t".join(species)
	for k in sorted(keggs_list):
		k_val = []
		for c in clus:
			for s in clus[c]:
				s = s.split("/")[-1]
				if s in files_short:
					k_val.append(str(kegg_matrix[s][k]))
				# ~ for f in files:
					# ~ f = f.split("/")[-1]
					# ~ if f == s:
						# ~ k_val.append(str(kegg_matrix[f][k]))
						# ~ break
		
		print k+"\t"+"\t".join(k_val)

print 

#PRINT KEGGS FROM (SPECIFIC) PATHWAYS
if args.pathway != "":
	print
	pathways = defaultdict(list)
	pathways_name = defaultdict(list)
	
	#READ IN ALL PATHWAYS
	with open("/home/jkominek/scripts/python/data/keggs_2020.txt") as f:
		pw = ""
		for l in f:
			l = l.strip()
			if l[:2] == "ko":
				pw = l.split()[0][2:]
				pathways[pw] = []
				pathways_name[pw] = l.replace("ko"+pw+" ","").replace(" ","_").strip()
			# ~ if pw != "" and int(pw) >= 1100:
				# ~ continue
			if pw != "" and len(l) > 1 and l[0] == "K":
				pathways[pw].append(l.split()[0])
	# ~ for pw in pathways:
		# ~ print pw+" "+"_".join(pathways[pw])
	
	#IF KEGG NUMBER SPECIFIED - LOAD ENTIRE PATHWAY
	final_pathways = []
	if args.pathway == ["all"]:
		final_pathways = sorted(pathways.keys())
	elif args.pathway != ["all"]:
		for p in args.pathway:
			if p.find("K") == -1:
				final_pathways.append(p)
			elif p.find("K") != -1:
				for pw in pathways.keys():
					if p in pathways[pw]:
						final_pathways.append(pw)
	
	
	#PRINT KEGGS FOR SPECIFIED PATHWAYS
	for p in final_pathways:
		keggs_list2 = sorted(set(pathways[p]).intersection(keggs_list))
		if len(keggs_list2) > 0:
			print "\nPathway #"+str(p)+" "+pathways_name[p]
			
			#PRINT KEGG FREQUENCIES FOR ALL SPECIES	
			print "\t".join(["Species","Cluster"]+sorted(keggs_list2))
			for c in sorted(clus.keys()):
				for s in clus[c]:
					s = s.split("/")[-1]
					if s in files_short:
						print "\t".join([s]+[str(c)]+[str(kegg_matrix[s][k]) for k in keggs_list2])
					# ~ for f in files:
						# ~ f = f.split("/")[-1]
						# ~ if f.find(s) != -1:
							# ~ print "\t".join([f]+[str(kegg_matrix[f][k]) for k in keggs_list2])
							# ~ break
			
			# ~ continue
			#PRINT KEGG FREQUENCIES FOR ALL CLUSTERS AND STORE CLUSTER SPECIFIC FREQUENCES FOR EACH KEGG
			kegg_cluster_freq = dict.fromkeys(keggs_list2)
			for k in kegg_cluster_freq:
				kegg_cluster_freq[k] = [0]*num_clusters
				
			for i,c in enumerate(clus.keys()):
				print "\nCluster"+str(i+1)+"_"+str(len(clus[c])),
				for k in sorted(keggs_list2):
					species_count = 0
					for s in clus[c]:
						s = s.split("/")[-1]
						if s in files_short and kegg_matrix[s][k] > 0:
								species_count += 1
						# ~ for f in files:
							# ~ f = f.split("/")[-1]
							# ~ if f.find(s) != -1 and kegg_matrix[f][k] > 0:
							# ~ if f.find(s) != -1:
								# ~ print f,"\t",s
								# ~ if kegg_matrix[f.split("/")[-1]][k] > 0:
									# ~ species_count += 1
									# ~ break
					print "\t"+str(species_count),
					kegg_cluster_freq[k][i] = species_count
			
			#PRINT KEGG TYPE FOR EACH CLUSTER (CONSERVED, LOST, GAINED, OTHER)
			print "\nType",
			for k in sorted(keggs_list2):
				nonzero = 0
				for freq in kegg_cluster_freq[k]:
					if freq > 0:
						nonzero += 1
				kegg_type = ""
				if nonzero == num_clusters:
					kegg_type = "C"
				elif nonzero == num_clusters-1:
					kegg_type = "L"
				elif nonzero == 1:
					kegg_type = "G"
				else:
					kegg_type = "X"	
				print "\t"+kegg_type,
			print "\n"












#PRINT KEGG FREQUENCIES FOR ALL CLUSTERS AND STORE CLUSTER SPECIFIC FREQUENCES FOR EACH KEGG
if args.print_kegg_counts_cluster == True:
	kegg_cluster_freq = dict.fromkeys(keggs_list)
	for k in kegg_cluster_freq.keys():
		kegg_cluster_freq[k] = [0]*len(clus.keys())
		
	for i,c in enumerate(clus.keys()):
		if args.transpose == False and args.pathway_only == False:
			print "\nCluster"+str(i+1)+"_"+str(len(clus[c])),
		for k in sorted(keggs_list):
			species_count = 0
			for s in clus[c]:
				for f in files:
					if f == s and kegg_matrix[f][k] > 0:
						species_count += 1
						break
			if args.transpose == False and args.pathway_only == False:
				print "\t"+str(species_count),
			kegg_cluster_freq[k][i] = species_count


	#DETERMINE THE CONSERVATION TYPE OF KEGG (Conserved,Loss,Gain,eXtra)
	if args.transpose == False and args.pathway_only == False:
		print "\nType",	

	kegg_type_list = dict.fromkeys(["C","L","G","X"])
	kegg_type_one = {}
	for k in kegg_type_list.keys():
		kegg_type_list[k] = list()

	for k in sorted(kegg_cluster_freq.keys()):
		nonzero = 0
		for i,freq in enumerate(kegg_cluster_freq[k]):
			if freq > 0:
				nonzero += 1
		kegg_type = ""
		if nonzero == num_clusters:
			kegg_type = "C"
		elif nonzero == num_clusters-1:
			kegg_type = "L"
		elif nonzero == 1:
			kegg_type = "G"
		else:
			kegg_type = "X"	
		if args.transpose == False and args.pathway_only == False:
			print "\t"+kegg_type,
		kegg_type_one[k] = kegg_type
		kegg_type_list[kegg_type].append(k)	
	print "\n"


	print "\nKEGG",
	for i,c in enumerate(clus.keys()):
		print "\tCluster"+str(i+1)+"_"+str(len(clus[c])),
	print "\tType"
	for k in sorted(keggs_list):
		print k,
		for i,c in enumerate(clus.keys()):	
			print "\t"+str(kegg_cluster_freq[k][i]),
		print "\t"+kegg_type_one[k]
			
	print "\n"

	for t in kegg_type_list.keys():
		print t,len(kegg_type_list[t])

	#PRINT SPECIFIC KEGG TYPES
	print "\nLOST KEGGS"
	for k in sorted(kegg_type_list["L"], key=getzero):
		print k+"\t"+"\t".join(str(f) for f in kegg_cluster_freq[k])
			
	print "\nGAINED KEGGS"
	for k in sorted(kegg_type_list["G"], key=getnonzero):
		print k+"\t"+"\t".join(str(f) for f in kegg_cluster_freq[k])

	for n in range(2,len(clus.keys())-1):
		print "\nEXTRA KEGGS "+str(n)
		sortlist = []
		for k in kegg_type_list["X"]:
			if getzerocount(k) == n:
				sortlist.append(k)
		sortlist2 = sorted(sortlist, key=lambda k: getzero(k))
		sortlist3 = sorted(sortlist2, key=lambda k: getnonzero(k), reverse=True)
		for k in sortlist3:
			print k+"\t"+"\t".join(str(f) for f in kegg_cluster_freq[k])

	if args.cons == True:
		print "\nCONSERVED KEGGS"
		for k in sorted(kegg_type_list["C"], key=lambda k: "_".join(str(f) for f in kegg_cluster_freq[k])):
			print k+"\t"+"\t".join(str(f) for f in kegg_cluster_freq[k])

	print "\nCLUSTER SPECIFIC KEGG LOSSES"
	for n in range(0,len(clus.keys())):
		print "\n\nCLUSTER "+str(n+1)
		for k in sorted(kegg_cluster_freq.keys()):
			if kegg_cluster_freq[k][n] == 0:
				print k+"\t"+"\t".join(str(f) for f in kegg_cluster_freq[k])








#PRINT TOTAL KEGG COPY NUMBERS PER EACH CLUSTER
if args.cnv == True:
	kegg_cluster_cnv = defaultdict(list)
	print "\n\nCNV analyses"
	if args.transpose == False:
		print "\nCluster\t"+"\t".join(sorted(keggs_list))
	for i,c in enumerate(clus.keys()):
		if args.transpose == False:
			print "\nCluster"+str(i+1)+"_"+str(len(clus[c])),
		for k in sorted(keggs_list):
			gene_count = 0
			for s in clus[c]:
				for f in files:
					if f == s and kegg_matrix[f][k] > 0:
						gene_count += int(kegg_matrix[f][k])
						break
			kegg_cluster_cnv[k].append(gene_count)
			if args.transpose == False:
				print "\t"+str(gene_count),
	
	if args.transpose == True:
		print "\nKEGG",
		for i,c in enumerate(clus.keys()):
			print "\tCluster"+str(i+1)+"_"+str(len(clus[c])),
		print 
		for k in sorted(keggs_list):
			print k,
			for i,c in enumerate(clus.keys()):	
				print "\t"+str(kegg_cluster_cnv[k][i]),
			print



#PRINT CLUSTER PERCENTEGE FREQUENCIES
if len(clus.keys()) > 1 and args.cluster_threshold != "0.001":
	kegg_cluster_freq2 = dict.fromkeys(keggs_list)
	for k in kegg_cluster_freq2.keys():
		kegg_cluster_freq2[k] = [0]*len(clus.keys())
	
	print "\n\nThreshold analyses ("+args.cluster_threshold+")"
	if args.transpose == False:
		print "Cluster\t"+"\t".join(sorted(keggs_list))
	for i,c in enumerate(clus.keys()):
		if args.transpose == False:
			print "\nCluster"+str(i+1)+"_"+str(len(clus[c])),
		for k in sorted(keggs_list):
			species_count = 0
			for s in clus[c]:
				for f in files:
					if f == s and kegg_matrix[f][k] > 0:
						#print kegg_matrix[f][k]
						species_count += int(kegg_matrix[f][k])
						break
			if args.transpose == False:
				print "\t"+"%.2f" % float(float(species_count)/float(len(clus[i+1]))),
			kegg_cluster_freq2[k][i] = "%.2f" % float(float(species_count)/float(len(clus[i+1])))
	
	
	print "\nType",		
	kegg_type_list2 = defaultdict(list)
	kegg_type_one2 = {}
	for k in sorted(kegg_cluster_freq2.keys()):
		one = 0
		less = 0
		more = 0
		for i,freq in enumerate(kegg_cluster_freq2[k]):
			if float(freq) == 1 or (float(freq) < 1 and float(freq) >= float(args.cluster_threshold)):
				one += 1
			elif float(freq) < 1 and float(freq) < float(args.cluster_threshold):
				less += 1
			elif float(freq) > 1:
				more += 1
		kegg_type = "C"+str(one)+"_+"+str(more)+"_-"+str(less)
		if args.transpose == False:
			print "\t"+kegg_type,
		
		kegg_type_list2[kegg_type].append(k)
		kegg_type_one2[k] = kegg_type
	print "\n"


	if args.transpose == True:
		print "\nKEGG",
		for i,c in enumerate(clus.keys()):
			print "\tCluster"+str(i+1)+"_"+str(len(clus[c])),
		print "\tType"
		for k in sorted(keggs_list):
			print k,
			for i,c in enumerate(clus.keys()):	
				print "\t"+str(kegg_cluster_freq2[k][i]),
			print "\t"+kegg_type_one2[k]
			
			

	print 
	for t in sorted(kegg_type_list2.keys()):
		print t+"\t"+str(len(kegg_type_list2[t]))
	
	for t in sorted(kegg_type_list2.keys()):
		print "\n"+t
		tmplist = []
		for k in sorted(kegg_type_list2[t]):
			tmplist.append([k]+kegg_cluster_freq2[k])
		#for k in sorted(tmplist, key = lambda x: (float(x[1]),float(x[2]),float(x[3]),float(x[4]),float(x[5]),float(x[6]),float(x[7]),x[0])):
		for k in sorted(tmplist, key = lambda x: (float(x[1]),float(x[2]),float(x[3]),float(x[4]),float(x[5]),float(x[6]),float(x[7]),x[0])):
			#print k
			print k[0]+"\t"+"\t".join([str(f) for f in k[1:]])
			#print k+"\t"+"\t".join(str(f) for f in kegg_cluster_freq2[k])
				





