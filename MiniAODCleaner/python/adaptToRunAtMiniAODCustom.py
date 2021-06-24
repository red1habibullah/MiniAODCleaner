import FWCore.ParameterSet.Config as cms
import six

import PhysicsTools.PatAlgos.tools.helpers as configtools
from PhysicsTools.PatAlgos.tools.helpers import cloneProcessingSnippet
from PhysicsTools.PatAlgos.tools.helpers import massSearchReplaceAnyInputTag
from PhysicsTools.PatAlgos.tools.helpers import removeIfInSequence

##############
#Tools to adapt Tau sequences to run tau ReReco+PAT at MiniAOD samples
#With cleaned PackedPFCandidate Collection
##############



def addTauReRecoCustom(process):
    #PAT
    process.load('PhysicsTools.PatAlgos.producersLayer1.tauProducer_cff')
    process.load('PhysicsTools.PatAlgos.selectionLayer1.tauSelector_cfi')
    process.selectedPatTaus.cut="pt > 18. && tauID(\'decayModeFindingNewDMs\')> 0.5"
    #Tau RECO
    process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")    
    process.miniAODTausTask = cms.Task(
    process.PFTauTask, 
    process.makePatTausTask,
    process.selectedPatTaus
    
    )
    process.miniAODTausSequence =cms.Sequence(process.miniAODTausTask)
    #######ElectronCleaned#########
    transfermods=[]
    transferlabels=[]
    for mods in process.miniAODTausTask.moduleNames():
        transfermods.append(mods)
    transfermodsnew=[]
    process.miniAODTausTaskElectronCleaned=cms.Task()
    #loop over the modules, rename and remake the task by hand
    for mod in transfermods:
        module=getattr(process,mod)
        transferlabels.append(module.label())
        newmod=module.clone()
        namepostfix='ElectronCleaned'
        newname=mod+namepostfix
        setattr(process,newname,newmod)
        process.miniAODTausTaskElectronCleaned.add(getattr(process,newname))
    for names in process.miniAODTausTaskElectronCleaned.moduleNames():
        if 'ak4PFJetTracksAssociatorAtVertexElectronCleaned' in names or 'pfRecoTauTagInfoProducerElectronCleaned' in names or 'recoTauAK4PFJets08RegionElectronCleaned' in names:
            process.miniAODTausTaskElectronCleaned.remove(getattr(process, names))
    
        
    process.LooseFilter = cms.EDFilter("ElectronFilter",
                                   vertex = cms.InputTag("offlineSlimmedPrimaryVertices"),
                                   Rho = cms.InputTag("fixedGridRhoFastjetAll"),
                                   electrons = cms.InputTag("slimmedElectrons"),
                                   conv = cms.InputTag("reducedConversions"),
                                   BM = cms.InputTag("offlineBeamSpot"),
                                   #Tracks = cms.InputTag("electronGsfTracks"),                                                       
    )    
    process.PackedCandsElectronCleaned =cms.EDProducer(
        'ElectronCleanedPackedCandidateProducer',
        electronSrc = cms.InputTag("LooseFilter","LooseElectronRef"),
        packedCandSrc = cms.InputTag("packedPFCandidates"),
    )
    
    process.electronCleanedPackedCandidateTask=cms.Task(process.LooseFilter,process.PackedCandsElectronCleaned)
    process.miniAODTausTaskElectronCleaned.add(process.electronCleanedPackedCandidateTask)
    
    labelpostfix='ElectronCleaned'
    renamedict={}
    for label in transferlabels:
        renamedict[label]=label+labelpostfix
    #print renamedict
    
    process.miniAODTausSequenceElectronCleaned =  cms.Sequence(process.miniAODTausTaskElectronCleaned)
    for label_old,label_new in renamedict.items():
        #print " old label: ", label_old
        #print "new label: ", label_new
        massSearchReplaceAnyInputTag(process.miniAODTausSequenceElectronCleaned,label_old,label_new)    
        massSearchReplaceAnyInputTag(process.miniAODTausSequenceElectronCleaned,cms.InputTag(label_old,"category"),cms.InputTag(label_new,"category"))    
    #########MuonCleaned########
    process.miniAODTausTaskMuonCleaned=cms.Task()
    for mod in transfermods:
        module=getattr(process,mod)
        #print mod
        #=============== name ==================="
        #print module.label()
        #print "=================== label ================"
        transferlabels.append(module.label())
        newmod=module.clone()
        namepostfix='MuonCleaned'
        newname=mod+namepostfix
        setattr(process,newname,newmod)
        process.miniAODTausTaskMuonCleaned.add(getattr(process,newname))
    for names in process.miniAODTausTaskMuonCleaned.moduleNames():
        if 'ak4PFJetTracksAssociatorAtVertexMuonCleaned' in names or 'pfRecoTauTagInfoProducerMuonCleaned' in names or 'recoTauAK4PFJets08RegionMuonCleaned' in names:
            process.miniAODTausTaskMuonCleaned.remove(getattr(process, names))
    

    
    process.LooseMuonFilter = cms.EDFilter('PATMuonRefSelector',
                                           src = cms.InputTag('slimmedMuons'),
                                           cut = cms.string('pt > 3.0 && passed("CutBasedIdLoose")'),
    )
    
    process.PackedCandsMuonCleaned =cms.EDProducer(
        'MuonCleanedPackedCandidateProducer',
        muonSrc = cms.InputTag("LooseMuonFilter"),
        packedCandSrc = cms.InputTag("packedPFCandidates"),
    )
    
    process.muonCleanedPackedCandidateTask=cms.Task(process.LooseMuonFilter,process.PackedCandsMuonCleaned)
    process.miniAODTausTaskMuonCleaned.add(process.muonCleanedPackedCandidateTask)
    
    labelmupostfix='MuonCleaned'
    renamedictmu={}
    for label in transferlabels:
        renamedictmu[label]=label+labelmupostfix
    print renamedictmu
    
    process.miniAODTausSequenceMuonCleaned =  cms.Sequence(process.miniAODTausTaskMuonCleaned)
    for label_old,label_new in renamedictmu.items():
        #print " old label: ", label_old
        #print "new label: ", label_new
        massSearchReplaceAnyInputTag(process.miniAODTausSequenceMuonCleaned,label_old,label_new)    
        massSearchReplaceAnyInputTag(process.miniAODTausSequenceMuonCleaned,cms.InputTag(label_old,"category"),cms.InputTag(label_new,"category"))    
    

    ######## Tau-Reco Path ####### 
    process.TauReco = cms.Path(process.miniAODTausSequence)
    process.TauRecoElectronCleaned = cms.Path(process.miniAODTausSequenceElectronCleaned)
    process.TauRecoMuonCleaned = cms.Path(process.miniAODTausSequenceMuonCleaned)
    #process.skimpath=cms.Path()

