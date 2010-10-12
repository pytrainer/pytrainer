import datetime
import math

#LISTPAST = [['All Time', -99999], ['Last 4 Weeks', -31],
#            ['Last 6 Months', -183], ['Last 12 Months', -366]]

class ListSearch(object):
    """ Builds SQLite condition out of search parameters"""
    def __init__(self,  parent = None, pytrainer_main = None):
        self.parent = parent    
        self.pytrainer_main = pytrainer_main
        self.title = ''
        self.sport = 0
        self.past = None
        self.duration = None        
        self.listSport = self.pytrainer_main.profile.getSportList()
        self.listPast = [['All Time', -99999], ['Last 4 Weeks', -31],
                         ['Last 6 Months', -183], ['Last 12 Months', -366]]
        self.listDuration = [['All Durations', [0,999999]],
                             ['<1 Hour', [0,3600]],
                             ['1-2 Hours', [3600,7200]],
                             ['>2 Hours', [7200,999999]]]
                             
        self.listDistance = [['All Distances', [0.0,999999.9]],
                             ['<1 km', [0.0, 1.0]],
                             ['1-5 km', [1.0, 5.0]],
                             ['5-20 km', [5.0, 20.0]],
                             ['20-50 km', [20.0, 50.0]],
                             ['50-100 km', [50.0, 100.0]],
                             ['>100 km', [100.0, 999999.9]]]
        #print self.listDistance           
        self.setup_lsa_sport()
        self.setup_lsa_past()
        self.setup_lsa_duration()
        self.setup_lsa_distance()
        
    def get_condition(self):
        """ Assembles sqlite condition """
        _search = ""
        _add_and = False
        if self.title != "":
            _search = "title like '%" +self.title + "%'"
            _add_and = True
        if self.sport > 0:
            _sport = self.listSport[self.sport-1][3]
            _here = "sport=%s" % _sport
            if _add_and:
                _search += " and " + _here
            else:
                _search = _here
            _add_and = True
        if self.listPast[self.past][1]:
            _delta = datetime.timedelta(days=self.listPast[self.past][1] )
            _date = datetime.datetime.today() + _delta
            _here = "date>'" + _date.isoformat() + "'"
            if _add_and:
                _search += " and " + _here
            else:
                _search = _here
            _add_and = True
        if self.listDuration[self.duration][1]:
            _dur_min = int(self.listDuration[self.duration][1][0])
            _dur_max = int(self.listDuration[self.duration][1][1])
            _here = "(time between %s and %s)" % (_dur_min, _dur_max)
            if _add_and:
                _search += " and " + _here
            else:
                _search = _here
            _add_and = True                 
        if self.listDistance[self.distance][1]:
            _dis_min = int(self.listDistance[self.distance][1][0])
            _dis_max = int(self.listDistance[self.distance][1][1])
            _here = "(distance between %s and %s)" % (_dis_min, _dis_max)
            if _add_and:
                _search += " and " + _here
            else:
                _search = _here
            _add_and = True                                             
        print _search
        return _search
        
    def get_listDistance(self):
        """ Not Finished. Eperimentally. Goal: compute distance intervals 
        for each sport individually from average and standard deviation.
        """  
        _all = ['All Distances', [0.0, 99999.9]]
        _back = []
        _back.append( [_all] )
        for sp in self.listSport:
            _back.append( [_all] )
        return _back    
        

    condition = property(get_condition)
    #listDuration = property(get_listDuration)
    
    def setup_lsa_sport(self):
        liststore_lsa =  self.parent.lsa_sport.get_model() 
        if self.parent.lsa_sport.get_active() is not 0:
            self.parent.lsa_sport.set_active(0) #Set first item active if isnt
        firstEntry = self.parent.lsa_sport.get_active_text()
        liststore_lsa.clear() #Delete all items
        #Re-add "All Sports"
        liststore_lsa.append([firstEntry])
        #Re-add all sports in listSport
        for i in self.listSport:
            liststore_lsa.append([i[0]])
        self.parent.lsa_sport.set_active(0)
        #Add handler manually, so above changes do not trigger recursive loop
        self.parent.lsa_sport.connect("changed", self.parent.on_listareasearch_clicked)

    def setup_lsa_past(self):
        liststore_lsa =  self.parent.lsa_past.get_model() 
        if self.parent.lsa_past.get_active() > 0:
            self.parent.lsa_past.set_active(0) #Set first item active isnt
        firstEntry = self.parent.lsa_past.get_active_text()
        liststore_lsa.clear() #Delete all items
        for i in self.listPast:
            liststore_lsa.append([i[0]])
        self.parent.lsa_past.set_active(0)    
        #Add handler manually, so above changes do not trigger recursive loop
        self.parent.lsa_past.connect("changed", self.parent.on_listareasearch_clicked)
        
    def setup_lsa_duration(self):
        liststore_lsa =  self.parent.lsa_duration.get_model() 
        if self.parent.lsa_duration.get_active() > 0:
            self.parent.lsa_duration.set_active(0) 
        firstEntry = self.parent.lsa_duration.get_active_text()
        liststore_lsa.clear() #Delete all items        
        for i in self.listDuration:
            liststore_lsa.append([i[0]])
        self.parent.lsa_duration.set_active(0)
        #Add handler manually, so above changes do not trigger recursive loop
        self.parent.lsa_duration.connect("changed", self.parent.on_listareasearch_clicked)        
        
    def setup_lsa_distance(self):
        liststore_lsa =  self.parent.lsa_distance.get_model() 
        if self.parent.lsa_distance.get_active() > 0:
            self.parent.lsa_distance.set_active(0) 
        firstEntry = self.parent.lsa_distance.get_active_text()
        liststore_lsa.clear() #Delete all items        
        for i in self.listDistance:
            liststore_lsa.append([i[0]])
        self.parent.lsa_distance.set_active(0)  
        #Add handler manually, so above changes do not trigger recursive loop
        self.parent.lsa_distance.connect("changed", self.parent.on_listareasearch_clicked)             

 