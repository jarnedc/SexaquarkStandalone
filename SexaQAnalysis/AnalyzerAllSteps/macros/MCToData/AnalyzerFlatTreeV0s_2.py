from ROOT import TFile, TH1F, TH2F, TEfficiency, TH1D, TH2D, TCanvas, gROOT,TProfile
import numpy as np
import copy
from array import array

fIns = [
#the standard V0s:
#'/storage_mnt/storage/user/jdeclerc/CMSSW_8_0_30_bis/src/SexaQAnalysis/AnalyzerAllSteps/test/FlatTreeProducerV0s/qsub/FlatTrees_DoubleMuon_standardV0s/combined_FlatTreeV0_DoubleMuonData_RunC_D_E_G_H.root',
#'/storage_mnt/storage/user/jdeclerc/CMSSW_8_0_30_bis/src/SexaQAnalysis/AnalyzerAllSteps/test/FlatTreeProducerV0s/qsub/FlatTrees_DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_standardV0s/combined_FlatTreeV0_DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8.root',

#the adapted V0s:
'/user/jdeclerc/CMSSW_8_0_30_bis/src/SexaQAnalysis/AnalyzerAllSteps/test/FlatTreeProducerV0s/qsub/Results/FlatTrees_DoubleMuon_adaptedV0s_extendedFlatTree6/combined_FlatTreeV0_DoubleMuonData_Run_G_H.root',
'/user/jdeclerc/CMSSW_8_0_30_bis/src/SexaQAnalysis/AnalyzerAllSteps/test/FlatTreeProducerV0s/qsub/Results/FlatTrees_DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_adaptedV0s_extendedFlatTree6/combined/combined_FlatTreeV0_DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8.root'
]

def eff_error(data,MC):
	return data/MC*np.sqrt(1/MC+1/data)	

#checks which one is the largest in absolute terms and then returns the signed value
def maxSigned(x1, x2):
	if(abs(x1) > abs(x2)):
		return x1
	else:
		return x2

#fist find which of the trees has the smallest number of entries. Data or MC?
fIn1 = TFile(fIns[0],'read')
fIn2 = TFile(fIns[1],'read')
treeKs1 = fIn1.Get('FlatTreeProducerV0s/FlatTreeKs')
treeKs2 = fIn2.Get('FlatTreeProducerV0s/FlatTreeKs')
min_entries = min( treeKs1.GetEntries(), treeKs2.GetEntries() )
print "the nentries in Data: " , treeKs1.GetEntries()
print "the nentries in MC: " , treeKs2.GetEntries()
print "the min_enties: ", min_entries

iFile = 0
h_RECO_PV0_vz_Data= TH1F('h_RECO_PV0_vz_Data'," ;PV vz (cm); #entries",20000,-100,100)
h_RECO_PV0_vz_MC= TH1F('h_RECO_PV0_vz_MC'," ;PV vz (cm); #entries",20000,-100,100)
for fIn in fIns:
	fIn = TFile(fIn,'read')
	treePV  = fIn.Get('FlatTreeProducerV0s/FlatTreePV')
	for i in range(0,min_entries):
		treePV.GetEntry(i)
		if(iFile == 0):
			h_RECO_PV0_vz_Data.Fill(treePV._PV0_vz[0])	
		else:	
			h_RECO_PV0_vz_MC.Fill(treePV._PV0_vz[0])
	iFile = iFile+1	

iFile = 0
h_RECO_beamspot_vz_Data= TH1F('h_RECO_beamspot_vz_Data'," ;PV vz (cm); #entries",2000,-2,2)
h_RECO_beamspot_vz_MC= TH1F('h_RECO_beamspot_vz_MC'," ;PV vz (cm); #entries",2000,-2,2)
h_RECO_beamspot_vz_Data.SetDirectory(0)
h_RECO_beamspot_vz_MC.SetDirectory(0)
for fIn in fIns:
	fIn = TFile(fIn,'read')
	treeBeamspot  = fIn.Get('FlatTreeProducerV0s/FlatTreeBeamspot')
	for i in range(0,min_entries):
		treeBeamspot.GetEntry(i)
		if(iFile == 0):
			h_RECO_beamspot_vz_Data.Fill(treeBeamspot._beampot_vz[0])	
		else:	
			h_RECO_beamspot_vz_MC.Fill(treeBeamspot._beampot_vz[0])
	iFile = iFile+1	