def convertModuleToMiniAODInput(process, name):
    module = getattr(process, name)
    if hasattr(module, 'particleFlowSrc'):
        if "ElectronCleanedPackedCandidateProducer" in name or "MuonCleanedPackeCandidateProducer" in name:
            module.particleFlowSrc = cms.InputTag("packedPFCandidates", "", "")
        elif "ElectronCleaned" in name:
            module.particleFlowSrc = cms.InputTag('PackedCandsElectronCleaned','packedPFCandidatesElectronCleaned')
        elif "MuonCleaned" in name:
            module.particleFlowSrc = cms.InputTag('PackedCandsMuonCleaned','packedPFCandidatesMuonCleaned')
        else:
            module.particleFlowSrc = cms.InputTag("packedPFCandidates", "", "")
    if hasattr(module, 'vertexSrc'):
        module.vertexSrc = cms.InputTag('offlineSlimmedPrimaryVertices')
    if hasattr(module, 'qualityCuts') and hasattr(module.qualityCuts, 'primaryVertexSrc'):
        module.qualityCuts.primaryVertexSrc = cms.InputTag('offlineSlimmedPrimaryVertices')
    
def adaptTauToMiniAODReReco(process, reclusterJets=True):
    jetCollection = 'slimmedJets'
    # Add new jet collections if reclustering is demanded
    if reclusterJets:
        jetCollection = 'patJetsPAT'
        from RecoJets.JetProducers.ak4PFJets_cfi import ak4PFJets
        process.ak4PFJetsPAT = ak4PFJets.clone(
            src=cms.InputTag("packedPFCandidates")
        )
        # trivial PATJets
        from PhysicsTools.PatAlgos.producersLayer1.jetProducer_cfi import _patJets
        process.patJetsPAT = _patJets.clone(
            jetSource            = cms.InputTag("ak4PFJetsPAT"),
            addJetCorrFactors    = cms.bool(False),
            jetCorrFactorsSource = cms.VInputTag(),
            addBTagInfo          = cms.bool(False),
            addDiscriminators    = cms.bool(False),
            discriminatorSources = cms.VInputTag(),
            addAssociatedTracks  = cms.bool(False),
            addJetCharge         = cms.bool(False),
            addGenPartonMatch    = cms.bool(False),
            embedGenPartonMatch  = cms.bool(False),
            addGenJetMatch       = cms.bool(False),
            getJetMCFlavour      = cms.bool(False),
            addJetFlavourInfo    = cms.bool(False),
        )
        process.miniAODTausTask.add(process.ak4PFJetsPAT)
        process.miniAODTausTask.add(process.patJetsPAT)
        ###################### ElectronCleaned ######################
        jetCollectionElectronCleaned = 'patJetsPATElectronCleaned'
        jetCollectionMuonCleaned = 'patJetsPATMuonCleaned'
        from RecoJets.JetProducers.ak4PFJets_cfi import ak4PFJets
        process.ak4PFJetsPATElectronCleaned = ak4PFJets.clone(
            src=cms.InputTag('PackedCandsElectronCleaned','packedPFCandidatesElectronCleaned')

        )
        from PhysicsTools.PatAlgos.producersLayer1.jetProducer_cfi import _patJets
        process.patJetsPATElectronCleaned = _patJets.clone(
            jetSource            = cms.InputTag("ak4PFJetsPATElectronCleaned"),
            addJetCorrFactors    = cms.bool(False),
            jetCorrFactorsSource = cms.VInputTag(),
            addBTagInfo          = cms.bool(False),
            addDiscriminators    = cms.bool(False),
            discriminatorSources = cms.VInputTag(),
            addAssociatedTracks  = cms.bool(False),
            addJetCharge         = cms.bool(False),
            addGenPartonMatch    = cms.bool(False),
            embedGenPartonMatch  = cms.bool(False),
            addGenJetMatch       = cms.bool(False),
            getJetMCFlavour      = cms.bool(False),
            addJetFlavourInfo    = cms.bool(False),
        )
       
        process.miniAODTausTaskElectronCleaned.add(process.ak4PFJetsPATElectronCleaned)
        process.miniAODTausTaskElectronCleaned.add(process.patJetsPATElectronCleaned)
        
        from RecoJets.JetProducers.ak4PFJets_cfi import ak4PFJets
        process.ak4PFJetsPATMuonCleaned = ak4PFJets.clone(
            src=cms.InputTag('PackedCandsMuonCleaned','packedPFCandidatesMuonCleaned')

        )
        from PhysicsTools.PatAlgos.producersLayer1.jetProducer_cfi import _patJets
        process.patJetsPATMuonCleaned = _patJets.clone(
            jetSource            = cms.InputTag("ak4PFJetsPATMuonCleaned"),
            addJetCorrFactors    = cms.bool(False),
            jetCorrFactorsSource = cms.VInputTag(),
            addBTagInfo          = cms.bool(False),
            addDiscriminators    = cms.bool(False),
            discriminatorSources = cms.VInputTag(),
            addAssociatedTracks  = cms.bool(False),
            addJetCharge         = cms.bool(False),
            addGenPartonMatch    = cms.bool(False),
            embedGenPartonMatch  = cms.bool(False),
            addGenJetMatch       = cms.bool(False),
            getJetMCFlavour      = cms.bool(False),
            addJetFlavourInfo    = cms.bool(False),
        )
       
        process.miniAODTausTaskMuonCleaned.add(process.ak4PFJetsPATMuonCleaned)
        process.miniAODTausTaskMuonCleaned.add(process.patJetsPATMuonCleaned)
        
        
    

    process.recoTauAK4Jets08RegionPAT = cms.EDProducer("RecoTauPatJetRegionProducer",
                                                       deltaR = process.recoTauAK4PFJets08Region.deltaR,
                                                       maxJetAbsEta = process.recoTauAK4PFJets08Region.maxJetAbsEta,
                                                       minJetPt = process.recoTauAK4PFJets08Region.minJetPt,
                                                       pfCandAssocMapSrc = cms.InputTag(""),
                                                       pfCandSrc = cms.InputTag("packedPFCandidates"),
                                                       src = cms.InputTag(jetCollection)
                                                       )

    process.recoTauPileUpVertices.src = cms.InputTag("offlineSlimmedPrimaryVertices")
    # Redefine recoTauCommonTask 
    # with redefined region and PU vertices, and w/o track-to-vertex associator and tauTagInfo (the two latter are probably obsolete and not needed at all)
    process.recoTauCommonTask = cms.Task(
        process.recoTauAK4Jets08RegionPAT,
        process.recoTauPileUpVertices
    )
    
    process.recoTauAK4Jets08RegionPATElectronCleaned = cms.EDProducer("RecoTauPatJetRegionProducer",
                                                                      deltaR = process.recoTauAK4PFJets08RegionElectronCleaned.deltaR,
                                                                      maxJetAbsEta = process.recoTauAK4PFJets08RegionElectronCleaned.maxJetAbsEta,
                                                                      minJetPt = process.recoTauAK4PFJets08RegionElectronCleaned.minJetPt,
                                                                      pfCandAssocMapSrc = cms.InputTag(""),
                                                                      pfCandSrc = cms.InputTag('PackedCandsElectronCleaned','packedPFCandidatesElectronCleaned'),
                                                                      src = cms.InputTag(jetCollectionElectronCleaned)
                                                                  )

    process.recoTauPileUpVerticesElectronCleaned.src = cms.InputTag("offlineSlimmedPrimaryVertices")
    
    
    # Redefine recoTauCommonTask-ElectronCleaned 
    process.miniAODTausTaskElectronCleaned.add(process.recoTauAK4Jets08RegionPATElectronCleaned)
    process.miniAODTausTaskElectronCleaned.add(process.recoTauPileUpVerticesElectronCleaned)
    
    process.recoTauAK4Jets08RegionPATMuonCleaned = cms.EDProducer("RecoTauPatJetRegionProducer",
                                                                      deltaR = process.recoTauAK4PFJets08RegionMuonCleaned.deltaR,
                                                                      maxJetAbsEta = process.recoTauAK4PFJets08RegionMuonCleaned.maxJetAbsEta,
                                                                      minJetPt = process.recoTauAK4PFJets08RegionMuonCleaned.minJetPt,
                                                                      pfCandAssocMapSrc = cms.InputTag(""),
                                                                      pfCandSrc = cms.InputTag('PackedCandsMuonCleaned','packedPFCandidatesMuonCleaned'),
                                                                      src = cms.InputTag(jetCollectionMuonCleaned)
                                                                  )

    process.recoTauPileUpVerticesMuonCleaned.src = cms.InputTag("offlineSlimmedPrimaryVertices")
    
    # Redefine recoTauCommonTask-MuonCleaned 
    process.miniAODTausTaskMuonCleaned.add(process.recoTauAK4Jets08RegionPATMuonCleaned)
    process.miniAODTausTaskMuonCleaned.add(process.recoTauPileUpVerticesMuonCleaned)
    

    for moduleName in process.TauReco.moduleNames(): 
        convertModuleToMiniAODInput(process, moduleName)
    
    for moduleName in process.TauRecoElectronCleaned.moduleNames(): 
        convertModuleToMiniAODInput(process, moduleName)

    for moduleName in process.TauRecoMuonCleaned.moduleNames(): 
        convertModuleToMiniAODInput(process, moduleName)
    
    # Adapt TauPiZeros producer
    process.ak4PFJetsLegacyHPSPiZeros.builders[0].qualityCuts.primaryVertexSrc = cms.InputTag("offlineSlimmedPrimaryVertices")
    process.ak4PFJetsLegacyHPSPiZeros.jetSrc = cms.InputTag(jetCollection)

    # Adapt TauPiZeros producer-ElectronCleaned
    process.ak4PFJetsLegacyHPSPiZerosElectronCleaned.builders[0].qualityCuts.primaryVertexSrc = cms.InputTag("offlineSlimmedPrimaryVertices")
    process.ak4PFJetsLegacyHPSPiZerosElectronCleaned.jetSrc = cms.InputTag(jetCollectionElectronCleaned)

    # Adapt TauPiZeros producer-MuonCleaned
    process.ak4PFJetsLegacyHPSPiZerosMuonCleaned.builders[0].qualityCuts.primaryVertexSrc = cms.InputTag("offlineSlimmedPrimaryVertices")
    process.ak4PFJetsLegacyHPSPiZerosMuonCleaned.jetSrc = cms.InputTag(jetCollectionMuonCleaned)

     

    # Adapt TauChargedHadrons producer
    for builder in process.ak4PFJetsRecoTauChargedHadrons.builders:
        builder.qualityCuts.primaryVertexSrc = cms.InputTag("offlineSlimmedPrimaryVertices")
        if builder.name.value() == 'tracks': #replace plugin based on generalTracks by one based on lostTracks
            builder.name = 'lostTracks'
            builder.plugin = 'PFRecoTauChargedHadronFromLostTrackPlugin'
            builder.srcTracks = cms.InputTag("lostTracks")
    process.ak4PFJetsRecoTauChargedHadrons.jetSrc = cms.InputTag(jetCollection)
    
    # Adapt TauChargedHadrons producer-ElectronCleaned
    for builder in process.ak4PFJetsRecoTauChargedHadronsElectronCleaned.builders:
        builder.qualityCuts.primaryVertexSrc = cms.InputTag("offlineSlimmedPrimaryVertices")
        if builder.name.value() == 'tracks': #replace plugin based on generalTracks by one based on lostTracks
            builder.name = 'lostTracks'
            builder.plugin = 'PFRecoTauChargedHadronFromLostTrackPlugin'
            builder.srcTracks = cms.InputTag("lostTracks")
    process.ak4PFJetsRecoTauChargedHadronsElectronCleaned.jetSrc = cms.InputTag(jetCollectionElectronCleaned)
    
    # Adapt TauChargedHadrons producer-MuonCleaned
    for builder in process.ak4PFJetsRecoTauChargedHadronsMuonCleaned.builders:
        builder.qualityCuts.primaryVertexSrc = cms.InputTag("offlineSlimmedPrimaryVertices")
        if builder.name.value() == 'tracks': #replace plugin based on generalTracks by one based on lostTracks
            builder.name = 'lostTracks'
            builder.plugin = 'PFRecoTauChargedHadronFromLostTrackPlugin'
            builder.srcTracks = cms.InputTag("lostTracks")
    process.ak4PFJetsRecoTauChargedHadronsMuonCleaned.jetSrc = cms.InputTag(jetCollectionMuonCleaned)
    
    
    # Adapt combinatoricRecoTau producer
    process.combinatoricRecoTaus.jetRegionSrc = 'recoTauAK4Jets08RegionPAT'
    process.combinatoricRecoTaus.jetSrc = jetCollection
    # Adapt builders
    for builder in process.combinatoricRecoTaus.builders:
        for name,value in six.iteritems(builder.parameters_()):
            if name == 'qualityCuts':
                builder.qualityCuts.primaryVertexSrc = 'offlineSlimmedPrimaryVertices'
            elif name == 'pfCandSrc':
                builder.pfCandSrc = 'packedPFCandidates'
                
    # Adapt combinatoricRecoTau producer - ElectronCleaned
    process.combinatoricRecoTausElectronCleaned.jetRegionSrc = 'recoTauAK4Jets08RegionPATElectronCleaned'
    process.combinatoricRecoTausElectronCleaned.jetSrc = jetCollectionElectronCleaned
    # Adapt builders - ElectronCleaned                                                                                                                 
    for builder in process.combinatoricRecoTausElectronCleaned.builders:
        for name,value in six.iteritems(builder.parameters_()):
            if name == 'qualityCuts':
                builder.qualityCuts.primaryVertexSrc = 'offlineSlimmedPrimaryVertices'
            elif name == 'pfCandSrc':
                builder.pfCandSrc =cms.InputTag('PackedCandsElectronCleaned','packedPFCandidatesElectronCleaned')
    
    # Adapt combinatoricRecoTau producer - MuonCleaned
    process.combinatoricRecoTausMuonCleaned.jetRegionSrc = 'recoTauAK4Jets08RegionPATMuonCleaned'
    process.combinatoricRecoTausMuonCleaned.jetSrc = jetCollectionMuonCleaned
    # Adapt builders - MuonCleaned                                                                                                                 
    for builder in process.combinatoricRecoTausMuonCleaned.builders:
        for name,value in six.iteritems(builder.parameters_()):
            if name == 'qualityCuts':
                builder.qualityCuts.primaryVertexSrc = 'offlineSlimmedPrimaryVertices'
            elif name == 'pfCandSrc':
                builder.pfCandSrc =cms.InputTag('PackedCandsMuonCleaned','packedPFCandidatesMuonCleaned')
    
    # Adapt supported modifiers and remove unsupported ones 
    modifiersToRemove_ = cms.VPSet()

    for mod in process.combinatoricRecoTaus.modifiers:
        if mod.name.value() == 'elec_rej':
            modifiersToRemove_.append(mod)
            continue
        elif mod.name.value() == 'TTIworkaround':
            modifiersToRemove_.append(mod)
            continue
        for name,value in six.iteritems(mod.parameters_()):
            if name == 'qualityCuts':
                mod.qualityCuts.primaryVertexSrc = 'offlineSlimmedPrimaryVertices'
    for mod in modifiersToRemove_:
        process.combinatoricRecoTaus.modifiers.remove(mod)
    
    modifiersToRemoveElectronCleaned_ = cms.VPSet()  
    
    for mod in process.combinatoricRecoTausElectronCleaned.modifiers:
        if mod.name.value() == 'elec_rej':
            modifiersToRemoveElectronCleaned_.append(mod)
            continue
        elif mod.name.value() == 'TTIworkaround':
            modifiersToRemoveElectronCleaned_.append(mod)
            continue
        for name,value in six.iteritems(mod.parameters_()):
            if name == 'qualityCuts':
                mod.qualityCuts.primaryVertexSrc = 'offlineSlimmedPrimaryVertices'
    for mod in modifiersToRemoveElectronCleaned_:
        process.combinatoricRecoTausElectronCleaned.modifiers.remove(mod)

    modifiersToRemoveMuonCleaned_ = cms.VPSet()  
    
    for mod in process.combinatoricRecoTausMuonCleaned.modifiers:
        if mod.name.value() == 'elec_rej':
            modifiersToRemoveMuonCleaned_.append(mod)
            continue
        elif mod.name.value() == 'TTIworkaround':
            modifiersToRemoveMuonCleaned_.append(mod)
            continue
        for name,value in six.iteritems(mod.parameters_()):
            if name == 'qualityCuts':
                mod.qualityCuts.primaryVertexSrc = 'offlineSlimmedPrimaryVertices'
    for mod in modifiersToRemoveMuonCleaned_:
        process.combinatoricRecoTausMuonCleaned.modifiers.remove(mod)

    
    # Redefine tau PV producer
    process.hpsPFTauPrimaryVertexProducer.__dict__['_TypedParameterizable__type'] = 'PFTauMiniAODPrimaryVertexProducer'
    process.hpsPFTauPrimaryVertexProducer.PVTag = 'offlineSlimmedPrimaryVertices'
    process.hpsPFTauPrimaryVertexProducer.packedCandidatesTag = cms.InputTag("packedPFCandidates")
    process.hpsPFTauPrimaryVertexProducer.lostCandidatesTag = cms.InputTag("lostTracks")

    # Redefine tau PV producer-ElectronCleaned
    process.hpsPFTauPrimaryVertexProducerElectronCleaned.__dict__['_TypedParameterizable__type'] = 'PFTauMiniAODPrimaryVertexProducer'
    process.hpsPFTauPrimaryVertexProducerElectronCleaned.PVTag = 'offlineSlimmedPrimaryVertices'
    process.hpsPFTauPrimaryVertexProducerElectronCleaned.packedCandidatesTag = cms.InputTag('PackedCandsElectronCleaned','packedPFCandidatesElectronCleaned')
    process.hpsPFTauPrimaryVertexProducerElectronCleaned.lostCandidatesTag = cms.InputTag("lostTracks")
    
    # Redefine tau PV producer-MuonCleaned
    process.hpsPFTauPrimaryVertexProducerMuonCleaned.__dict__['_TypedParameterizable__type'] = 'PFTauMiniAODPrimaryVertexProducer'
    process.hpsPFTauPrimaryVertexProducerMuonCleaned.PVTag = 'offlineSlimmedPrimaryVertices'
    process.hpsPFTauPrimaryVertexProducerMuonCleaned.packedCandidatesTag = cms.InputTag('PackedCandsMuonCleaned','packedPFCandidatesMuonCleaned')
    process.hpsPFTauPrimaryVertexProducerMuonCleaned.lostCandidatesTag = cms.InputTag("lostTracks")
    
    
    # Redefine tau SV producer
    process.hpsPFTauSecondaryVertexProducer = cms.EDProducer("PFTauSecondaryVertexProducer",
                                                             PFTauTag = cms.InputTag("hpsPFTauProducer")
    )
    
    # Redefine tau SV producer-ElectronCleaned
    process.hpsPFTauSecondaryVertexProducerElectronCleaned = cms.EDProducer("PFTauSecondaryVertexProducer",
                                                             PFTauTag = cms.InputTag("hpsPFTauProducerElectronCleaned")
    )
    
    # Redefine tau SV producer-MuonCleaned
    process.hpsPFTauSecondaryVertexProducerMuonCleaned = cms.EDProducer("PFTauSecondaryVertexProducer",
                                                             PFTauTag = cms.InputTag("hpsPFTauProducerMuonCleaned")
    
    )
    # Remove RecoTau producers which are not supported (yet?), i.e. against-e/mu discriminats
    for moduleName in process.TauReco.moduleNames(): 
        if 'ElectronRejection' in moduleName or 'MuonRejection' in moduleName:
            process.miniAODTausTask.remove(getattr(process, moduleName))
    
    
    # Remove RecoTau producers which are not supported (yet?), i.e. against-e/mu discriminats
    for moduleName in process.TauRecoElectronCleaned.moduleNames(): 
        if 'ElectronRejection' in moduleName or 'MuonRejection' in moduleName:
            process.miniAODTausTaskElectronCleaned.remove(getattr(process, moduleName))
    

    # Remove RecoTau producers which are not supported (yet?), i.e. against-e/mu discriminats
    for moduleName in process.TauRecoMuonCleaned.moduleNames(): 
        if 'ElectronRejection' in moduleName or 'MuonRejection' in moduleName:
            process.miniAODTausTaskMuonCleaned.remove(getattr(process, moduleName))
            
            
    
    
    # Instead add against-mu discriminants which are MiniAOD compatible
    from RecoTauTag.RecoTau.hpsPFTauDiscriminationByAMuonRejectionSimple_cff import hpsPFTauDiscriminationByLooseMuonRejectionSimple, hpsPFTauDiscriminationByTightMuonRejectionSimple
    
    process.hpsPFTauDiscriminationByLooseMuonRejectionSimple = hpsPFTauDiscriminationByLooseMuonRejectionSimple
    process.hpsPFTauDiscriminationByTightMuonRejectionSimple = hpsPFTauDiscriminationByTightMuonRejectionSimple
    process.miniAODTausTask.add(process.hpsPFTauDiscriminationByLooseMuonRejectionSimple)
    process.miniAODTausTask.add(process.hpsPFTauDiscriminationByTightMuonRejectionSimple)

    process.hpsPFTauDiscriminationByLooseMuonRejectionSimpleElectronCleaned = process.hpsPFTauDiscriminationByLooseMuonRejectionSimple.clone(PFTauProducer = cms.InputTag("hpsPFTauProducerElectronCleaned"))
    process.hpsPFTauDiscriminationByTightMuonRejectionSimpleElectronCleaned = hpsPFTauDiscriminationByTightMuonRejectionSimple.clone(PFTauProducer = cms.InputTag("hpsPFTauProducerElectronCleaned"))
    process.miniAODTausTaskElectronCleaned.add(process.hpsPFTauDiscriminationByLooseMuonRejectionSimpleElectronCleaned)
    process.miniAODTausTaskElectronCleaned.add(process.hpsPFTauDiscriminationByTightMuonRejectionSimpleElectronCleaned)
    
    process.hpsPFTauDiscriminationByLooseMuonRejectionSimpleMuonCleaned = process.hpsPFTauDiscriminationByLooseMuonRejectionSimple.clone(PFTauProducer = cms.InputTag("hpsPFTauProducerMuonCleaned"))
    process.hpsPFTauDiscriminationByTightMuonRejectionSimpleMuonCleaned = hpsPFTauDiscriminationByTightMuonRejectionSimple.clone(PFTauProducer = cms.InputTag("hpsPFTauProducerMuonCleaned"))
    process.miniAODTausTaskMuonCleaned.add(process.hpsPFTauDiscriminationByLooseMuonRejectionSimpleMuonCleaned)
    process.miniAODTausTaskMuonCleaned.add(process.hpsPFTauDiscriminationByTightMuonRejectionSimpleMuonCleaned)

    #####
    # PAT part in the following

    process.tauGenJets.GenParticles = cms.InputTag("prunedGenParticles")
    process.tauMatch.matched = cms.InputTag("prunedGenParticles")

    process.tauGenJetsElectronCleaned.GenParticles = cms.InputTag("prunedGenParticles")
    process.tauMatchElectronCleaned.matched = cms.InputTag("prunedGenParticles")
   
    process.tauGenJetsMuonCleaned.GenParticles = cms.InputTag("prunedGenParticles")
    process.tauMatchMuonCleaned.matched = cms.InputTag("prunedGenParticles")
    
    
    
    
    # Remove unsupported tauIDs
    for name, src in six.iteritems(process.patTaus.tauIDSources.parameters_()):
        if name.find('againstElectron') > -1 or name.find('againstMuon') > -1:
            delattr(process.patTaus.tauIDSources,name)
    # Add MiniAOD specific ones
    setattr(process.patTaus.tauIDSources,'againstMuonLooseSimple',cms.InputTag('hpsPFTauDiscriminationByLooseMuonRejectionSimple'))
    setattr(process.patTaus.tauIDSources,'againstMuonTightSimple',cms.InputTag('hpsPFTauDiscriminationByTightMuonRejectionSimple'))


    for name, src in six.iteritems(process.patTausElectronCleaned.tauIDSources.parameters_()):
        if name.find('againstElectron') > -1 or name.find('againstMuon') > -1:
            delattr(process.patTausElectronCleaned.tauIDSources,name)
    # Add MiniAOD specific ones
    setattr(process.patTausElectronCleaned.tauIDSources,'againstMuonLooseSimple',cms.InputTag('hpsPFTauDiscriminationByLooseMuonRejectionSimpleElectronCleaned'))
    setattr(process.patTausElectronCleaned.tauIDSources,'againstMuonTightSimple',cms.InputTag('hpsPFTauDiscriminationByTightMuonRejectionSimpleElectronCleaned'))

    
    for name, src in six.iteritems(process.patTausMuonCleaned.tauIDSources.parameters_()):
        if name.find('againstElectron') > -1 or name.find('againstMuon') > -1:
            delattr(process.patTausMuonCleaned.tauIDSources,name)
    # Add MiniAOD specific ones
    setattr(process.patTausMuonCleaned.tauIDSources,'againstMuonLooseSimple',cms.InputTag('hpsPFTauDiscriminationByLooseMuonRejectionSimpleMuonCleaned'))
    setattr(process.patTausMuonCleaned.tauIDSources,'againstMuonTightSimple',cms.InputTag('hpsPFTauDiscriminationByTightMuonRejectionSimpleMuonCleaned'))

    from PhysicsTools.PatAlgos.slimming.slimmedTaus_cfi import slimmedTaus
    #process.slimmedTausElectronCleaned = slimmedTaus.clone(src = cms.InputTag('selectedPatTausElectronCleaned'))
    #process.slimmedTausMuonCleaned = slimmedTaus.clone(src = cms.InputTag('selectedPatTausMuonCleaned'))
    #process.skimpath *=process.slimmedTausElectronCleaned
    #process.skimpath *=process.slimmedTausMuonCleaned

