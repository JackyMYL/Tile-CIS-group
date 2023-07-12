from workers.noise.NoiseWorker import NoiseWorker

class PedestalCompare2DB(NoiseWorker):
    '''
    Class to compare new pedestal values with values stored in DB
    '''
    def __init__(self, hgThresholds, lgThresholds, isRelativeThreshold,
                 verbose, attributes, dbAttributes,                  
                 maskBad, 
                 output,
                 createUpdateEvent=True, runTypeUpdate='', runTypeDB='',
                 onlyWriteUpdated=True,
                 hgLargeDiffThresholds=None,
                 lgLargeDiffThresholds=None,
                 absurdValThresholds=None,
                 includeDrawers=None,
                 keepDBValueForZero=False):
        self.m_hgThresholds = hgThresholds
        self.m_lgThresholds = lgThresholds
        self.m_isRelativeThreshold = isRelativeThreshold
        self.m_verbose = verbose
        self.m_attributes = attributes
        self.m_dbAttributes = dbAttributes
        self.m_maskBad = maskBad
        self.m_output = output
        self.m_createUpdateEvent = createUpdateEvent
        self.m_runTypeUpdate = runTypeUpdate
        self.m_runTypeDB = runTypeDB

        self.m_nregions = 0
        self.m_ndifferences = 0
        self.m_ndifferencesLG = 0
        self.m_ndifferencesHG = 0
        self.m_differencesPerDrawer = {}
        self.m_differencesLGPerDrawer = {}
        self.m_differencesHGPerDrawer = {}
        self.m_regions = set()
        self.m_onlyWriteUpdated = onlyWriteUpdated
        self.m_hgLargeDiffThresholds = hgLargeDiffThresholds
        self.m_lgLargeDiffThresholds = lgLargeDiffThresholds
        self.m_largeDiffChannels = []
        self.m_absurdValThresholds = absurdValThresholds
        self.m_absurdValChannels = {}
        self.m_runDate = None
        self.m_zeroVars = {}
        self.m_includeDrawers = includeDrawers.split(',') if includeDrawers else None
        self.m_missingChannels = set()
        self.m_missingBADChannels = set()
        self.m_keepDBForZero = keepDBValueForZero

    def _IsADC(self, region):
        return 'gain' in region.GetHash()

    def _DrawerID(self, region):
        return '_'.join(region.GetHash().split('_')[0:3])

    # **** Implementation of Worker ****

    def ProcessStart(self):
        self.m_output_data = {}
        
    def ProcessStop(self):
        # Missing channels
        for missing in self.m_missingChannels:
            self.m_output.print_log("Missing %s" % (missing.GetHash()))
        self.m_output.print_log("%d ADC:s are missing" % len(self.m_missingChannels))

        for missing in self.m_missingBADChannels:
            self.m_output.print_log("Missing BAD %s" % (missing.GetHash()))
        self.m_output.print_log("%d BAD ADC:s are missing" % len(self.m_missingBADChannels))

        # Very large differences
        self.m_output.print_log("%s ADC:s with large difference" % len(self.m_largeDiffChannels))
        for vbc in self.m_largeDiffChannels:
            self.m_output.print_log("Very large %s %s cell type: '%s' -- run value: %f db value: %f difference: %f threshold: %s isBad: %s isAffected: %s" % (vbc['region'], vbc['attribute'], vbc['ctype'], vbc['value'], vbc['db_value'], vbc['difference'], vbc['threshold'], vbc['is_bad'], vbc['is_affected']))

        # Zeros
        for zval in self.m_zeroVars:
            self.m_output.print_log('Zero %s : %s' % (zval, self.m_zeroVars[zval]))

        # Absurd values
        for aval in self.m_absurdValChannels:
            self.m_output.print_log('Absurd %s : %s' % (aval, self.m_absurdValChannels[aval]))

        self.m_output.print_log("Zeros: %d" % len(self.m_zeroVars))
        self.m_output.print_log("Large differences: %d" % len(self.m_largeDiffChannels))
        self.m_output.print_log("Absurd values: %d" % len(self.m_absurdValChannels))
        self.m_output.print_log("Total number of ADCs: %d" % self.m_nregions)
        self.m_output.print_log("Total differences: %d LG: %d HG: %d" % (self.m_ndifferences, self.m_ndifferencesLG, self.m_ndifferencesHG))
        self.m_output.print_log("Drawers with updates: %d" % len(self.m_differencesPerDrawer))

        if not self.m_runDate:
            self.m_output.print_log("Warning: No run date")

        json_output = {'data': self.m_output_data, 'lg_thresholds': self.m_lgThresholds, 'hg_thresholds': self.m_hgThresholds, 'attributes': self.m_attributes, 'date':self.m_runDate}
        
        self.m_output.add_json('PedestalValues', json_output)

        for drawerId in self.m_differencesPerDrawer:
            nlgdiffs = self.m_differencesLGPerDrawer[drawerId] if drawerId in self.m_differencesLGPerDrawer else 0
            nhgdiffs = self.m_differencesHGPerDrawer[drawerId] if drawerId in self.m_differencesHGPerDrawer else 0
            self.m_output.print_log("%s : %d LG: %d HG: %d" % (drawerId, self.m_differencesPerDrawer[drawerId], nlgdiffs, nhgdiffs))

        if self.m_onlyWriteUpdated:
            # Do not write data for drawers without updated ADCs
            for region in self.m_regions:
                # Has any ADC in the drawer been updated?
                drawerId = self._DrawerID(region)
                if drawerId not in self.m_differencesPerDrawer:
                    # find the update event
                    updateEvent = None
                    for event in region.GetEvents():
                        if event.run.runType == self.m_runTypeUpdate:
                            updateEvent = event
                            break
                    if updateEvent:
                        region.GetEvents().remove(updateEvent)
        # Only write certain drawers
        if self.m_includeDrawers:
            includedDrawers = set()
            excludedDrawers = set()
            for region in self.m_regions:
                # Require the drawer id to be present in the list of drawers to include
                drawerId = self._DrawerID(region)
                if drawerId in self.m_differencesPerDrawer:
                    if not [1 for idr in self.m_includeDrawers if idr in drawerId]:
                        if drawerId not in excludedDrawers:
                            self.m_output.print_log("Ignoring drawer '%s' in output" % drawerId)
                            excludedDrawers.add(drawerId)
                        # find the update event
                        updateEvent = None
                        for event in region.GetEvents():
                            if event.run.runType == self.m_runTypeUpdate:
                                updateEvent = event
                                break
                        if updateEvent:
                            region.GetEvents().remove(updateEvent)
                    else:
                        if drawerId not in includedDrawers:
                            self.m_output.print_log("Writing drawer '%s'" % drawerId)
                            includedDrawers.add(drawerId)
        print(" ")

    def ProcessRegion(self, region):
        # we only care about ADCs
        if not self._IsADC(region):
            return
        [part, mod, chan, gain] = region.GetNumber()

        newDBVal = None
        runValue= {}
        dbValue = {}
        isBad = False
        
        self.m_nregions += 1
        self.m_regions.add(region)

        ctype = ''
        for event in region.GetEvents():
            # Default event with DB values
            if event.run.runType == self.m_runTypeDB:
                ctype = event.data['special_cell_type']
                # Check if the part is marked as bad
                isBad = ('isStatusBad' in event.data) and event.data['isStatusBad']
                isAffected = ('isBad' in event.data) and event.data['isBad']

                self.m_runDate = event.run.getTimeSeconds()

                if isBad and self.m_verbose:
                    if 'problems' in event.data:
                        self.m_output.print_log("%s  is bad, problems: %s" % (region.GetHash(), event.data['problems']))
                    else:
                        self.m_output.print_log("%s  is bad!" % region.GetHash())
                                
                # Get all DB attributes
                for attrnr in range(len(self.m_attributes)):
                    db_attr = self.m_dbAttributes[attrnr]
                    if db_attr not in event.data:
                        self.m_output.print_log("Error: DB attribute '%s' not found in event" % (db_attr))
                        return
                    attr = self.m_attributes[attrnr]
                    if attr in dbValue:
                        if dbValue[attr] != event.data[db_attr]:
                            self.m_output.print_log("Error: ADC: %s DB attribute '%s' mismatches!!!" % (region.GetHash(), db_attr))
                    dbValue[attr] = event.data[db_attr]
            # Update event
            elif event.run.runType == self.m_runTypeUpdate:
                # Check all attributes
                for attr in self.m_attributes:
                    if attr not in event.data:
                        self.m_output.print_log("Error: Attribute '%s' not found in event" % (attr))
                        return
                    if attr in runValue:
                        if runValue[attr] != event.data[attr]:
                            self.m_output.print_log("Error: ADC: %s Run attribute '%s' mismatches!!!" % (region.GetHash(), attr))
                    runValue[attr] = event.data[attr]

        # Check for zeros
        for event in region.GetEvents():
            if event.run.runType == self.m_runTypeUpdate:
                for attrnr in range(len(self.m_attributes)):
                    attr = self.m_attributes[attrnr]

                    # very small values
                    if abs(runValue[attr]) < 1e-5:
                        # A hfnsigma2 of 0 is expected for MBTS and E4' connected channels
                        if ctype in ['MBTS', 'E4\''] and attr=='hfnsigma2':
                            self.m_output.print_log("Variable %s is zero for %s as expected evt: %s" % (attr, region.GetHash(), str(event)))
                        else:
                            if self.m_keepDBForZero:
                                self.m_zeroVars[region.GetHash()+'_'+attr] = "Attribute '%s' ADC: %s Cell type: '%s' isBad: %s isAffected: %s -- close to zero, val: %f replacing by db val: %f" % (attr, region.GetHash(), ctype, str(isBad), str(isAffected), runValue[attr], dbValue[attr])
                                event.data[attr] = dbValue[attr]
                                runValue[attr] = dbValue[attr]
                            else:
                                self.m_zeroVars[region.GetHash()+'_'+attr] = "Attribute '%s' ADC: %s Cell type: '%s' isBad: %s isAffected: %s -- close to zero, val: %f " % (attr, region.GetHash(), ctype, str(isBad), str(isAffected), runValue[attr])

        # Replace strange values
        if self.m_absurdValThresholds:
            for event in region.GetEvents():
                if event.run.runType == self.m_runTypeUpdate:
                    for attrnr in range(len(self.m_attributes)):
                        attr = self.m_attributes[attrnr]

                        # Increase the threshold for channels connected to a cell with only one PMT
                        threshold = self.m_absurdValThresholds[attrnr] * (2.0 if (ctype in ['E1m', 'E'] and 'fn' in attr) else 1.0)
                        # very large values
                        if abs(runValue[attr]) > threshold:
                            self.m_absurdValChannels[region.GetHash()+'_'+attr] =  "Attribute '%s' ADC: %s Cell type: '%s' isBad: %s isAffected: %s -- Absurd value: %f threshold: %f, replacing by db val: %f" % (attr, region.GetHash(), ctype, str(isBad), str(isAffected), runValue[attr], threshold, dbValue[attr])
                            event.data[attr] = dbValue[attr]
                            runValue[attr] = dbValue[attr]

        for event in region.GetEvents():
            if event.run.runType == self.m_runTypeUpdate:
                # check if the channel was missing in the input file
                if '_missing' in event.data:
                    if isBad:
                        self.m_missingBADChannels.add(region)
                    else:
                        self.m_missingChannels.add(region)
        # Prepare storage
        partname = region.get_partition()
        if not partname in self.m_output_data:
            self.m_output_data[partname] = {}
        if not mod in self.m_output_data[partname]:
            self.m_output_data[partname][mod] = {}
        if not chan in self.m_output_data[partname][mod]:
            self.m_output_data[partname][mod][chan] = {}
        if not gain in self.m_output_data[partname][mod][chan]:
            self.m_output_data[partname][mod][chan][gain] = [0]*(len(self.m_attributes)*2 + 1)
        output_data = self.m_output_data[partname][mod][chan][gain]
        output_data[len(self.m_attributes)*2] = isBad

        # Compare updated value to the value in the DB 
        for attrnr in range(len(self.m_attributes)):
            attr = self.m_attributes[attrnr]
            threshold = self.m_lgThresholds[attrnr] if gain == 0 else self.m_hgThresholds[attrnr]
            largeDiffThreshold = self.m_lgLargeDiffThresholds[attrnr] if gain == 0 else self.m_hgLargeDiffThresholds[attrnr]

            if attr not in dbValue:
                self.m_output.print_log("Error: unable to find DB valte for attribute '%s' region: '%s'" %(attr, region.GetHash()))
                continue

            diff = abs(runValue[attr] - dbValue[attr])
            if self.m_isRelativeThreshold[attrnr] and (dbValue[attr] != 0.0):
                diff = diff/dbValue[attr]
            
            output_data[attrnr*2] = round(runValue[attr], 6)
            output_data[attrnr*2 + 1] = round(dbValue[attr], 6)                

            if dbValue[attr] == 0.0:
                self.m_output.print_log("Warning: DB value for %s is 0, is bad: %s" % (region.GetHash(), str(isBad)))

            if (threshold > 0) and (diff >= threshold) and not (self.m_maskBad and isBad):
                diffstr = '(relative)' if self.m_isRelativeThreshold[attrnr] else ''
                self.m_output.print_log("%s %s -- run value: %f db value: %f %s difference: %f threshold: %s isBad: %s isAffected: %s" % (region.GetHash(), attr, runValue[attr], dbValue[attr], diffstr, diff, threshold, isBad, str(isAffected)))
                self.m_ndifferences += 1
                drawerId = self._DrawerID(region)
                if drawerId not in self.m_differencesPerDrawer:
                    self.m_differencesPerDrawer[drawerId] = 1
                else:
                    self.m_differencesPerDrawer[drawerId] += 1

                # Count differences per gain
                if gain == 0:
                    self.m_ndifferencesLG += 1
                else:
                    self.m_ndifferencesHG += 1

                diffsPerGain = self.m_differencesLGPerDrawer if gain == 0 else self.m_differencesHGPerDrawer
                if drawerId not in diffsPerGain:
                    diffsPerGain[drawerId] = 1
                else:
                    diffsPerGain[drawerId] += 1

                # check if the ADC has a large deviation
                if largeDiffThreshold > 0 and diff > largeDiffThreshold:
                    vbdata = {'region':region.GetHash(), 'attribute': attr, 'value':runValue[attr], 'db_value':dbValue[attr], 'difference':diff, 'threshold':largeDiffThreshold, 'is_bad':isBad, 'is_affected': isAffected, 'ctype':ctype}
                    self.m_largeDiffChannels.append(vbdata)