#normalize the histogram of PV in data to later use it for reweighting 
#h_RECO_PV0_vz_Data.Scale(1./h_RECO_PV0_vz_Data.Integral(), "width")
#h_RECO_PV0_vz_MC.Scale(1./h_RECO_PV0_vz_MC.Integral(), "width")

fOut = TFile('Results/output_DataToMC_RunG_H_with_dxy_dz_min_PV_reweighing_on_Ks_vz_Dz_min_PV.root','RECREATE')
h_dummy =  TH1F('h_dummy'," x; y",20,0,10)
histos_Data = [h_dummy]*9
histos_MC = [h_dummy]*9

nKshortPerEventData = []
nKshortPerEventMC = []

iFile = 0
for fIn in fIns:

	print "creating plots for file: ", fIn

	fIn = TFile(fIn,'read')

	treeKs = fIn.Get('FlatTreeProducerV0s/FlatTreeKs') 
	treeZ = fIn.Get('FlatTreeProducerV0s/FlatTreeZ')
	treePV = fIn.Get('FlatTreeProducerV0s/FlatTreePV')
	treeBeamspot = fIn.Get('FlatTreeProducerV0s/FlatTreeBeamspot')

	nEntriesKs = treeKs.GetEntries()
	nEntriesZ = treeZ.GetEntries()
	nEntriesPV = treePV.GetEntries()
	nEntriesBeamspot = treeBeamspot.GetEntries()

	print 'Number of entries in the treeKs: ', nEntriesKs
	print 'Number of entries in the treeZ: ', nEntriesZ
	print 'Number of entries in the treePV: ', nEntriesPV
	print 'Number of entries in the treeBeamspot: ', nEntriesBeamspot

	bins1 = np.arange(-150,-60,10)
	bins2 = np.arange(-60,60,1)
	bins3 = np.arange(60,150,10)
	args = (bins1,bins2,bins3)
	bins = np.concatenate(args)
	h_RECO_Ks_vz = TH1F('h_RECO_Ks_vz'," ;Ks v_{z} (cm); #entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_vz_beamspot = TH1F('h_RECO_Ks_vz_beamspot'," ;Ks v_{z} (beamspot) (cm); #entries",len(bins)-1,array('d',bins))

	bins1 = np.arange(0,50,1)
	bins2 = np.arange(50,56,1.5)
	bins3 = np.arange(56,65,1.8)
	bins4 = np.arange(65,70,2.5)
	bins5 = np.arange(70,90,5)
	args = (bins1,bins2,bins3,bins4,bins5)
	bins = np.concatenate(args)
	h_RECO_Ks_lxy = TH1F('h_RECO_Ks_lxy'," ;Ks l_{0} (beamspot) (cm);#entries",len(bins)-1,array('d',bins))

	bins0 = np.arange(0,0.8,0.02)
	bins1 = np.arange(0.8,2,0.1)
	bins2 = np.arange(2,8,0.2)
	bins3 = np.arange(8,10.1,0.3)
	args = (bins0,bins1,bins2,bins3)
	bins = np.concatenate(args)
	h_RECO_Ks_pt = TH1F('h_RECO_Ks_pt',"; Ks p_{t} (GeV);#entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_pt_tracks1 = TH1F('h_RECO_Ks_pt_tracks1',"; Ks daughter 1 p_{t} (GeV);#entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_pt_tracks2 = TH1F('h_RECO_Ks_pt_tracks2',"; Ks daughter 2 p_{t} (GeV);#entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_pt_tracks1_and_2 = TH1F('h_RECO_Ks_pt_tracks1_and_2',"; Ks daughter 1 and 2 p_{t} (GeV);#entries",len(bins)-1,array('d',bins))

	bins1 = np.arange(0,15,1)
	bins2 = np.arange(15,21,1.5)
	bins3 = np.arange(21,25,2)
	bins4 = np.arange(25,40,5)
	args = (bins1,bins2,bins3,bins4)
	bins = np.concatenate(args)
	h_RECO_Ks_pz= TH1F('h_RECO_Ks_pz',"; Ks p_{z} (GeV);#entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_pz_tracks1 = TH1F('h_RECO_Ks_pz_tracks1',"; Ks daughter 1 p_{z} (GeV);#entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_pz_tracks2 = TH1F('h_RECO_Ks_pz_tracks2',"; Ks daughter 2 p_{z} (GeV);#entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_pz_tracks1_and_2 = TH1F('h_RECO_Ks_pz_tracks1_and_2',"; Ks daughter 1 and 2 p_{z} (GeV);#entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_dxy_PV= TH1F('h_RECO_Ks_dxy_PV',"; Ks d_{0} (cm); #entries",100,-10,10)

	bins = [ -30,-28,-26,-24,-22,-20,-18,-16,-14,-12,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,22,24,26,28,30 ]
	bins1 = np.arange(-30,-20,2)
	bins2 = np.arange(-20,-14,1.5)
	bins3 = np.arange(-14,14,1)
	bins4 = np.arange(14,20,1.5)
	bins5 = np.arange(20,30,2)
	args = (bins1,bins2,bins3,bins4,bins5)
	bins = np.concatenate(args)
	h_RECO_Ks_dz= TH1F('h_RECO_Ks_dz',";  Ks d_{z}(0,0,0) (cm); #entries",len(bins)-1,array('d',bins))

	bins = [ 0, .5, 1, 1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,8,9,10,12,14,16 ]
	h_RECO_Ks_Track1_dxy_beamspot= TH1F('h_RECO_Ks_Track1_dxy_beamspot',";d_{0}(beamspot) track1 (cm) ;#entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_Track2_dxy_beamspot= TH1F('h_RECO_Ks_Track2_dxy_beamspot',";d_{0}(beamspot) track2 (cm) ;#entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_Track1_and_2_dxy_beamspot= TH1F('h_RECO_Ks_Track1_and_2_dxy_beamspot',";d_{0}(beamspot) track1 and 2 (cm) ;#entries",len(bins)-1,array('d',bins))

	bins = [ -40,-35,-30,-28,-26,-24,-22,-20,-18,-16,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,16,18,20,22,24,26,28,30,35,40 ]
	h_RECO_Ks_Track1Track2_max_dz_min_PV = TH1F('h_RECO_Ks_Track1Track2_max_dz_min_PV',"; maxSigned[d_{z}(best PV Ks) track1, d_{z}(best PV Ks) track2]   Ks (cm) ;#entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_Track1Track2_max_dz_beamspot = TH1F('h_RECO_Ks_Track1Track2_max_dz_beamspot',"; maxSigned[d_{z}(beamspot) track1, d_{z}(beamspot) track2]   Ks (cm) ;#entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_Track1_dz_min_PV = TH1F('h_RECO_Ks_Track1_dz_min_PV',"; d_{z}(best PV Ks) track1 (cm) ;#entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_Track2_dz_min_PV = TH1F('h_RECO_Ks_Track2_dz_min_PV',"; d_{z}(best PV Ks) track2 (cm) ;#entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_Track1_and_2_dz_min_PV = TH1F('h_RECO_Ks_Track1_and_2_dz_min_PV',"; d_{z}(best PV Ks) track 1 and 2 (cm) ;#entries",len(bins)-1,array('d',bins))
	h_RECO_Ks_Track1_and_2_dz_beamspot = TH1F('h_RECO_Ks_Track1_and_2_dz_beamspot',"; d_{z}(beamspot) track 1 and 2 (cm) ;#entries",len(bins)-1,array('d',bins))

	histos= [
	h_RECO_Ks_vz, 
	h_RECO_Ks_vz_beamspot, 
	h_RECO_Ks_lxy, 
	h_RECO_Ks_pt, 
	h_RECO_Ks_pt_tracks1, 
	h_RECO_Ks_pt_tracks2,
	h_RECO_Ks_pt_tracks1_and_2, 
	h_RECO_Ks_pz, 
	h_RECO_Ks_pz_tracks1, 
	h_RECO_Ks_pz_tracks2, 
	h_RECO_Ks_pz_tracks1_and_2,
	h_RECO_Ks_dxy_PV, 
	h_RECO_Ks_dz, 
	h_RECO_Ks_Track1_dxy_beamspot,
	h_RECO_Ks_Track2_dxy_beamspot,
	h_RECO_Ks_Track1_and_2_dxy_beamspot,
	h_RECO_Ks_Track1Track2_max_dz_min_PV,
	h_RECO_Ks_Track1Track2_max_dz_beamspot,
	h_RECO_Ks_Track1_dz_min_PV,
	h_RECO_Ks_Track2_dz_min_PV,
	h_RECO_Ks_Track1_and_2_dz_min_PV,
	h_RECO_Ks_Track1_and_2_dz_beamspot
	] 
	#check the reweighting
	h_RECO_PV0_vz_MC_reweighted_to_data = TH1F('h_RECO_PV0_vz_MC_reweighted_to_data'," ;PV v_{z} (cm); #entries",200,-100,100)
	h_RECO_PV0_vz_MC_NOTreweighted_to_data = TH1F('h_RECO_PV0_vz_MC_NOTreweighted_to_data',"; PV v_{z} (cm); #entries",200,-100,100)
	#check the reweighing factor versus the _Ks_vz_dz_min_PV
	tprof_Ks_vz_dz_min_PV_reweighing_factor = TProfile('tprof_Ks_vz_dz_min_PV_reweighing_factor',"; _Ks_vz_dz_min_PV (cm); reweighing factor",100,-50,50,0,2)
	tprof_Ks_vz_reweighing_factor = TProfile('tprof_Ks_vz_reweighing_factor',"; _Ks_vz (cm); reweighing factor",300,-150,150,0,2)
	#check the reweighing of the beamspot
	h_RECO_beamspot_vz_MC_reweighted_to_data = TH1F('h_RECO_beamspot_vz_MC_reweighted_to_data'," ;beamspot v_{z} (cm); #entries",200,-100,100)
	h_RECO_beamspot_vz_MC_NOTreweighted_to_data = TH1F('h_RECO_beamspot_vz_MC_NOTreweighted_to_data',"; beamspot v_{z} (cm); #entries",200,-100,100)

	for i in range(0,min_entries):
		if(i > 10e5):
			continue
		if(i%1e5 == 0):
			print 'reached event ', i
	
		treeZ.GetEntry(i)
		treeKs.GetEntry(i)
		treePV.GetEntry(i)
		treeBeamspot.GetEntry(i)
		
		nKshortThisEvent = 0
	

		#only select a certain hard scale
#		if(treeZ._Z_ptMuMu[0] < 5):
#		       continue
		
		#now loop over all the Ks in this event:
		for j in range(0, len(treeKs._Ks_mass)):
			
			#require only Ks coming from the first PV
			#if(treeKs._Ks_mass[j] > 0.48 and treeKs._Ks_mass[j] < 0.52 and  abs(treeKs._Ks_eta[j]) < 2 and treeKs._Ks_dxy_beamspot[j] < 0.1 and treeKs._Ks_dxy_beamspot[j] > 0. and abs(treeKs._Ks_dz_PV0[j]) < 0.2) :
			#require only Ks which point to a 'best PV'
			if(treeKs._Ks_mass[j] > 0.48 and treeKs._Ks_mass[j] < 0.52 and  abs(treeKs._Ks_eta[j]) < 2 and treeKs._Ks_dxy_beamspot[j] < 0.1 and treeKs._Ks_dxy_beamspot[j] > 0. and abs(treeKs._Ks_dz_min_PV[j]) < 0.2) :
			#require only Ks which point away in dz from any PV
			#if(treeKs._Ks_mass[j] > 0.48 and treeKs._Ks_mass[j] < 0.52 and  abs(treeKs._Ks_eta[j]) < 2 and treeKs._Ks_dxy_beamspot[j] < 0.1 and treeKs._Ks_dxy_beamspot[j] > 0. and abs(treeKs._Ks_dz_min_PV[j]) > 0.2) :
			#require 'PU Ks' by asking for a Ks with large _Ks_dz_PV0, but small _Ks_dz_min_PV
			#if(treeKs._Ks_mass[j] > 0.48 and treeKs._Ks_mass[j] < 0.52 and  abs(treeKs._Ks_eta[j]) < 2 and treeKs._Ks_dxy_beamspot[j] < 0.1 and treeKs._Ks_dxy_beamspot[j] > 0. and abs(treeKs._Ks_dz_PV0[j]) > 0.2 and abs(treeKs._Ks_dz_min_PV[j]) < 0.2) :

				nKshortThisEvent+=1

				#1st reweigihing factor
				x_axis_h_RECO_PV0_vz_Data = h_RECO_PV0_vz_Data.GetXaxis()
				bin_prob_h_RECO_PV0_vz_Data = x_axis_h_RECO_PV0_vz_Data.FindBin(treeKs._Ks_vz_dz_min_PV[j]) 
				prob_h_RECO_PV0_vz_Data = h_RECO_PV0_vz_Data.GetBinContent(bin_prob_h_RECO_PV0_vz_Data) #the actual probability

				x_axis_h_RECO_PV0_vz_MC= h_RECO_PV0_vz_MC.GetXaxis()
				bin_prob_h_RECO_PV0_vz_MC= x_axis_h_RECO_PV0_vz_MC.FindBin(treeKs._Ks_vz_dz_min_PV[j]) 
				prob_h_RECO_PV0_vz_MC= h_RECO_PV0_vz_MC.GetBinContent(bin_prob_h_RECO_PV0_vz_MC) #the actual probability

				PV_Z_reweighting_factor = 1
				if(prob_h_RECO_PV0_vz_MC > 0 and iFile == 1): #only reweigh for MC
					PV_Z_reweighting_factor = prob_h_RECO_PV0_vz_Data/prob_h_RECO_PV0_vz_MC


				#2nd reweighing factor
				x_axis_h_RECO_beamspot_vz_Data = h_RECO_beamspot_vz_Data.GetXaxis()
				bin_prob_h_RECO_beamspot_vz_Data = x_axis_h_RECO_beamspot_vz_Data.FindBin(treeBeamspot._beampot_vz[0]) 
				prob_h_RECO_beamspot_vz_Data = h_RECO_beamspot_vz_Data.GetBinContent(bin_prob_h_RECO_beamspot_vz_Data) #the actual probability

				x_axis_h_RECO_beamspot_vz_MC= h_RECO_beamspot_vz_MC.GetXaxis()
				bin_prob_h_RECO_beamspot_vz_MC= x_axis_h_RECO_beamspot_vz_MC.FindBin(treeBeamspot._beampot_vz[0]) 
				prob_h_RECO_beamspot_vz_MC= h_RECO_beamspot_vz_MC.GetBinContent(bin_prob_h_RECO_beamspot_vz_MC) #the actual probability

				beamspot_Z_reweighting_factor = 1
				if(prob_h_RECO_beamspot_vz_MC > 0 and iFile == 1): #only reweigh for MC
					beamspot_Z_reweighting_factor = prob_h_RECO_beamspot_vz_Data/prob_h_RECO_beamspot_vz_MC

				#if(iFile == 1):
				#	print 'PV_Z_reweighting_factor: ' , str(PV_Z_reweighting_factor)
				#	print 'beamspot_Z_reweighting_factor: ' , str(beamspot_Z_reweighting_factor)

				if(iFile == 1): #for MC
					h_RECO_PV0_vz_MC_reweighted_to_data.Fill(treePV._PV0_vz[0], PV_Z_reweighting_factor)
					h_RECO_PV0_vz_MC_NOTreweighted_to_data.Fill(treePV._PV0_vz[0], 1)
					tprof_Ks_vz_dz_min_PV_reweighing_factor.Fill(treeKs._Ks_vz_dz_min_PV[j],PV_Z_reweighting_factor)
					tprof_Ks_vz_reweighing_factor.Fill(treeKs._Ks_vz[j],PV_Z_reweighting_factor)
					h_RECO_beamspot_vz_MC_reweighted_to_data.Fill(treeBeamspot._beampot_vz[0], beamspot_Z_reweighting_factor)
					h_RECO_beamspot_vz_MC_NOTreweighted_to_data.Fill(treeBeamspot._beampot_vz[0], 1)


				histos[0].Fill(treeKs._Ks_vz[j], PV_Z_reweighting_factor)
				histos[1].Fill(treeBeamspot._beampot_vz[0]-treeKs._Ks_vz[j], beamspot_Z_reweighting_factor)

				histos[2].Fill(treeKs._Ks_Lxy[j], PV_Z_reweighting_factor)

				histos[3].Fill(treeKs._Ks_pt[j], PV_Z_reweighting_factor)
				histos[4].Fill(treeKs._Ks_daughterTrack1_pt[j],PV_Z_reweighting_factor) 
				histos[5].Fill(treeKs._Ks_daughterTrack2_pt[j],PV_Z_reweighting_factor)
				histos[6].Fill(treeKs._Ks_daughterTrack1_pt[j],PV_Z_reweighting_factor)
				histos[6].Fill(treeKs._Ks_daughterTrack2_pt[j],PV_Z_reweighting_factor)

				histos[7].Fill(treeKs._Ks_pz[j], PV_Z_reweighting_factor)
				histos[8].Fill(treeKs._Ks_daughterTrack1_pz[j], PV_Z_reweighting_factor)
				histos[9].Fill(treeKs._Ks_daughterTrack2_pz[j], PV_Z_reweighting_factor)
				histos[10].Fill(treeKs._Ks_daughterTrack1_pz[j], PV_Z_reweighting_factor)
				histos[10].Fill(treeKs._Ks_daughterTrack2_pz[j], PV_Z_reweighting_factor)

				histos[11].Fill(treeKs._Ks_dxy_beamspot[j], PV_Z_reweighting_factor)

				histos[12].Fill(treeKs._Ks_dz_000[j], PV_Z_reweighting_factor)

				histos[13].Fill(treeKs._Ks_daughterTrack1_dxy_beamspot[j], PV_Z_reweighting_factor)
				histos[14].Fill(treeKs._Ks_daughterTrack2_dxy_beamspot[j], PV_Z_reweighting_factor)
				histos[15].Fill(treeKs._Ks_daughterTrack1_dxy_beamspot[j], PV_Z_reweighting_factor)
				histos[15].Fill(treeKs._Ks_daughterTrack2_dxy_beamspot[j], PV_Z_reweighting_factor)

				histos[16].Fill(maxSigned(treeKs._Ks_daughterTrack1_dz_min_PV[j],treeKs._Ks_daughterTrack2_dz_min_PV[j]), PV_Z_reweighting_factor)
				histos[17].Fill(maxSigned(treeKs._Ks_daughterTrack1_dz_beamspot[j],treeKs._Ks_daughterTrack2_dz_beamspot[j]), PV_Z_reweighting_factor)
				histos[18].Fill(treeKs._Ks_daughterTrack1_dz_min_PV[j], PV_Z_reweighting_factor)
				histos[19].Fill(treeKs._Ks_daughterTrack2_dz_min_PV[j], PV_Z_reweighting_factor)
				histos[20].Fill(treeKs._Ks_daughterTrack1_dz_min_PV[j], PV_Z_reweighting_factor)
				histos[20].Fill(treeKs._Ks_daughterTrack2_dz_min_PV[j], PV_Z_reweighting_factor)
				histos[21].Fill(treeKs._Ks_daughterTrack1_dz_beamspot[j], beamspot_Z_reweighting_factor)
				histos[21].Fill(treeKs._Ks_daughterTrack2_dz_beamspot[j], beamspot_Z_reweighting_factor)



		if(iFile == 0):#for Data
			nKshortPerEventData.append(nKshortThisEvent)
		if(iFile == 1): #for MC
			nKshortPerEventMC.append(nKshortThisEvent)
			
			
	for h in histos:
		h.SetDirectory(0)
	if(iFile == 0):
		histos_Data = histos
	else:
		histos_MC = histos

	iFile += 1


fOut.mkdir('PV_Histos')
fOut.cd('PV_Histos')
h_RECO_PV0_vz_Data.Rebin(10)
h_RECO_PV0_vz_Data.Scale(1./h_RECO_PV0_vz_Data.Integral(), "width")
h_RECO_PV0_vz_Data.Write()

h_RECO_PV0_vz_MC.Rebin(10)
h_RECO_PV0_vz_MC.Scale(1./h_RECO_PV0_vz_MC.Integral(), "width")
h_RECO_PV0_vz_MC.Write()

h_RECO_PV0_vz_MC_reweighted_to_data.Scale(1./h_RECO_PV0_vz_MC_reweighted_to_data.Integral(), "width")
h_RECO_PV0_vz_MC_reweighted_to_data.Write()
h_RECO_PV0_vz_MC_NOTreweighted_to_data.Scale(1./h_RECO_PV0_vz_MC_NOTreweighted_to_data.Integral(), "width")
h_RECO_PV0_vz_MC_NOTreweighted_to_data.Write()

tprof_Ks_vz_dz_min_PV_reweighing_factor.Write()
tprof_Ks_vz_reweighing_factor.Write()

h_RECO_beamspot_vz_Data.Rebin(100)
h_RECO_beamspot_vz_Data.Scale(1./h_RECO_beamspot_vz_Data.Integral(), "width")
h_RECO_beamspot_vz_Data.Write()

h_RECO_beamspot_vz_MC.Rebin(100)
h_RECO_beamspot_vz_MC.Scale(1./h_RECO_beamspot_vz_MC.Integral(), "width")
h_RECO_beamspot_vz_MC.Write()

#h_RECO_beamspot_vz_MC_reweighted_to_data.Scale(1./h_RECO_beamspot_vz_MC_reweighted_to_data.Integral(), "width")
#h_RECO_beamspot_vz_MC_reweighted_to_data.Write()
#h_RECO_beamspot_vz_MC_NOTreweighted_to_data.Scale(1./h_RECO_beamspot_vz_MC_NOTreweighted_to_data.Integral(), "width")
#h_RECO_beamspot_vz_MC_NOTreweighted_to_data.Write()


fOut.mkdir('Data_Histos')
fOut.cd('Data_Histos')
for h in histos_Data:
#	h.Scale(1./h.Integral(),"Width")
	h.Write()

fOut.mkdir('MC_Histos')
fOut.cd('MC_Histos')
for h in histos_MC:
#	h.Scale(1./h.Integral(),"Width")
	h.Write()

fOut.mkdir('Data_TO_MC_Histos')
fOut.cd('Data_TO_MC_Histos')
i = 0
for i in range(0,len(histos_Data)):
	#histos_Data[i].Divide(histos_MC[i])
	#histos_Data[i].SetName(histos_Data[i].GetName()+'DataToMC')
	#histos_Data[i].Write()

	histo_Divide = histos_Data[i].Clone()
	for j in range(1,histo_Divide.GetNbinsX()):
		data = histos_Data[i].GetBinContent(j) 
		MC = histos_MC[i].GetBinContent(j)
		ratio = 0
		error = 0
		if(MC != 0 and data != 0):
			ratio = data/MC
			error = eff_error(data,MC)
		histo_Divide.SetBinContent(j, ratio)
		histo_Divide.SetBinError(j, error)

	histo_Divide.SetName(histo_Divide.GetName()+'_DataToMC')
	histo_Divide.GetYaxis().SetTitle('Data/MC')
	histo_Divide.Write()

print "number of Kshort going into the histos for Data: ", sum(nKshortPerEventData)
print "number of Kshort going into the histos for MC: ", sum(nKshortPerEventMC)

print "mean number of Kshort per event in data (x1e3): ", sum(nKshortPerEventData)*1e3/len(nKshortPerEventData)
print "mean number of Kshort per event in MC (x1e3): ", sum(nKshortPerEventMC)*1e3/len(nKshortPerEventMC)
print "ratio of the nKshortData/nKshortMC: ", float(sum(nKshortPerEventData))/float(sum(nKshortPerEventMC))


fOut.Close()
