import datetime
#from profile import Profile

class ListSearch(object):
    """ Builds SQLite condition out of search parameters"""
    def __init__(self,  parent = None, pytrainer_main = None): #, data_path = None):
        self.parent = parent    
        self.pytrainer_main = pytrainer_main
        self.title = ''
        self.sport = None
        self.past = None

        #print self.pytrainer_main.__dict__.keys()
        
        #self.data_path = data_path
        # just dummy until get the right listSport
        #self.listSport = [0,1,2,3,4,5,6,7,8,9,10]
        
        self.listSport = self.pytrainer_main.profile.getSportList()
        #print self.listSport
        # make this a constant? -az               
        self.listPast = [['All Time', -99999], ['Last 4 Weeks', -31],
                      ['Last 6 Months', -183], ['Last 12 Months', -366]]
        self.setup_lsa_sport()
        self.setup_lsa_past()
        
    def get_condition(self):
        ''' sqlite condition is glued together here'''
        _search = ""
        _add_and = False
        if self.title != "":
            _search = "title like '%" +self.title + "%'"
            _add_and = True
        if self.sport > 0:
            _sport = self.listSport[self.sport-1][3]
            _here = "sport=%s" % _sport
            if _add_and:
                _search +=" and " + _here
            else:
                _search = _here
            _add_and = True
        if self.listPast[self.past][1]:
            _delta = datetime.timedelta(days=self.listPast[self.past][1] )
            _date = datetime.datetime.today() + _delta
            _here = "date>'"+ _date.isoformat() + "'"
            if _add_and:
                _search += " and " + _here
            else:
                _search = _here
            _add_and = True
        print _search
        return _search

    condition = property(get_condition)

    def setup_lsa_sport(self):
        liststore_lsa =  self.parent.lsa_sport.get_model() #az
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
        liststore_lsa =  self.parent.lsa_past.get_model() #az
        if self.parent.lsa_past.get_active() > 0:
            self.parent.lsa_past.set_active(0) #Set first item active isnt
        firstEntry = self.parent.lsa_past.get_active_text()
        liststore_lsa.clear() #Delete all items
        for i in self.listPast:
            liststore_lsa.append([i[0]])
        self.parent.lsa_past.set_active(0)    
        #Add handler manually, so above changes do not trigger recursive loop
        self.parent.lsa_past.connect("changed", self.parent.on_listareasearch_clicked)
 