# def addFurtherSkimming(process):
#     process.slimpath = cms.Path()
#     from PhysicsTools.PatAlgos.slimming.slimmedTaus_cfi import slimmedTaus
#     process.slimmedTausElectronCleaned = slimmedTaus.clone(src = cms.InputTag('selectedPatTausElectronCleaned'), packedPFCandidates = cms.InputTag('PackedCandsElectronCleaned','packedPFCandidatesElectronCleaned'))
#     process.slimmedTausMuonCleaned = slimmedTaus.clone(src = cms.InputTag('selectedPatTausMuonCleaned'), packedPFCandidates = cms.InputTag('PackedCandsMuonCleaned','packedPFCandidatesMuonCleaned'))
#     process.slimpath  *=process.slimmedTausElectronCleaned
#     process.slimpath  *=process.slimmedTausMuonCleaned
    
    

#####
def setOutputModule(mode=0):
    #mode = 0: store original MiniAOD and new selectedPatTaus 
    #mode = 1: store original MiniAOD, new selectedPatTaus, and all PFTau products as in AOD (except of unsuported ones), plus a few additional collections (charged hadrons, pi zeros, combinatoric reco taus)
    
    import Configuration.EventContent.EventContent_cff as evtContent
    output = cms.OutputModule(
        'PoolOutputModule',
        fileName=cms.untracked.string('miniAOD_TauReco.root'),
        fastCloning=cms.untracked.bool(False),
        dataset=cms.untracked.PSet(
            dataTier=cms.untracked.string('MINIAODSIM'),
            filterName=cms.untracked.string('')
        ),
        outputCommands = evtContent.MINIAODSIMEventContent.outputCommands,
        SelectEvents=cms.untracked.PSet(
            SelectEvents=cms.vstring('*',)
        )
    )
    output.outputCommands.append('keep *_selectedPatTaus_*_*')
    #output.outputCommands.append('keep *_slimmedTausElectronCleaned_*_*')                                                                                                                                                                                             
    #output.outputCommands.append('keep *_slimmedTausMuonCleaned_*_*')
    if mode==1:
        for prod in evtContent.RecoTauTagAOD.outputCommands:
            if prod.find('ElectronRejection') > -1:
                continue
            if prod.find('MuonRejection') > -1:
                    continue
                    output.outputCommands.append(prod)
        output.outputCommands.append('keep *_hpsPFTauDiscriminationByLooseMuonRejectionSimple_*_*')
        output.outputCommands.append('keep *_hpsPFTauDiscriminationByTightMuonRejectionSimple_*_*')
        output.outputCommands.append('keep *_combinatoricReco*_*_*')
        output.outputCommands.append('keep *_ak4PFJetsRecoTauChargedHadrons_*_*')
        output.outputCommands.append('keep *_ak4PFJetsLegacyHPSPiZeros_*_*')
        output.outputCommands.append('keep *_patJetsPAT_*_*')

    return output

#####
