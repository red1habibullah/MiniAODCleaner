# MiniAODSkimmerThis package is used to apply cleaning on the MiniAOD samples. We do the Electron/Muon Cleaning in this step and store results for Taus  collections cleaned. # Setting up the environment:```bash$ setenv SCRAM_ARCH slc7_amd64_gcc700 $ cmsrel CMSSW_10_6_20$ cd CMSSW_10_6_20/src$ git cms-init$ cmsenv$ git clone git@github.com:red1habibullah/MiniAODSkimmer.git$ scram b -j8```